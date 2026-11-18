import React from 'react';
import { Link } from 'react-router-dom';
import { 
  ShieldCheck, Sparkles, LayoutDashboard, BrainCircuit, Globe2, 
  SearchCheck, FileSearch, ArrowRight, CheckCircle2, AlertTriangle, 
  HelpCircle, ChevronDown, Cpu, Database, Eye, Terminal, Lock
} from 'lucide-react';

export default function LandingPage() {
  const [openFaq, setOpenFaq] = React.useState(null);

  const toggleFaq = (index) => {
    setOpenFaq(openFaq === index ? null : index);
  };

  const faqs = [
    {
      q: "Does TruthLens AI claim machine learning alone establishes whether news is true?",
      a: "No. TruthLens AI strictly adheres to the principle that machine learning models cannot replace empirical truth or independent human journalism. The platform produces a model-derived probabilistic credibility index (Likely Genuine, Potentially Misleading, Needs Further Verification) based on linguistic markers, cross-model consensus, and verified factual evidence retrieval."
    },
    {
      q: "How does the evidence-based claim verification work?",
      a: "The system parses verifiable factual assertions (quantities, dates, institutional statements) and queries an index of authenticated records from international wire services (Reuters, AP), peer-reviewed scientific journals (Nature, The Lancet), and certified fact-checkers (PIB, WHO). It never fabricates citations or URLs."
    },
    {
      q: "Does AI-generated writing style mean an article is fake news?",
      a: "No. Our AI-Writing-Style assessment is explicitly labeled as experimental. Many professional newsrooms and journalists utilize AI-assisted drafting. High structural uniformity is not proof of misinformation."
    },
    {
      q: "What languages are currently supported?",
      a: "TruthLens AI natively supports English and Hindi, with custom tokenization, stopword preservation, and Devanagari script processing designed to expand into other Indian regional languages."
    }
  ];

  return (
    <div className="space-y-24 pb-20">
      {/* Hero Section */}
      <section className="relative pt-12 pb-16 overflow-hidden">
        {/* Glow backdrop */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[600px] h-[300px] bg-gradient-to-tr from-purple-600/20 via-indigo-500/15 to-cyan-400/20 blur-[120px] pointer-events-none rounded-full" />

        <div className="max-w-5xl mx-auto text-center px-4 relative z-10">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-[#10182A] border border-purple-500/30 text-purple-300 text-xs font-semibold mb-6 shadow-lg shadow-purple-500/10 animate-fade">
            <Sparkles className="w-4 h-4 text-cyan-400" />
            <span>AI-Powered News Credibility & Verification Intelligence</span>
          </div>

          <h1 className="text-4xl sm:text-6xl lg:text-7xl font-black tracking-tight text-white leading-[1.1] mb-6">
            Don't Just Read the News.{' '}
            <span className="bg-gradient-to-r from-purple-400 via-indigo-300 to-cyan-400 bg-clip-text text-transparent">
              Verify It.
            </span>
          </h1>

          <p className="text-lg sm:text-xl text-slate-300 max-w-2xl mx-auto mb-10 leading-relaxed font-normal">
            See beyond sensational headlines. Analyze articles, detect suspicious linguistic patterns, extract factual claims, and cross-reference verified evidence with explainable AI.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              to="/studio"
              className="w-full sm:w-auto flex items-center justify-center gap-2.5 px-8 py-4 rounded-xl bg-gradient-to-r from-purple-600 to-cyan-500 hover:from-purple-500 hover:to-cyan-400 text-white font-bold text-base shadow-xl shadow-purple-600/30 hover:scale-[1.02] active:scale-[0.98] transition-all"
            >
              <Sparkles className="w-5 h-5" />
              <span>Analyze News</span>
              <ArrowRight className="w-4 h-4 ml-1" />
            </Link>

            <Link
              to="/dashboard"
              className="w-full sm:w-auto flex items-center justify-center gap-2.5 px-8 py-4 rounded-xl bg-[#141F35] hover:bg-[#1A2946] border border-white/10 hover:border-white/20 text-slate-200 font-semibold text-base transition-all"
            >
              <LayoutDashboard className="w-5 h-5 text-cyan-400" />
              <span>Explore Dashboard</span>
            </Link>
          </div>
        </div>

        {/* Live Interactive Preview Card */}
        <div className="max-w-4xl mx-auto mt-16 px-4">
          <div className="bg-[#10182A]/90 backdrop-blur-xl rounded-2xl border border-white/10 p-6 sm:p-8 shadow-2xl relative overflow-hidden">
            <div className="flex items-center justify-between pb-4 border-b border-white/10 mb-6">
              <div className="flex items-center gap-3">
                <span className="w-3 h-3 rounded-full bg-rose-500"></span>
                <span className="w-3 h-3 rounded-full bg-amber-500"></span>
                <span className="w-3 h-3 rounded-full bg-emerald-500"></span>
                <span className="text-xs font-mono text-slate-400 ml-2">TruthLens Studio Live Preview</span>
              </div>
              <span className="text-xs font-semibold px-2.5 py-1 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                Verified Benchmark
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-center">
              <div className="md:col-span-2 space-y-3">
                <span className="text-xs font-bold text-purple-400 uppercase tracking-wider block">Sample Headline</span>
                <h3 className="text-lg font-bold text-white">
                  NASA James Webb Space Telescope Discovers Oldest Confirmed Black Hole in Early Universe
                </h3>
                <p className="text-xs text-slate-400 leading-relaxed">
                  Published in The Astrophysical Journal. Multi-model ensemble consensus indicates high consistency with verified astronomical peer-reviewed records.
                </p>

                <div className="flex flex-wrap gap-2 pt-2">
                  <span className="text-[11px] px-2.5 py-1 rounded bg-white/5 border border-white/10 text-slate-300">
                    Language: English
                  </span>
                  <span className="text-[11px] px-2.5 py-1 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                    Citations: 2 Primary Sources
                  </span>
                  <span className="text-[11px] px-2.5 py-1 rounded bg-purple-500/10 text-purple-300 border border-purple-500/20">
                    Model Consensus: 100%
                  </span>
                </div>
              </div>

              {/* Gauge preview */}
              <div className="flex flex-col items-center justify-center p-4 bg-[#141F35] rounded-xl border border-white/5">
                <span className="text-3xl font-black text-emerald-400">92 / 100</span>
                <span className="text-xs font-bold uppercase tracking-wider text-emerald-300 mt-1">
                  Likely Genuine
                </span>
                <span className="text-[10px] text-slate-400 text-center mt-2">
                  Calibrated Consensus Index
                </span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="max-w-6xl mx-auto px-4">
        <div className="text-center max-w-2xl mx-auto mb-14">
          <h2 className="text-3xl font-extrabold text-white tracking-tight mb-3">
            How TruthLens AI Works
          </h2>
          <p className="text-sm text-slate-400 leading-relaxed">
            A transparent 4-stage pipeline combining deep linguistic parsing, multi-model consensus, explainable AI, and authenticated evidence retrieval.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {[
            {
              step: '01',
              title: 'Multi-Modal Ingestion',
              desc: 'Submit raw text, web URLs with SSRF protection, or upload TXT, PDF, and DOCX documents with metadata parsing.',
              icon: FileSearch,
              color: 'text-purple-400'
            },
            {
              step: '02',
              title: 'Linguistic Signal Engine',
              desc: 'Inspects capitalization, clickbait phrasing, emotional urgency, and stylometric characteristics without confusing style with truth.',
              icon: BrainCircuit,
              color: 'text-cyan-400'
            },
            {
              step: '03',
              title: 'Multi-Model Consensus',
              desc: 'Evaluates text across Logistic Regression, Naive Bayes, Linear SVM, Random Forest, and Bidirectional LSTM sequence models.',
              icon: Cpu,
              color: 'text-indigo-400'
            },
            {
              step: '04',
              title: 'Evidence Verification',
              desc: 'Extracts verifiable claims and cross-checks them against authenticated primary sources with transparent citations.',
              icon: SearchCheck,
              color: 'text-emerald-400'
            }
          ].map((item, idx) => {
            const Icon = item.icon;
            return (
              <div key={idx} className="p-6 rounded-2xl bg-[#141F35] border border-white/5 hover:border-purple-500/30 transition-all space-y-3 relative group">
                <span className="text-4xl font-black text-white/5 absolute top-4 right-4 group-hover:text-purple-500/10 transition-colors font-mono">
                  {item.step}
                </span>
                <div className={`p-3 rounded-xl bg-[#10182A] w-fit border border-white/5 ${item.color}`}>
                  <Icon className="w-6 h-6" />
                </div>
                <h3 className="text-base font-bold text-white">{item.title}</h3>
                <p className="text-xs text-slate-400 leading-relaxed">{item.desc}</p>
              </div>
            );
          })}
        </div>
      </section>

      {/* Feature Grid */}
      <section className="max-w-6xl mx-auto px-4">
        <div className="text-center max-w-2xl mx-auto mb-14">
          <h2 className="text-3xl font-extrabold text-white tracking-tight mb-3">
            Comprehensive Verification Features
          </h2>
          <p className="text-sm text-slate-400">
            Engineered with the rigor of an academic AI project and the design of a commercial SaaS platform.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[
            {
              title: 'Multilingual NLP (EN & HI)',
              desc: 'Custom tokenization, stopword preservation, and negation handling for English and Hindi news sources.',
              icon: Globe2
            },
            {
              title: 'Explainable AI (XAI) Saliency',
              desc: 'Visualizes positive and negative word-level feature contributions and sentence risk breakdown using transparent linear projection.',
              icon: Eye
            },
            {
              title: 'Evidence-Based Fact Checking',
              desc: 'Matches extracted claims to verified primary records from NASA, WHO, Reuters, PIB, and peer-reviewed journals.',
              icon: SearchCheck
            },
            {
              title: 'AI-Writing-Style Assessment',
              desc: 'Analyzes sentence burstiness and formulaic transition phrases with clear ethical non-conflation disclaimers.',
              icon: Terminal
            },
            {
              title: 'Source Intelligence & SSRF Guard',
              desc: 'Safely extracts URLs, maps domains to documented publisher databases, and blocks internal network access.',
              icon: Lock
            },
            {
              title: 'Image Metadata & Provenance',
              desc: 'Extracts EXIF camera tags, software signatures, and dimensions with education on social media metadata stripping.',
              icon: Database
            }
          ].map((feat, idx) => {
            const Icon = feat.icon;
            return (
              <div key={idx} className="p-6 rounded-2xl bg-[#10182A] border border-white/10 hover:border-white/20 transition-all space-y-3">
                <div className="p-2.5 rounded-xl bg-purple-500/10 text-purple-400 w-fit border border-purple-500/20">
                  <Icon className="w-5 h-5" />
                </div>
                <h3 className="text-base font-bold text-white">{feat.title}</h3>
                <p className="text-xs text-slate-400 leading-relaxed">{feat.desc}</p>
              </div>
            );
          })}
        </div>
      </section>

      {/* Demo Statistics */}
      <section className="max-w-5xl mx-auto px-4">
        <div className="p-8 rounded-2xl bg-gradient-to-r from-purple-950/40 via-[#141F35] to-cyan-950/40 border border-white/10 text-center">
          <div className="inline-block px-3 py-1 rounded-full bg-purple-500/20 text-purple-300 text-xs font-bold uppercase tracking-wider mb-6">
            Demo Platform Metrics
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-6">
            <div>
              <span className="text-3xl sm:text-4xl font-extrabold text-white block mb-1">5+</span>
              <span className="text-xs text-slate-400">ML & DL Models</span>
            </div>
            <div>
              <span className="text-3xl sm:text-4xl font-extrabold text-cyan-400 block mb-1">100%</span>
              <span className="text-xs text-slate-400">Verifiable Citations</span>
            </div>
            <div>
              <span className="text-3xl sm:text-4xl font-extrabold text-purple-400 block mb-1">2</span>
              <span className="text-xs text-slate-400">Languages (EN/HI)</span>
            </div>
            <div>
              <span className="text-3xl sm:text-4xl font-extrabold text-emerald-400 block mb-1">&lt;15ms</span>
              <span className="text-xs text-slate-400">Inference Latency</span>
            </div>
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="max-w-4xl mx-auto px-4">
        <div className="text-center max-w-xl mx-auto mb-10">
          <h2 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight mb-2">
            Frequently Asked Questions
          </h2>
          <p className="text-xs text-slate-400">
            Transparency, ethical considerations, and technical methodology.
          </p>
        </div>

        <div className="space-y-3">
          {faqs.map((faq, idx) => (
            <div
              key={idx}
              className="rounded-xl bg-[#141F35] border border-white/10 overflow-hidden transition-all"
            >
              <button
                onClick={() => toggleFaq(idx)}
                className="w-full p-4 text-left flex items-center justify-between text-sm font-bold text-white hover:text-purple-300 transition-colors"
              >
                <span>{faq.q}</span>
                <ChevronDown className={`w-4 h-4 text-slate-400 transition-transform ${openFaq === idx ? 'rotate-180 text-purple-400' : ''}`} />
              </button>
              {openFaq === idx && (
                <div className="px-4 pb-4 pt-1 text-xs text-slate-300 leading-relaxed border-t border-white/5">
                  {faq.a}
                </div>
              )}
            </div>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-white/10 pt-10 text-center text-xs text-slate-400">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-purple-400" />
            <span className="font-bold text-slate-200">TruthLens AI</span>
            <span>— "See Beyond Headlines. Discover What's True."</span>
          </div>
          <div>
            Built with Flask, React, Scikit-learn, BiLSTM, and Sublinear TF-IDF.
          </div>
        </div>
      </footer>
    </div>
  );
}
