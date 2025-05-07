import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Doc2Dev - 添加 GitHub 仓库",
  description: "添加并索引 GitHub 仓库，使其可以被 AI 编程助手查询和使用。",
};

export default function DownloadLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
