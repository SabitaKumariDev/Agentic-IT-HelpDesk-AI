import { useState } from "react";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Shield, User, FileText, Server,
  Clock, BookOpen, Ticket, ExternalLink, Tag, Calendar, Loader2,
  ThumbsUp, ThumbsDown, RefreshCw, ShieldCheck, ShieldAlert,
  AlertTriangle,
} from "lucide-react";
import ReactMarkdown from "react-markdown";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const CONFIDENCE_STYLES = {
  high: { bg: "bg-emerald-500/10", text: "text-emerald-400", border: "border-emerald-500/20" },
  medium: { bg: "bg-amber-500/10", text: "text-amber-400", border: "border-amber-500/20" },
  low: { bg: "bg-red-500/10", text: "text-red-400", border: "border-red-500/20" },
};

export const ChatMessage = ({ message, intentIcon, intentColor }) => {
  const [openDoc, setOpenDoc] = useState(null);
  const [docLoading, setDocLoading] = useState(false);
  const [feedback, setFeedback] = useState(null);
  const [feedbackLoading, setFeedbackLoading] = useState(false);
  const isUser = message.role === "user";

  const handleSourceClick = async (src) => {
    setDocLoading(true);
    setOpenDoc({ loading: true });
    try {
      let res;
      if (src.id) {
        res = await axios.get(`${API}/knowledge-base/${src.id}`);
      } else {
        res = await axios.get(`${API}/knowledge-base/search-by-title`, {
          params: { title: src.title },
        });
      }
      setOpenDoc(res.data);
    } catch {
      setOpenDoc({
        title: src.title, source: src.source,
        content: "Failed to load document content. Please try again.",
        category: "unknown", tags: [], last_updated: "",
      });
    } finally {
      setDocLoading(false);
    }
  };

  const handleFeedback = async (type) => {
    if (feedbackLoading || feedback) return;
    setFeedbackLoading(true);
    try {
      await axios.post(`${API}/feedback`, {
        message_id: message.id,
        feedback: type,
      });
      setFeedback(type);
    } catch (e) {
      console.error("Feedback submit failed", e);
    } finally {
      setFeedbackLoading(false);
    }
  };

  if (isUser) {
    return (
      <div className="flex justify-end py-3 animate-fade-in-up" data-testid="user-message">
        <div className="flex gap-3 max-w-[80%] flex-row-reverse">
          <div className="w-8 h-8 rounded-lg bg-[#27272A] flex items-center justify-center shrink-0">
            <User className="w-4 h-4 text-zinc-400" />
          </div>
          <div className="bg-[#27272A] text-white px-4 py-3 rounded-2xl rounded-tr-sm text-sm leading-relaxed">
            {message.content}
          </div>
        </div>
      </div>
    );
  }

  const quality = message.quality;
  const confStyle = quality?.retrieval_confidence_label
    ? CONFIDENCE_STYLES[quality.retrieval_confidence_label] || CONFIDENCE_STYLES.medium
    : null;

  return (
    <div className="py-3 animate-fade-in-up" data-testid="ai-message">
      <div className="flex gap-3 max-w-[90%]">
        <div className="w-8 h-8 rounded-lg bg-blue-500/10 flex items-center justify-center shrink-0 mt-0.5">
          <Shield className="w-4 h-4 text-blue-400" />
        </div>
        <div className="flex-1 space-y-3 min-w-0">
          {/* Intent Badge + Quality Signals + Latency */}
          <div className="flex items-center gap-2 flex-wrap">
            {message.intent && (
              <Badge
                data-testid={`intent-badge-${message.intent}`}
                className={`text-[10px] border ${intentColor(message.intent)} gap-1`}
              >
                {intentIcon(message.intent)}
                {message.intent?.replace("_", " ")}
              </Badge>
            )}
            {quality?.query_rewritten && (
              <Badge
                data-testid="query-rewritten-badge"
                title={`Rewritten to: ${quality.rewritten_query}`}
                className="text-[10px] bg-violet-500/10 text-violet-400 border border-violet-500/20 gap-1 cursor-help"
              >
                <RefreshCw className="w-2.5 h-2.5" />
                rewritten
              </Badge>
            )}
            {confStyle && (
              <Badge
                data-testid="confidence-badge"
                title={`Retrieval score: ${(quality.retrieval_score || 0).toFixed(3)} | Groundedness: ${((quality.groundedness_score || 0) * 100).toFixed(0)}%`}
                className={`text-[10px] ${confStyle.bg} ${confStyle.text} border ${confStyle.border} gap-1 cursor-help`}
              >
                {quality.retrieval_confidence_label === "high" ? (
                  <ShieldCheck className="w-2.5 h-2.5" />
                ) : quality.retrieval_confidence_label === "low" ? (
                  <ShieldAlert className="w-2.5 h-2.5" />
                ) : (
                  <AlertTriangle className="w-2.5 h-2.5" />
                )}
                {quality.retrieval_confidence_label} conf.
              </Badge>
            )}
            {message.latency != null && (
              <span className="flex items-center gap-1 text-[10px] text-zinc-600">
                <Clock className="w-3 h-3" />
                {message.latency}s
              </span>
            )}
          </div>

          {/* Response Content */}
          <div className="bg-transparent border border-[#27272A] px-4 py-3 rounded-2xl rounded-tl-sm text-sm text-gray-200">
            <div className="markdown-response">
              <ReactMarkdown>{message.content}</ReactMarkdown>
            </div>
          </div>

          {/* Feedback Buttons */}
          <div className="flex items-center gap-2" data-testid="feedback-buttons">
            <button
              data-testid="feedback-helpful-btn"
              onClick={() => handleFeedback("helpful")}
              disabled={!!feedback || feedbackLoading}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs transition-all duration-200 ${
                feedback === "helpful"
                  ? "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30"
                  : feedback
                  ? "bg-[#111111] text-zinc-600 border border-white/5 cursor-default"
                  : "bg-[#111111] text-zinc-400 border border-white/5 hover:border-emerald-500/30 hover:text-emerald-400 hover:bg-emerald-500/5"
              }`}
            >
              <ThumbsUp className="w-3 h-3" />
              Helpful
            </button>
            <button
              data-testid="feedback-not-helpful-btn"
              onClick={() => handleFeedback("not_helpful")}
              disabled={!!feedback || feedbackLoading}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs transition-all duration-200 ${
                feedback === "not_helpful"
                  ? "bg-red-500/15 text-red-400 border border-red-500/30"
                  : feedback
                  ? "bg-[#111111] text-zinc-600 border border-white/5 cursor-default"
                  : "bg-[#111111] text-zinc-400 border border-white/5 hover:border-red-500/30 hover:text-red-400 hover:bg-red-500/5"
              }`}
            >
              <ThumbsDown className="w-3 h-3" />
              Not Helpful
            </button>
            {feedbackLoading && <Loader2 className="w-3 h-3 animate-spin text-zinc-600" />}
            {feedback && <span className="text-[10px] text-zinc-600">Thank you for your feedback</span>}
          </div>

          {/* Sources */}
          {message.sources && message.sources.length > 0 && (
            <div className="space-y-1.5" data-testid="message-sources">
              <p className="text-[10px] uppercase tracking-wider text-zinc-600 font-semibold flex items-center gap-1">
                <BookOpen className="w-3 h-3" /> Sources
              </p>
              <div className="flex flex-wrap gap-2">
                {message.sources.map((src, i) => (
                  <button
                    key={i}
                    data-testid={`source-btn-${i}`}
                    onClick={() => handleSourceClick(src)}
                    className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-[#111111] border border-white/5 text-xs hover:border-blue-500/30 hover:bg-[#1A1A1A] transition-colors duration-200 cursor-pointer group"
                  >
                    <FileText className="w-3 h-3 text-blue-400 shrink-0" />
                    <span className="text-zinc-400 group-hover:text-zinc-200 transition-colors duration-200">
                      {src.title}
                    </span>
                    <span className="text-zinc-600 text-[10px]">({src.source})</span>
                    <span className="text-blue-400 text-[10px] font-mono">
                      {(src.score * 100).toFixed(0)}%
                    </span>
                    <ExternalLink className="w-2.5 h-2.5 text-zinc-600 group-hover:text-blue-400 transition-colors duration-200" />
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Actions */}
          {message.actions && message.actions.length > 0 && (
            <div className="space-y-2" data-testid="message-actions">
              {message.actions.map((action, i) => (
                <div key={i}>
                  {action.type === "system_check" && action.result && (
                    <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-[#111111] border border-white/5 text-xs">
                      <Server className="w-3.5 h-3.5 text-blue-400 shrink-0" />
                      <span className="text-zinc-400">{action.result.name}:</span>
                      <Badge
                        className={`text-[10px] border-0 ${
                          action.result.status === "operational"
                            ? "bg-emerald-500/15 text-emerald-400"
                            : "bg-amber-500/15 text-amber-400"
                        }`}
                      >
                        {action.result.status}
                      </Badge>
                    </div>
                  )}
                  {(action.type === "ticket_created" || action.type === "auto_escalated") && action.ticket && (
                    <div
                      className="px-4 py-3 rounded-xl bg-emerald-500/5 border border-emerald-500/20 space-y-2"
                      data-testid="ticket-card"
                    >
                      <div className="flex items-center gap-2">
                        <Ticket className="w-4 h-4 text-emerald-400" />
                        <span className="text-xs font-semibold text-emerald-400">
                          {action.type === "auto_escalated" ? "Auto-Escalated Ticket" : "Ticket Created"}
                        </span>
                      </div>
                      <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-xs">
                        <div>
                          <span className="text-zinc-600">Ticket ID: </span>
                          <span className="text-white font-mono">{action.ticket.ticket_id}</span>
                        </div>
                        <div>
                          <span className="text-zinc-600">Priority: </span>
                          <Badge
                            className={`text-[10px] border-0 ${
                              action.ticket.priority === "high"
                                ? "bg-red-500/15 text-red-400"
                                : action.ticket.priority === "medium"
                                ? "bg-amber-500/15 text-amber-400"
                                : "bg-blue-500/15 text-blue-400"
                            }`}
                          >
                            {action.ticket.priority}
                          </Badge>
                        </div>
                        <div>
                          <span className="text-zinc-600">Category: </span>
                          <span className="text-zinc-300">{action.ticket.category}</span>
                        </div>
                        <div>
                          <span className="text-zinc-600">ETA: </span>
                          <span className="text-zinc-300">{action.ticket.estimated_resolution}</span>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Source Document Dialog */}
      <Dialog open={!!openDoc} onOpenChange={(open) => { if (!open) setOpenDoc(null); }}>
        <DialogContent
          className="bg-[#111111] border-white/10 text-white max-w-2xl max-h-[80vh]"
          data-testid="source-document-dialog"
        >
          {(docLoading || openDoc?.loading) ? (
            <div className="flex flex-col items-center justify-center py-12 gap-3">
              <Loader2 className="w-6 h-6 animate-spin text-blue-400" />
              <p className="text-xs text-zinc-500">Loading document...</p>
            </div>
          ) : openDoc && !openDoc.loading && (
            <>
              <DialogHeader>
                <div className="flex items-center gap-2 mb-1">
                  <FileText className="w-5 h-5 text-blue-400" />
                  <DialogTitle
                    className="text-lg font-bold text-white"
                    style={{ fontFamily: "'Manrope', sans-serif" }}
                  >
                    {openDoc.title}
                  </DialogTitle>
                </div>
                <div className="flex items-center gap-3 flex-wrap mt-2">
                  <span className="flex items-center gap-1 text-[11px] text-zinc-500">
                    <BookOpen className="w-3 h-3" /> {openDoc.source}
                  </span>
                  {openDoc.category && (
                    <Badge className="text-[10px] bg-blue-500/10 text-blue-400 border-blue-500/20">
                      {openDoc.category}
                    </Badge>
                  )}
                  {openDoc.last_updated && (
                    <span className="flex items-center gap-1 text-[11px] text-zinc-600">
                      <Calendar className="w-3 h-3" /> {openDoc.last_updated}
                    </span>
                  )}
                </div>
                {openDoc.tags && openDoc.tags.length > 0 && (
                  <div className="flex items-center gap-1.5 flex-wrap mt-2">
                    <Tag className="w-3 h-3 text-zinc-600" />
                    {openDoc.tags.map((tag, i) => (
                      <span key={i} className="text-[10px] px-2 py-0.5 rounded-full bg-white/5 text-zinc-500">
                        {tag}
                      </span>
                    ))}
                  </div>
                )}
              </DialogHeader>
              <ScrollArea className="max-h-[50vh] mt-4 pr-4">
                <div className="text-sm text-zinc-300 leading-relaxed whitespace-pre-line">
                  {openDoc.content}
                </div>
              </ScrollArea>
            </>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default ChatMessage;