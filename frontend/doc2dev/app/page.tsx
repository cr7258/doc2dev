"use client";

import React, { useState, useMemo, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Dropdown } from "@/components/dropdown";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  ChevronDown,
  ChevronUp,
  ExternalLink,
  Github,
  MoreHorizontal,
  Plus,
  Search,
  Database,
  FileText,
  FileJson,
  Trash2,
} from "lucide-react";
import { Navbar } from "@/components/navbar";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { useToast, Toaster } from "@/components/ui/toast";

interface Repository {
  id: string;
  name: string;
  description: string;
  repo: string;
  repo_url?: string;
  tokens: number;
  snippets: number;
  lastUpdated: string;
  status: "active" | "archived" | "private";
}

interface StatsCardProps {
  title: string;
  value: number;
  icon: React.ReactNode;
  className?: string;
}

const StatsCard: React.FC<StatsCardProps> = ({ title, value, icon, className }) => {
  return (
    <div className={`flex flex-col justify-between p-6 border rounded-md bg-white ${className}`}>
      <div className="mb-4">{icon}</div>
      <h2 className="text-3xl tracking-tighter font-medium">{value.toLocaleString()}</h2>
      <p className="text-base text-muted-foreground">{title}</p>
    </div>
  );
};

export default function Home() {
  const [searchQuery, setSearchQuery] = useState("");
  const [sortColumn, setSortColumn] = useState<keyof Repository>("name");
  const [sortDirection, setSortDirection] = useState<"asc" | "desc">("asc");
  const [repositories, setRepositories] = useState<Repository[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [repoToDelete, setRepoToDelete] = useState<Repository | null>(null);
  const { toast } = useToast();
  const router = useRouter();
  
  // 点击页面其他区域关闭建议列表
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (showSuggestions) {
        const target = event.target as Node;
        const searchContainer = document.getElementById('search-container');
        if (searchContainer && !searchContainer.contains(target)) {
          setShowSuggestions(false);
        }
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [showSuggestions]);
  
  // 删除仓库的函数
  const handleDeleteRepo = async () => {
    if (!repoToDelete) return;
    
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'}/repositories/${repoToDelete.id}`, {
        method: 'DELETE',
      });
      
      if (response.ok) {
        const data = await response.json();
        toast({
          title: "删除成功",
          description: data.message || `仓库 ${repoToDelete.name} 已成功删除`,
          variant: "success",
          duration: 3000,
        });
        // 刷新页面以更新仓库列表
        setTimeout(() => window.location.reload(), 1000);
      } else {
        const error = await response.json();
        toast({
          title: "删除失败",
          description: error.detail || '未知错误',
          variant: "destructive",
          duration: 5000,
        });
      }
    } catch (error) {
      console.error('删除仓库时出错:', error);
      toast({
        title: "删除失败",
        description: error instanceof Error ? error.message : '未知错误',
        variant: "destructive",
        duration: 5000,
      });
    } finally {
      setDeleteDialogOpen(false);
      setRepoToDelete(null);
    }
  };
  
  // 从后端 API 获取仓库数据
  useEffect(() => {
    const fetchRepositories = async () => {
      try {
        setLoading(true);
        const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'}/repositories/`);
        
        if (!response.ok) {
          throw new Error(`获取仓库数据失败: ${response.status} ${response.statusText}`);
        }
        
        const data = await response.json();
        
        if (data.status === "success" && Array.isArray(data.repositories)) {
          // 将后端数据转换为前端所需的格式
          const formattedRepositories: Repository[] = data.repositories.map((repo: any) => ({
            id: repo.id.toString(),
            name: repo.name,
            description: repo.description || '',
            repo: repo.repo,
            repo_url: repo.repo_url,
            tokens: repo.tokens || 0,
            snippets: repo.snippets || 0,
            lastUpdated: repo.last_updated || '-',
            status: "active"
          }));
          
          setRepositories(formattedRepositories);
        } else {
          throw new Error('获取仓库数据格式不正确');
        }
      } catch (err) {
        console.error('获取仓库数据失败:', err);
        setError(err instanceof Error ? err.message : '获取仓库数据失败');
      } finally {
        setLoading(false);
      }
    };
    
    fetchRepositories();
  }, []);
  
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      // 跳转到查询页面，并传递搜索查询参数
      router.push(`/query?q=${encodeURIComponent(searchQuery)}`);
    }
  };
  
  const handleSort = (column: keyof Repository) => {
    if (sortColumn === column) {
      setSortDirection(sortDirection === "asc" ? "desc" : "asc");
    } else {
      setSortColumn(column);
      setSortDirection("asc");
    }
  };
  
  const filteredRepositories = useMemo(() => {
    let filtered = [...repositories];
    
    // 搜索过滤
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(
        (repo) =>
          repo.name.toLowerCase().includes(query) ||
          repo.description.toLowerCase().includes(query) ||
          repo.repo.toLowerCase().includes(query)
      );
    }
    
    return filtered;
  }, [repositories, searchQuery]);

  // 计算过滤后的搜索建议
  const filteredSuggestions = useMemo(() => {
    if (!searchQuery.trim()) return [];
    
    const query = searchQuery.toLowerCase();
    return repositories
      .filter(repo => 
        repo.name.toLowerCase().includes(query) ||
        repo.description.toLowerCase().includes(query) ||
        repo.repo.toLowerCase().includes(query)
      )
      .slice(0, 5); // 只显示前5个结果
  }, [searchQuery, repositories]);

  // 计算过滤和排序后的仓库列表
  const sortedRepositories = useMemo(() => {
    return [...filteredRepositories].sort((a, b) => {
      if (typeof a[sortColumn] === 'string' && typeof b[sortColumn] === 'string') {
        return sortDirection === "asc"
          ? (a[sortColumn] as string).localeCompare(b[sortColumn] as string)
          : (b[sortColumn] as string).localeCompare(a[sortColumn] as string);
      } else {
        return sortDirection === "asc"
          ? (a[sortColumn] as number) - (b[sortColumn] as number)
          : (b[sortColumn] as number) - (a[sortColumn] as number);
      }
    });
  }, [filteredRepositories, sortColumn, sortDirection]);

  const formatNumber = (num: number) => {
    return num.toLocaleString();
  };
  
  // 计算统计数据
  const totalTokens = useMemo(() => {
    return repositories.reduce((sum, repo) => sum + repo.tokens, 0);
  }, [repositories]);

  const totalSnippets = useMemo(() => {
    return repositories.reduce((sum, repo) => sum + repo.snippets, 0);
  }, [repositories]);

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      <div className="container mx-auto py-10 px-4">
        {/* 顶部导航栏 - 只显示 logo，并对齐到左侧 */}
        <div className="max-w-5xl mx-auto">
          <Navbar showSearch={false} alignment="left" />
        </div>

        <div className="mb-10 text-center max-w-5xl mx-auto">
          <h1 className="text-4xl font-bold tracking-tight mb-4">
            Doc2Dev - 为 LLM 和 AI 编程助手提供实时文档
          </h1>
          <p className="text-muted-foreground max-w-2xl mx-auto mb-8">
            索引并查询任何 GitHub 仓库的最新文档，通过 MCP 轻松与 Cursor、Windsurf 等 AI 编程助手集成。拒绝代码幻觉，让 AI 编写更靠谱的代码。
          </p>
        </div>
        
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 max-w-5xl mx-auto mb-6">
          <StatsCard 
            title="索引的仓库" 
            value={repositories.length} 
            icon={<Database className="w-5 h-5 text-blue-500" />} 
            className="border-blue-100"
          />
          <StatsCard 
            title="Tokens 总数" 
            value={totalTokens} 
            icon={<FileText className="w-5 h-5 text-green-500" />} 
            className="border-green-100"
          />
          <StatsCard 
            title="Snippets 总数" 
            value={totalSnippets} 
            icon={<FileJson className="w-5 h-5 text-purple-500" />} 
            className="border-purple-100"
          />
        </div>
        
        {/* Search and Add Repository */}
        <div className="flex flex-wrap items-center justify-between gap-4 max-w-5xl mx-auto mb-6">
          <div className="relative">
            <form onSubmit={handleSearch} className="flex items-center">
              <div className="relative w-64">
                <Input
                  className="pl-9 pr-4 bg-white border-border w-full cursor-pointer"
                  placeholder="搜索仓库..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  type="search"
                />
                <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3 text-muted-foreground">
                  <Search size={16} strokeWidth={2} />
                </div>
                <button type="submit" className="sr-only">搜索</button>
              </div>
            </form>
          </div>
          <Link href="/download">
            <Button className="bg-blue-500 hover:bg-blue-600 text-white cursor-pointer">
              <Plus className="mr-1 h-4 w-4" />
              添加 GitHub 仓库
            </Button>
          </Link>
        </div>

        {loading ? (
          <div className="flex items-center justify-center h-64 bg-white rounded-md border max-w-5xl mx-auto">
            <div className="flex flex-col items-center gap-2">
              <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent"></div>
              <p className="text-muted-foreground">加载仓库数据中...</p>
            </div>
          </div>
        ) : error ? (
          <div className="flex items-center justify-center h-64 bg-white rounded-md border max-w-5xl mx-auto">
            <div className="flex flex-col items-center gap-2 text-destructive">
              <div className="rounded-full bg-destructive/10 p-3">
                <ExternalLink className="h-6 w-6" />
              </div>
              <p>加载仓库数据失败</p>
              <p className="text-sm text-muted-foreground">{error}</p>
              <Button 
                variant="outline" 
                size="sm"
                onClick={() => window.location.reload()}
              >
                重试
              </Button>
            </div>
          </div>
        ) : (
          <div className="rounded-md border max-w-5xl mx-auto bg-white overflow-hidden">
            <Table>
              <TableHeader className="bg-blue-50">
                <TableRow>
                  <TableHead 
                    className="w-[160px] cursor-pointer font-medium"
                    onClick={() => handleSort("name")}
                  >
                    <div className="flex items-center">
                      名称
                      {sortColumn === "name" && (
                        sortDirection === "asc" ? 
                        <ChevronUp className="ml-1 h-4 w-4" /> : 
                        <ChevronDown className="ml-1 h-4 w-4" />
                      )}
                    </div>
                  </TableHead>
                  <TableHead className="w-[160px]">仓库</TableHead>
                  <TableHead 
                    className="w-[80px] cursor-pointer"
                    onClick={() => handleSort("tokens")}
                  >
                    <div className="flex items-center">
                      Tokens
                      {sortColumn === "tokens" && (
                        sortDirection === "asc" ? 
                        <ChevronUp className="ml-1 h-4 w-4" /> : 
                        <ChevronDown className="ml-1 h-4 w-4" />
                      )}
                    </div>
                  </TableHead>
                  <TableHead 
                    className="w-[80px] cursor-pointer"
                    onClick={() => handleSort("snippets")}
                  >
                    <div className="flex items-center">
                      代码片段
                      {sortColumn === "snippets" && (
                        sortDirection === "asc" ? 
                        <ChevronUp className="ml-1 h-4 w-4" /> : 
                        <ChevronDown className="ml-1 h-4 w-4" />
                      )}
                    </div>
                  </TableHead>
                  <TableHead 
                    className="w-[100px] cursor-pointer"
                    onClick={() => handleSort("lastUpdated")}
                  >
                    <div className="flex items-center">
                      更新时间
                      {sortColumn === "lastUpdated" && (
                        sortDirection === "asc" ? 
                        <ChevronUp className="ml-1 h-4 w-4" /> : 
                        <ChevronDown className="ml-1 h-4 w-4" />
                      )}
                    </div>
                  </TableHead>
                  <TableHead className="w-[60px] text-center">操作</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredRepositories.length > 0 ? (
                  filteredRepositories.map((repo) => (
                    <TableRow key={repo.id}>
                      <TableCell className="font-medium">
                        <div className="flex flex-col">
                          <a 
                            href="#" 
                            onClick={(e) => {
                              e.preventDefault();
                              // 从仓库路径中提取组织和仓库名
                              const repoPath = repo.repo.startsWith('/') ? repo.repo.substring(1) : repo.repo;
                              const [org, repoName] = repoPath.split('/');
                              // 使用下划线拼接作为表名
                              const tableName = `${org}_${repoName}`.toLowerCase();
                              router.push(`/query?table=${tableName}&repo_name=${repo.name}&repo_path=${repoPath}`);
                            }}
                            className="text-blue-500 font-semibold hover:text-blue-700 hover:underline cursor-pointer"
                          >
                            {repo.name}
                          </a>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center">
                          <Github className="mr-2 h-4 w-4" />
                          <a 
                            href={repo.repo_url || `https://github.com${repo.repo}`} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="text-blue-600 hover:underline flex items-center"
                          >
                            <span>{repo.repo}</span>
                            <ExternalLink className="ml-1 h-3 w-3" />
                          </a>
                        </div>
                      </TableCell>
                      <TableCell>{formatNumber(repo.tokens)}</TableCell>
                      <TableCell>{formatNumber(repo.snippets)}</TableCell>
                      <TableCell>
                        <Badge variant="outline" className="font-normal">
                          {repo.lastUpdated}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-center">
                        <div className="flex justify-center gap-2">
                          {/* 使用下拉菜单组件 */}
                          <Dropdown 
                            items={[
                              {
                                id: 1,
                                label: "查询",
                                icon: Search,
                                onClick: () => {
                                  // 从仓库路径中提取组织和仓库名
                                  const repoPath = repo.repo.startsWith('/') ? repo.repo.substring(1) : repo.repo;
                                  const [org, repoName] = repoPath.split('/');
                                  // 使用下划线拼接作为表名
                                  const tableName = `${org}_${repoName}`.toLowerCase();
                                  router.push(`/query?table=${tableName}&repo_name=${repo.name}&repo_path=${repoPath}`);
                                }
                              },
                              {
                                id: 2,
                                label: "删除",
                                icon: Trash2,
                                onClick: () => {
                                  setRepoToDelete(repo);
                                  setDeleteDialogOpen(true);
                                }
                              }
                            ]}
                          />
                        </div>
                      </TableCell>
                    </TableRow>
                  ))
                ) : (
                  <TableRow>
                    <TableCell colSpan={6} className="h-24 text-center">
                      没有找到仓库。
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </div>
        )}
      </div>
      
      {/* 删除确认对话框 */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>删除仓库？</AlertDialogTitle>
            <AlertDialogDescription>
              {repoToDelete && (
                <>
                  确定要删除仓库 <span className="font-medium">{repoToDelete.name}</span> 吗？
                  <span className="block mt-2 text-red-500">此操作不可恢复，删除后所有相关数据将被清除。</span>
                </>
              )}
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel className="cursor-pointer">取消</AlertDialogCancel>
            <AlertDialogAction onClick={handleDeleteRepo} className="bg-red-500 hover:bg-red-600 cursor-pointer">
              删除
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
      
      {/* Toast 通知组件 */}
      <Toaster />
    </div>
  );
}