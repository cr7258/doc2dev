"use client";

import React, { useState, useEffect, useRef } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Progress } from "@/components/ui/progress";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Github, Gitlab, FileText, FileJson, AlertCircle, CheckCircle, Search, Database, ExternalLink } from "lucide-react";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import SearchBar from "@/components/search";
import { Navbar } from "@/components/navbar";
import Footer from "@/components/footer";
import { useAuth } from "@/lib/auth";

export default function DownloadPage() {
  const { token, user } = useAuth();
  const [repoUrl, setRepoUrl] = useState("");
  const [selectedPlatform, setSelectedPlatform] = useState("github"); // Default to GitHub
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ type: "", content: "", queryUrl: "", repoPath: "" });

  // WebSocket and progress state
  const [connected, setConnected] = useState(false);
  const [clientId, setClientId] = useState("");
  const [downloadProgress, setDownloadProgress] = useState(0);
  const [downloadStatus, setDownloadStatus] = useState("");
  const [downloadMessage, setDownloadMessage] = useState("");
  const [embeddingProgress, setEmbeddingProgress] = useState(0);
  const [embeddingStatus, setEmbeddingStatus] = useState("");
  const [embeddingMessage, setEmbeddingMessage] = useState("");
  
  const wsRef = useRef<WebSocket | null>(null);
  
  // Generate random client ID
  useEffect(() => {
    const id = `client_${Math.random().toString(36).substring(2, 9)}_${Date.now()}`;
    setClientId(id);
  }, []);

  // Connect WebSocket
  useEffect(() => {
    if (!clientId) return;

    // Get current domain and protocol
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

    // Reset all states
    setLoading(true);
    setMessage({ type: "", content: "", queryUrl: "", repoPath: "" });
    setDownloadProgress(0);
    setDownloadStatus("");
    setDownloadMessage("");
    setEmbeddingProgress(0);
    setEmbeddingStatus("");
    setEmbeddingMessage("");

    try {
      const headers: Record<string, string> = {
        "Content-Type": "application/json",
      };

      if (token) {
        headers["Authorization"] = `Bearer ${token}`;
      }

      const response = await fetch("/api/download", {
        method: "POST",
        headers,
        body: JSON.stringify({
          repo_url: repoUrl,
          client_id: clientId, // Pass client ID for WebSocket connection
          platform: selectedPlatform, // Pass user selected platform
        }),
      });
      
      const data = await response.json();
      
      if (data.status === "success") {
        setMessage({
          type: "success",
          content: `Repository successfully downloaded and indexed!`,
          queryUrl: "",
          repoPath: ""
        });
        setRepoUrl("");
      } else if (data.status === "exists" && data.query_url) {
        // Repository already exists, has query link
        setMessage({
          type: "info",
          content: data.message || "This repository already exists",
          queryUrl: data.query_url,
          repoPath: data.repo_path || "this repository"
        });
      } else if (data.status === "accepted") {
        // Repository processing started in background, show blue notification
        setMessage({
          type: "processing",
          content: data.message || "Repository processing has started in the background. You can continue using the application.",
          queryUrl: "",
          repoPath: ""
        });
      } else {
        setMessage({
          type: "error",
          content: data.message || "Download failed, please try again later.",
          queryUrl: "",
          repoPath: ""
        });
      }
    } catch (error) {
      console.error("Error downloading:", error);
      setMessage({
        type: "error",
        content: "An error occurred, please try again later.",
        queryUrl: "",
        repoPath: ""
      });
    } finally {
      setLoading(false);
    }
  };
  
  // Search functionality
  const [searchQuery, setSearchQuery] = useState("");

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      window.location.href = `/?search=${encodeURIComponent(searchQuery)}`;
    }
  };
  
  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white flex flex-col">
      <div className="container mx-auto py-10 px-4 flex-1">
        {/* Top navigation bar */}
        <Navbar />

        {/* Removed title text */}

        <Card className="max-w-4xl mx-auto mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              {selectedPlatform === "gitlab" ? (
                <Gitlab className="h-5 w-5 text-orange-500" />
              ) : (
                <Github className="h-5 w-5" />
              )}
              Add New Repository
            </CardTitle>
            <CardDescription>
              Enter {selectedPlatform === "gitlab" ? "GitLab" : "GitHub"} repository URL, the system will automatically download and index the documentation
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-4">
                {/* Platform selection dropdown */}
                <div className="space-y-2">
                  <label htmlFor="platform" className="text-sm font-medium text-gray-700">
                    Select Git Platform
                  </label>
                  <Select value={selectedPlatform} onValueChange={setSelectedPlatform}>
                    <SelectTrigger className="w-full">
                      <SelectValue placeholder="Select Platform" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="github">
                        <div className="flex items-center gap-2">
                          <Github className="h-4 w-4" />
                          <span>GitHub</span>
                        </div>
                      </SelectItem>
                      <SelectItem value="gitlab">
                        <div className="flex items-center gap-2">
                          <Gitlab className="h-4 w-4 text-orange-500" />
                          <span>GitLab</span>
                        </div>
                      </SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {/* Repository URL input */}
                <div className="space-y-2">
                  <label htmlFor="repoUrl" className="text-sm font-medium text-gray-700">
                    Repository URL
                  </label>
                  <div className="flex items-center space-x-2">
                    <div className="relative flex-1">
                      <Input
                        id="repoUrl"
                        type="text"
                        value={repoUrl}
                        onChange={(e) => setRepoUrl(e.target.value)}
                        className="px-4 bg-white border-border w-full"
                        placeholder={
                          selectedPlatform === "gitlab"
                            ? "https://gitlab.com/<org>/<repo>"
                            : "https://github.com/<org>/<repo>"
                        }
                        required
                      />
                    </div>
                    <Button
                      type="submit"
                      disabled={loading}
                      className="bg-blue-500 hover:bg-blue-600 text-white cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {loading ? "Processing..." : "Download & Index"}
                    </Button>
                  </div>
                </div>

                {/* Message notifications */}
                {message.type === "info" && message.queryUrl && (
                  <div className="mt-4 text-red-500/80 text-sm flex items-start gap-2">
                    <AlertCircle className="h-4 w-4 mt-0.5 flex-shrink-0" />
                    <p>
                      {message.content.split("Check")[0]}
                      Check <Link
                        href={message.queryUrl}
                        className="text-red-500/80 hover:underline font-medium inline-flex items-center"
                      >
                        {message.repoPath || "this repository"}
                        <ExternalLink className="ml-1 h-2.5 w-2.5" />
                      </Link>
                    </p>
                  </div>
                )}
                {message.type === "processing" && (
                  <div className="mt-4 text-blue-500 text-sm flex items-start gap-2">
                    <CheckCircle className="h-4 w-4 mt-0.5 flex-shrink-0" />
                    <p>{message.content}</p>
                  </div>
                )}
              </div>
            </form>
          </CardContent>
        </Card>
        
        {/* Download progress */}
        {(downloadStatus || loading) && (
          <Card className="max-w-4xl mx-auto mb-6">
            <CardHeader className="pb-2">
              <CardTitle className="text-lg flex items-center gap-2">
                <FileText className="h-5 w-5 text-blue-500" />
                Download Progress
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <Progress value={downloadProgress} className="h-2" />
              <p className="text-sm text-muted-foreground">
                {downloadMessage || "Preparing download..."}
              </p>
              {downloadStatus === "error" && (
                <Badge variant="outline" className="bg-red-50 text-red-700 border-red-200">
                  <AlertCircle className="h-3.5 w-3.5 mr-1" />
                  Download Error
                </Badge>
              )}
              {downloadStatus === "completed" && (
                <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
                  <CheckCircle className="h-3.5 w-3.5 mr-1" />
                  Download Complete
                </Badge>
              )}
            </CardContent>
          </Card>
        )}
        
        {/* Embedding progress */}
        {(embeddingStatus || (downloadStatus === "completed" && loading)) && (
          <Card className="max-w-4xl mx-auto mb-6">
            <CardHeader className="pb-2">
              <CardTitle className="text-lg flex items-center gap-2">
                <FileJson className="h-5 w-5 text-purple-500" />
                Embedding Progress
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <Progress value={embeddingProgress} className="h-2" />
              <p className="text-sm text-muted-foreground">
                {embeddingMessage || "Waiting for embedding to start..."}
              </p>
              {embeddingStatus === "error" && (
                <Badge variant="outline" className="bg-red-50 text-red-700 border-red-200">
                  <AlertCircle className="h-3.5 w-3.5 mr-1" />
                  Embedding Error
                </Badge>
              )}
              {embeddingStatus === "completed" && (
                <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
                  <CheckCircle className="h-3.5 w-3.5 mr-1" />
                  Embedding Complete
                </Badge>
              )}
            </CardContent>
          </Card>
        )}
        
        {/* Message notifications - only show success and error messages */}
        {message.content && message.type !== "info" && message.type !== "processing" && (
          <Card className={`max-w-4xl mx-auto mb-6 ${
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
            <CardTitle>Usage Instructions</CardTitle>
          </CardHeader>
          <CardContent>
            <ol className="list-decimal pl-5 space-y-2 text-sm">
              <li>Enter the complete GitHub repository URL</li>
              <li>Click the“Download & Index”button</li>
              <li>Wait for the system to download and process Markdown files in the repository</li>
              <li>After processing is complete, you can view the newly added library on the homepage</li>
              <li>Click on library cards or use the query page to search documentation</li>
            </ol>
          </CardContent>
        </Card>
        
        {/* Back to homepage button */}
        <div className="flex justify-center mt-8 mb-4">
          <Button variant="outline" asChild>
            <Link href="/" className="inline-flex items-center">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M9.707 16.707a1 1 0 01-1.414 0l-6-6a1 1 0 010-1.414l6-6a1 1 0 011.414 1.414L5.414 9H17a1 1 0 110 2H5.414l4.293 4.293a1 1 0 010 1.414z" clipRule="evenodd" />
              </svg>
              Back to Homepage
            </Link>
          </Button>
        </div>
      </div>

      {/* Footer */}
      <Footer />
    </div>
  );
}
