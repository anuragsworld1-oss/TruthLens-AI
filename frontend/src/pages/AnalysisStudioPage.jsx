import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  FileText, Link2, UploadCloud, Image as ImageIcon, Sparkles, 
  Trash2, BookOpen, AlertCircle, CheckCircle2, Loader2, ArrowRight
} from 'lucide-react';
import api from '../services/api';
import SampleArticleModal from '../components/SampleArticleModal';

export default function AnalysisStudioPage() {
  const navigate = useNavigate();

  // Mode: 'paste' | 'url' | 'document' | 'image'
  const [mode, setMode] = useState('paste');

  // Form states
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [url, setUrl] = useState('');
  const [language, setLanguage] = useState('auto');
  const [sourceUrl, setSourceUrl] = useState('');
  const [uploadedFile, setUploadedFile] = useState(null);
  const [uploadedImage, setUploadedImage] = useState(null);

  // Execution states
  const [analyzing, setAnalyzing] = useState(false);
  const [currentStage, setCurrentStage] = useState(0);
  const [error, setError] = useState(null);
  const [imageResult, setImageResult] = useState(null);
  const [isSampleModalOpen, setIsSampleModalOpen] = useState(false);

  const stages = [
    'Extracting & normalizing article content...',
    'Running multilingual tokenization & negation preservation...',
    'Extracting sublinear TF-IDF & recurrent embedding features...',
    'Executing multi-model ensemble (LR, NB, SVM, RF, BiLSTM)...',
    'Querying verified evidence repository for factual claims...',
    'Synthesizing explainable credibility dossier...'
  ];

  const wordCount = content.trim() ? content.trim().split(/\s+/).length : 0;

  const handleClear = () => {
    setTitle('');
    setContent('');
    setUrl('');
    setSourceUrl('');
    setUploadedFile(null);
    setUploadedImage(null);
    setError(null);
    setImageResult(null);
  };

  const handleSampleSelect = (sample) => {
    setTitle(sample.title);
    setContent(sample.text);
    setLanguage(sample.language);
    setMode('paste');
    setError(null);
  };

  const runAnalysis = async () => {
    setError(null);
    setAnalyzing(true);
    setCurrentStage(0);

    // Progressive stage ticker
    const stageInterval = setInterval(() => {
      setCurrentStage((prev) => (prev < stages.length - 1 ? prev + 1 : prev));
    }, 450);

    try {
      let response;

      if (mode === 'paste') {
        if (!content.trim() || content.trim().length < 15) {
          throw new Error('Please enter at least 15 characters of article text.');
        }
        response = await api.analyzeText({
          title,
          text: content,
          language: language === 'auto' ? null : language,
          source_url: sourceUrl
        });
      } else if (mode === 'url') {
        if (!url.trim()) {
          throw new Error('Please enter a valid news article URL.');
        }
        response = await api.analyzeUrl({ url });
      } else if (mode === 'document') {
        if (!uploadedFile) {
          throw new Error('Please select a TXT, PDF, or DOCX document to upload.');
        }
        const formData = new FormData();
        formData.append('file', uploadedFile);
        response = await api.analyzeDocument(formData);
      } else if (mode === 'image') {
        if (!uploadedImage) {
          throw new Error('Please select an image file (JPG, PNG, WEBP).');
        }
        const formData = new FormData();
        formData.append('image', uploadedImage);
        const imgRes = await api.analyzeImage(formData);
        setImageResult(imgRes.data);
        clearInterval(stageInterval);
        setAnalyzing(false);
        return;
      }

      clearInterval(stageInterval);
      setAnalyzing(false);

      if (response && response.data && response.data.analysis_id) {
        // Save current analysis into sessionStorage for instant report view
        sessionStorage.setItem(`truthlens_report_${response.data.analysis_id}`, JSON.stringify(response.data));
        navigate(`/report/${response.data.analysis_id}`);
      }
    } catch (err) {
      clearInterval(stageInterval);
      setAnalyzing(false);
      console.error('Analysis error:', err);
      const errMsg = err.response?.data?.error || err.message || 'An unexpected error occurred during analysis.';
      setError(errMsg);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 pb-16">
      {/* Sample Modal */}
      <SampleArticleModal
        isOpen={isSampleModalOpen}
        onClose={() => setIsSampleModalOpen(false)}
        onSelect={handleSampleSelect}
      />

      {/* Header */}
      <div className="text-center max-w-xl mx-auto space-y-2">
        <h1 className="text-3xl font-extrabold text-white tracking-tight">News Analysis Studio</h1>
        <p className="text-xs sm:text-sm text-slate-400">
          Analyze full news articles, headlines, documents, or URLs with multi-model NLP, claim extraction, and explainable AI.
        </p>
      </div>

      {/* Mode Selector Tabs */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 bg-[#10182A] p-1.5 rounded-2xl border border-white/10">
        {[
          { id: 'paste', label: 'Paste Article', icon: FileText },
          { id: 'url', label: 'Article URL', icon: Link2 },
          { id: 'document', label: 'Upload Doc', icon: UploadCloud },
          { id: 'image', label: 'Image Provenance', icon: ImageIcon }
        ].map((tab) => {
          const Icon = tab.icon;
          const active = mode === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => {
                setMode(tab.id);
                setError(null);
              }}
              className={`flex items-center justify-center gap-2 py-3 px-3 rounded-xl text-xs sm:text-sm font-semibold transition-all ${
                active
                  ? 'bg-gradient-to-r from-purple-600 to-indigo-600 text-white shadow-lg shadow-purple-600/30'
                  : 'text-slate-400 hover:text-white hover:bg-white/5'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Error Banner */}
      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 flex items-start gap-3 text-rose-300 text-xs animate-shake">
          <AlertCircle className="w-4 h-4 text-rose-400 mt-0.5 flex-shrink-0" />
          <div className="flex-1">
            <span className="font-bold block">Validation Notice:</span>
            <span>{error}</span>
          </div>
        </div>
      )}

      {/* Analysis Container Card */}
      <div className="p-6 sm:p-8 rounded-2xl bg-[#141F35] border border-white/10 shadow-2xl relative">
        {/* Mode 1: Paste Text */}
        {mode === 'paste' && (
          <div className="space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <span className="text-xs font-bold text-slate-300 uppercase tracking-wider">
                Article Information
              </span>
              <div className="flex items-center gap-3">
                <button
                  type="button"
                  onClick={() => setIsSampleModalOpen(true)}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-purple-500/10 hover:bg-purple-500/20 text-purple-300 border border-purple-500/20 text-xs font-medium transition-colors"
                >
                  <BookOpen className="w-3.5 h-3.5 text-cyan-400" />
                  <span>Load Benchmark Sample</span>
                </button>

                <select
                  value={language}
                  onChange={(e) => setLanguage(e.target.value)}
                  className="px-3 py-1.5 rounded-lg bg-[#10182A] border border-white/10 text-xs text-slate-200 focus:outline-none focus:border-purple-500"
                >
                  <option value="auto">Auto-Detect Language</option>
                  <option value="en">English (EN)</option>
                  <option value="hi">Hindi / हिन्दी (HI)</option>
                </select>
              </div>
            </div>

            <div>
              <input
                type="text"
                placeholder="News Headline / Article Title (Optional)"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="w-full px-4 py-3 rounded-xl bg-[#10182A] border border-white/10 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-purple-500 transition-colors font-sans"
              />
            </div>

            <div>
              <textarea
                rows={8}
                placeholder="Paste the full news article body or textual claim here for deep credibility analysis..."
                value={content}
                onChange={(e) => setContent(e.target.value)}
                className="w-full p-4 rounded-xl bg-[#10182A] border border-white/10 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-purple-500 transition-colors font-sans leading-relaxed resize-y"
              />
            </div>

            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs text-slate-400 pt-2 border-t border-white/5">
              <div className="flex items-center gap-4">
                <span>Words: <strong className="text-white font-mono">{wordCount}</strong></span>
                <span>Characters: <strong className="text-white font-mono">{content.length}</strong></span>
              </div>
              <button
                type="button"
                onClick={handleClear}
                className="flex items-center gap-1.5 text-slate-400 hover:text-rose-400 transition-colors"
              >
                <Trash2 className="w-3.5 h-3.5" />
                <span>Clear Input</span>
              </button>
            </div>
          </div>
        )}

        {/* Mode 2: Article URL */}
        {mode === 'url' && (
          <div className="space-y-4 py-4">
            <div className="space-y-1">
              <label className="text-xs font-bold text-slate-300 uppercase tracking-wider block">
                Submit Public Article URL
              </label>
              <p className="text-xs text-slate-400">
                Safe SSRF-protected scraper extracts headline, author, publication timestamp, and body text.
              </p>
            </div>

            <div className="relative">
              <input
                type="url"
                placeholder="https://www.reuters.com/world/article-slug..."
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                className="w-full pl-11 pr-4 py-3.5 rounded-xl bg-[#10182A] border border-white/10 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition-colors font-mono"
              />
              <Link2 className="w-5 h-5 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            </div>

            <div className="p-3 rounded-xl bg-purple-500/10 border border-purple-500/20 text-xs text-purple-300/80">
              * Note: For security, links resolving to private IP ranges, localhost, or cloud metadata services are blocked.
            </div>
          </div>
        )}

        {/* Mode 3: Upload Document */}
        {mode === 'document' && (
          <div className="space-y-4 py-4">
            <div className="space-y-1">
              <label className="text-xs font-bold text-slate-300 uppercase tracking-wider block">
                Upload News Document
              </label>
              <p className="text-xs text-slate-400">
                Supports TXT, PDF, and DOCX files up to 10MB.
              </p>
            </div>

            <label className="flex flex-col items-center justify-center p-8 rounded-2xl border-2 border-dashed border-white/15 hover:border-purple-500/50 bg-[#10182A] cursor-pointer transition-all group">
              <UploadCloud className="w-10 h-10 text-slate-400 group-hover:text-purple-400 group-hover:scale-110 transition-all mb-3" />
              <span className="text-sm font-semibold text-white">
                {uploadedFile ? uploadedFile.name : 'Click to select or drag and drop a news document'}
              </span>
              <span className="text-xs text-slate-500 mt-1">
                {uploadedFile ? `${Math.round(uploadedFile.size / 1024)} KB` : 'PDF, DOCX, or TXT'}
              </span>
              <input
                type="file"
                accept=".txt,.pdf,.docx"
                className="hidden"
                onChange={(e) => setUploadedFile(e.target.files[0] || null)}
              />
            </label>
          </div>
        )}

        {/* Mode 4: Image Provenance */}
        {mode === 'image' && (
          <div className="space-y-6 py-4">
            <div className="space-y-1">
              <label className="text-xs font-bold text-slate-300 uppercase tracking-wider block">
                Image Provenance & Metadata Inspection
              </label>
              <p className="text-xs text-slate-400">
                Inspects EXIF camera tags, digitized timestamps, resolution, software markers (Photoshop/GIMP), and C2PA manifests.
              </p>
            </div>

            <label className="flex flex-col items-center justify-center p-8 rounded-2xl border-2 border-dashed border-white/15 hover:border-cyan-500/50 bg-[#10182A] cursor-pointer transition-all group">
              <ImageIcon className="w-10 h-10 text-slate-400 group-hover:text-cyan-400 group-hover:scale-110 transition-all mb-3" />
              <span className="text-sm font-semibold text-white">
                {uploadedImage ? uploadedImage.name : 'Select an image associated with the news article'}
              </span>
              <span className="text-xs text-slate-500 mt-1">
                {uploadedImage ? `${Math.round(uploadedImage.size / 1024)} KB` : 'JPG, PNG, or WEBP up to 12MB'}
              </span>
              <input
                type="file"
                accept=".jpg,.jpeg,.png,.webp"
                className="hidden"
                onChange={(e) => setUploadedImage(e.target.files[0] || null)}
              />
            </label>

            {/* Image Provenance Result Card */}
            {imageResult && (
              <div className="p-5 rounded-2xl bg-[#10182A] border border-cyan-500/30 space-y-4 animate-fadeIn">
                <div className="flex items-center justify-between pb-3 border-b border-white/10">
                  <span className="text-xs font-bold text-cyan-400 uppercase tracking-wider">Provenance Assessment</span>
                  <span className="text-xs px-2.5 py-0.5 rounded-full bg-cyan-500/10 text-cyan-300 border border-cyan-500/20 font-semibold">
                    {imageResult.provenance_status}
                  </span>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                  <div className="p-2.5 rounded-lg bg-[#141F35]">
                    <span className="text-slate-400 block mb-0.5">Dimensions</span>
                    <span className="font-bold text-white font-mono">{imageResult.dimensions}</span>
                  </div>
                  <div className="p-2.5 rounded-lg bg-[#141F35]">
                    <span className="text-slate-400 block mb-0.5">Aspect Ratio</span>
                    <span className="font-bold text-white font-mono">{imageResult.aspect_ratio}</span>
                  </div>
                  <div className="p-2.5 rounded-lg bg-[#141F35]">
                    <span className="text-slate-400 block mb-0.5">Camera Hardware</span>
                    <span className="font-bold text-white">{imageResult.camera_make} {imageResult.camera_model}</span>
                  </div>
                  <div className="p-2.5 rounded-lg bg-[#141F35]">
                    <span className="text-slate-400 block mb-0.5">Software Signature</span>
                    <span className="font-bold text-white">{imageResult.software_signature}</span>
                  </div>
                </div>

                <div className="p-3 rounded-xl bg-purple-950/20 border border-purple-500/20 text-xs text-purple-300/80 leading-relaxed">
                  <strong>Notice:</strong> {imageResult.educational_disclaimer}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Action Button & Processing Stepper */}
        <div className="mt-8 pt-6 border-t border-white/10">
          {analyzing ? (
            <div className="p-5 rounded-2xl bg-[#10182A] border border-purple-500/30 space-y-4 animate-pulse">
              <div className="flex items-center justify-between text-xs text-purple-300 font-bold">
                <span className="flex items-center gap-2">
                  <Loader2 className="w-4 h-4 animate-spin text-cyan-400" />
                  Stage {currentStage + 1} of {stages.length}
                </span>
                <span className="font-mono">{Math.round(((currentStage + 1) / stages.length) * 100)}%</span>
              </div>

              {/* Progress bar */}
              <div className="w-full h-2 rounded-full bg-[#141F35] overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-purple-600 via-indigo-500 to-cyan-400 transition-all duration-300 rounded-full"
                  style={{ width: `${((currentStage + 1) / stages.length) * 100}%` }}
                />
              </div>

              <p className="text-xs text-slate-300 font-mono text-center">
                {stages[currentStage]}
              </p>
            </div>
          ) : (
            <button
              onClick={runAnalysis}
              className="w-full py-4 rounded-xl bg-gradient-to-r from-purple-600 to-cyan-500 hover:from-purple-500 hover:to-cyan-400 text-white font-bold text-base shadow-xl shadow-purple-600/30 hover:scale-[1.01] active:scale-[0.99] transition-all flex items-center justify-center gap-2"
            >
              <Sparkles className="w-5 h-5" />
              <span>Execute TruthLens Credibility Analysis</span>
              <ArrowRight className="w-4 h-4 ml-1" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
