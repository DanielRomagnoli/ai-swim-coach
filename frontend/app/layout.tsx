import "./globals.css";

export const metadata = {
  title: "AI Swim Coach",
  description: "Swim analysis + AI coaching",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-purple-900 text-gray-900">
        {children}
      </body>
    </html>
  );
}