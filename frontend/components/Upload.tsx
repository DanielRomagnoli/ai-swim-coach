"use client";

import { UploadDropzone } from "@uploadthing/react";
import type { OurFileRouter } from "@/app/api/uploadthing/route";

const API = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export default function Upload({ setResult, setContext }: any) {
  return (
    <UploadDropzone<OurFileRouter, "videoUploader">
      endpoint="videoUploader"

      onClientUploadComplete={async (res: any[]) => {
        const videoUrl = res[0].url;

        const response = await fetch(`${API}/upload-url`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ url: videoUrl }),
        });

        const data = await response.json();

        setResult(data);
        setContext(data.metrics);
      }}

      onUploadError={(error: Error) => {
        alert(`Upload failed: ${error.message}`);
      }}
    />
  );
}