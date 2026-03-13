import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Shield, ArrowRight, Cpu, Network, Ticket } from "lucide-react";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function LoginPage({ onLogin }) {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email.trim() || !email.includes("@")) {
      setError("Please enter a valid corporate email");
      return;
    }
    setLoading(true);
    setError("");
    try {
      const res = await axios.post(`${API}/login`, { email: email.trim() });
      onLogin(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Login failed. Try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex" data-testid="login-page">
      {/* Left: Background Image */}
      <div
        className="hidden lg:flex lg:w-1/2 relative items-center justify-center"
        style={{
          backgroundImage: `url(https://images.unsplash.com/photo-1759735541630-036eefb7cd3a?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjAzNzl8MHwxfHNlYXJjaHwzfHxmdXR1cmlzdGljJTIwYWJzdHJhY3QlMjBibHVlJTIwdGVjaG5vbG9neSUyMGJhY2tncm91bmR8ZW58MHx8fHwxNzczMjcwMTA5fDA&ixlib=rb-4.1.0&q=85)`,
          backgroundSize: "cover",
          backgroundPosition: "center",
        }}
      >
        <div className="absolute inset-0 bg-black/80" />
        <div className="relative z-10 max-w-md px-8">
          <div className="flex items-center gap-3 mb-8">
            <div className="w-12 h-12 rounded-xl bg-blue-500/20 flex items-center justify-center">
              <Shield className="w-6 h-6 text-blue-400" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-white" style={{ fontFamily: "'Manrope', sans-serif" }}>
                AI IT Assistant
              </h2>
              <p className="text-sm text-zinc-400">Enterprise Support Platform</p>
            </div>
          </div>

          <div className="space-y-6">
            {[
              { icon: Cpu, label: "Intelligent Diagnostics", desc: "AI-powered troubleshooting with RAG" },
              { icon: Network, label: "Semantic Search", desc: "Knowledge base with vector retrieval" },
              { icon: Ticket, label: "Auto Ticket Creation", desc: "Automated issue escalation" },
            ].map((item, i) => (
              <div
                key={i}
                className="flex items-start gap-4 p-4 rounded-xl border border-white/5 bg-white/5 backdrop-blur-sm"
                style={{ animationDelay: `${i * 0.15}s` }}
              >
                <div className="w-10 h-10 rounded-lg bg-blue-500/10 flex items-center justify-center shrink-0">
                  <item.icon className="w-5 h-5 text-blue-400" />
                </div>
                <div>
                  <p className="font-semibold text-white text-sm">{item.label}</p>
                  <p className="text-xs text-zinc-500 mt-0.5">{item.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Right: Login Form */}
      <div className="flex-1 flex items-center justify-center p-8 bg-[#0A0A0A]">
        <div className="w-full max-w-sm">
          <div className="lg:hidden flex items-center gap-3 mb-10">
            <div className="w-10 h-10 rounded-xl bg-blue-500/20 flex items-center justify-center">
              <Shield className="w-5 h-5 text-blue-400" />
            </div>
            <span className="text-lg font-bold" style={{ fontFamily: "'Manrope', sans-serif" }}>
              AI IT Assistant
            </span>
          </div>

          <h1
            className="text-3xl sm:text-4xl font-extrabold tracking-tight mb-2"
            style={{ fontFamily: "'Manrope', sans-serif", letterSpacing: "-0.02em" }}
          >
            Welcome back
          </h1>
          <p className="text-zinc-500 mb-10 text-sm">
            Sign in with your corporate email to access IT support
          </p>

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-xs font-medium text-zinc-400 mb-2 uppercase tracking-wider">
                Corporate Email
              </label>
              <Input
                data-testid="login-email-input"
                type="email"
                placeholder="you@company.com"
                value={email}
                onChange={(e) => { setEmail(e.target.value); setError(""); }}
                className="h-12 bg-[#1A1A1A] border-transparent focus:border-blue-500 focus:ring-1 focus:ring-blue-500 text-white placeholder:text-zinc-600"
              />
            </div>

            {error && (
              <p className="text-red-400 text-xs" data-testid="login-error">{error}</p>
            )}

            <Button
              data-testid="login-submit-btn"
              type="submit"
              disabled={loading}
              className="w-full h-12 bg-blue-600 hover:bg-blue-500 text-white font-semibold rounded-xl active:scale-95 transition-transform duration-100"
            >
              {loading ? (
                <span className="flex items-center gap-2">
                  <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Signing in...
                </span>
              ) : (
                <span className="flex items-center gap-2">
                  Sign In <ArrowRight className="w-4 h-4" />
                </span>
              )}
            </Button>
          </form>

          <p className="text-center text-zinc-600 text-xs mt-8">
            No password required for demo. Enter any corporate email.
          </p>
        </div>
      </div>
    </div>
  );
}
