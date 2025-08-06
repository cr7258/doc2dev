"use client";

import React, { useState, useEffect, Suspense } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Github, Clock, RefreshCw, ExternalLink, FileText, FileJson, FileCode, Copy } from "lucide-react";
import { getRelativeTime} from "@/utils/date";
import { Navbar } from "@/components/navbar";
import Footer from "@/components/footer";
import { useAuth } from "@/lib/auth";
import { useToast, Toaster } from "@/components/ui/toast";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";


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
  repo_status?: "in_progress" | "completed" | "failed" | "pending";
}

// Format date time to local time
// Time and number formatting functions moved to utils/date-utils.ts

function QueryPageContent() {
  const { token } = useAuth();
  const { toast } = useToast();
  const searchParams = useSearchParams();
  const initialTable = searchParams.get("table") || "";
  const initialQuery = searchParams.get("q") || "";
  const repoName = searchParams.get("repo_name") || "";
  const repoPath = searchParams.get("repo_path") || "";
  
  // Convert table name to correct format
  const formatTableName = (name: string) => {
    // If table name is numeric ID, we need to get the real table name
    if (/^\d+$/.test(name)) {
      // Generate table name based on repository path
      if (repoPath) {
        // Replace slashes with underscores and convert to lowercase
        return repoPath.toLowerCase().replace(/\//g, '_');
      }
    }
    return name;
  };
  
  const [tableName, setTableName] = useState(formatTableName(initialTable));
  const [query, setQuery] = useState(initialQuery);
  // Query state already declared above

  // Repository data state
  const [loading, setLoading] = useState(false);
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [results, setResults] = useState<{
    id: string;
    source: string;
    content: string;
    distance?: number;
  }[]>([]);
  const [summary, setSummary] = useState("");
  const [repoData, setRepoData] = useState<RepositoryData | null>(null);

  // Get status badge component like homepage
  const getStatusBadge = () => {
    if (!repoData || !repoData.repo_status) {
      return (
        <Badge className="bg-amber-50 text-amber-600 border-amber-200 hover:bg-amber-100">
          Pending
        </Badge>
      );
    }
    
    switch (repoData.repo_status) {
      case 'completed':
        return (
          <Badge className="bg-green-50 text-green-600 border-green-200 hover:bg-green-100">
            Completed
          </Badge>
        );
      case 'in_progress':
        return (
          <Badge className="bg-blue-50 text-blue-600 border-blue-200 hover:bg-blue-100">
            In Progress
          </Badge>
        );
      case 'failed':
        return (
          <Badge className="bg-red-50 text-red-600 border-red-200 hover:bg-red-100">
            Failed
          </Badge>
        );
      case 'pending':
      default:
        return (
          <Badge className="bg-amber-50 text-amber-600 border-amber-200 hover:bg-amber-100">
            Pending
          </Badge>
        );
    }
  };

  // Build DocumentItem based on actual data
  const documentItem: DocumentItem = {
    projectName: repoName,
    githubLink: `https://github.com/${repoPath}`,
    description: repoData?.description || "A GitHub repository for documentation queries and code reference",
    tokens: repoData ? repoData.tokens.toLocaleString() : "0",
    snippets: repoData ? repoData.snippets.toLocaleString() : "0",
    updatedAt: repoData?.updated_at ? getRelativeTime(repoData.updated_at) : ""
  };
  
  // Get repository data
  useEffect(() => {
    if (repoPath) {
      // Clear previous query results and query content
      setResults([]);
      setSummary("");
      setQuery("");

      // Update tableName to new repository path
      const newTableName = repoPath.toLowerCase().replace(/\//g, '_');
      setTableName(newTableName);

      const fetchRepoData = async () => {
        try {
          const headers: Record<string, string> = {
            "Content-Type": "application/json",
          };

          // If there's an auth token, add it to request headers
          if (token) {
            headers.authorization = `Bearer ${token}`;
          }

          const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/repositories/${repoPath.replace('/', '_')}`, {
            headers: headers,
          });

          if (response.ok) {
            const data = await response.json();
            if (data.status === "success" && data.repository) {
              setRepoData(data.repository);
            }
          } else {
            console.error("Failed to fetch repository data:", response.status, response.statusText);
          }
        } catch (error) {
          console.error("Error fetching repository data:", error);
        }
      };
      
      fetchRepoData();
    }
  }, [repoPath, token]);

  // Function to refresh repository
  const handleRefreshRepo = async () => {
    if (!repoData) {
      toast({
        title: "Refresh Failed",
        description: "Repository data not available for refresh",
        variant: "destructive",
        duration: 3000,
      });
      return;
    }

    try {
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
      };

      // Only add authorization header if token exists
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/repositories/${repoData.id}/refresh`, {
        method: 'POST',
        headers: headers,
      });

      if (response.ok) {
        const data = await response.json();
        toast({
          title: "Refresh Started",
          description: data.message || `Repository ${repoData.name} refresh started`,
          variant: "success",
          duration: 3000,
        });
        
        // Refresh repository data after a short delay
        setTimeout(async () => {
          const fetchRepoData = async () => {
            try {
              const headers: Record<string, string> = {
                "Content-Type": "application/json",
              };

              if (token) {
                headers.authorization = `Bearer ${token}`;
              }

              const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/repositories/${repoPath.replace('/', '_')}`, {
                headers: headers,
              });

              if (response.ok) {
                const data = await response.json();
                if (data.status === "success" && data.repository) {
                  setRepoData(data.repository);
                }
              }
            } catch (error) {
              console.error("Error refreshing repository data:", error);
            }
          };
          
          fetchRepoData();
        }, 1000);
        
      } else {
        const error = await response.json();
        toast({
          title: "Refresh Failed",
          description: error.detail || 'Failed to start refresh',
          variant: "destructive",
          duration: 5000,
        });
      }
    } catch (error) {
      console.error('Error refreshing repository:', error);
      toast({
        title: "Refresh Failed",
        description: error instanceof Error ? error.message : 'Unknown error',
        variant: "destructive",
        duration: 5000,
      });
    }
  };
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!tableName || !query) return;
    
    setLoading(true);
    setResults([]);
    setSummary("");
    
    try {
      const headers: Record<string, string> = {
        "Content-Type": "application/json",
      };

      // 如果有认证token，添加到请求头
      if (token) {
        headers.authorization = `Bearer ${token}`;
      }

      const response = await fetch("/api/query", {
        method: "POST",
        headers: headers,
        body: JSON.stringify({
          // 表名应该是原始格式，不需要添加前缀
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
        // 显示错误信息给用户
        setSummary(`查询出错: ${data.message}\n\n请检查以下可能的问题:\n1. 表名格式是否正确\n2. 该仓库是否已成功索引\n3. 后端服务是否正常运行`);
      }
    } catch (error) {
      console.error("Error querying:", error);
      // 显示错误信息给用户
      setSummary(`查询请求失败: ${error instanceof Error ? error.message : String(error)}\n\n请检查网络连接和后端服务是否正常运行。`);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white flex flex-col">
      <div className="container mx-auto px-4 pt-6 flex-1">
        {/* 顶部导航栏 */}
        <Navbar />
      {/* 仓库信息区域 */}
      {documentItem.projectName && (
        <Card className="w-full max-w-4xl mx-auto mb-6 overflow-hidden shadow-sm border border-gray-100">
          <CardHeader className="pb-2">
            <div className="flex justify-between items-start">
              <div className="flex flex-col flex-1">
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
              <Button
                onClick={handleRefreshRepo}
                variant="outline"
                size="sm"
                className="flex items-center gap-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 transition-colors cursor-pointer"
                disabled={!repoData}
              >
                <RefreshCw className="h-4 w-4" />
                Refresh
              </Button>
            </div>
          </CardHeader>
          <CardContent className="pb-3">
            <div className="flex flex-wrap gap-3">
              {getStatusBadge()}
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
      
      <Card className="w-full max-w-4xl mx-auto mb-6 overflow-hidden shadow-sm border border-gray-100">
        <CardHeader className="pb-2">
          <CardTitle className="text-lg flex items-center gap-2">
            <FileCode className="h-5 w-5 text-blue-500" />
            Document Query
          </CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit}>
            {/* Hidden vector database name input */}
            <input
              id="tableName"
              type="hidden"
              value={tableName}
            />
            
            <div className="mb-6">
              <label htmlFor="query" className="block text-sm font-medium mb-2">
                Query Content
              </label>
              <div className="flex items-center space-x-2">
                <div className="relative flex-1">
                  <input
                    id="query"
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
                    placeholder="Enter your question..."
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
                  className="bg-blue-500 hover:bg-blue-600 text-white cursor-pointer h-[42px] px-6 text-base font-medium"
                  disabled={loading}
                >
                  {loading ? (
                    <>
                      <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Querying...
                    </>
                  ) : "Query"}
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
            <p className="mt-4 text-gray-600">Querying documents, please wait...</p>
          </div>
        </div>
      )}
      
      {/* Removed query results section, only keep summary */}

      {/* Summary section */}
      {summary && (
        <Card className="w-full max-w-4xl mx-auto mb-6 overflow-hidden shadow-sm border border-gray-100">
          <CardHeader className="pb-2">
            <div className="flex justify-between items-center">
              <CardTitle className="text-lg flex items-center gap-2">
                <FileText className="h-5 w-5 text-blue-500" />
                Query Results
              </CardTitle>
              <Button 
                variant="ghost" 
                size="sm" 
                className="h-8 w-8 p-0 text-gray-500 hover:text-blue-600 hover:bg-blue-50 cursor-pointer"
                onClick={() => {
                  navigator.clipboard.writeText(summary);
                  // Use state variable to show copy success notification
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
                title="Copy to clipboard"
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
            Back to Homepage
          </Link>
        </Button>
      </div>
      </div>

      {/* Footer */}
      <Footer />
      
      {/* Toast notification component */}
      <Toaster />
    </div>
  );
}

export default function QueryPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto mb-4"></div>
          <p className="text-lg">Loading...</p>
        </div>
      </div>
    }>
      <QueryPageContent />
    </Suspense>
  )
}
