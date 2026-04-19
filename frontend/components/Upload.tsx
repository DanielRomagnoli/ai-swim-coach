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

          const data = await response.json();

          // 🔥 convert base64 → blob
          const byteCharacters = atob(data.video);
          const byteNumbers = new Array(byteCharacters.length);

          for (let i = 0; i < byteCharacters.length; i++) {
            byteNumbers[i] = byteCharacters.charCodeAt(i);
          }

          const byteArray = new Uint8Array(byteNumbers);
          const blob = new Blob([byteArray], { type: "video/mp4" });

          const videoUrlBlob = URL.createObjectURL(blob);

          // 🔥 set full result
          setResult({
            processed_video: videoUrlBlob,
            metrics: data.metrics,
            feedback: data.feedback,
            drills: data.drills,
            practice: data.practice,
          });

          setContext(data.metrics);

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