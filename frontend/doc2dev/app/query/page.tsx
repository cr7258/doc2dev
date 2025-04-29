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
  
  const [tableName, setTableName] = useState(initialTable);
  const [query, setQuery] = useState(initialQuery);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<QueryResult[]>([]);
  const [summary, setSummary] = useState("");
  
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
      <h1 className="text-3xl font-bold mb-6 text-center">文档查询</h1>
      
      <div className="max-w-2xl mx-auto bg-white rounded-lg shadow-md p-6 mb-8">
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label htmlFor="tableName" className="block text-sm font-medium mb-1">
              库名称
            </label>
            <input
              id="tableName"
              type="text"
              value={tableName}
              onChange={(e) => setTableName(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
              placeholder="例如: react_vectors"
              required
            />
          </div>
          
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
