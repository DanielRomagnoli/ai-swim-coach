"use client";

import { useState } from "react";
const API = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export default function Upload({ setContext, setResult }: any) {
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState("");

  const handleUpload = async () => {
    if (!file) {
      setStatus("Please select a file");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    setStatus("Uploading...");

    try {
      const res = await fetch('${API}/chat', {
        method: "POST",
        body: formData,
      });

      const data = await res.json();

      setResult(data);
      setContext(data.metrics);

      setStatus("Upload complete");
    } catch (err) {
      console.error(err);
      setStatus("Upload failed");
    }
  };

  return (
    <div>
      <h2 className="text-lg font-semibold mb-2">
        Upload Swim Video
      </h2>

      <input
        type="file"
        accept="video/*"
        onChange={(e) =>
          setFile(e.target.files?.[0] || null)
        }
      />

      <button
        className="bg-purple-800 text-white px-4 py-2 rounded-lg hover:bg-purple-700"
        onClick={handleUpload}
      >
        Upload
      </button>

      <p className="text-sm mt-2 text-gray-500">
        {status}
      </p>
    </div>
  );
}