import React from 'react';
import { Sparkles, X, CheckCircle2, AlertTriangle, HelpCircle } from 'lucide-react';

export const SAMPLE_ARTICLES = [
  {
    id: 'sample_jwst',
    title: 'NASA James Webb Space Telescope Discovers Oldest Confirmed Black Hole in Early Universe',
    text: "Astronomers using NASA's James Webb Space Telescope have discovered the most distant active supermassive black hole found to date. The galaxy, CEERS 1019, existed just over 570 million years after the Big Bang, and its black hole is less massive than any other yet identified in the early universe. Researchers published their peer-reviewed findings in The Astrophysical Journal. The team noted that the spectroscopic data gathered by Webb's NIRSpec instrument provided unequivocal evidence of ionized gas accretion around the galactic nucleus.",
    category: 'Likely Genuine (Science)',
    language: 'en'
  },
  {
    id: 'sample_5g',
    title: 'SHOCKING SECRET: 5G Cell Towers Are Transmitting Mind-Control Frequencies to Alter Human DNA!',
    text: "BOMBSHELL REVELATION!! Whistleblowers have finally leaked classified military documents PROVING that 5G cellular antennas are secretly vibrating at quantum bio-resonance frequencies designed to reprogram human genetic codes! Mainstream doctors and the lying media are covering this up! Drink raw alkaline miracle water with boiled lemon peels immediately to shield your pineal gland from total electromagnetic mind enslavement! SHARE BEFORE THEY DELETE THIS TRUTH!!",
    category: 'Potentially Misleading (Conspiracy)',
    language: 'en'
  },
  {
    id: 'sample_prelim',
    title: 'Preliminary Study Suggests Potential Association Between Herbal Tea Compound and Cellular Longevity',
    text: "An early-stage in-vitro laboratory study published on a preprint server reported that a polyphenol extracted from wild mountain tea demonstrated antioxidant activity in cultured rodent fibroblasts. However, lead authors strongly cautioned that results have not undergone peer review, human clinical trials have not been conducted, and bio-availability in live organisms remains completely unproven. Medical experts warn the public against self-medication based on preliminary cell-culture observations.",
    category: 'Needs Verification (Preprint)',
    language: 'en'
  },
  {
    id: 'sample_hindi_real',
    title: 'इसरो ने चंद्रयान-3 के डेटा से चंद्रमा के दक्षिणी ध्रुव पर सल्फर की पुष्टि की',
    text: "भारतीय अंतरिक्ष अनुसंधान संगठन (ISRO) ने पुष्टि की है कि प्रज्ञान रोवर पर लगे लेजर-इंड्यूस्ड ब्रेकडाउन स्पेक्ट्रोस्कोप (LIBS) उपकरण ने चंद्रमा के दक्षिणी ध्रुव के पास सतह में सल्फर की स्पष्ट उपस्थिति दर्ज की है। वैज्ञानिक विश्लेषण से पुष्टि हुई है कि एल्युमिनियम, कैल्शियम, आयरन, क्रोमियम और टाइटेनियम भी मौजूद हैं। यह शोध नेचर एस्ट्रोनॉमी पत्रिका में प्रकाशित हुआ है।",
    category: 'Likely Genuine (Hindi Science)',
    language: 'hi'
  },
  {
    id: 'sample_hindi_fake',
    title: 'सनसनीखेज खुलासा: 5G टावरों से निकल रही जानलेवा किरणें, नीम की पत्तियां खाने से होगा बचाव!',
    text: "व्हाट्सएप पर तेजी से वायरल हो रहे गुप्त संदेश में दावा किया गया है कि 5G नेटवर्क रेडिएशन के जरिए लोगों के दिमाग को नियंत्रित किया जा रहा है। सरकार इस सच को छिपा रही है। यदि आप रोज सुबह खाली पेट नीम के रस में कपूर मिलाकर पिएंगे तो रेडिएशन बेअसर हो जाएगा। इस संदेश को सभी ग्रुपों में तुरंत फॉरवर्ड करें!",
    category: 'Potentially Misleading (Hindi Hoax)',
    language: 'hi'
  }
];

export default function SampleArticleModal({ isOpen, onClose, onSelect }) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm animate-fadeIn">
      <div className="bg-[#141F35] rounded-2xl border border-white/10 w-full max-w-2xl max-h-[85vh] overflow-hidden flex flex-col shadow-2xl">
        {/* Header */}
        <div className="p-5 border-b border-white/10 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-purple-400" />
            <h3 className="text-lg font-bold text-white">Select Benchmark News Sample</h3>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-white/5 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content list */}
        <div className="p-5 overflow-y-auto space-y-3">
          {SAMPLE_ARTICLES.map((item) => (
            <div
              key={item.id}
              onClick={() => {
                onSelect(item);
                onClose();
              }}
              className="p-4 rounded-xl bg-[#10182A] border border-white/5 hover:border-purple-500/40 hover:bg-[#1A2946] cursor-pointer transition-all group"
            >
              <div className="flex items-center justify-between gap-2 mb-1.5">
                <span className="text-xs font-semibold px-2 py-0.5 rounded bg-purple-500/15 text-purple-300 border border-purple-500/20">
                  {item.category}
                </span>
                <span className="text-[10px] font-mono text-slate-400 uppercase">
                  Language: {item.language}
                </span>
              </div>
              <h4 className="text-sm font-bold text-white group-hover:text-purple-300 transition-colors line-clamp-2">
                {item.title}
              </h4>
              <p className="text-xs text-slate-400 mt-1 line-clamp-2">
                {item.text}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
