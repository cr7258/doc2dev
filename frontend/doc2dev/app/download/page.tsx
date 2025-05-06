"use client";

import React, { useState, useEffect, useRef } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Progress } from "@/components/ui/progress";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Github, FileText, FileJson, AlertCircle, CheckCircle, Search, Database, ExternalLink } from "lucide-react";
import SearchBar from "@/components/search";
import { Navbar } from "@/components/navbar";

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
  
  // 搜索功能
  const [searchQuery, setSearchQuery] = useState("");
  
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      window.location.href = `/?search=${encodeURIComponent(searchQuery)}`;
    }
  };
  
  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      <div className="container mx-auto py-10 px-4">
        {/* 顶部导航栏 */}
        <Navbar />
        
        {/* 移除了标题文字 */}
        
        <Card className="max-w-4xl mx-auto mb-8">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Github className="h-5 w-5" />
              添加新仓库
            </CardTitle>
            <CardDescription>
              输入 GitHub 仓库 URL，系统将自动下载并索引其中的文档
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                {/* 移除了 GitHub 仓库 URL 标签 */}
                <div className="flex items-center space-x-2">
                  <div className="relative w-3/4">
                    <Input
                      id="repoUrl"
                      type="text"
                      value={repoUrl}
                      onChange={(e) => setRepoUrl(e.target.value)}
                      className="px-4 bg-white border-border w-full"
                      placeholder="https://github.com/<org>/<repo>"
                      required
                    />
                    {/* 移除了 GitHub 图标 */}
                  </div>
                  <Button 
                    type="submit" 
                    disabled={loading}
                    className="bg-blue-500 hover:bg-blue-600 text-white cursor-pointer"
                  >
                    {loading ? "处理中..." : "下载并索引"}
                  </Button>
                </div>
                {/* 移除了示例提示文本 */}
                {message.type === "info" && message.queryUrl && (
                  <div className="mt-4 text-red-500/80 text-sm flex items-start gap-2">
                    <AlertCircle className="h-4 w-4 mt-0.5 flex-shrink-0" />
                    <p>
                      {message.content.split("Check")[0]}
                      查看 <Link 
                        href={message.queryUrl} 
                        className="text-red-500/80 hover:underline font-medium inline-flex items-center"
                      >
                        {message.repoPath || "该仓库"}
                        <ExternalLink className="ml-1 h-2.5 w-2.5" />
                      </Link>
                    </p>
                  </div>
                )}
              </div>
            </form>
          </CardContent>
        </Card>
        
        {/* 下载进度 */}
        {(downloadStatus || loading) && (
          <Card className="max-w-4xl mx-auto mb-4">
            <CardHeader className="pb-2">
              <CardTitle className="text-lg flex items-center gap-2">
                <FileText className="h-5 w-5 text-blue-500" />
                下载进度
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <Progress value={downloadProgress} className="h-2" />
              <p className="text-sm text-muted-foreground">
                {downloadMessage || "正在准备下载..."}
              </p>
              {downloadStatus === "error" && (
                <Badge variant="outline" className="bg-red-50 text-red-700 border-red-200">
                  <AlertCircle className="h-3.5 w-3.5 mr-1" />
                  下载出错
                </Badge>
              )}
              {downloadStatus === "completed" && (
                <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
                  <CheckCircle className="h-3.5 w-3.5 mr-1" />
                  下载完成
                </Badge>
              )}
            </CardContent>
          </Card>
        )}
        
        {/* 嵌入进度 */}
        {(embeddingStatus || (downloadStatus === "completed" && loading)) && (
          <Card className="max-w-4xl mx-auto mb-4">
            <CardHeader className="pb-2">
              <CardTitle className="text-lg flex items-center gap-2">
                <FileJson className="h-5 w-5 text-purple-500" />
                嵌入进度
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <Progress value={embeddingProgress} className="h-2" />
              <p className="text-sm text-muted-foreground">
                {embeddingMessage || "等待嵌入开始..."}
              </p>
              {embeddingStatus === "error" && (
                <Badge variant="outline" className="bg-red-50 text-red-700 border-red-200">
                  <AlertCircle className="h-3.5 w-3.5 mr-1" />
                  嵌入出错
                </Badge>
              )}
              {embeddingStatus === "completed" && (
                <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
                  <CheckCircle className="h-3.5 w-3.5 mr-1" />
                  嵌入完成
                </Badge>
              )}
            </CardContent>
          </Card>
        )}
        
        {/* 消息提示 - 只显示成功和错误提示 */}
        {message.content && message.type !== "info" && (
          <Card className={`max-w-4xl mx-auto mb-4 ${
            message.type === "success" ? "border-green-200" : "border-red-200"
          }`}>
            <CardContent className="pt-4">
              <div className={`flex items-start gap-3 ${
                message.type === "success" ? "text-green-700" : "text-red-700"
              }`}>
                {message.type === "success" && <CheckCircle className="h-5 w-5 mt-0.5" />}
                {message.type === "error" && <AlertCircle className="h-5 w-5 mt-0.5" />}
                
                <div>
                  <p>{message.content}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
        
        {/* 使用说明 */}
        <Card className="max-w-4xl mx-auto">
          <CardHeader>
            <CardTitle>使用说明</CardTitle>
          </CardHeader>
          <CardContent>
            <ol className="list-decimal pl-5 space-y-2 text-sm">
              <li>输入完整的 GitHub 仓库 URL</li>
              <li>点击“下载并索引”按钮</li>
              <li>等待系统下载并处理仓库中的 Markdown 文件</li>
              <li>处理完成后，您可以在首页查看新添加的库</li>
              <li>点击库卡片或使用查询页面来搜索文档</li>
            </ol>
          </CardContent>
        </Card>
        
        {/* 返回首页按钮 */}
        <div className="flex justify-center mt-8 mb-4">
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
