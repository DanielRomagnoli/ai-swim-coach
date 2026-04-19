"use client";

import { UploadDropzone } from "@uploadthing/react";
import type { OurFileRouter } from "@/app/api/uploadthing/route";

const API = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export default function Upload({ setResult, setContext }: any) {
  return (
    <div className="flex flex-col gap-4">

      <UploadDropzone<OurFileRouter, "videoUploader">
        endpoint="videoUploader"

        appearance={{
          container: "border-2 border-dashed border-purple-300 rounded-xl p-6 bg-purple-50 hover:bg-purple-100 transition",
          label: "text-purple-700 font-medium",
          allowedContent: "text-xs text-gray-500",
          button: "bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition"
        }}

        onClientUploadComplete={async (res: any[]) => {
          try {
            console.log("Upload complete:", res);

            const videoUrl = res[0].url;

            // 🔥 Send video URL to backend for processing
            const response = await fetch(`${API}/upload-url`, {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
              },
              body: JSON.stringify({ url: videoUrl }),
            });

            // 🔥 Backend now returns VIDEO (blob), not JSON
            const blob = await response.blob();

            const processedVideoUrl = URL.createObjectURL(blob);

            // 👇 If you ALSO return metrics separately later, update here
            setResult({
              processed_video: processedVideoUrl,
              metrics: null,
              feedback: [],
              drills: [],
              practice: {}
            });

            // Optional: keep context empty for now
            setContext(null);

          } catch (err) {
            console.error("Processing error:", err);
            alert("Error processing video");
          }
        }}

        onUploadError={(error: Error) => {
          console.error(error);
          alert(`Upload failed: ${error.message}`);
        }}
      />

    </div>
  );
}