import { createUploadthing, type FileRouter } from "uploadthing/next";
import { createRouteHandler } from "uploadthing/next";

const f = createUploadthing();

export const ourFileRouter = {
  videoUploader: f({ video: { maxFileSize: "64MB" } })
    .onUploadComplete(async ({ file }) => {
      console.log("Uploaded file:", file.url);
    }),
} satisfies FileRouter;

// ✅ THIS LINE IS CRITICAL
export type OurFileRouter = typeof ourFileRouter;

// ✅ Required for Next.js
export const { GET, POST } = createRouteHandler({
  router: ourFileRouter,
});