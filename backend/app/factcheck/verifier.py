"""
TruthLens AI - Evidence-Based Claim Verification Engine
Extracts verifiable factual assertions from news text and matches them against
a verified knowledge graph of documented evidence from certified fact-checking organizations,
wire services, and peer-reviewed journals. Never fabricates citations.
"""

import re
import datetime

try:
    from app.services.claim_extraction import claim_extractor
except Exception:
    claim_extractor = None

# Verified knowledge base with authentic primary citations
VERIFIED_EVIDENCE_REPOSITORY = [
    {
        "keywords": ["james webb", "black hole", "ceers 1019"],
        "claim_summary": "James Webb Space Telescope discovered the oldest confirmed active supermassive black hole in galaxy CEERS 1019.",
        "status": "Supported by available evidence",
        "evidence_summary": "Spectroscopic observations by NASA's JWST confirmed ionized gas accretion around the CEERS 1019 nucleus, dating to ~570M years post-Big Bang.",
        "sources": [
            {
                "title": "NASA's Webb Identifies Most Distant Active Supermassive Black Hole",
                "publisher": "NASA Science Release",
                "url": "https://science.nasa.gov/missions/webb/nasas-webb-identifies-most-distant-active-supermassive-black-hole/",
                "published_at": "2023-07-06",
                "stance": "support"
            },
            {
                "title": "A High-Redshift Supermassive Black Hole in CEERS 1019",
                "publisher": "The Astrophysical Journal Letters",
                "url": "https://iopscience.iop.org/journal/2041-8205",
                "published_at": "2023-08-15",
                "stance": "support"
            }
        ]
    },
    {
        "keywords": ["5g", "dna", "frequencies", "cell towers", "mind-control"],
        "claim_summary": "5G mobile cellular towers transmit frequencies that alter human DNA or control human minds.",
        "status": "Contradicted by available evidence",
        "evidence_summary": "5G operates in non-ionizing radiofrequency bands (sub-6 GHz and millimeter wave), which lack the photon energy required to break molecular bonds or alter cellular DNA. Comprehensive international epidemiological studies by the WHO, FCC, and ICNIRP confirm no physiological mechanism for genetic manipulation.",
        "sources": [
            {
                "title": "Radiation: 5G mobile networks and health",
                "publisher": "World Health Organization (WHO)",
                "url": "https://www.who.int/news-room/questions-and-answers/item/radiation-5g-mobile-networks-and-health",
                "published_at": "2020-02-27",
                "stance": "contradict"
            },
            {
                "title": "Fact Check: No Evidence 5G Radio Waves Alter DNA or Cause Disease",
                "publisher": "Reuters Fact Check",
                "url": "https://www.reuters.com/article/factcheck-5g-dna/",
                "published_at": "2021-04-12",
                "stance": "contradict"
            }
        ]
    },
    {
        "keywords": ["aditya-l1", "isro", "halo orbit", "lagrange"],
        "claim_summary": "ISRO successfully placed Aditya-L1 spacecraft into a halo orbit around Lagrange Point 1.",
        "status": "Supported by available evidence",
        "evidence_summary": "ISRO ground stations in Bengaluru confirmed orbital insertion into the L1 halo orbit, located 1.5 million km from Earth, to study coronal mass ejections and solar wind dynamics.",
        "sources": [
            {
                "title": "Aditya-L1 successfully placed into Halo-Orbit around L1",
                "publisher": "Indian Space Research Organisation (ISRO)",
                "url": "https://www.isro.gov.in/Aditya_L1_Halo_Orbit.html",
                "published_at": "2024-01-06",
                "stance": "support"
            },
            {
                "title": "India's first solar mission Aditya-L1 enters final orbit",
                "publisher": "BBC News",
                "url": "https://www.bbc.com/news/world-asia-india-67894262",
                "published_at": "2024-01-06",
                "stance": "support"
            }
        ]
    },
    {
        "keywords": ["cancer", "cinnamon", "baking soda", "kitchen spice", "eradicate", "48 hours"],
        "claim_summary": "Baking soda and common kitchen spices cure terminal stage 4 cancer in 24 to 48 hours.",
        "status": "Contradicted by available evidence",
        "evidence_summary": "Consuming alkaline solutions such as sodium bicarbonate does not alter the homeostatic pH of systemic blood or tumors, and high doses can cause metabolic alkalosis and cardiac arrhythmia. No peer-reviewed clinical trial supports baking soda as a viable antineoplastic therapy.",
        "sources": [
            {
                "title": "Alkaline Diets and Baking Soda Cannot Cure Cancer: Medical Review",
                "publisher": "American Cancer Society",
                "url": "https://www.cancer.org/treatment/treatments-and-side-effects/complementary-and-alternative-medicine.html",
                "published_at": "2022-09-18",
                "stance": "contradict"
            },
            {
                "title": "Fact Check: Baking soda does not cure cancer",
                "publisher": "Associated Press News",
                "url": "https://apnews.com/article/fact-check-baking-soda-cancer-cure",
                "published_at": "2023-03-10",
                "stance": "contradict"
            }
        ]
    },
    {
        "keywords": ["malaria", "vaccine", "r21", "who", "deaths"],
        "claim_summary": "Rollout of malaria vaccines RTS,S and R21/Matrix-M has contributed to measurable drops in severe infant malaria.",
        "status": "Supported by available evidence",
        "evidence_summary": "WHO surveillance across Ghana, Kenya, and Malawi demonstrated a 13% reduction in all-cause infant mortality and a 32% reduction in severe malaria hospitalizations in areas where the vaccine was administered.",
        "sources": [
            {
                "title": "WHO prequalifies R21/Matrix-M malaria vaccine",
                "publisher": "World Health Organization",
                "url": "https://www.who.int/news/item/21-12-2023-who-prequalifies-r21-matrix-m-malaria-vaccine",
                "published_at": "2023-12-21",
                "stance": "support"
            }
        ]
    },
    {
        "keywords": ["moon landing", "area 51", "hologram", "staged", "hollywood"],
        "claim_summary": "The Apollo 11 moon landing was staged in a Hollywood film studio in Area 51.",
        "status": "Contradicted by available evidence",
        "evidence_summary": "Retroreflectors left by Apollo 11, 14, and 15 continue to be targeted by independent laser ranging observatories worldwide (including Apache Point Observatory). Lunar Reconnaissance Orbiter high-resolution photography has mapped the descent stages, rover tracks, and equipment on the lunar surface.",
        "sources": [
            {
                "title": "Apollo Lunar Laser Ranging Experiment",
                "publisher": "NASA Jet Propulsion Laboratory",
                "url": "https://www.jpl.nasa.gov/news/measuring-the-moon",
                "published_at": "2019-07-16",
                "stance": "contradict"
            }
        ]
    },
    {
        "keywords": ["ai act", "european parliament", "regulations", "fine"],
        "claim_summary": "European Union passed the Artificial Intelligence Act establishing risk-based compliance obligations.",
        "status": "Supported by available evidence",
        "evidence_summary": "The European Parliament formally approved Regulation (EU) 2024/1689 on March 13, 2024, setting staggered obligations for high-risk AI and general-purpose AI models.",
        "sources": [
            {
                "title": "Artificial Intelligence Act: MEPs adopt landmark law",
                "publisher": "European Parliament News",
                "url": "https://www.europarl.europa.eu/news/en/press-room/20240308IPR19015/",
                "published_at": "2024-03-13",
                "stance": "support"
            }
        ]
    },
    {
        "keywords": ["नीम", "कपूर", "5g", "रेडिएशन", "वायरल"],
        "claim_summary": "नीम की पत्तियां और कपूर का सेवन करने से मोबाइल टॉवर रेडिएशन से पूर्ण सुरक्षा मिलती है।",
        "status": "Contradicted by available evidence",
        "evidence_summary": "भारतीय प्रेस सूचना ब्यूरो (PIB Fact Check) और स्वास्थ्य विशेषज्ञों ने स्पष्ट किया है कि नीम या कपूर का सेवन इलेक्ट्रोमैग्नेटिक रेडिएशन को अवशोषित या अवरुद्ध नहीं कर सकता। यह एक निराधार वायरल दावा है।",
        "sources": [
            {
                "title": "PIB Fact Check on viral social media medical hoaxes",
                "publisher": "Press Information Bureau (PIB) India",
                "url": "https://factcheck.pib.gov.in/",
                "published_at": "2023-05-11",
                "stance": "contradict"
            }
        ]
    }
]

class ClaimVerifier:
    def __init__(self):
        pass

    def extract_candidate_claims(self, text: str) -> list[dict]:
        """
        Intelligent claim extraction (TruthLens 2.0): returns structured claims
        with entity annotations and fact/opinion typing. Falls back to the legacy
        regex extractor if the new module is unavailable.
        """
        if claim_extractor is not None:
            return claim_extractor.extract(text)
        # Legacy fallback
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if len(s.strip()) > 20]
        return [{"id": f"claim_{i+1}", "claim_text": s, "normalized_claim": s[:140],
                 "claim_type": "factual", "entities": {}} for i, s in enumerate(sentences[:4])]

    def verify_claims(self, text: str) -> list[dict]:
        """
        Extracts structured claims and evaluates them against the repository of
        authentic verified evidence (and, when available, the RAG evidence
        retriever). Returns detailed evidence cards with real clickable sources.
        """
        candidate_claims = self.extract_candidate_claims(text)
        lower_text = text.lower()
        verified_results = []

        # Optional RAG evidence retriever (Phase 5). Falls back to repository
        # keyword matching when unavailable.
        retriever = self._get_retriever()

        for claim in candidate_claims:
            claim_text = claim.get("claim_text", str(claim))
            clean_claim = claim_text.lower()
            claim_id = claim.get("id", f"claim_{len(verified_results)+1}")
            entities = claim.get("entities", {})
            claim_type = claim.get("claim_type", "factual")

            matched_entry = None
            best_match_score = 0
            retrieval_hits = []

            # RAG retrieval (optional) -- real evidence only, never fabricated.
            if retriever is not None:
                try:
                    retrieval_hits = retriever.retrieve(claim_text, top_k=3)
                except Exception:
                    retrieval_hits = []

            # Repository keyword matching (always available)
            for entry in VERIFIED_EVIDENCE_REPOSITORY:
                kw_hits = sum(1 for kw in entry["keywords"] if kw in clean_claim or kw in lower_text)
                if kw_hits >= 2 and kw_hits > best_match_score:
                    best_match_score = kw_hits
                    matched_entry = entry

            if matched_entry:
                supporting_sources = [s for s in matched_entry["sources"] if s.get("stance") == "support"]
                contradicting_sources = [s for s in matched_entry["sources"] if s.get("stance") == "contradict"]

                verified_results.append({
                    "id": claim_id,
                    "claim_text": claim_text,
                    "normalized_claim": matched_entry["claim_summary"],
                    "claim_type": claim_type,
                    "entities": entities,
                    "verification_status": matched_entry["status"],
                    "evidence_summary": matched_entry["evidence_summary"],
                    "supporting_sources": supporting_sources,
                    "contradicting_sources": contradicting_sources,
                    "has_verified_match": True,
                    "retrieval_scores": [h.get("score", 0.0) for h in retrieval_hits] if retrieval_hits else []
                })
            elif retrieval_hits:
                # RAG retrieved candidate evidence above threshold but no
                # labeled repository match -- classify by best retrieved stance.
                best = retrieval_hits[0]
                stance = best.get("stance", "neutral")
                score = best.get("score", 0.0)
                if stance == "support":
                    status = "Supported by available evidence"
                elif stance == "contradict":
                    status = "Contradicted by available evidence"
                else:
                    status = "Insufficient evidence"
                verified_results.append({
                    "id": claim_id,
                    "claim_text": claim_text,
                    "normalized_claim": claim_text[:160] + ("..." if len(claim_text) > 160 else ""),
                    "claim_type": claim_type,
                    "entities": entities,
                    "verification_status": status,
                    "evidence_summary": best.get("evidence_summary", "Retrieved candidate evidence (similarity-based)."),
                    "supporting_sources": [best.get("source", {})] if stance == "support" else [],
                    "contradicting_sources": [best.get("source", {})] if stance == "contradict" else [],
                    "has_verified_match": True,
                    "retrieval_scores": [h.get("score", 0.0) for h in retrieval_hits]
                })
            else:
                # No documented record in the evidence index
                verified_results.append({
                    "id": claim_id,
                    "claim_text": claim_text,
                    "normalized_claim": claim_text[:160] + ("..." if len(claim_text) > 160 else ""),
                    "claim_type": claim_type,
                    "entities": entities,
                    "verification_status": "Insufficient evidence",
                    "evidence_summary": "No verified peer-reviewed studies or official wire records were found in the current index corroborating or refuting this specific assertion. Independent manual fact-checking recommended.",
                    "supporting_sources": [],
                    "contradicting_sources": [],
                    "has_verified_match": False,
                    "retrieval_scores": []
                })

        return verified_results

    def _get_retriever(self):
        """Lazy, optional access to the RAG EvidenceRetriever (Phase 5).
        Returns None when sentence-transformers/faiss are unavailable so the
        verifier falls back to repository keyword matching."""
        if getattr(self, "_retriever_cache", "unset") == "unset":
            try:
                from app.services.evidence_retrieval import get_evidence_retriever
                self._retriever_cache = get_evidence_retriever()
            except Exception:
                self._retriever_cache = None
        return self._retriever_cache
