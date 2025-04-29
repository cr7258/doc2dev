"use client";

import React, { useState } from "react";
import Link from "next/link";

export default function DownloadPage() {
  const [repoUrl, setRepoUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ type: "", content: "" });
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!repoUrl) return;
    
    setLoading(true);
    setMessage({ type: "", content: "" });
    
    try {
      const response = await fetch("/api/download", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          repo_url: repoUrl,
        }),
      });
      
      const data = await response.json();
      
      if (data.status === "success") {
        setMessage({
          type: "success",
          content: `成功下载并索引了仓库！`,
        });
        setRepoUrl("");
      } else {
        setMessage({
          type: "error",
          content: data.message || "下载失败，请稍后重试。",
        });
      }
    } catch (error) {
      console.error("Error downloading:", error);
      setMessage({
        type: "error",
        content: "发生错误，请稍后重试。",
      });
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="container mx-auto py-10 px-4">
      <h1 className="text-3xl font-bold mb-6 text-center">添加 GitHub 仓库</h1>
      
      <div className="max-w-2xl mx-auto bg-white rounded-lg shadow-md p-6 mb-8">
        <form onSubmit={handleSubmit}>

          <div className="mb-6">
            <label htmlFor="repoUrl" className="block text-sm font-medium mb-1">
              GitHub 仓库 URL
            </label>
            <input
              id="repoUrl"
              type="text"
              value={repoUrl}
              onChange={(e) => setRepoUrl(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
              placeholder="https://github.com/facebook/react"
              required
            />
            <p className="text-sm text-gray-500 mt-1">
              请输入完整的 GitHub 仓库 URL
            </p>
          </div>
          
          <button
            type="submit"
            className="w-full bg-primary text-white py-2 px-4 rounded-md hover:bg-primary/90 transition-colors"
            disabled={loading}
          >
            {loading ? "处理中..." : "下载并索引"}
          </button>
        </form>
      </div>
      
      {message.content && (
        <div className={`max-w-2xl mx-auto p-4 rounded-md mb-8 ${
          message.type === "success" ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"
        }`}>
          <p>{message.content}</p>
        </div>
      )}
      
      <div className="max-w-2xl mx-auto bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-bold mb-4">使用说明</h2>
        
        <div className="prose max-w-none">
          <ol className="list-decimal pl-5 space-y-2">
            <li>输入完整的 GitHub 仓库 URL</li>
            <li>点击“下载并索引”按钮</li>
            <li>系统将自动从 URL 中提取组织和仓库名称，并以 “组织_仓库” 的格式生成向量表名称</li>
            <li>等待系统下载并处理仓库中的 Markdown 文件</li>
            <li>处理完成后，您可以在首页查看新添加的库</li>
            <li>点击库卡片或使用查询页面来搜索文档</li>
          </ol>
        </div>
      </div>
      
      <div className="text-center mt-8">
        <Link href="/" className="text-primary hover:underline">
          返回首页
        </Link>
      </div>
    </div>
  );
}
