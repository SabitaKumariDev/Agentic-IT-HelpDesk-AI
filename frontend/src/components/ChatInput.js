import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Send, Loader2 } from "lucide-react";

export const ChatInput = ({ onSend, loading }) => {
  const [value, setValue] = useState("");
  const textareaRef = useRef(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!value.trim() || loading) return;
    onSend(value.trim());
    setValue("");
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  // Auto-resize textarea
  useEffect(() => {
    const el = textareaRef.current;
    if (el) {
      el.style.height = "auto";
      el.style.height = Math.min(el.scrollHeight, 160) + "px";
    }
  }, [value]);

  return (
    <div className="border-t border-white/5 bg-[#0A0A0A] px-5 py-4" data-testid="chat-input-area">
      <form onSubmit={handleSubmit} className="max-w-3xl mx-auto">
        <div className="flex items-end gap-3 bg-[#111111] border border-white/5 rounded-xl px-4 py-3 focus-within:border-blue-500/40 transition-colors duration-200">
          <textarea
            ref={textareaRef}
            data-testid="chat-input"
            value={value}
            onChange={(e) => setValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Describe your IT issue or ask a question..."
            rows={1}
            className="flex-1 bg-transparent text-sm text-white placeholder:text-zinc-600 resize-none outline-none min-h-[24px] max-h-[160px]"
          />
          <Button
            data-testid="chat-send-btn"
            type="submit"
            disabled={!value.trim() || loading}
            size="sm"
            className="h-8 w-8 p-0 bg-blue-600 hover:bg-blue-500 disabled:bg-zinc-800 disabled:text-zinc-600 rounded-lg shrink-0 active:scale-90 transition-transform duration-100"
          >
            {loading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
          </Button>
        </div>
        <p className="text-[10px] text-zinc-700 text-center mt-2">
          AI IT Assistant uses RAG to provide answers grounded in the enterprise knowledge base
        </p>
      </form>
    </div>
  );
};

export default ChatInput;
