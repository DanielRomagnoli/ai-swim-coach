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
            const videoUrl = res[0].url;

            const response = await fetch(`${API}/upload-url`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ url: videoUrl }),
          });

          const data = await response.json();

          // 🔥 show video immediately
          setResult({
            processed_video: `${API}${data.video_url}`,
          });

          // 🔥 poll AI
          const video_id = data.video_id;

          const interval = setInterval(async () => {
            const res = await fetch(`${API}/status/${video_id}`);
            const status = await res.json();

            if (status.status === "done") {
              clearInterval(interval);

              setResult((prev: any) => ({
                ...prev,
                metrics: status.metrics,
                feedback: status.feedback,
                drills: status.drills,
                practice: status.practice,
              }));

              setContext(status.metrics);
            }

            if (status.status === "error") {
              clearInterval(interval);
              alert("AI processing failed");
            }

          }, 2000);
          } catch (err) {
            console.error(err);
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