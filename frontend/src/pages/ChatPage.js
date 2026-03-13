import { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import {
  Shield, MessageSquare, Plus, BarChart3, LogOut, Send,
  Search, Wrench, Ticket, ChevronDown, Clock, FileText,
  Activity, Zap, User, Loader2, AlertCircle, CheckCircle2,
  BookOpen, Server, TrendingUp
} from "lucide-react";
import ChatMessage from "@/components/ChatMessage";
import ChatInput from "@/components/ChatInput";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const QUICK_QUERIES = [
  { label: "Reset Okta MFA", query: "How do I reset my Okta MFA?", icon: Shield },
  { label: "VPN Issues", query: "My VPN is not connecting.", icon: Activity },
  { label: "WiFi Problems", query: "My laptop wifi is not working.", icon: Zap },
  { label: "Create Ticket", query: "Create a ticket for laptop repair.", icon: Ticket },
];

export default function ChatPage({ user, onLogout }) {
  const navigate = useNavigate();
  const [conversations, setConversations] = useState([]);
  const [activeConversationId, setActiveConversationId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const messagesEndRef = useRef(null);

  // Fetch conversations on mount
  useEffect(() => {
    fetchConversations();
  }, []);

  const fetchConversations = async () => {
    try {
      const res = await axios.get(`${API}/conversations`, {
        params: { user_email: user.email },
      });
      setConversations(res.data || []);
    } catch (err) {
      console.error("Failed to fetch conversations", err);
    }
  };

  const loadConversation = async (convId) => {
    setActiveConversationId(convId);
    try {
      const res = await axios.get(`${API}/conversations/${convId}`);
      setMessages(res.data.messages || []);
    } catch (err) {
      console.error("Failed to load conversation", err);
    }
  };

  const startNewConversation = () => {
    setActiveConversationId(null);
    setMessages([]);
  };

  const handleSend = async (query) => {
    if (!query.trim() || loading) return;

    // Optimistic user message
    const userMsg = {
      id: `temp-${Date.now()}`,
      role: "user",
      content: query,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);

    try {
      const res = await axios.post(`${API}/chat`, {
        query,
        conversation_id: activeConversationId,
        user_email: user.email,
      });

      const aiMsg = {
        id: res.data.message_id,
        role: "assistant",
        content: res.data.response,
        intent: res.data.intent,
        sources: res.data.sources,
        actions: res.data.actions,
        ticket: res.data.ticket,
        latency: res.data.latency,
        quality: res.data.quality,
        created_at: new Date().toISOString(),
      };

      if (!activeConversationId) {
        setActiveConversationId(res.data.conversation_id);
      }

      setMessages((prev) => [...prev, aiMsg]);
      fetchConversations();
    } catch (err) {
      const errorMsg = {
        id: `error-${Date.now()}`,
        role: "assistant",
        content: "Sorry, I encountered an error processing your request. Please try again.",
        intent: "error",
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const intentIcon = (intent) => {
    const map = {
      knowledge_search: <Search className="w-3 h-3" />,
      troubleshooting: <Wrench className="w-3 h-3" />,
      ticket_creation: <Ticket className="w-3 h-3" />,
    };
    return map[intent] || <MessageSquare className="w-3 h-3" />;
  };

  const intentColor = (intent) => {
    const map = {
      knowledge_search: "bg-blue-500/15 text-blue-400 border-blue-500/20",
      troubleshooting: "bg-amber-500/15 text-amber-400 border-amber-500/20",
      ticket_creation: "bg-emerald-500/15 text-emerald-400 border-emerald-500/20",
    };
    return map[intent] || "bg-zinc-500/15 text-zinc-400 border-zinc-500/20";
  };

  return (
    <TooltipProvider delayDuration={100}>
      <div className="flex h-screen bg-[#0A0A0A]" data-testid="chat-page">
        {/* Sidebar */}
        {sidebarOpen && (
          <div
            className="w-72 border-r border-white/5 flex flex-col backdrop-blur-xl bg-black/60"
            data-testid="chat-sidebar"
          >
            {/* Sidebar Header */}
            <div className="p-4 border-b border-white/5">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-9 h-9 rounded-lg bg-blue-500/15 flex items-center justify-center">
                  <Shield className="w-5 h-5 text-blue-400" />
                </div>
                <div>
                  <h1
                    className="text-sm font-bold text-white"
                    style={{ fontFamily: "'Manrope', sans-serif" }}
                  >
                    IT Assistant
                  </h1>
                  <p className="text-[10px] text-zinc-500 uppercase tracking-wider">Enterprise AI</p>
                </div>
              </div>
              <Button
                data-testid="new-conversation-btn"
                onClick={startNewConversation}
                className="w-full h-9 bg-blue-600 hover:bg-blue-500 text-white text-xs font-medium rounded-lg active:scale-95 transition-transform duration-100"
              >
                <Plus className="w-3.5 h-3.5 mr-1.5" /> New Conversation
              </Button>
            </div>

            {/* Conversation List */}
            <ScrollArea className="flex-1 px-3 py-3">
              <p className="text-[10px] uppercase tracking-wider text-zinc-600 font-semibold px-2 mb-2">
                Recent Conversations
              </p>
              {conversations.length === 0 ? (
                <p className="text-xs text-zinc-600 px-2 py-4">No conversations yet</p>
              ) : (
                <div className="space-y-1">
                  {conversations.map((conv) => (
                    <button
                      key={conv.id}
                      data-testid={`conversation-${conv.id}`}
                      onClick={() => loadConversation(conv.id)}
                      className={`w-full text-left px-3 py-2.5 rounded-lg text-xs transition-colors duration-200 ${
                        activeConversationId === conv.id
                          ? "bg-white/10 text-white"
                          : "text-zinc-400 hover:bg-white/5 hover:text-zinc-200"
                      }`}
                    >
                      <div className="flex items-center gap-2">
                        <MessageSquare className="w-3.5 h-3.5 shrink-0" />
                        <span className="truncate">{conv.title}</span>
                      </div>
                      <p className="text-[10px] text-zinc-600 mt-1 ml-5">
                        {conv.message_count || 0} messages
                      </p>
                    </button>
                  ))}
                </div>
              )}
            </ScrollArea>

            {/* Sidebar Footer */}
            <div className="p-3 border-t border-white/5 space-y-1">
              <Button
                data-testid="evaluation-nav-btn"
                variant="ghost"
                onClick={() => navigate("/evaluation")}
                className="w-full justify-start h-8 text-xs text-zinc-400 hover:text-white hover:bg-white/5"
              >
                <BarChart3 className="w-3.5 h-3.5 mr-2" /> Evaluation Metrics
              </Button>
              <Button
                data-testid="feedback-analysis-nav-btn"
                variant="ghost"
                onClick={() => navigate("/feedback-analysis")}
                className="w-full justify-start h-8 text-xs text-zinc-400 hover:text-white hover:bg-white/5"
              >
                <TrendingUp className="w-3.5 h-3.5 mr-2" /> Feedback Analysis
              </Button>
              <Separator className="bg-white/5" />
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <button
                    data-testid="user-menu-btn"
                    className="flex items-center gap-2 w-full px-2 py-2 rounded-lg text-xs text-zinc-400 hover:bg-white/5 hover:text-white transition-colors duration-200"
                  >
                    <div className="w-7 h-7 rounded-full bg-blue-500/20 flex items-center justify-center">
                      <User className="w-3.5 h-3.5 text-blue-400" />
                    </div>
                    <div className="flex-1 text-left">
                      <p className="text-xs font-medium text-zinc-300">{user.name}</p>
                      <p className="text-[10px] text-zinc-600">{user.email}</p>
                    </div>
                    <ChevronDown className="w-3 h-3" />
                  </button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="bg-[#111111] border-white/10">
                  <DropdownMenuItem
                    data-testid="logout-btn"
                    onClick={onLogout}
                    className="text-xs text-zinc-400 hover:text-white focus:text-white focus:bg-white/5"
                  >
                    <LogOut className="w-3.5 h-3.5 mr-2" /> Sign Out
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </div>
        )}

        {/* Main Chat Area */}
        <div className="flex-1 flex flex-col min-w-0">
          {/* Chat Header */}
          <div className="h-14 border-b border-white/5 flex items-center justify-between px-5 backdrop-blur-xl bg-black/40">
            <div className="flex items-center gap-3">
              <button
                data-testid="toggle-sidebar-btn"
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="text-zinc-500 hover:text-white transition-colors duration-200"
              >
                <MessageSquare className="w-4 h-4" />
              </button>
              <h2
                className="text-sm font-semibold text-zinc-200"
                style={{ fontFamily: "'Manrope', sans-serif" }}
              >
                {activeConversationId ? "Conversation" : "New Conversation"}
              </h2>
            </div>
            <div className="flex items-center gap-2">
              <Tooltip>
                <TooltipTrigger asChild>
                  <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20">
                    <div className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                    <span className="text-[10px] text-emerald-400 font-medium">System Online</span>
                  </div>
                </TooltipTrigger>
                <TooltipContent className="bg-[#1A1A1A] border-white/10">
                  <p className="text-xs">All services operational</p>
                </TooltipContent>
              </Tooltip>
            </div>
          </div>

          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto px-5 py-6">
            {messages.length === 0 && !loading ? (
              /* Empty State / Quick Actions */
              <div className="flex flex-col items-center justify-center h-full max-w-2xl mx-auto">
                <div className="w-16 h-16 rounded-2xl bg-blue-500/10 flex items-center justify-center mb-6 animate-pulse-glow">
                  <Shield className="w-8 h-8 text-blue-400" />
                </div>
                <h2
                  className="text-2xl sm:text-3xl font-bold mb-2 text-center"
                  style={{ fontFamily: "'Manrope', sans-serif", letterSpacing: "-0.02em" }}
                >
                  Enterprise IT Assistant
                </h2>
                <p className="text-zinc-500 text-sm mb-10 text-center max-w-md">
                  AI-powered IT support with intelligent diagnostics, knowledge base retrieval, and automated ticket creation
                </p>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full max-w-lg">
                  {QUICK_QUERIES.map((q, i) => (
                    <button
                      key={i}
                      data-testid={`quick-query-${i}`}
                      onClick={() => handleSend(q.query)}
                      className="flex items-center gap-3 px-4 py-3.5 rounded-xl border border-white/5 bg-[#111111] hover:border-blue-500/30 hover:bg-[#1A1A1A] text-left transition-colors duration-300 group"
                    >
                      <div className="w-8 h-8 rounded-lg bg-white/5 flex items-center justify-center group-hover:bg-blue-500/10 transition-colors duration-300">
                        <q.icon className="w-4 h-4 text-zinc-500 group-hover:text-blue-400 transition-colors duration-300" />
                      </div>
                      <div>
                        <p className="text-xs font-medium text-zinc-300">{q.label}</p>
                        <p className="text-[10px] text-zinc-600 mt-0.5 truncate max-w-[160px]">{q.query}</p>
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              /* Chat Messages */
              <div className="max-w-3xl mx-auto space-y-1">
                {messages.map((msg, i) => (
                  <ChatMessage
                    key={msg.id || i}
                    message={msg}
                    intentIcon={intentIcon}
                    intentColor={intentColor}
                  />
                ))}

                {loading && (
                  <div className="flex gap-3 py-4 animate-fade-in-up">
                    <div className="w-8 h-8 rounded-lg bg-blue-500/10 flex items-center justify-center shrink-0">
                      <Shield className="w-4 h-4 text-blue-400" />
                    </div>
                    <div className="flex items-center gap-1 px-4 py-3 rounded-2xl rounded-tl-sm border border-[#27272A] bg-transparent">
                      <div className="w-2 h-2 rounded-full bg-blue-400 typing-dot" />
                      <div className="w-2 h-2 rounded-full bg-blue-400 typing-dot" />
                      <div className="w-2 h-2 rounded-full bg-blue-400 typing-dot" />
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>
            )}
          </div>

          {/* Input Area */}
          <ChatInput onSend={handleSend} loading={loading} />
        </div>
      </div>
    </TooltipProvider>
  );
}
