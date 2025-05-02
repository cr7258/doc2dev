"use client";

import React, { useState, useEffect, useRef } from "react";
import Link from "next/link";
import { Progress } from "@/components/ui/progress";

export default function DownloadPage() {
  const [repoUrl, setRepoUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ type: "", content: "", queryUrl: "", repoPath: "" });
  
  // WebSocket 和进度状态
  const [connected, setConnected] = useState(false);
  const [clientId, setClientId] = useState("");
  const [downloadProgress, setDownloadProgress] = useState(0);
  const [downloadStatus, setDownloadStatus] = useState("");
  const [downloadMessage, setDownloadMessage] = useState("");
  const [embeddingProgress, setEmbeddingProgress] = useState(0);
  const [embeddingStatus, setEmbeddingStatus] = useState("");
  const [embeddingMessage, setEmbeddingMessage] = useState("");
  
  const wsRef = useRef<WebSocket | null>(null);
  
  // 生成随机客户端 ID
  useEffect(() => {
    const id = `client_${Math.random().toString(36).substring(2, 9)}_${Date.now()}`;
    setClientId(id);
  }, []);
  
  // 连接 WebSocket
  useEffect(() => {
    if (!clientId) return;
    
    // 获取当前域名和协议
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.hostname;
    const port = process.env.NEXT_PUBLIC_BACKEND_PORT || '8000';
    const wsUrl = `${protocol}//${host}:${port}/ws/${clientId}`;
    
    const ws = new WebSocket(wsUrl);
    
    ws.onopen = () => {
      console.log('WebSocket connected');
      setConnected(true);
    };
    
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log('WebSocket message:', data);
        
        if (data.type === 'download') {
          setDownloadStatus(data.status);
          setDownloadProgress(data.progress);
          setDownloadMessage(data.message);
        } else if (data.type === 'embedding') {
          setEmbeddingStatus(data.status);
          setEmbeddingProgress(data.progress);
          setEmbeddingMessage(data.message);
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };
    
    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setConnected(false);
    };
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
    
    wsRef.current = ws;
    
    return () => {
      ws.close();
    };
  }, [clientId]);
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!repoUrl) return;
    
    // 重置所有状态
    setLoading(true);
    setMessage({ type: "", content: "", queryUrl: "", repoPath: "" });
    setDownloadProgress(0);
    setDownloadStatus("");
    setDownloadMessage("");
    setEmbeddingProgress(0);
    setEmbeddingStatus("");
    setEmbeddingMessage("");
    
    try {
      const response = await fetch("/api/download", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          repo_url: repoUrl,
          client_id: clientId, // 传递客户端 ID 用于 WebSocket 连接
        }),
      });
      
      const data = await response.json();
      
      if (data.status === "success") {
        setMessage({
          type: "success",
          content: `成功下载并索引了仓库！`,
          queryUrl: "",
          repoPath: ""
        });
        setRepoUrl("");
      } else if (data.status === "exists" && data.query_url) {
        // 仓库已存在，有查询链接
        setMessage({
          type: "info",
          content: data.message || "此仓库已存在",
          queryUrl: data.query_url,
          repoPath: data.repo_path || "该仓库"
        });
      } else {
        setMessage({
          type: "error",
          content: data.message || "下载失败，请稍后重试。",
          queryUrl: "",
          repoPath: ""
        });
      }
    } catch (error) {
      console.error("Error downloading:", error);
      setMessage({
        type: "error",
        content: "发生错误，请稍后重试。",
        queryUrl: "",
        repoPath: ""
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
      
      {/* 下载进度 */}
      {(downloadStatus || loading) && (
        <div className="max-w-2xl mx-auto bg-white rounded-lg shadow-md p-6 mb-4">
          <h3 className="text-lg font-semibold mb-2">下载进度</h3>
          <Progress value={downloadProgress} className="mb-2" />
          <p className="text-sm text-gray-600">
            {downloadMessage || "正在准备下载..."}
          </p>
          {downloadStatus === "error" && (
            <p className="text-sm text-red-600 mt-2">下载出错</p>
          )}
          {downloadStatus === "completed" && (
            <p className="text-sm text-green-600 mt-2">下载完成</p>
          )}
        </div>
      )}
      
      {/* 嵌入进度 */}
      {(embeddingStatus || (downloadStatus === "completed" && loading)) && (
        <div className="max-w-2xl mx-auto bg-white rounded-lg shadow-md p-6 mb-4">
          <h3 className="text-lg font-semibold mb-2">嵌入进度</h3>
          <Progress value={embeddingProgress} className="mb-2" />
          <p className="text-sm text-gray-600">
            {embeddingMessage || "等待嵌入开始..."}
          </p>
          {embeddingStatus === "error" && (
            <p className="text-sm text-red-600 mt-2">嵌入出错</p>
          )}
          {embeddingStatus === "completed" && (
            <p className="text-sm text-green-600 mt-2">嵌入完成</p>
          )}
        </div>
      )}
      
      {message.content && (
        <div className={`max-w-2xl mx-auto p-4 rounded-md mb-8 ${
          message.type === "success" ? "bg-green-100 text-green-800" : 
          message.type === "info" ? "bg-blue-100 text-blue-800" : 
          "bg-red-100 text-red-800"
        }`}>
          {message.queryUrl ? (
            <p>
              {message.content.split("Check")[0]}
              Check <a 
                href={message.queryUrl} 
                className="text-blue-600 hover:underline"
                target="_blank" 
                rel="noopener noreferrer"
              >
                {message.repoPath || "该仓库"}
              </a> to see it.
            </p>
          ) : (
            <p>{message.content}</p>
          )}
        </div>
      )}
      
      <div className="max-w-2xl mx-auto bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-bold mb-4">使用说明</h2>
        
        <div className="prose max-w-none">
          <ol className="list-decimal pl-5 space-y-2">
            <li>输入完整的 GitHub 仓库 URL</li>
            <li>点击“下载并索引”按钮</li>
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
