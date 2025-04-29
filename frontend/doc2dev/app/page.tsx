"use client";

import React, { useState, useMemo, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
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
  Ellipsis,
  ExternalLink,
  Filter,
  Github,
  ListFilter,
  MoreHorizontal,
  Plus,
  Search,
} from "lucide-react";

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

export default function Home() {
  const [searchQuery, setSearchQuery] = useState("");
  const [sortColumn, setSortColumn] = useState<keyof Repository>("name");
  const [sortDirection, setSortDirection] = useState<"asc" | "desc">("asc");
  const [repositories, setRepositories] = useState<Repository[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();
  
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
    
    // 排序
    filtered.sort((a, b) => {
      const valueA = a[sortColumn];
      const valueB = b[sortColumn];
      
      if (typeof valueA === "string" && typeof valueB === "string") {
        return sortDirection === "asc"
          ? valueA.localeCompare(valueB)
          : valueB.localeCompare(valueA);
      }
      
      // 对于数字类型
      if (typeof valueA === "number" && typeof valueB === "number") {
        return sortDirection === "asc" ? valueA - valueB : valueB - valueA;
      }
      
      return 0;
    });
    
    return filtered;
  }, [repositories, searchQuery, sortColumn, sortDirection]);
  
  const formatNumber = (num: number) => {
    return num.toLocaleString();
  };
  
  return (
    <div className="container mx-auto py-10 px-4">
      <div className="mb-10 text-center">
        <h1 className="text-4xl font-bold tracking-tight mb-4">
          Doc2Dev - 文档检索系统
        </h1>
        <p className="text-muted-foreground max-w-2xl mx-auto mb-8">
          欢迎使用 Doc2Dev 文档检索系统。我们索引了各种库的文档，帮助您快速找到所需的信息。
        </p>
        
        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-8">
          <form onSubmit={handleSearch} className="relative w-full max-w-md">
            <Input
              type="text"
              placeholder="搜索库..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pr-10"
            />
            <Button 
              type="submit"
              size="icon"
              variant="ghost"
              className="absolute right-0 top-0 h-full"
            >
              <Search className="h-4 w-4" />
            </Button>
          </form>
          
          <Link href="/download">
            <Button className="bg-green-500 hover:bg-green-600">
              <Plus className="mr-2 h-4 w-4" /> 添加 GitHub 仓库
            </Button>
          </Link>
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="flex flex-col items-center gap-2">
            <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent"></div>
            <p className="text-muted-foreground">加载仓库数据中...</p>
          </div>
        </div>
      ) : error ? (
        <div className="flex items-center justify-center h-64">
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
        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead 
                  className="w-[250px] cursor-pointer"
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
                <TableHead>仓库</TableHead>
                <TableHead 
                  className="cursor-pointer"
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
                  className="cursor-pointer"
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
                  className="cursor-pointer"
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
                <TableHead className="text-right">操作</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredRepositories.length > 0 ? (
                filteredRepositories.map((repo) => (
                  <TableRow key={repo.id}>
                    <TableCell className="font-medium">
                      <div className="flex flex-col">
                        <span className="text-primary font-semibold">{repo.name}</span>
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
                    <TableCell className="text-right">
                      <div className="flex justify-end gap-2">
                        <Button 
                          variant="ghost" 
                          size="icon"
                          onClick={() => {
                            // 从仓库路径中提取组织和仓库名
                            const repoPath = repo.repo.startsWith('/') ? repo.repo.substring(1) : repo.repo;
                            const [org, repoName] = repoPath.split('/');
                            // 使用下划线拼接作为表名
                            const tableName = `${org}_${repoName}`.toLowerCase();
                            router.push(`/query?table=${tableName}&repo_name=${repo.name}&repo_path=${repoPath}`);
                          }}
                        >
                          <Search className="h-4 w-4" />
                        </Button>
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" size="icon">
                              <MoreHorizontal className="h-4 w-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuItem onClick={() => {
                            // 从仓库路径中提取组织和仓库名
                            const repoPath = repo.repo.startsWith('/') ? repo.repo.substring(1) : repo.repo;
                            const [org, repoName] = repoPath.split('/');
                            // 使用下划线拼接作为表名
                            const tableName = `${org}_${repoName}`.toLowerCase();
                            router.push(`/query?table=${tableName}&repo_name=${repo.name}&repo_path=${repoPath}`);
                          }}>查询</DropdownMenuItem>
                            <DropdownMenuItem>查看详情</DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
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
  );
}
