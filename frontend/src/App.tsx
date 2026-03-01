import { useState, useEffect, useRef } from 'react';
import {
  MessageSquare,
  Briefcase,
  Bookmark,
  Building2,
  TrendingUp,
  Info,
  Search,
  Send,
  ExternalLink,
  MapPin,
  Clock,
  DollarSign,
  Trash2,
  ChevronRight,
  Sparkles,
  ArrowRight
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';
import GradientBlinds from './components/GradientBlinds';
import './App.css';

// --- Types ---
interface Job {
  id?: number;
  title: string;
  company: string;
  location: string;
  salary: string;
  experience: string;
  description: string;
  url: string;
  source: string;
  wfh?: boolean;
}

interface Message {
  role: 'user' | 'bot';
  content: string;
}

interface CompanyInfo {
  name: string;
  type?: string;
  founded?: string;
  hq?: string;
  employees?: string;
  revenue?: string;
  rating?: string;
  ceo?: string;
  message?: string;
}

const API_BASE = 'http://localhost:8000';

function App() {
  const [hasStarted, setHasStarted] = useState(false);
  const [activeTab, setActiveTab] = useState('chat');
  const [messages, setMessages] = useState<Message[]>([
    { role: 'bot', content: "👋 **Hi there! I'm CareerBot.** I've just powered up my global search engines to help you find your dream role. What's on your mind today?" }
  ]);
  const [input, setInput] = useState('');
  const [jobs, setJobs] = useState<Job[]>([]);
  const [savedJobs, setSavedJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(false);
  const [companyRes, setCompanyRes] = useState<CompanyInfo | null>(null);
  const [intelRes, setIntelRes] = useState<string | null>(null);

  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (activeTab === 'saved') fetchSavedJobs();
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [activeTab, messages]);

  const fetchSavedJobs = async () => {
    try {
      const res = await axios.get(`${API_BASE}/jobs/saved`);
      setSavedJobs(res.data);
    } catch (e) { console.error(e); }
  };

  const sendMessage = async () => {
    if (!input.trim()) return;
    const userMsg = { role: 'user', content: input } as Message;
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const res = await axios.post(`${API_BASE}/chat`, { message: input });
      setMessages(prev => [...prev, { role: 'bot', content: res.data.response }]);
    } catch (e) {
      setMessages(prev => [...prev, { role: 'bot', content: "😓 I'm having a little trouble connecting to my brain. Is the backend running on port 8000?" }]);
    } finally {
      setLoading(false);
    }
  };

  const handleJobSearch = async (keyword: string) => {
    setLoading(true);
    setJobs([]);
    try {
      const res = await axios.post(`${API_BASE}/chat`, {
        message: `I am using the Job Listings tab. Please find jobs for: ${keyword}`
      });
      const match = res.data.response.match(/\[\{.*\}\]/s);
      if (match) {
        setJobs(JSON.parse(match[0]));
      } else {
        setMessages(prev => [...prev, { role: 'bot', content: res.data.response }]);
        setActiveTab('chat');
      }
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  };

  const handleCompanyResearch = async (name: string) => {
    setLoading(true);
    setCompanyRes(null);
    try {
      const res = await axios.post(`${API_BASE}/chat`, {
        message: `Research the company '${name}' and return details as JSON.`
      });
      const match = res.data.response.match(/\{.*\}/s);
      if (match) setCompanyRes(JSON.parse(match[0]));
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  };

  const handleIntel = async (city: string) => {
    setLoading(true);
    setIntelRes(null);
    try {
      const res = await axios.post(`${API_BASE}/chat`, {
        message: `Analysis of current hiring trends in ${city} for tech roles.`
      });
      setIntelRes(res.data.response);
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  };

  return (
    <div className="h-screen w-full bg-slate-950 text-slate-200 relative overflow-hidden font-['Outfit']">
      <AnimatePresence mode="wait">
        {!hasStarted ? (
          <motion.div
            key="welcome"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0, scale: 1.1, filter: "blur(20px)" }}
            className="absolute inset-0 z-50 flex flex-col items-center justify-center p-6 text-center"
          >
            {/* Dynamic Background Animation - Only on Welcome */}
            <div className="absolute inset-0 z-0 pointer-events-none opacity-80">
              <GradientBlinds
                gradientColors={['#1e1b4b', '#4c1d95', '#831843']}
                angle={20}
                noise={0.5}
                blindCount={16}
                blindMinWidth={60}
                spotlightRadius={0.5}
                spotlightSoftness={1.0}
                spotlightOpacity={0.8}
                mouseDampening={0.15}
                mixBlendMode="screen"
              />
            </div>

            <motion.div
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.2 }}
              className="mb-8 z-10"
            >
              <div className="w-24 h-24 rounded-[2rem] bg-gradient-to-br from-purple-500 to-blue-600 flex items-center justify-center shadow-[0_0_50px_rgba(168,85,247,0.4)] mx-auto mb-10">
                <Sparkles className="text-white w-12 h-12" />
              </div>
              <h1 className="text-7xl md:text-9xl font-black tracking-tighter bg-gradient-to-b from-white via-white to-white/20 bg-clip-text text-transparent mb-4">
                CAREERBOT
              </h1>
              <p className="text-xl md:text-2xl text-slate-400 font-medium tracking-wide max-w-2xl mx-auto leading-relaxed">
                Your cinematic gateway to the next level of <span className="text-purple-400 font-bold">AI-driven</span> career intelligence.
              </p>
            </motion.div>

            <motion.button
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.4 }}
              onClick={() => setHasStarted(true)}
              className="group relative px-12 py-6 bg-white text-black font-black text-xl rounded-2xl hover:bg-purple-500 hover:text-white transition-all duration-500 shadow-[0_20px_40px_rgba(255,255,255,0.1)] hover:shadow-purple-500/40 flex items-center gap-4 overflow-hidden z-10"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000" />
              START YOUR JOURNEY <ArrowRight className="group-hover:translate-x-2 transition-transform" />
            </motion.button>
          </motion.div>
        ) : (
          <motion.div
            key="workspace"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="flex h-screen w-full relative z-10 bg-[radial-gradient(circle_at_top_right,#1e1b4b,#020617_50%)]"
          >
            {/* Sidebar */}
            <aside className="w-72 glass h-full flex flex-col p-6 z-20 border-r border-white/10 relative">
              <div className="flex items-center gap-3 mb-10">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 to-blue-600 flex items-center justify-center shadow-lg shadow-purple-500/20">
                  <Sparkles className="text-white w-6 h-6" />
                </div>
                <h1 className="text-2xl font-black tracking-tighter bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">
                  CAREERBOT
                </h1>
              </div>

              <nav className="flex-1 space-y-2">
                <TabButton icon={<MessageSquare size={18} />} label="Agent Chat" active={activeTab === 'chat'} onClick={() => setActiveTab('chat')} />
                <TabButton icon={<Briefcase size={18} />} label="Job Listings" active={activeTab === 'jobs'} onClick={() => setActiveTab('jobs')} />
                <TabButton icon={<Bookmark size={18} />} label="Saved Jobs" active={activeTab === 'saved'} onClick={() => setActiveTab('saved')} />
                <TabButton icon={<Building2 size={18} />} label="Company Research" active={activeTab === 'company'} onClick={() => setActiveTab('company')} />
                <TabButton icon={<TrendingUp size={18} />} label="Market Intelligence" active={activeTab === 'intel'} onClick={() => setActiveTab('intel')} />
              </nav>

              <div className="mt-auto pt-6 border-t border-white/5">
                <div className="flex items-center gap-3 px-4 py-2 text-xs text-gray-500 font-bold uppercase tracking-widest">
                  <Info size={14} /> v2.0 AI-Agent
                </div>
              </div>
            </aside>

            {/* Main Content */}
            <main className="flex-1 h-full overflow-hidden relative flex flex-col bg-slate-950/20">
              <header className="h-20 flex items-center justify-between px-10 border-b border-white/5 backdrop-blur-md z-10 bg-black/20">
                <h2 className="text-sm font-black text-gray-400 uppercase tracking-[0.3em]">
                  {activeTab === 'chat' && 'Your Career Partner'}
                  {activeTab === 'jobs' && 'Job Explorer'}
                  {activeTab === 'saved' && 'My Saved Future'}
                  {activeTab === 'company' && 'Company Stories'}
                  {activeTab === 'intel' && 'The Hiring World'}
                </h2>
                {loading && <div className="flex items-center gap-2 text-purple-400 text-xs font-bold animate-pulse">
                  <div className="w-2 h-2 bg-purple-500 rounded-full" /> SCANNING THE GLOBE FOR YOU...
                </div>}
              </header>

              <div className="flex-1 p-10 overflow-y-auto custom-scroll">
                <AnimatePresence mode="wait">
                  {activeTab === 'chat' && (
                    <motion.div
                      key="chat"
                      initial={{ opacity: 0, x: 20 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: -20 }}
                      className="max-w-4xl mx-auto h-full flex flex-col"
                    >
                      <div className="flex-1 space-y-6 mb-24">
                        {messages.map((m, i) => (
                          <motion.div
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            key={i}
                            className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}
                          >
                            <div className={`max-w-[85%] rounded-3xl p-5 shadow-2xl ${m.role === 'user'
                              ? 'bg-gradient-to-br from-purple-600 to-blue-700 text-white border border-white/10'
                              : 'glass border-white/5 text-slate-300'
                              }`}>
                              <p className="whitespace-pre-wrap leading-relaxed text-[15px] font-medium">{m.content}</p>
                            </div>
                          </motion.div>
                        ))}
                        <div ref={chatEndRef} />
                      </div>

                      <div className="fixed bottom-10 left-[calc(280px+2.5rem)] right-10 max-w-4xl mx-auto z-30">
                        <div className="glass rounded-[2rem] p-2 flex items-center shadow-[0_20px_50px_rgba(0,0,0,0.5)] border-white/10 ring-1 ring-white/5">
                          <input
                            className="flex-1 bg-transparent border-none outline-none px-6 text-white text-lg h-14 placeholder:text-slate-600 font-medium"
                            placeholder="Ask me anything about your career journey..."
                            value={input}
                            onChange={e => setInput(e.target.value)}
                            onKeyPress={e => e.key === 'Enter' && sendMessage()}
                          />
                          <button
                            onClick={sendMessage}
                            className="bg-purple-600 hover:bg-purple-500 p-4 rounded-2xl transition-all shadow-lg active:scale-95 text-white mr-1"
                          >
                            <Send size={24} />
                          </button>
                        </div>
                      </div>
                    </motion.div>
                  )}

                  {activeTab === 'jobs' && (
                    <motion.div key="jobs" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="max-w-6xl mx-auto">
                      <div className="glass rounded-[2rem] p-2 mb-12 flex items-center border-white/10 ring-1 ring-white/5">
                        <Search className="ml-6 text-slate-500" />
                        <input
                          className="flex-1 bg-transparent border-none outline-none px-6 py-4 text-white text-lg h-14 font-medium"
                          placeholder="What role would you love next? (e.g. Creative Lead)"
                          onKeyPress={e => {
                            if (e.key === 'Enter') handleJobSearch((e.target as HTMLInputElement).value);
                          }}
                        />
                      </div>
                      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 pb-32">
                        {jobs.map((j, i) => <JobCard key={i} job={j} />)}
                        {jobs.length === 0 && !loading && (
                          <div className="col-span-full py-32 text-center opacity-40">
                            <Briefcase className="mx-auto mb-6" size={64} />
                            <p className="text-xl font-bold uppercase tracking-widest">Enter a role above to begin global search</p>
                          </div>
                        )}
                      </div>
                    </motion.div>
                  )}

                  {activeTab === 'saved' && (
                    <motion.div key="saved" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="max-w-6xl mx-auto">
                      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 pb-20">
                        {savedJobs.map((j, i) => <JobCard key={i} job={j} isSaved fetchSaved={fetchSavedJobs} />)}
                        {savedJobs.length === 0 && (
                          <div className="col-span-full py-32 text-center opacity-40">
                            <Bookmark className="mx-auto mb-6" size={64} />
                            <p className="text-xl font-bold uppercase tracking-widest">Your archives are empty</p>
                          </div>
                        )}
                      </div>
                    </motion.div>
                  )}

                  {activeTab === 'company' && (
                    <motion.div key="company" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="max-w-4xl mx-auto">
                      <div className="glass rounded-[2rem] p-2 mb-12 flex items-center border-white/10">
                        <Building2 className="ml-6 text-slate-500" />
                        <input
                          className="flex-1 bg-transparent border-none outline-none px-6 py-4 text-white text-lg h-14 font-medium"
                          placeholder="Which company should we peek into?"
                          onKeyPress={e => {
                            if (e.key === 'Enter') handleCompanyResearch((e.target as HTMLInputElement).value);
                          }}
                        />
                      </div>
                      {companyRes && (
                        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="glass p-10 rounded-[3rem] border-white/10">
                          <div className="flex justify-between items-start mb-10">
                            <div>
                              <h3 className="text-4xl font-black text-white mb-2">{companyRes.name}</h3>
                              <p className="text-blue-400 font-bold text-lg">{companyRes.type} · Founded {companyRes.founded}</p>
                            </div>
                            <div className="bg-emerald-500/20 text-emerald-400 px-4 py-2 rounded-2xl border border-emerald-500/20 font-black">
                              {companyRes.rating} ★
                            </div>
                          </div>
                          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-10">
                            <MetricBox label="Employees" value={companyRes.employees || 'N/A'} />
                            <MetricBox label="Revenue" value={companyRes.revenue || 'N/A'} />
                            <MetricBox label="Headquarters" value={companyRes.hq || 'N/A'} />
                            <MetricBox label="CEO" value={companyRes.ceo || 'N/A'} />
                          </div>
                          {companyRes.message && <div className="p-6 bg-white/5 rounded-2xl border border-white/5 text-slate-400 leading-relaxed italic">{companyRes.message}</div>}
                        </motion.div>
                      )}
                    </motion.div>
                  )}

                  {activeTab === 'intel' && (
                    <motion.div key="intel" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="max-w-4xl mx-auto">
                      <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-12">
                        {['Bangalore', 'Mumbai', 'Hyderabad', 'Pune', 'Delhi', 'Chennai'].map(city => (
                          <button
                            key={city}
                            onClick={() => handleIntel(city)}
                            className="glass py-4 rounded-2xl hover:bg-white/10 transition-all font-bold border-white/5 active:scale-95"
                          >
                            {city}
                          </button>
                        ))}
                      </div>
                      {intelRes && (
                        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="glass p-10 rounded-[3rem] border-white/10 leading-relaxed font-medium text-slate-300 whitespace-pre-wrap">
                          <Sparkles className="text-purple-400 mb-6" size={32} />
                          {intelRes}
                        </motion.div>
                      )}
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </main>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

// --- Sub-components ---

function TabButton({ icon, label, active, onClick }: any) {
  return (
    <button
      onClick={onClick}
      className={`w-full flex items-center gap-4 px-5 py-4 rounded-2xl transition-all duration-300 group ${active
        ? 'bg-gradient-to-r from-purple-500/20 to-transparent text-white shadow-inner border-l-4 border-purple-500'
        : 'text-gray-500 hover:text-gray-200 hover:bg-white/5'
        }`}
    >
      <span className={`${active ? 'text-purple-400' : 'group-hover:text-gray-300'} transition-colors`}>{icon}</span>
      <span className="font-bold text-sm tracking-wide">{label}</span>
      {active && <ChevronRight size={16} className="ml-auto text-purple-500" />}
    </button>
  );
}

function MetricBox({ label, value }: { label: string, value: string }) {
  return (
    <div className="bg-white/5 p-4 rounded-3xl border border-white/5">
      <p className="text-[10px] uppercase font-black tracking-widest text-slate-500 mb-1">{label}</p>
      <p className="text-white font-bold text-sm truncate">{value}</p>
    </div>
  );
}

function JobCard({ job, isSaved, fetchSaved }: { job: Job, isSaved?: boolean, fetchSaved?: () => void }) {
  const saveJob = async () => {
    try {
      await axios.post(`${API_BASE}/jobs/save`, { job });
      alert("Added to Archives! 🔥");
    } catch (e) { console.error(e); }
  };

  const deleteSaved = async () => {
    try {
      if (job.id) {
        await axios.delete(`${API_BASE}/jobs/saved/${job.id}`);
        fetchSaved?.();
      }
    } catch (e) { console.error(e); }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass p-8 rounded-[2.5rem] border-white/10 hover:border-purple-500/50 transition-all duration-500 group relative flex flex-col overflow-hidden shadow-2xl"
    >
      <div className="absolute top-0 right-0 w-40 h-40 bg-purple-500/10 blur-[80px] -mr-16 -mt-16 group-hover:bg-purple-500/20 transition-all" />

      <div className="flex justify-between items-start mb-6 z-10">
        <div className="flex-1">
          <h3 className="text-2xl font-black text-white group-hover:text-purple-400 transition-colors uppercase tracking-tight leading-none mb-2">{job.title}</h3>
          <p className="text-blue-400 font-black text-sm uppercase tracking-widest">{job.company}</p>
        </div>
        <div className="bg-white/5 backdrop-blur-md px-4 py-1.5 rounded-xl border border-white/10 text-[9px] font-black text-slate-500 uppercase tracking-widest">
          {job.source}
        </div>
      </div>

      <div className="flex flex-wrap gap-2 mb-8 z-10">
        <Badge icon={<MapPin size={14} />} text={job.location} color="blue" />
        <Badge icon={<DollarSign size={14} />} text={job.salary} color="purple" />
        <Badge icon={<Clock size={14} />} text={job.experience} color="emerald" />
      </div>

      <p className="text-slate-400 line-clamp-3 mb-10 leading-relaxed text-sm z-10 font-medium">
        {job.description}
      </p>

      <div className="flex items-center gap-4 mt-auto z-10">
        {isSaved ? (
          <button
            onClick={deleteSaved}
            className="flex-1 bg-red-500/10 text-red-400 border border-red-500/20 hover:bg-red-500/20 py-4 rounded-2xl transition-all font-black text-[10px] uppercase tracking-widest flex items-center justify-center gap-2"
          >
            <Trash2 size={16} /> Remove
          </button>
        ) : (
          <button
            onClick={saveJob}
            className="flex-1 bg-white/5 border border-white/10 hover:border-purple-500/30 hover:bg-white/10 py-4 rounded-2xl transition-all font-black text-[10px] uppercase tracking-widest"
          >
            Keep for Later
          </button>
        )}
        <a
          href={job.url}
          target="_blank"
          rel="noopener"
          className="flex-1 bg-gradient-to-br from-blue-600 via-purple-600 to-pink-600 hover:from-blue-500 hover:to-pink-500 py-4 rounded-2xl transition-all font-black text-center text-[10px] uppercase tracking-widest shadow-xl shadow-purple-600/30 text-white flex items-center justify-center gap-2"
        >
          Explore <ExternalLink size={14} />
        </a>
      </div>
    </motion.div>
  );
}

function Badge({ icon, text, color }: any) {
  const colors: any = {
    blue: 'text-blue-400 bg-blue-400/10 border-blue-400/20',
    purple: 'text-purple-400 bg-purple-400/10 border-purple-400/20',
    emerald: 'text-emerald-400 bg-emerald-400/10 border-emerald-400/20',
  };
  return (
    <div className={`flex items-center gap-1.5 px-3 py-1 rounded-xl border text-[10px] font-black uppercase tracking-widest ${colors[color]}`}>
      {icon}
      {text}
    </div>
  );
}

export default App;
