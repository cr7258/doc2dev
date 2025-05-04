import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Doc2Dev - 文档查询",
  description: "查询索引的 GitHub 仓库文档，获取准确的代码示例和技术信息。",
};

export default function QueryLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
