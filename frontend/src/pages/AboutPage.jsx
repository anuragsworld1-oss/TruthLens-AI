import React from 'react';
import { BookOpen, ShieldCheck, Cpu, BrainCircuit, SearchCheck, Eye, Terminal, Lock, Scale } from 'lucide-react';

export default function AboutPage() {
  return (
    <div className="max-w-4xl mx-auto space-y-12 pb-20">
      {/* Header */}
      <div className="text-center max-w-2xl mx-auto space-y-3">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-purple-500/10 border border-purple-500/20 text-purple-300 text-xs font-semibold">
          <BookOpen className="w-3.5 h-3.5" />
          <span>Technical Whitepaper & Methodology</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
          TruthLens AI Architecture
        </h1>
        <p className="text-xs sm:text-sm text-slate-400 leading-relaxed">
          Comprehensive documentation of the Natural Language Processing, Machine Learning, Deep Learning, and Evidence Verification systems powering TruthLens AI.
        </p>
      </div>

      {/* Section 1: The Problem & Ethical Philosophy */}
      <div className="p-6 sm:p-8 rounded-2xl bg-[#141F35] border border-white/10 shadow-xl space-y-4">
        <div className="flex items-center gap-2.5 text-purple-400">
          <Scale className="w-5 h-5" />
          <h2 className="text-lg font-bold text-white">1. Problem Formulation & Responsible AI Principles</h2>
        </div>
        <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
          Misinformation distorts public health decisions, financial markets, democratic processes, and social cohesion. However, algorithmic classification poses fundamental epistemological risks: <strong>machine learning classifiers cannot establish absolute ontological truth</strong>. 
        </p>
        <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
          TruthLens AI is therefore deliberately engineered not as an infallible arbiter of truth, but as an <em>explainable decision-support system</em> for journalists, researchers, and citizens. We reject binary True/False declarations in favor of calibrated credibility categories:
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2">
          <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-xs">
            <strong className="text-emerald-400 block mb-1">Likely Genuine (70-100)</strong>
            <span className="text-slate-300">High alignment with verified sources, neutral syntax, absence of clickbait heuristics.</span>
          </div>
          <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-xs">
            <strong className="text-rose-400 block mb-1">Potentially Misleading (40-69)</strong>
            <span className="text-slate-300">Elevated sensationalism, clickbait phrasing, or contradiction with documented empirical records.</span>
          </div>
          <div className="p-3 rounded-xl bg-amber-500/10 border border-amber-500/20 text-xs">
            <strong className="text-amber-400 block mb-1">Needs Verification (&lt;40 / Conflict)</strong>
            <span className="text-slate-300">High model divergence, preprint unverified assertions, or insufficient corroborating evidence.</span>
          </div>
        </div>
      </div>

      {/* Section 2: Multilingual NLP Preprocessing */}
      <div className="p-6 sm:p-8 rounded-2xl bg-[#141F35] border border-white/10 shadow-xl space-y-4">
        <div className="flex items-center gap-2.5 text-cyan-400">
          <BrainCircuit className="w-5 h-5" />
          <h2 className="text-lg font-bold text-white">2. Multilingual NLP Pipeline & Negation Preservation</h2>
        </div>
        <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
          Traditional NLP pipelines indiscriminately eliminate stopwords. In fact-checking, however, tokens such as <code>not</code>, <code>never</code>, <code>no</code>, and <code>without</code> completely invert factual truth. TruthLens AI implements:
        </p>
        <ul className="list-disc list-inside space-y-2 text-xs sm:text-sm text-slate-300 pl-2">
          <li><strong>Negation Preservation:</strong> Explicitly shields polarity-inverting tokens from stopword pruning.</li>
          <li><strong>Unicode NFKC Normalization:</strong> Strips zero-width joiners, resolves obfuscated homoglyphs, and cleans HTML tags safely.</li>
          <li><strong>Devanagari (Hindi) Script Handler:</strong> Tailored regex tokenization and dedicated Hindi stopword filtering preserving terms like <code>नहीं</code>.</li>
          <li><strong>WordNet Lemmatization:</strong> Normalizes inflectional endings to base lexical representations.</li>
        </ul>
      </div>

      {/* Section 3: Feature Engineering & Classical ML */}
      <div className="p-6 sm:p-8 rounded-2xl bg-[#141F35] border border-white/10 shadow-xl space-y-4">
        <div className="flex items-center gap-2.5 text-indigo-400">
          <Cpu className="w-5 h-5" />
          <h2 className="text-lg font-bold text-white">3. Sublinear TF-IDF & Calibrated Probabilities</h2>
        </div>
        <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
          To capture both isolated keywords and idiomatic phrases, we compute unigram and bigram features:
        </p>
        <div className="p-3 rounded-xl bg-[#10182A] font-mono text-xs text-purple-300 border border-white/5">
          TF-IDF(t, d) = (1 + log(tf(t, d))) * (log((1 + N) / (1 + df(t))) + 1)
        </div>
        <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
          For classification, raw decision function scores from Support Vector Machines are not true probabilities. TruthLens AI employs <strong>Platt Scaling</strong> (fitting an empirical logistic sigmoid over SVM margins) to generate genuine calibrated confidence distributions.
        </p>
      </div>

      {/* Section 4: Deep Learning BiLSTM Architecture */}
      <div className="p-6 sm:p-8 rounded-2xl bg-[#141F35] border border-white/10 shadow-xl space-y-4">
        <div className="flex items-center gap-2.5 text-purple-400">
          <Layers className="w-5 h-5" />
          <h2 className="text-lg font-bold text-white">4. Bidirectional LSTM Neural Sequence Architecture</h2>
        </div>
        <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
          While n-gram TF-IDF models capture vocabulary frequency, sequential context and long-range dependencies are modeled via a Bidirectional LSTM:
        </p>
        <div className="p-4 rounded-xl bg-[#10182A] border border-white/5 space-y-2 text-xs font-mono text-slate-300">
          <div>1. Tokenizer Vocab Indexing (Max Sequence Length: 90 tokens)</div>
          <div>2. Trainable Dense Embedding Layer (Dimension: 48)</div>
          <div>3. Forward LSTM Recurrent Cells (Hidden Dimension: 32)</div>
          <div>4. Backward LSTM Recurrent Cells (Hidden Dimension: 32)</div>
          <div>5. Concatenated Hidden State [h_fwd; h_bwd] (Dimension: 64)</div>
          <div>6. Dropout Regularization (p=0.3)</div>
          <div>7. Dense Projection & Softmax Cross-Entropy Output (3 Classes)</div>
        </div>
      </div>

      {/* Section 5: Explainable AI & Evidence Verification */}
      <div className="p-6 sm:p-8 rounded-2xl bg-[#141F35] border border-white/10 shadow-xl space-y-4">
        <div className="flex items-center gap-2.5 text-emerald-400">
          <SearchCheck className="w-5 h-5" />
          <h2 className="text-lg font-bold text-white">5. Explainable AI & Evidence-Based Verification</h2>
        </div>
        <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
          Every decision rendered by TruthLens AI is fully auditable:
        </p>
        <ul className="list-disc list-inside space-y-2 text-xs sm:text-sm text-slate-300 pl-2">
          <li><strong>Token Attribution (XAI):</strong> Highlighting words that actively pull the score toward credibility or sensationalism.</li>
          <li><strong>Claim Extraction:</strong> Syntactic parsing of quantitative metrics, named entities, and declarative verbs.</li>
          <li><strong>Zero-Hallucination Evidence Retrieval:</strong> Queries are matched exclusively against verified records from international agencies (NASA, WHO, Reuters, PIB). <em>The system never hallucinates fake URLs or synthetic quotes.</em></li>
        </ul>
      </div>
    </div>
  );
}

function Layers(props) {
  return (
    <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="m12.83 2.18a2 2 0 0 0-1.66 0L2.6 6.08a1 1 0 0 0 0 1.83l8.58 3.91a2 2 0 0 0 1.66 0l8.58-3.9a1 1 0 0 0 0-1.83Z"/>
      <path d="m22 17.65-9.17 4.16a2 2 0 0 1-1.66 0L2 17.65"/>
      <path d="m22 12.65-9.17 4.16a2 2 0 0 1-1.66 0L2 12.65"/>
    </svg>
  );
}
