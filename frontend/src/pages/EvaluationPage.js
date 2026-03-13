import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  ArrowLeft, Play, Loader2, CheckCircle2, XCircle, Clock,
  Target, Shield, AlertTriangle, BarChart3, Zap
} from "lucide-react";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function EvaluationPage({ user, onLogout }) {
  const navigate = useNavigate();
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const runEvaluation = async () => {
    setLoading(true);
    setError("");
    try {
      // Start evaluation task
      const startRes = await axios.post(`${API}/evaluation/run`);
      const taskId = startRes.data.task_id;

      // Poll for results every 3 seconds
      const poll = async () => {
        for (let i = 0; i < 60; i++) {
          await new Promise((r) => setTimeout(r, 3000));
          try {
            const statusRes = await axios.get(`${API}/evaluation/status/${taskId}`);
            if (statusRes.data.status === "completed") {
              setResults(statusRes.data.results);
              return;
            }
            if (statusRes.data.status === "error") {
              setError(`Evaluation error: ${statusRes.data.error || "Unknown error"}`);
              return;
            }
          } catch {
            // Polling request failed, retry
          }
        }
        setError("Evaluation timed out after 3 minutes. Please try again.");
      };

      await poll();
    } catch (err) {
      const detail = err.response?.data?.detail || err.message || "Unknown error";
      setError(`Evaluation failed: ${detail}`);
    } finally {
      setLoading(false);
    }
  };

  const metricCards = results?.summary
    ? [
        {
          label: "Retrieval Accuracy",
          value: results.summary.retrieval_accuracy,
          icon: Target,
          color: "text-blue-400",
          bg: "bg-blue-500/10",
        },
        {
          label: "Intent Accuracy",
          value: results.summary.intent_accuracy,
          icon: Shield,
          color: "text-emerald-400",
          bg: "bg-emerald-500/10",
        },
        {
          label: "Groundedness Rate",
          value: results.summary.groundedness_rate,
          icon: CheckCircle2,
          color: "text-violet-400",
          bg: "bg-violet-500/10",
        },
        {
          label: "Avg Latency",
          value: results.summary.average_latency,
          unit: "s",
          icon: Clock,
          color: "text-amber-400",
          bg: "bg-amber-500/10",
        },
      ]
    : [];

  return (
    <div className="min-h-screen bg-[#0A0A0A] p-6" data-testid="evaluation-page">
      <div className="max-w-5xl mx-auto">
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
                RAG Evaluation Pipeline
              </h1>
              <p className="text-zinc-500 text-sm mt-1">
                Measure retrieval accuracy, response groundedness, hallucination rate, and latency
              </p>
            </div>
          </div>
          <Button
            data-testid="run-evaluation-btn"
            onClick={runEvaluation}
            disabled={loading}
            className="bg-blue-600 hover:bg-blue-500 text-white font-medium rounded-xl active:scale-95 transition-transform duration-100"
          >
            {loading ? (
              <span className="flex items-center gap-2">
                <Loader2 className="w-4 h-4 animate-spin" /> Running...
              </span>
            ) : (
              <span className="flex items-center gap-2">
                <Play className="w-4 h-4" /> Run Evaluation
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

        {!results && !loading && (
          <div className="flex flex-col items-center justify-center py-24">
            <div className="w-16 h-16 rounded-2xl bg-blue-500/10 flex items-center justify-center mb-6">
              <BarChart3 className="w-8 h-8 text-blue-400" />
            </div>
            <h3 className="text-lg font-semibold text-zinc-300 mb-2" style={{ fontFamily: "'Manrope', sans-serif" }}>
              No Evaluation Results
            </h3>
            <p className="text-zinc-600 text-sm text-center max-w-md mb-6">
              Run the evaluation pipeline to test 8 queries against the AI system and measure retrieval accuracy, intent classification, response groundedness, and latency.
            </p>
          </div>
        )}

        {loading && (
          <div className="flex flex-col items-center justify-center py-24">
            <Loader2 className="w-10 h-10 text-blue-400 animate-spin mb-4" />
            <p className="text-zinc-400 text-sm">Running evaluation pipeline across 8 test queries...</p>
            <p className="text-zinc-600 text-xs mt-1">This may take 30-60 seconds</p>
          </div>
        )}

        {results && !loading && (
          <div className="space-y-6 animate-fade-in-up">
            {/* Summary Metrics */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {metricCards.map((m, i) => (
                <Card
                  key={i}
                  className="p-5 bg-[#111111] border-white/5 hover:border-white/10 transition-colors duration-300"
                >
                  <div className="flex items-center gap-3 mb-3">
                    <div className={`w-9 h-9 rounded-lg ${m.bg} flex items-center justify-center`}>
                      <m.icon className={`w-4 h-4 ${m.color}`} />
                    </div>
                    <span className="text-xs text-zinc-500 font-medium">{m.label}</span>
                  </div>
                  <div className="flex items-end gap-1">
                    <span className="text-3xl font-bold text-white" style={{ fontFamily: "'Manrope', sans-serif" }}>
                      {m.value}
                    </span>
                    <span className="text-sm text-zinc-500 mb-1">{m.unit || "%"}</span>
                  </div>
                  {!m.unit && (
                    <Progress value={m.value} className="h-1 mt-3 bg-white/5" />
                  )}
                </Card>
              ))}
            </div>

            {/* Detailed Results Tabs */}
            <Tabs defaultValue="retrieval" className="w-full">
              <TabsList className="bg-[#111111] border border-white/5">
                <TabsTrigger
                  data-testid="tab-retrieval"
                  value="retrieval"
                  className="text-xs data-[state=active]:bg-white/10 data-[state=active]:text-white"
                >
                  Retrieval
                </TabsTrigger>
                <TabsTrigger
                  data-testid="tab-intent"
                  value="intent"
                  className="text-xs data-[state=active]:bg-white/10 data-[state=active]:text-white"
                >
                  Intent
                </TabsTrigger>
                <TabsTrigger
                  data-testid="tab-groundedness"
                  value="groundedness"
                  className="text-xs data-[state=active]:bg-white/10 data-[state=active]:text-white"
                >
                  Groundedness
                </TabsTrigger>
                <TabsTrigger
                  data-testid="tab-latency"
                  value="latency"
                  className="text-xs data-[state=active]:bg-white/10 data-[state=active]:text-white"
                >
                  Latency
                </TabsTrigger>
              </TabsList>

              <TabsContent value="retrieval">
                <Card className="bg-[#111111] border-white/5 p-0 overflow-hidden">
                  <ScrollArea className="max-h-[400px]">
                    <table className="w-full text-xs">
                      <thead>
                        <tr className="border-b border-white/5">
                          <th className="text-left p-3 text-zinc-500 font-medium">Query</th>
                          <th className="text-left p-3 text-zinc-500 font-medium">Expected</th>
                          <th className="text-left p-3 text-zinc-500 font-medium">Retrieved</th>
                          <th className="text-left p-3 text-zinc-500 font-medium">Score</th>
                          <th className="text-center p-3 text-zinc-500 font-medium">Hit</th>
                        </tr>
                      </thead>
                      <tbody>
                        {results.retrieval_results?.map((r, i) => (
                          <tr key={i} className="border-b border-white/5 hover:bg-white/[0.02]">
                            <td className="p-3 text-zinc-300 max-w-[200px] truncate">{r.query}</td>
                            <td className="p-3 text-zinc-500">{r.expected?.join(", ")}</td>
                            <td className="p-3 text-zinc-500">{r.retrieved?.join(", ")}</td>
                            <td className="p-3 text-zinc-400">{r.top_score?.toFixed(3)}</td>
                            <td className="p-3 text-center">
                              {r.hit ? (
                                <CheckCircle2 className="w-4 h-4 text-emerald-400 mx-auto" />
                              ) : (
                                <XCircle className="w-4 h-4 text-red-400 mx-auto" />
                              )}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </ScrollArea>
                </Card>
              </TabsContent>

              <TabsContent value="intent">
                <Card className="bg-[#111111] border-white/5 p-0 overflow-hidden">
                  <ScrollArea className="max-h-[400px]">
                    <table className="w-full text-xs">
                      <thead>
                        <tr className="border-b border-white/5">
                          <th className="text-left p-3 text-zinc-500 font-medium">Query</th>
                          <th className="text-left p-3 text-zinc-500 font-medium">Expected</th>
                          <th className="text-left p-3 text-zinc-500 font-medium">Predicted</th>
                          <th className="text-center p-3 text-zinc-500 font-medium">Correct</th>
                        </tr>
                      </thead>
                      <tbody>
                        {results.intent_results?.map((r, i) => (
                          <tr key={i} className="border-b border-white/5 hover:bg-white/[0.02]">
                            <td className="p-3 text-zinc-300 max-w-[250px] truncate">{r.query}</td>
                            <td className="p-3">
                              <Badge className="text-[10px] bg-zinc-800 text-zinc-300 border-0">{r.expected}</Badge>
                            </td>
                            <td className="p-3">
                              <Badge className="text-[10px] bg-zinc-800 text-zinc-300 border-0">{r.predicted}</Badge>
                            </td>
                            <td className="p-3 text-center">
                              {r.correct ? (
                                <CheckCircle2 className="w-4 h-4 text-emerald-400 mx-auto" />
                              ) : (
                                <XCircle className="w-4 h-4 text-red-400 mx-auto" />
                              )}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </ScrollArea>
                </Card>
              </TabsContent>

              <TabsContent value="groundedness">
                <Card className="bg-[#111111] border-white/5 p-0 overflow-hidden">
                  <ScrollArea className="max-h-[400px]">
                    <table className="w-full text-xs">
                      <thead>
                        <tr className="border-b border-white/5">
                          <th className="text-left p-3 text-zinc-500 font-medium">Query</th>
                          <th className="text-left p-3 text-zinc-500 font-medium">Keyword Coverage</th>
                          <th className="text-center p-3 text-zinc-500 font-medium">Grounded</th>
                        </tr>
                      </thead>
                      <tbody>
                        {results.groundedness_results?.map((r, i) => (
                          <tr key={i} className="border-b border-white/5 hover:bg-white/[0.02]">
                            <td className="p-3 text-zinc-300 max-w-[300px] truncate">{r.query}</td>
                            <td className="p-3 text-zinc-400">{r.keyword_coverage}</td>
                            <td className="p-3 text-center">
                              {r.grounded ? (
                                <CheckCircle2 className="w-4 h-4 text-emerald-400 mx-auto" />
                              ) : (
                                <XCircle className="w-4 h-4 text-red-400 mx-auto" />
                              )}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </ScrollArea>
                </Card>
              </TabsContent>

              <TabsContent value="latency">
                <Card className="bg-[#111111] border-white/5 p-0 overflow-hidden">
                  <ScrollArea className="max-h-[400px]">
                    <table className="w-full text-xs">
                      <thead>
                        <tr className="border-b border-white/5">
                          <th className="text-left p-3 text-zinc-500 font-medium">Query</th>
                          <th className="text-left p-3 text-zinc-500 font-medium">Latency</th>
                          <th className="text-left p-3 text-zinc-500 font-medium">Status</th>
                        </tr>
                      </thead>
                      <tbody>
                        {results.latencies?.map((r, i) => (
                          <tr key={i} className="border-b border-white/5 hover:bg-white/[0.02]">
                            <td className="p-3 text-zinc-300 max-w-[300px] truncate">{r.query}</td>
                            <td className="p-3 text-zinc-400">{r.latency}s</td>
                            <td className="p-3">
                              <Badge
                                className={`text-[10px] border-0 ${
                                  r.latency < 3
                                    ? "bg-emerald-500/15 text-emerald-400"
                                    : r.latency < 5
                                    ? "bg-amber-500/15 text-amber-400"
                                    : "bg-red-500/15 text-red-400"
                                }`}
                              >
                                {r.latency < 3 ? "Fast" : r.latency < 5 ? "Normal" : "Slow"}
                              </Badge>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </ScrollArea>
                </Card>
              </TabsContent>
            </Tabs>

            {/* Hallucination Rate */}
            <Card className="p-5 bg-[#111111] border-white/5">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-9 h-9 rounded-lg bg-red-500/10 flex items-center justify-center">
                    <AlertTriangle className="w-4 h-4 text-red-400" />
                  </div>
                  <div>
                    <p className="text-xs text-zinc-500 font-medium">Hallucination Rate</p>
                    <p className="text-sm text-zinc-400 mt-0.5">
                      Percentage of responses not grounded in knowledge base
                    </p>
                  </div>
                </div>
                <div className="flex items-end gap-1">
                  <span className="text-2xl font-bold text-white" style={{ fontFamily: "'Manrope', sans-serif" }}>
                    {results.summary.hallucination_rate}
                  </span>
                  <span className="text-sm text-zinc-500 mb-0.5">%</span>
                </div>
              </div>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
}
