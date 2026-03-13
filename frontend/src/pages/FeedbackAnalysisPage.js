import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  ArrowLeft, Loader2, BarChart3, ThumbsUp, ThumbsDown,
  AlertTriangle, ShieldCheck, ShieldAlert, Clock, RefreshCw,
  Ticket, Target, Lightbulb, FileWarning, TrendingUp,
} from "lucide-react";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const PRIORITY_STYLES = {
  high: "bg-red-500/10 text-red-400 border-red-500/20",
  medium: "bg-amber-500/10 text-amber-400 border-amber-500/20",
  low: "bg-blue-500/10 text-blue-400 border-blue-500/20",
};

export default function FeedbackAnalysisPage() {
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchAnalysis = async () => {
    setLoading(true);
    setError("");
    try {
      const res = await axios.get(`${API}/feedback/analysis`);
      setData(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to load analysis data");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalysis();
  }, []);

  const stats = data?.stats || {};

  return (
    <div className="min-h-screen bg-[#0A0A0A] p-6" data-testid="feedback-analysis-page">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-4">
            <Button
              data-testid="back-to-chat-btn"
              variant="ghost"
              onClick={() => navigate("/chat")}
              className="text-zinc-400 hover:text-white hover:bg-white/5"
            >
              <ArrowLeft className="w-4 h-4 mr-2" /> Back to Chat
            </Button>
            <div>
              <h1
                className="text-2xl sm:text-3xl font-bold"
                style={{ fontFamily: "'Manrope', sans-serif", letterSpacing: "-0.02em" }}
              >
                Feedback Analysis
              </h1>
              <p className="text-zinc-500 text-sm mt-1">
                Self-improving RAG quality signals and failure analysis
              </p>
            </div>
          </div>
          <Button
            data-testid="refresh-analysis-btn"
            onClick={fetchAnalysis}
            disabled={loading}
            className="bg-blue-600 hover:bg-blue-500 text-white font-medium rounded-xl active:scale-95 transition-transform duration-100"
          >
            {loading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <span className="flex items-center gap-2">
                <RefreshCw className="w-4 h-4" /> Refresh
              </span>
            )}
          </Button>
        </div>

        {error && (
          <div className="flex items-center gap-2 p-4 rounded-xl bg-red-500/10 border border-red-500/20 mb-6">
            <AlertTriangle className="w-4 h-4 text-red-400" />
            <p className="text-sm text-red-400">{error}</p>
          </div>
        )}

        {loading && (
          <div className="flex flex-col items-center justify-center py-24">
            <Loader2 className="w-10 h-10 text-blue-400 animate-spin mb-4" />
            <p className="text-zinc-400 text-sm">Loading analysis data...</p>
          </div>
        )}

        {!loading && data && (
          <div className="space-y-6 animate-fade-in-up">
            {/* ─── Operational Metrics ─────────────────────────────── */}
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
              <MetricCard
                icon={BarChart3} color="text-blue-400" bg="bg-blue-500/10"
                label="Total Interactions" value={stats.total_interactions || 0}
              />
              <MetricCard
                icon={ThumbsUp} color="text-emerald-400" bg="bg-emerald-500/10"
                label="Helpful Rate" value={`${stats.helpful_rate || 0}%`}
              />
              <MetricCard
                icon={ThumbsDown} color="text-red-400" bg="bg-red-500/10"
                label="Not Helpful Rate" value={`${stats.not_helpful_rate || 0}%`}
              />
              <MetricCard
                icon={ShieldAlert} color="text-amber-400" bg="bg-amber-500/10"
                label="Low Confidence" value={`${stats.low_confidence_rate || 0}%`}
              />
              <MetricCard
                icon={FileWarning} color="text-orange-400" bg="bg-orange-500/10"
                label="Ungrounded" value={`${stats.ungrounded_rate || 0}%`}
              />
              <MetricCard
                icon={Clock} color="text-violet-400" bg="bg-violet-500/10"
                label="Avg Latency" value={`${Math.round(stats.average_latency_ms || 0)}ms`}
              />
            </div>

            {/* ─── Secondary Stats Row ───────────────────────────── */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <StatPill label="Queries Rewritten" value={stats.query_rewrite_count || 0} total={stats.total_interactions} />
              <StatPill label="Tickets Created" value={stats.ticket_creation_count || 0} total={stats.total_interactions} />
              <StatPill label="Helpful Responses" value={stats.helpful_count || 0} total={stats.helpful_count + stats.not_helpful_count} />
              <StatPill label="No Feedback Yet" value={stats.no_feedback_count || 0} total={stats.total_interactions} />
            </div>

            {/* ─── Failure Breakdown ─────────────────────────────── */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {/* Intent Failure Breakdown */}
              <Card className="p-5 bg-[#111111] border-white/5">
                <h3
                  className="text-sm font-semibold text-zinc-200 mb-4 flex items-center gap-2"
                  style={{ fontFamily: "'Manrope', sans-serif" }}
                >
                  <Target className="w-4 h-4 text-blue-400" />
                  Failure by Intent
                </h3>
                {Object.keys(data.intent_failure_breakdown || {}).length === 0 ? (
                  <p className="text-xs text-zinc-600">No failures recorded yet</p>
                ) : (
                  <div className="space-y-3">
                    {Object.entries(data.intent_failure_breakdown || {}).map(([intent, count]) => (
                      <div key={intent} className="space-y-1">
                        <div className="flex justify-between text-xs">
                          <span className="text-zinc-400">{intent.replace("_", " ")}</span>
                          <span className="text-zinc-500">{count} failures</span>
                        </div>
                        <Progress
                          value={data.failure_count ? (count / data.failure_count) * 100 : 0}
                          className="h-1.5 bg-white/5"
                        />
                      </div>
                    ))}
                  </div>
                )}
              </Card>

              {/* Category Failure Breakdown */}
              <Card className="p-5 bg-[#111111] border-white/5">
                <h3
                  className="text-sm font-semibold text-zinc-200 mb-4 flex items-center gap-2"
                  style={{ fontFamily: "'Manrope', sans-serif" }}
                >
                  <TrendingUp className="w-4 h-4 text-amber-400" />
                  Failure by Category
                </h3>
                {Object.keys(data.category_failure_breakdown || {}).length === 0 ? (
                  <p className="text-xs text-zinc-600">No category data available yet</p>
                ) : (
                  <div className="space-y-3">
                    {Object.entries(data.category_failure_breakdown || {}).map(([cat, count]) => (
                      <div key={cat} className="space-y-1">
                        <div className="flex justify-between text-xs">
                          <span className="text-zinc-400">{cat}</span>
                          <span className="text-zinc-500">{count}</span>
                        </div>
                        <Progress
                          value={data.failure_count ? (count / data.failure_count) * 100 : 0}
                          className="h-1.5 bg-white/5"
                        />
                      </div>
                    ))}
                  </div>
                )}
              </Card>
            </div>

            {/* ─── Recommendations ────────────────────────────────── */}
            <Card className="p-5 bg-[#111111] border-white/5">
              <h3
                className="text-sm font-semibold text-zinc-200 mb-4 flex items-center gap-2"
                style={{ fontFamily: "'Manrope', sans-serif" }}
              >
                <Lightbulb className="w-4 h-4 text-amber-400" />
                Actionable Recommendations
              </h3>
              <div className="space-y-3">
                {(data.recommendations || []).map((rec, i) => (
                  <div
                    key={i}
                    data-testid={`recommendation-${i}`}
                    className="flex items-start gap-3 p-3 rounded-lg bg-white/[0.02] border border-white/5"
                  >
                    <Badge className={`text-[10px] border shrink-0 mt-0.5 ${PRIORITY_STYLES[rec.priority] || PRIORITY_STYLES.low}`}>
                      {rec.priority}
                    </Badge>
                    <div className="flex-1 min-w-0">
                      <p className="text-xs font-medium text-zinc-200">{rec.action}</p>
                      <p className="text-[11px] text-zinc-500 mt-1">{rec.reason}</p>
                      <Badge className="text-[10px] bg-white/5 text-zinc-500 border-0 mt-1.5">
                        {rec.category}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            </Card>

            {/* ─── Sample Failure Cases ───────────────────────────── */}
            <Card className="p-5 bg-[#111111] border-white/5">
              <h3
                className="text-sm font-semibold text-zinc-200 mb-4 flex items-center gap-2"
                style={{ fontFamily: "'Manrope', sans-serif" }}
              >
                <FileWarning className="w-4 h-4 text-red-400" />
                Sample Failure Cases
              </h3>
              <ScrollArea className="max-h-[500px]">
                <div className="space-y-4">
                  {(data.sample_failures || []).map((f, i) => (
                    <div
                      key={i}
                      data-testid={`failure-case-${i}`}
                      className="p-4 rounded-xl border border-white/5 bg-white/[0.01] space-y-3"
                    >
                      <div className="flex items-start justify-between gap-4">
                        <p className="text-sm text-zinc-200 font-medium">"{f.query}"</p>
                        <div className="flex items-center gap-2 shrink-0">
                          <Badge className={`text-[10px] border ${
                            PRIORITY_STYLES[f.confidence_label] ||
                            (f.confidence_label === "high" ? PRIORITY_STYLES.low : PRIORITY_STYLES.medium)
                          }`}>
                            {f.confidence_label} conf.
                          </Badge>
                          {f.user_feedback && (
                            <Badge className={`text-[10px] border-0 ${
                              f.user_feedback === "helpful"
                                ? "bg-emerald-500/15 text-emerald-400"
                                : "bg-red-500/15 text-red-400"
                            }`}>
                              {f.user_feedback === "helpful" ? "Helpful" : "Not Helpful"}
                            </Badge>
                          )}
                        </div>
                      </div>
                      <div className="grid grid-cols-2 gap-3 text-xs">
                        <div>
                          <span className="text-zinc-600">Grounded: </span>
                          <span className={f.groundedness?.grounded ? "text-emerald-400" : "text-red-400"}>
                            {f.groundedness?.grounded ? "Yes" : "No"} ({((f.groundedness?.score || 0) * 100).toFixed(0)}%)
                          </span>
                        </div>
                        <div>
                          <span className="text-zinc-600">Reasoning: </span>
                          <span className="text-zinc-400">{f.groundedness?.reasoning || "N/A"}</span>
                        </div>
                      </div>
                      <div className="p-2.5 rounded-lg bg-amber-500/5 border border-amber-500/10">
                        <p className="text-[11px] text-amber-300">
                          <Lightbulb className="w-3 h-3 inline mr-1" />
                          {f.recommended_fix}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </ScrollArea>
            </Card>
          </div>
        )}

        {!loading && !data && !error && (
          <div className="flex flex-col items-center justify-center py-24">
            <div className="w-16 h-16 rounded-2xl bg-blue-500/10 flex items-center justify-center mb-6">
              <BarChart3 className="w-8 h-8 text-blue-400" />
            </div>
            <h3 className="text-lg font-semibold text-zinc-300 mb-2" style={{ fontFamily: "'Manrope', sans-serif" }}>
              No Analysis Data
            </h3>
            <p className="text-zinc-600 text-sm text-center max-w-md">
              Start using the chat to generate interaction data. The analysis engine will detect
              patterns and generate improvement recommendations.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

function MetricCard({ icon: Icon, color, bg, label, value }) {
  return (
    <Card
      data-testid={`metric-${label.toLowerCase().replace(/\s+/g, "-")}`}
      className="p-4 bg-[#111111] border-white/5 hover:border-white/10 transition-colors duration-300"
    >
      <div className={`w-8 h-8 rounded-lg ${bg} flex items-center justify-center mb-3`}>
        <Icon className={`w-4 h-4 ${color}`} />
      </div>
      <p className="text-[10px] text-zinc-500 uppercase tracking-wider font-medium">{label}</p>
      <p className="text-xl font-bold text-white mt-1" style={{ fontFamily: "'Manrope', sans-serif" }}>
        {value}
      </p>
    </Card>
  );
}

function StatPill({ label, value, total }) {
  const pct = total > 0 ? Math.round((value / total) * 100) : 0;
  return (
    <div className="flex items-center justify-between px-4 py-3 rounded-xl bg-[#111111] border border-white/5">
      <span className="text-xs text-zinc-500">{label}</span>
      <span className="text-sm font-semibold text-zinc-200">
        {value} <span className="text-zinc-600 text-[10px]">({pct}%)</span>
      </span>
    </div>
  );
}
