"use client";

import { useState } from "react";
import Upload from "../components/Upload";
import Chat from "../components/Chat";

import {
  Activity,
  Gauge,
  RefreshCw,
  Waves,
  AlignVerticalJustifyCenter,
  Video,
  Brain,
} from "lucide-react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

const metricIcons: any = {
  stroke_rate: <Gauge size={18} />,
  symmetry: <RefreshCw size={18} />,
  alternation: <Activity size={18} />,
  hip: <Waves size={18} />,
  head: <AlignVerticalJustifyCenter size={18} />,
  stroke_type: <Activity size={18} />,
};

const metricDescriptions: any = {
  stroke_rate: "Strokes per minute — tempo",
  symmetry: "Left vs right stroke balance",
  alternation: "Timing consistency",
  hip: "Hip position (higher = better)",
  head: "Head alignment (stable = good)",
  stroke_type: "Detected stroke style",
};

export default function Home() {
  const [context, setContext] = useState<any>(null);
  const [result, setResult] = useState<any>(null);

  return (
    <div className="min-h-screen p-6 max-w-7xl mx-auto">

      {/* Header */}
      <h1 className="text-3xl font-bold mb-6">
        Laurier AI Assistant Coach
      </h1>

      {/* Chat */}
      <div className="bg-white rounded-xl shadow p-4 mb-6">
        <Chat context={context} />
      </div>

      {/* Main Layout */}
      <div className="grid grid-cols-2 gap-6">

        {/* LEFT: Upload + Video */}
        <div className="bg-white rounded-xl shadow p-4">
          <Upload setContext={setContext} setResult={setResult} />

          {result && (
            <div className="mt-4">
            <div className="flex items-center gap-2 mb-2">
              <Video size={18} />
              <h2 className="font-semibold">Processed Video</h2>
            </div>

            <video
            className="rounded-xl w-full border shadow-sm"
            controls
          >
            <source src={result.processed_video} />
          </video>
          </div>
          )}
        </div>

        {/* RIGHT: Analysis */}
        <div className="bg-white rounded-xl shadow p-4">

          {!result && (
            <p className="text-gray-500">
              Upload a video to see analysis
            </p>
          )}

          {result && (
            <>
              <div className="flex items-center gap-2 mb-4">
                <Brain size={18} />
                <h2 className="text-xl font-semibold">AI Analysis</h2>
              </div>

              {/* Metrics */}
              <div className="grid grid-cols-2 gap-4 mb-4">
              {Object.entries(result.metrics).map(([key, value]: any) => (
                <div
                  key={key}
                  className="bg-white border rounded-xl p-4 shadow-sm hover:shadow-md transition"
                >
                  <div className="flex items-center gap-2 mb-2 text-gray-600">
                    {metricIcons[key]}
                    <p className="text-sm capitalize">{key.replace("_", " ")}</p>
                  </div>

                  <p className="text-2xl font-bold">
                    {typeof value === "number" ? value.toFixed(2) : value}
                  </p>

                  <p className="text-xs text-gray-400 mt-1">
                    {metricDescriptions[key]}
                  </p>
                </div>
              ))}
            </div>
              {/* Feedback */}
              <h3 className="font-semibold mt-4">Feedback</h3>
              {result.feedback.map((f: any, i: number) => (
                <div
                  key={i}
                  className="bg-blue-50 border border-blue-100 p-4 rounded-xl mt-3 shadow-sm"
                >
                  <p className="font-semibold text-blue-800">{f.issue}</p>
                  <p className="text-sm mt-1">{f.why}</p>
                  <p className="text-sm italic text-blue-600 mt-1">
                    {f.fix}
                  </p>
                </div>
              ))}

              {/* Drills */}
              <h3 className="font-semibold mt-4">Drills</h3>
              <ul className="mt-2 space-y-2">
                {result.drills.map((d: string, i: number) => (
                  <li
                    key={i}
                    className="bg-gray-50 p-3 rounded-lg border text-sm"
                  >
                    {d}
                  </li>
                ))}
              </ul>

              {/* Practice */}
              <h3 className="font-semibold mt-4">Practice</h3>
              <div className="bg-gray-50 p-4 rounded-xl border text-sm mt-2 space-y-1">
                {Object.entries(result.practice).map(([k, v]: any) => (
                  <p key={k}>
                    <b className="capitalize">{k}:</b>{" "}
                    {Array.isArray(v) ? v.join(", ") : v}
                  </p>
                ))}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}