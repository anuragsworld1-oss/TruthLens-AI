"""
TruthLens AI 2.0 - Intelligent Claim Extraction
Extracts structured factual claims from article text, separates factual
statements from opinions, and identifies entities (dates, organizations,
people, locations, numerical claims) using lightweight regex + gazetteer
heuristics (no spaCy dependency to keep the install light).

This module is heuristic by design and is labelled as such in the UI; it is
NOT presented as proof of falsity.
"""

import re

# Opinion cue phrases: sentences starting with or containing these are subjective.
OPINION_CUES = [
    "i believe", "i think", "in my opinion", "personally", "it seems to me",
    "arguably", "perhaps", "maybe", "i feel", "we should", "must be", "ought to",
    "it is clear that", "one could argue", "undoubtedly", "surely",
]

# Gazetteers for lightweight entity recognition.
ORGANIZATION_KEYWORDS = [
    "nasa", "who", "isro", "fda", "united nations", "un ", "fbi", "cia",
    "parliament", "congress", "senate", "court", "supreme court", "ministry",
    "reuters", "bloomberg", "associated press", "european union", "european parliament",
    "world bank", "imf", "international monetary fund", "world health organization",
    "food and drug administration", " centers for disease", "cdc", "isa",
    "oxford university", "harvard", "mit", "stanford", "the lancet", "nature",
    "sebi", "reserve bank", "rbi", "ntsb", "faa", "iea", "wmo", "esa",
]

LOCATION_KEYWORDS = [
    "united states", "usa", "india", "china", "russia", "europe", "european",
    "washington", "new york", "london", "beijing", "moscow", "tokyo", "delhi",
    "mumbai", "bengaluru", "paris", "berlin", "geneva", "california", "texas",
    "pacific", "atlantic", "mediterranean", "middle east", "africa", "asia",
]

# Titles preceding capitalized person names.
PERSON_TITLE = r"\b(?:President|Prime Minister|Minister|Senator|Secretary|Dr\.?|Mr\.?|Ms\.?|Mrs\.?|Professor|Chair|Chairman|Director|Chief|Captain|General|Judge)\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2}"


class ClaimExtractor:
    """Extracts and structures factual claims with entity annotations."""

    def __init__(self, max_claims=5):
        self.max_claims = max_claims

    # ------------------------------------------------------------------ #
    # Entity extractors
    # ------------------------------------------------------------------ #
    @staticmethod
    def _extract_dates(text):
        dates = re.findall(
            r"\b(?:\d{1,2}(?:st|nd|rd|th)?\s+(?:January|February|March|April|May|June|July|"
            r"August|September|October|November|December)\s+\d{4}"
            r"|(?:January|February|March|April|May|June|July|August|September|October|"
            r"November|December)\s+\d{1,2},?\s+\d{4}"
            r"|\d{4}\s+(?:BCE|CE|AD|BC)"
            r"|(?:after|before|since|in|by)\s+\d{4})\b",
            text, flags=re.IGNORECASE
        )
        return list(dict.fromkeys(d.strip() for d in dates))[:5]

    @staticmethod
    def _extract_organizations(text):
        found = []
        lower = text.lower()
        for org in ORGANIZATION_KEYWORDS:
            if org.strip() in lower:
                found.append(org.strip().title())
        # Also detect all-caps acronyms (2-6 letters)
        acronyms = re.findall(r"\b([A-Z]{2,6})\b", text)
        for a in acronyms:
            if a not in ["CEO", "USA", "UK", "EU", "AI", "ML", "DNA", "RNA", "GDP", "CCTV", "DNA"]:
                found.append(a)
        return list(dict.fromkeys(found))[:6]

    @staticmethod
    def _extract_people(text):
        people = re.findall(PERSON_TITLE, text)
        return list(dict.fromkeys(p.strip() for p in people))[:5]

    @staticmethod
    def _extract_locations(text):
        lower = text.lower()
        found = [loc.title() for loc in LOCATION_KEYWORDS if loc in lower]
        return list(dict.fromkeys(found))[:5]

    @staticmethod
    def _extract_numbers(text):
        nums = re.findall(
            r"\b(?:\d+(?:\.\d+)?\s*(?:percent|%)|\$\s*\d+(?:\.\d+)?\s*(?:million|billion|trillion)?"
            r"|\d+\s*(?:million|billion|trillion|thousand)|\d{1,3}(?:,\d{3})+)\b",
            text, flags=re.IGNORECASE
        )
        return list(dict.fromkeys(n.strip() for n in nums))[:5]

    @staticmethod
    def _is_opinion(sentence):
        lower = sentence.lower().strip()
        for cue in OPINION_CUES:
            if lower.startswith(cue) or (" " + cue + " ") in (" " + lower + " "):
                return True
        return False

    # ------------------------------------------------------------------ #
    # Main extraction
    # ------------------------------------------------------------------ #
    def extract(self, text):
        """Returns a list of structured claim dicts."""
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if len(s.strip()) > 15]
        if not sentences:
            return []

        # Factual-claim indicator patterns (a sentence must hit >=1 to be a candidate).
        factual_patterns = [
            r'\b(\d+(\.\d+)?%|\$\d+|\d+\s+(million|billion|trillion|percent|years))\b',
            r'\b(confirmed|announced|discovered|published|approved|ruled|found|tested|'
            r'reported|launched|passed|signed|funded|detected|measured|estimated|concluded)\b',
            r'\b(cure|causes|destroys|eradicates|transmits|secretly|mandated|banned|'
            r'leaked|funneled|proves|exposed)\b',
            r'\b(nasa|who|isro|fda|un|fbi|parliament|court|ministry|reuters|esa|wmo|iea)\b',
            r'[\u0900-\u097F]+',  # Devanagari (Hindi) content
        ]

        scored = []
        for s in sentences:
            is_op = self._is_opinion(s)
            matches = sum(1 for pat in factual_patterns if re.search(pat, s, re.IGNORECASE))
            # Entity richness boosts claim-worthiness.
            ents = (
                len(self._extract_dates(s)) + len(self._extract_organizations(s))
                + len(self._extract_numbers(s)) + len(self._extract_people(s))
            )
            score = matches * 2 + ents
            if score > 0:
                scored.append((score, s, is_op))

        # Sort by score descending; if none matched, take top sentences as unverified.
        scored.sort(key=lambda x: -x[0])
        if not scored:
            scored = [(0, s, self._is_opinion(s)) for s in sentences[:3]]

        claims = []
        for idx, (score, sent, is_op) in enumerate(scored[:self.max_claims]):
            entities = {
                "dates": self._extract_dates(sent),
                "organizations": self._extract_organizations(sent),
                "people": self._extract_people(sent),
                "locations": self._extract_locations(sent),
                "numbers": self._extract_numbers(sent),
            }
            has_entities = any(len(v) > 0 for v in entities.values())
            claims.append({
                "id": f"claim_{idx + 1}",
                "claim_text": sent,
                "normalized_claim": sent[:160] + ("..." if len(sent) > 160 else ""),
                "claim_type": "opinion" if is_op else "factual",
                "entities": entities,
                "has_entities": has_entities,
                "extraction_score": score,
            })
        return claims


# Module-level singleton.
claim_extractor = ClaimExtractor()
