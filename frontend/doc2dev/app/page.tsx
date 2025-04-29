"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Book, Code, Database, FileCode, Library, Package } from "lucide-react";

interface LibraryCardProps {
  name: string;
  description: string;
  icon: React.ReactNode;
  count: number;
}

const LibraryCard: React.FC<LibraryCardProps> = ({
  name,
  description,
  icon,
  count,
}) => {
  return (
    <Card className="overflow-hidden transition-all hover:shadow-md">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {icon}
            <CardTitle className="text-xl">{name}</CardTitle>
          </div>
          <Badge variant="secondary">{count}</Badge>
        </div>
        <CardDescription>{description}</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="h-2 w-full bg-muted overflow-hidden rounded-full">
          <div
            className="h-full bg-primary"
            style={{ width: `${Math.min(count / 10, 100)}%` }}
          ></div>
        </div>
      </CardContent>
    </Card>
  );
};

interface HomePageProps {
  libraries: {
    name: string;
    description: string;
    icon: keyof typeof libraryIcons;
    count: number;
  }[];
}

const libraryIcons = {
  npm: <Package className="h-5 w-5 text-primary" />,
  react: <Code className="h-5 w-5 text-blue-500" />,
  vue: <FileCode className="h-5 w-5 text-green-500" />,
  angular: <Book className="h-5 w-5 text-red-500" />,
  database: <Database className="h-5 w-5 text-yellow-500" />,
  library: <Library className="h-5 w-5 text-purple-500" />,
};

const HomePage: React.FC<HomePageProps> = ({ libraries }) => {
  const [searchQuery, setSearchQuery] = useState("");
  const router = useRouter();
  
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      // 跳转到查询页面，并传递搜索查询参数
      router.push(`/query?q=${encodeURIComponent(searchQuery)}`);
    }
  };
  
  return (
    <div className="container mx-auto py-10">
      <div className="mb-10 text-center">
        <h1 className="text-4xl font-bold tracking-tight mb-4">
          Doc2Dev - 文档检索系统
        </h1>
        <p className="text-muted-foreground max-w-2xl mx-auto">
          欢迎使用 Doc2Dev 文档检索系统。我们索引了各种库的文档，帮助您快速找到所需的信息。
        </p>
        
        <div className="mt-6 flex justify-center">
          <form onSubmit={handleSearch} className="relative w-full max-w-lg">
            <input
              type="text"
              placeholder="搜索库..."
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            <button 
              type="submit"
              className="absolute right-2 top-1/2 transform -translate-y-1/2 px-3 py-1 bg-primary text-white rounded-md"
            >
              搜索
            </button>
          </form>
        </div>
        
        <div className="mt-6">
          <a href="/download" className="inline-flex items-center justify-center px-4 py-2 bg-green-500 text-white rounded-md hover:bg-green-600 transition-colors">
            添加 GitHub 仓库
          </a>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {libraries.map((library) => (
          <LibraryCard
            key={library.name}
            name={library.name}
            description={library.description}
            icon={libraryIcons[library.icon]}
            count={library.count}
          />
        ))}
      </div>
    </div>
  );
};

// 示例数据 - 这里会被替换为从后端 API 获取的真实数据
const libraries: {
  name: string;
  description: string;
  icon: keyof typeof libraryIcons;
  count: number;
}[] = [
  {
    name: "React",
    description: "用于构建用户界面的 JavaScript 库",
    icon: "react",
    count: 1245,
  },
  {
    name: "Vue.js",
    description: "渐进式 JavaScript 框架",
    icon: "vue",
    count: 856,
  },
  {
    name: "Angular",
    description: "由 Google 维护的 TypeScript 框架",
    icon: "angular",
    count: 643,
  },
  {
    name: "Express",
    description: "Node.js Web 应用程序框架",
    icon: "npm",
    count: 954,
  },
  {
    name: "MongoDB",
    description: "文档数据库，提供高可扩展性和灵活性",
    icon: "database",
    count: 512,
  },
  {
    name: "Lodash",
    description: "JavaScript 实用工具库",
    icon: "library",
    count: 387,
  },
];

export default function Home() {
  return <HomePage libraries={libraries} />;
}
