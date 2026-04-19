"use client";

import { UploadDropzone } from "@uploadthing/react";
import type { OurFileRouter } from "@/app/api/uploadthing/route";

const API = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export default function Upload({ setResult, setContext }: any) {

  const pollStatus = async (video_id: string) => {
    let attempts = 0;

    while (attempts < 40) {
      attempts++;

      try {
        const res = await fetch(`${API}/status/${video_id}`);
        const data = await res.json();

        console.log("Polling:", data);

        if (data.status === "done") {
          setResult({
            processed_video: `${API}${data.video_url}`,
            metrics: data.metrics,
            feedback: data.feedback,
            drills: data.drills,
            practice: data.practice,
          });

          setContext(data.metrics);
          return;
        }

        if (data.status === "error") {
          alert("Processing failed");
          console.error(data.error);
          return;
        }

        await new Promise((r) => setTimeout(r, 2000));

      } catch (err) {
        console.error(err);
        return;
      }
    }

    alert("Timed out");
  };

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

            // 🔥 STEP 1: start processing
            const response = await fetch(`${API}/upload-url`, {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
              },
              body: JSON.stringify({ url: videoUrl }),
            });

            const data = await response.json();
            const video_id = data.video_id;

            if (!video_id) throw new Error("No video_id returned");

            // 🔥 show video instantly
            setResult({
              processed_video: `${API}${data.video_url}`,
              metrics: data.metrics,
              feedback: null,
              drills: null,
              practice: null,
            });

            setContext(data.metrics);

            // 🔥 STEP 2: poll AI
            pollStatus(video_id);

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