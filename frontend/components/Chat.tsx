"use client";
import { MessageCircle } from "lucide-react";
import { useState } from "react";
import ReactMarkdown from "react-markdown";
const API = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
export default function Chat({ context }: any) {
  const [messages, setMessages] = useState<any[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { role: "user", text: input };

    setMessages((prev) => [...prev, userMessage]);

    const currentInput = input;
    setInput("");
    setLoading(true);

    try {
      const res = await fetch(`${API}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: currentInput,
          context: context || {},
        }),
      });
      console.log("API URL:", API);
      const text = await res.text();
      const data = JSON.parse(text)


      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: data.response },
      ]);
    } catch (err) {
      console.error(err);

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text: "Something went wrong. Try again.",
        },
      ]);
    }

    setLoading(false);
  };

  return (
    <div>
      <div className="flex items-center gap-2 mb-2">
        <MessageCircle size={18} />
        <h2 className="text-xl font-semibold">Assistant Coach</h2>
        </div>

      <div className="h-64 overflow-y-auto bg-gray-50 p-4 rounded-lg mb-3 flex flex-col gap-3">

        {messages.length === 0 && (
          <p className="text-gray-400 text-sm">
            Ask about technique, training, or your swim analysis...
          </p>
        )}

        {messages.map((m, i) => (
          <div
            key={i}
            className={`flex ${
              m.role === "user" ? "justify-end" : "justify-start"
            }`}
          >
            <div
              className={`p-3 rounded-xl max-w-[75%] ${
                m.role === "user"
                  ? "bg-blue-500 text-white"
                  : "bg-white border"
              }`}
            >
              {m.role === "user" ? (
                <p className="whitespace-pre-wrap">{m.text}</p>
              ) : (
                <div className="prose prose-sm max-w-none">
                  <ReactMarkdown>{m.text}</ReactMarkdown>
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="text-sm text-gray-400 italic">
            Coach is typing...
          </div>
        )}
      </div>

      <div className="flex gap-2">
        <input
          className="border p-2 flex-1 rounded-lg"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question..."
          onKeyDown={(e) => {
            if (e.key === "Enter") sendMessage();
          }}
        />

        <button
          className="bg-purple-800 text-white px-4 py-2 rounded-lg hover:bg-purple-700"
          onClick={sendMessage}
        >
          Send
        </button>
      </div>
    </div>
  );
}