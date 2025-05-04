"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Github, Clock, Code, RefreshCw, ExternalLink, FileText, FileJson, FileCode, Database, Search, Copy } from "lucide-react";
import SearchWithSuggestions from "@/components/search-with-suggestions";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";

interface QueryResult {
  id: string;
  source: string;
  content: string;
}

interface DocumentItem {
  projectName: string;
  githubLink: string;
  description: string;
  tokens: string;
  snippets: string;
  updatedAt: string;
}

interface RepositoryData {
  id: number;
  name: string;
  description: string;
  repo: string;
  repo_url: string;
  tokens: number;
  snippets: number;
  created_at: string;
  updated_at: string;
  last_updated: string;
}

export default function QueryPage() {
  const searchParams = useSearchParams();
  const initialTable = searchParams.get("table") || "";
  const initialQuery = searchParams.get("q") || "";
  const repoName = searchParams.get("repo_name") || "";
  const repoPath = searchParams.get("repo_path") || "";
  
  const [tableName, setTableName] = useState(initialTable);
  const [query, setQuery] = useState(initialQuery);
  // 查询状态已在上面声明
  
  // 仓库数据状态
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<any[]>([]);
  const [summary, setSummary] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [repoData, setRepoData] = useState<RepositoryData | null>(null);
  
  // 根据实际数据构建 DocumentItem
  const documentItem: DocumentItem = {
    projectName: repoName,
    githubLink: `https://github.com/${repoPath}`,
    description: repoData?.description || "一个用于文档查询和代码参考的GitHub仓库",
    tokens: repoData ? repoData.tokens.toLocaleString() : "0",
    snippets: repoData ? repoData.snippets.toLocaleString() : "0",
    updatedAt: repoData?.last_updated || ""
  };
  
  // 获取仓库数据
  useEffect(() => {
    if (repoPath) {
      const fetchRepoData = async () => {
        try {
          const response = await fetch(`http://localhost:8000/repositories/${repoPath.replace('/', '_')}`);
          if (response.ok) {
            const data = await response.json();
            if (data.status === "success" && data.repository) {
              setRepoData(data.repository);
            }
          }
        } catch (error) {
          console.error("Error fetching repository data:", error);
        }
      };
      
      fetchRepoData();
    }
  }, [repoPath]);
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!tableName || !query) return;
    
    setLoading(true);
    setResults([]);
    setSummary("");
    
    try {
      const response = await fetch("/api/query", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          table_name: tableName,
          query: query,
          k: 5,
          summarize: true,
        }),
      });
      
      const data = await response.json();
      
      if (data.status === "success") {
        setResults(data.results || []);
        setSummary(data.summary || "");
      } else {
        console.error("Error:", data.message);
      }
    } catch (error) {
      console.error("Error querying:", error);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      <div className="container mx-auto px-4 pt-6 pb-10">
        {/* 顶部导航栏 */}
        <div className="flex flex-wrap items-center justify-between gap-4 max-w-4xl mx-auto mb-8">
          <div className="flex items-center gap-4">
            <Link href="/" className="flex items-center gap-2">
              <Database className="h-6 w-6 text-blue-600" />
              <span className="text-xl font-bold">Doc2Dev</span>
            </Link>
            
            <SearchWithSuggestions />
          </div>
        </div>
      {/* 仓库信息区域 */}
      {documentItem.projectName && (
        <Card className="w-full max-w-4xl mx-auto mb-8 overflow-hidden shadow-sm border border-gray-100">
          <CardHeader className="pb-2">
            <div className="flex flex-col">
              <CardTitle className="text-xl font-bold">{documentItem.projectName}</CardTitle>
              <CardDescription className="mt-1 mb-2 line-clamp-2">
                {documentItem.description}
              </CardDescription>
              <a 
                href={documentItem.githubLink} 
                target="_blank" 
                rel="noopener noreferrer"
                className="flex items-center gap-1 text-sm text-blue-500 hover:text-blue-700 transition-colors"
              >
                <Github className="h-4 w-4" />
                <span>{repoPath}</span>
                <ExternalLink className="h-3 w-3" />
              </a>
            </div>
          </CardHeader>
          <CardContent className="pb-3">
            <div className="flex flex-wrap gap-3">
              <Badge variant="outline" className="flex items-center gap-1.5 bg-blue-50 px-3 py-1 text-blue-700 border-blue-100">
                <FileText className="h-3.5 w-3.5" />
                <span>{documentItem.tokens} tokens</span>
              </Badge>
              <Badge variant="outline" className="flex items-center gap-1.5 bg-purple-50 px-3 py-1 text-purple-700 border-purple-100">
                <FileJson className="h-3.5 w-3.5" />
                <span>{documentItem.snippets} snippets</span>
              </Badge>
              <Badge variant="outline" className="flex items-center gap-1.5 bg-green-50 px-3 py-1 text-green-700 border-green-100">
                <Clock className="h-3.5 w-3.5" />
                <span>Updated {documentItem.updatedAt}</span>
              </Badge>
            </div>
          </CardContent>
        </Card>
      )}
      
      <Card className="w-full max-w-4xl mx-auto mb-8 overflow-hidden shadow-sm border border-gray-100">
        <CardHeader className="pb-2">
          <CardTitle className="text-lg flex items-center gap-2">
            <FileCode className="h-5 w-5 text-blue-500" />
            文档查询
          </CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit}>
            {/* 隐藏向量库名称输入框 */}
            <input
              id="tableName"
              type="hidden"
              value={tableName}
            />
            
            <div className="mb-6">
              <label htmlFor="query" className="block text-sm font-medium mb-2">
                查询内容
              </label>
              <div className="flex items-center space-x-2">
                <div className="relative flex-1">
                  <input
                    id="query"
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
                    placeholder="输入您的问题..."
                    required
                  />
                  {query && (
                    <button 
                      type="button" 
                      className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                      onClick={() => setQuery('')}
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                      </svg>
                    </button>
                  )}
                </div>
                <Button
                  type="submit"
                  className="bg-blue-500 hover:bg-blue-600 text-white cursor-pointer"
                  disabled={loading}
                >
                  {loading ? (
                    <>
                      <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      查询中...
                    </>
                  ) : "查询"}
                </Button>
              </div>
            </div>
          </form>
        </CardContent>
      </Card>
      
      {loading && (
        <div className="flex justify-center items-center py-10">
          <div className="flex flex-col items-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            <p className="mt-4 text-gray-600">正在查询文档，请稍候...</p>
          </div>
        </div>
      )}
      
      {/* 已移除查询结果部分，只保留摘要 */}
      
      {/* 摘要部分 */}
      {summary && (
        <Card className="w-full max-w-4xl mx-auto mb-8 overflow-hidden shadow-sm border border-gray-100">
          <CardHeader className="pb-2">
            <div className="flex justify-between items-center">
              <CardTitle className="text-lg flex items-center gap-2">
                <FileText className="h-5 w-5 text-blue-500" />
                查询结果
              </CardTitle>
              <Button 
                variant="ghost" 
                size="sm" 
                className="h-8 w-8 p-0 text-gray-500 hover:text-blue-600 hover:bg-blue-50 cursor-pointer"
                onClick={() => {
                  navigator.clipboard.writeText(summary);
                  // 使用状态变量来显示复制成功提示
                  const button = document.getElementById('copy-button');
                  if (button) {
                    const originalContent = button.innerHTML;
                    button.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="h-4 w-4"><polyline points="20 6 9 17 4 12"></polyline></svg>';
                    button.classList.add('text-green-500');
                    
                    setTimeout(() => {
                      button.innerHTML = originalContent;
                      button.classList.remove('text-green-500');
                    }, 2000);
                  }
                }}
                title="复制到剪贴板"
                id="copy-button"
              >
                <Copy className="h-4 w-4" />
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="prose max-w-none">
              <div className="whitespace-pre-wrap text-sm bg-white p-5 rounded-lg overflow-x-auto border border-gray-100 text-gray-800">
                {summary}
              </div>
            </div>
          </CardContent>
        </Card>
      )}
      
      <div className="text-center mt-8">
        <Button variant="outline" asChild>
          <Link href="/" className="inline-flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M9.707 16.707a1 1 0 01-1.414 0l-6-6a1 1 0 010-1.414l6-6a1 1 0 011.414 1.414L5.414 9H17a1 1 0 110 2H5.414l4.293 4.293a1 1 0 010 1.414z" clipRule="evenodd" />
            </svg>
            返回首页
          </Link>
        </Button>
      </div>
      </div>
    </div>
  );
}
