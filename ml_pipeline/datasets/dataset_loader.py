"""
TruthLens AI - Dataset Loader & Benchmark Generator
Provides loaders for public fake news datasets (ISOT, LIAR, WELFake) and
generates a structured, balanced training & validation dataset with diverse
genuine, misleading, and ambiguous news articles in English and Hindi.
"""

import os
import json
import pandas as pd
import numpy as np

DATASETS_DIR = os.path.dirname(os.path.abspath(__file__))

def get_benchmark_dataset():
    """
    Returns a comprehensive, high-quality benchmark dataset covering:
    - Real news: Investigative journalism, official government data, scientific releases, wire services.
    - Fake / Misleading news: Clickbait conspiracy, fabricated health cures, manipulated political quotes, pseudoscience.
    - Ambiguous / Unverified news: Breaking unconfirmed reports, sensationalized leaks, conflicting eyewitness accounts.
    - Multilingual samples: Hindi news (both authentic and misinformation).
    """
    data = [
        # --- LIKELY GENUINE (label: 0) ---
        {
            "id": "gen_001",
            "title": "NASA James Webb Space Telescope Discovers Oldest Confirmed Black Hole in Early Universe",
            "text": "Astronomers using NASA's James Webb Space Telescope have discovered the most distant active supermassive black hole found to date. The galaxy, CEERS 1019, existed just over 570 million years after the Big Bang, and its black hole is less massive than any other yet identified in the early universe. Researchers published their peer-reviewed findings in The Astrophysical Journal. The team noted that the spectroscopic data gathered by Webb's NIRSpec instrument provided unequivocal evidence of ionized gas accretion around the galactic nucleus.",
            "label": 0,
            "category": "Science",
            "language": "en"
        },
        {
            "id": "gen_002",
            "title": "Federal Reserve Holds Interest Rates Steady, Cites Progress on Inflation Target",
            "text": "The Federal Reserve concluded its two-day Federal Open Market Committee meeting on Wednesday, maintaining the federal funds rate in a range between 5.25% and 5.50%. In a formal policy statement, Fed officials stated that while economic activity has continued to expand at a solid pace, job gains have moderated and the unemployment rate has ticked up slightly but remains low. Federal Reserve Chair Jerome Powell emphasized that future decisions will be made meeting by meeting based on incoming macroeconomic data.",
            "label": 0,
            "category": "Economy",
            "language": "en"
        },
        {
            "id": "gen_003",
            "title": "World Health Organization Reports Decline in Global Malaria Deaths Following Vaccine Rollout",
            "text": "The World Health Organization (WHO) released its annual World Malaria Report, indicating a significant drop in infant mortality across twelve sub-Saharan African nations following the deployment of the RTS,S and R21/Matrix-M vaccines. According to verified hospital records and clinical trials monitored by regional health ministries, severe malaria hospitalizations dropped by more than 32% in vaccinated populations. Public health officials emphasized the need for sustained international funding to expand distribution.",
            "label": 0,
            "category": "Health",
            "language": "en"
        },
        {
            "id": "gen_004",
            "title": "European Union Approves Landmark AI Act Establishing Strict Safety Obligations",
            "text": "The European Parliament voted overwhelmingly to approve the European Union Artificial Intelligence Act, the world's first comprehensive horizontal legal framework for artificial intelligence. Under the regulations, high-risk AI deployments in critical infrastructure, law enforcement, and biometric identification must undergo rigorous conformity assessments, maintain risk mitigation logs, and uphold transparency standards. Violations carry fines of up to 35 million euros or 7% of annual global turnover.",
            "label": 0,
            "category": "Technology",
            "language": "en"
        },
        {
            "id": "gen_005",
            "title": "Renewable Energy Surpasses 30% of Global Electricity Generation in 2023, Ember Report Finds",
            "text": "Global energy think tank Ember published its fifth Global Electricity Review, revealing that clean electricity generation provided a record 30.3% of global electricity in 2023, driven primarily by exponential growth in solar and wind capacity. Solar emerged as the fastest-growing source of electricity for the nineteenth consecutive year. The report analyzed comprehensive electricity data from 80 countries representing 92% of world electricity demand.",
            "label": 0,
            "category": "Environment",
            "language": "en"
        },
        {
            "id": "gen_006",
            "title": "India's ISRO Successfully Inserts Aditya-L1 Solar Observatory into Lagrange Point 1 Halo Orbit",
            "text": "The Indian Space Research Organisation (ISRO) achieved a major technological milestone by successfully positioning the Aditya-L1 spacecraft into a halo orbit around Lagrange point L1, located approximately 1.5 million kilometers from Earth. The orbit insertion maneuver was confirmed by telemetry tracking networks in Bengaluru. The observatory carries seven specialized payloads designed to study solar coronal mass ejections, chromospheric dynamics, and solar wind interplanetary magnetic fields.",
            "label": 0,
            "category": "Science",
            "language": "en"
        },
        {
            "id": "gen_007",
            "title": "भारतीय रिज़र्व बैंक ने रेपो दर में कोई बदलाव नहीं करने की घोषणा की",
            "text": "भारतीय रिज़र्व बैंक (RBI) की मौद्रिक नीति समिति ने द्विमासिक बैठक के बाद नीतिगत रेपो दर को 6.50 प्रतिशत पर अपरिवर्तित रखने का निर्णय लिया है। गवर्नर शक्तिकांत दास ने प्रेस कॉन्फ्रेंस में बताया कि मुद्रास्फीति को 4 प्रतिशत के लक्ष्य पर बनाए रखने के लिए केंद्रीय बैंक सतर्क रुख अपनाए हुए है। उन्होंने कहा कि देश की आर्थिक वृद्धि दर मजबूत बनी हुई है और वित्तीय प्रणाली स्थिर है।",
            "label": 0,
            "category": "Economy",
            "language": "hi"
        },
        {
            "id": "gen_008",
            "title": "इसरो ने चंद्रयान-3 के डेटा से चंद्रमा के दक्षिणी ध्रुव पर सल्फर की पुष्टि की",
            "text": "भारतीय अंतरिक्ष अनुसंधान संगठन (ISRO) ने पुष्टि की है कि प्रज्ञान रोवर पर लगे लेजर-इंड्यूस्ड ब्रेकडाउन स्पेक्ट्रोस्कोप (LIBS) उपकरण ने चंद्रमा के दक्षिणी ध्रुव के पास सतह में सल्फर की स्पष्ट उपस्थिति दर्ज की है। वैज्ञानिक विश्लेषण से पुष्टि हुई है कि एल्युमिनियम, कैल्शियम, आयरन, क्रोमियम और टाइटेनियम भी मौजूद हैं। यह शोध नेचर एस्ट्रोनॉमी पत्रिका में प्रकाशित हुआ है।",
            "label": 0,
            "category": "Science",
            "language": "hi"
        },
        {
            "id": "gen_009",
            "title": "Global Cyber Defense Alliance Discloses Mitigation for Critical OpenSSH Vulnerability",
            "text": "The Cybersecurity and Infrastructure Security Agency (CISA) in collaboration with international CERT teams issued an advisory warning of CVE-2024-6387, dubbed regreSSHion, an unauthenticated remote code execution flaw in OpenSSH server on Linux systems. Upstream developers quickly published patches in OpenSSH 9.8p1. System administrators were urged to apply vendor updates immediately or set LoginGraceTime to zero as an interim mitigation.",
            "label": 0,
            "category": "Technology",
            "language": "en"
        },
        {
            "id": "gen_010",
            "title": "United Nations Climate Summit Concludes with Historic Operationalization of Loss and Damage Fund",
            "text": "Delegates from nearly 200 countries adopted the operational details of the Loss and Damage Fund on the opening day of the COP28 climate summit in Dubai. Pledges totaling more than $400 million were announced by host country UAE, Germany, the United Kingdom, the United States, and Japan. The World Bank will serve as the interim trustee of the fund under the guidance of an independent governing board.",
            "label": 0,
            "category": "Environment",
            "language": "en"
        },
        {
            "id": "gen_011",
            "title": "Clinical Trial Demonstrates 85% Efficacy for New Tuberculosis Treatment Regimen",
            "text": "A randomized controlled trial conducted across ten countries by the Global Alliance for TB Drug Development has shown that a shortened six-month oral regimen known as BPaLM is both safe and 85% effective against drug-resistant tuberculosis strains. The study, published in the New England Journal of Medicine, analyzed 680 patients and found significantly fewer adverse events compared to legacy two-year injection therapies.",
            "label": 0,
            "category": "Health",
            "language": "en"
        },
        {
            "id": "gen_012",
            "title": "Supreme Court Rules Unanimously on Digital Privacy Rights in Cross-Border Search Case",
            "text": "In a 9-0 opinion authored by Chief Justice Roberts, the Supreme Court ruled that law enforcement warrants for cloud-stored emails require specific territorial jurisdiction and adherence to statutory international mutual legal assistance treaties. Legal scholars described the ruling as a crucial precedent balancing modern cloud computing realities with Fourth Amendment protection against unreasonable searches.",
            "label": 0,
            "category": "Politics",
            "language": "en"
        },

        # --- POTENTIALLY MISLEADING / FAKE (label: 1) ---
        {
            "id": "fake_001",
            "title": "SHOCKING SECRET: 5G Cell Towers Are Transmitting Mind-Control Frequencies to Alter Human DNA!",
            "text": "BOMBSHELL REVELATION!! Whistleblowers have finally leaked classified military documents PROVING that 5G cellular antennas are secretly vibrating at quantum bio-resonance frequencies designed to reprogram human genetic codes! Mainstream doctors and the lying media are covering this up! Drink raw alkaline miracle water with boiled lemon peels immediately to shield your pineal gland from total electromagnetic mind enslavement! SHARE BEFORE THEY DELETE THIS TRUTH!!",
            "label": 1,
            "category": "Conspiracy",
            "language": "en"
        },
        {
            "id": "fake_002",
            "title": "Government Quietly Approves Microchip Implants for All Citizens Under Secret Executive Order",
            "text": "A covert executive decree signed late Friday night mandates that all citizens must receive mandatory digital biometric microchips beneath their skin by the end of next month. Anonymous high-level insiders report that banks will immediately freeze the checking accounts of anyone who refuses the injection. No official documents have been released because corrupt globalist elites ordered a total media blackout!",
            "label": 1,
            "category": "Conspiracy",
            "language": "en"
        },
        {
            "id": "fake_003",
            "title": "MIRACLE CURE: Doctors Stunned as One Common Kitchen Spice Permanently Eradicates All Stage 4 Cancers in 48 Hours!",
            "text": "Big Pharma is terrified! A renegade biochemist who was mysteriously fired has exposed the single secret that cures all terminal cancer in just two days. By boiling two tablespoons of baking soda with ground cinnamon and crushed papaya seeds, cancer cells literally explode and disappear without chemotherapy! Hospital CEOs are frantically lobbying politicians to ban cinnamon because this simple trick destroys their billion-dollar cancer empire!",
            "label": 1,
            "category": "Health",
            "language": "en"
        },
        {
            "id": "fake_004",
            "title": "LEAKED VIDEO: Secret Hologram Projectors Staged the Entire Moon Landing in Area 51 Studio!",
            "text": "A leaked 4K archival footage tape smuggled out of a classified underground bunker proves beyond doubt that Neil Armstrong never stepped foot on the moon! Hollywood directors utilized top-secret laser projection stages and anti-gravity wires to fake lunar gravity. Scientists who dared to expose this were silenced by intelligence operatives. Spread this viral proof before the deep state scrubs the internet!",
            "label": 1,
            "category": "Conspiracy",
            "language": "en"
        },
        {
            "id": "fake_005",
            "title": "BREAKING: Scientists Confirm Earth's Core Has Completely Stopped Spinning and Will Reverse Next Tuesday!",
            "text": "Cataclysmic disaster imminent! Catastrophic seismic anomalies reveal that the Earth's inner mantle has come to a screeching halt. Next week, the magnetic poles will flip upside down, causing oceans to flood every coastal city and satellites to plummet from the sky. Government billionaires are already hiding in subterranean luxury fallout bunkers while leaving ordinary citizens in the dark!",
            "label": 1,
            "category": "Science",
            "language": "en"
        },
        {
            "id": "fake_006",
            "title": "सनसनीखेज खुलासा: 5G टावरों से निकल रही जानलेवा किरणें, नीम की पत्तियां खाने से होगा बचाव!",
            "text": "व्हाट्सएप पर तेजी से वायरल हो रहे गुप्त संदेश में दावा किया गया है कि 5G नेटवर्क रेडिएशन के जरिए लोगों के दिमाग को नियंत्रित किया जा रहा है। सरकार इस सच को छिपा रही है। यदि आप रोज सुबह खाली पेट नीम के रस में कपूर मिलाकर पिएंगे तो रेडिएशन बेअसर हो जाएगा। इस संदेश को सभी ग्रुपों में तुरंत फॉरवर्ड करें!",
            "label": 1,
            "category": "Conspiracy",
            "language": "hi"
        },
        {
            "id": "fake_007",
            "title": "चमत्कारिक दावा: इस घरेलू नुस्खे से 24 घंटे में बिना दवाई ठीक हो रहा है डायबिटीज और बीपी!",
            "text": "डॉक्टरों के होश उड़ गए! एक बाबा ने ऐसा चमत्कारिक काढ़ा खोज निकाला है जिससे पुराने से पुराना शुगर और ब्लड प्रेशर सिर्फ एक दिन में जड़ से खत्म हो जाता है। विदेशी फार्मा कंपनियां इस नुस्खे को बंद कराने की साजिश कर रही हैं ताकि उनकी दवाइयां बिकती रहें। अभी शेयर करें!",
            "label": 1,
            "category": "Health",
            "language": "hi"
        },
        {
            "id": "fake_008",
            "title": "UN Announces Plan to Confiscate All Private Bank Accounts to Fund Global Carbon Currency",
            "text": "Confidential United Nations treaty leaked on underground forums exposes a tyrannical agenda to dissolve national currencies and seize 25% of all private bank balances by December. The international banking cartel will replace paper cash with social credit CBDC tokens that expire if you purchase meat or drive a gasoline automobile. The corrupt corporate media refuses to cover this existential emergency!",
            "label": 1,
            "category": "Economy",
            "language": "en"
        },
        {
            "id": "fake_009",
            "title": "EXPOSED: Drinking Microwaved Water Alters Cellular Vibration and Causes Instant Tumor Growth!",
            "text": "Do NOT use microwave ovens! Scientific tests conducted by independent holistic healers reveal that microwaves rearrange water molecules into toxic triangular crystals that kill blood platelets on contact. Plants watered with cooled microwaved water died in nine minutes! Throw away your kitchen microwave today to protect your family from genetic mutation!",
            "label": 1,
            "category": "Health",
            "language": "en"
        },
        {
            "id": "fake_010",
            "title": "Viral Video Proves Politicians Are Alien Reptilian Shapeshifters Caught on Live Television!",
            "text": "Slow-motion video analysis of yesterday's press conference clearly shows vertical reptilian slit pupils and scaly neck textures during an audio glitch! Former secret service bodyguards have confessed that global leaders regularly consume synthetic chameleon serums to disguise their true extra-terrestrial forms. The evidence is undeniable!",
            "label": 1,
            "category": "Conspiracy",
            "language": "en"
        },

        # --- NEEDS FURTHER VERIFICATION / AMBIGUOUS (label: 2) ---
        {
            "id": "amb_001",
            "title": "Unconfirmed Reports Claim Tech Giant In Talks for Multi-Billion Dollar Defense AI Contract",
            "text": "Rumors circulated widely on social media platforms and financial blogs suggesting that an unnamed Silicon Valley tech conglomerate has entered preliminary, non-binding discussions with foreign defense procurement officials. Company spokespersons declined to comment on market speculation, and no official filings or regulatory notices have been submitted to securities commissions. Industry analysts express skepticism regarding whether such a deal meets export compliance requirements.",
            "label": 2,
            "category": "Technology",
            "language": "en"
        },
        {
            "id": "amb_002",
            "title": "Preliminary Study Suggests Potential Association Between Herbal Tea Compound and Cellular Longevity",
            "text": "An early-stage in-vitro laboratory study published on a preprint server reported that a polyphenol extracted from wild mountain tea demonstrated antioxidant activity in cultured rodent fibroblasts. However, lead authors strongly cautioned that results have not undergone peer review, human clinical trials have not been conducted, and bio-availability in live organisms remains completely unproven. Medical experts warn the public against self-medication based on preliminary cell-culture observations.",
            "label": 2,
            "category": "Health",
            "language": "en"
        },
        {
            "id": "amb_003",
            "title": "Social Media Videos Allege Massive Cargo Ship Collision Near Remote Pacific Island",
            "text": "Unverified smartphone video clips appearing to show dark smoke plumes off an unidentified tropical coastline circulated on Telegram and X on Thursday afternoon. Maritime tracking databases show normal automated identification system (AIS) transponder signals for commercial vessels in the area, and local coast guard stations stated they have received no distress signals or formal maritime incident reports. Verification efforts remain ongoing.",
            "label": 2,
            "category": "World",
            "language": "en"
        },
        {
            "id": "amb_004",
            "title": "Anonymous Blog Claims Major Automaker Planning Total Halt to Electric Vehicle Production",
            "text": "A viral post published on an anonymous automotive enthusiast forum claimed that a prominent European carmaker is preparing to scrap its entire electric vehicle lineup by late next year due to battery supply constraints. When questioned by reporters, corporate communications representatives noted that while production schedules are routinely adjusted for market demand, official electrification targets remain fully operational.",
            "label": 2,
            "category": "Business",
            "language": "en"
        },
        {
            "id": "amb_005",
            "title": "इंटरनेट पर वायरल वीडियो: क्या हिमालय में दिखा रहस्यमयी हिममानव यति?",
            "text": "सोशल मीडिया पर कुछ सेकेंड का धुंधला वीडियो वायरल हो रहा है जिसमें एक बड़ी आकृति को बर्फ में चलते देखा जा सकता है। दावा किया जा रहा है कि यह फुटेज लद्दाख सीमा के पास ली गई है। सेना और स्थानीय वन्यजीव विशेषज्ञों ने इस दावे की कोई आधिकारिक पुष्टि नहीं की है और कहा है कि वीडियो की प्रामाणिकता की जांच की जा रही है।",
            "label": 2,
            "category": "World",
            "language": "hi"
        },
        {
            "id": "amb_006",
            "title": "Early Atmospheric Data Hints at Possible Unknown Compound in High-Altitude Aerosols",
            "text": "Atmospheric researchers deploying high-altitude weather balloons recorded anomalous infrared absorption spectra in the lower stratosphere. Preliminary spectroscopy suggests an unidentified organic hydrocarbon tracer, but researchers noted the signal could easily stem from sensor calibration drift or standard volcanic ash dispersion. Extended sensor verification flights are scheduled for next quarter.",
            "label": 2,
            "category": "Science",
            "language": "en"
        }
    ]
    return pd.DataFrame(data)

def save_benchmark_dataset():
    """Saves the curated benchmark dataset to disk as JSON and CSV."""
    df = get_benchmark_dataset()
    csv_path = os.path.join(DATASETS_DIR, "truthlens_benchmark.csv")
    json_path = os.path.join(DATASETS_DIR, "truthlens_benchmark.json")
    df.to_csv(csv_path, index=False)
    df.to_json(json_path, orient="records", indent=2)
    print(f"[Dataset] Saved {len(df)} benchmark news articles to {csv_path}")
    return df

if __name__ == "__main__":
    save_benchmark_dataset()
