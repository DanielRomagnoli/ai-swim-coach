"use client";

import { useState } from "react";
const API = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export default function Upload({ setContext, setResult }: any) {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  
  const handleUpload = async () => {
    if (!file) return;

    setLoading(true);
    console.log("File size (MB):", file.size / 1024 / 1024);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch(`${API}/upload`, {
        method: "POST",
        body: formData,
      });

      const data = await res.json();

      // 🔥 FORMAT DATA FOR YOUR UI
      const formatted = {
        ...data,
        feedback: [
          {
            issue: "Technique Analysis",
            why: data.feedback,
            fix: "Follow suggested drills below",
          },
        ],
        drills: Array.isArray(data.drills)
          ? data.drills
          : data.drills.split("\n"),
        practice:
          typeof data.practice === "string"
            ? { plan: data.practice }
            : data.practice,
      };

      setResult(formatted);
      setContext(data.metrics); // for chat
    } catch (err) {
      console.error(err);
    }

    setLoading(false);
  };

  return (
    <div>
      <input
        type="file"
        accept="video/*"
        onChange={(e) => setFile(e.target.files?.[0] || null)}
      />

      <button
        onClick={handleUpload}
        className="bg-purple-600 text-white px-4 py-2 rounded mt-2"
      >
        Upload
      </button>

      {loading && <p className="mt-2">Processing...</p>}
    </div>
  );
}