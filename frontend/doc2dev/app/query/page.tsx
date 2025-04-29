"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";

interface QueryResult {
  id: string;
  source: string;
  content: string;
}

export default function QueryPage() {
  const searchParams = useSearchParams();
  const initialTable = searchParams.get("table") || "";
  const initialQuery = searchParams.get("q") || "";
  const repoName = searchParams.get("repo_name") || "";
  const repoPath = searchParams.get("repo_path") || "";
  
  const [tableName, setTableName] = useState(initialTable);
  const [query, setQuery] = useState(initialQuery);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<QueryResult[]>([]);
  const [summary, setSummary] = useState("");
  
  // 模拟仓库信息
  const repoInfo = {
    name: repoName,
    path: repoPath,
    url: `https://github.com/${repoPath}`,
    tokens: "460,748",
    snippets: "3,777",
    lastUpdated: "1 day ago"
  };
  
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
    <div className="container mx-auto py-10 px-4">
      {/* 仓库信息区域 */}
      {repoInfo.name && (
        <div className="max-w-4xl mx-auto mb-8 bg-white rounded-lg shadow-md p-6">
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
            <div>
              <h1 className="text-2xl font-bold">{repoInfo.name}</h1>
              <a 
                href={repoInfo.url} 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-blue-600 hover:underline flex items-center mt-1"
              >
                <span>{repoInfo.path}</span>
                <svg className="ml-1 h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
              </a>
            </div>
            <div className="flex items-center gap-4 text-sm text-gray-600">
              <div>
                <span className="font-medium">Tokens:</span> {repoInfo.tokens}
              </div>
              <div>
                <span className="font-medium">Snippets:</span> {repoInfo.snippets}
              </div>
              <div>
                <span className="font-medium">Update:</span> {repoInfo.lastUpdated}
              </div>
            </div>
          </div>
        </div>
      )}
      
      <div className="max-w-4xl mx-auto bg-white rounded-lg shadow-md p-6 mb-8">
        <h2 className="text-xl font-bold mb-4">文档查询</h2>
        <form onSubmit={handleSubmit}>
          {/* 隐藏向量库名称输入框 */}
          <input
            id="tableName"
            type="hidden"
            value={tableName}
          />
          
          <div className="mb-6">
            <label htmlFor="query" className="block text-sm font-medium mb-1">
              查询内容
            </label>
            <input
              id="query"
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
              placeholder="输入您的问题..."
              required
            />
          </div>
          
          <button
            type="submit"
            className="w-full bg-primary text-white py-2 px-4 rounded-md hover:bg-primary/90 transition-colors"
            disabled={loading}
          >
            {loading ? "查询中..." : "查询"}
          </button>
        </form>
      </div>
      
      {loading && (
        <div className="flex justify-center items-center py-10">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-primary"></div>
        </div>
      )}
      
      {summary && (
        <div className="max-w-4xl mx-auto bg-white rounded-lg shadow-md p-6 mb-8">
          <h2 className="text-xl font-bold mb-4">摘要</h2>
          <div className="prose max-w-none">
            <pre className="whitespace-pre-wrap text-sm bg-gray-50 p-4 rounded-md overflow-x-auto">
              {summary}
            </pre>
          </div>
        </div>
      )}
      
      <div className="text-center mt-8">
        <Link href="/" className="text-primary hover:underline">
          返回首页
        </Link>
      </div>
    </div>
  );
}
