import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "不標準答案｜Creator OS",
  description: "內容營運工作站 MVP",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="zh-Hant">
      <body>{children}</body>
    </html>
  );
}
