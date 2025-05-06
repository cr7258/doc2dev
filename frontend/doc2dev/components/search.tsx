"use client";

import React, { useState, useEffect, useMemo } from "react";
import { useRouter } from "next/navigation";
import { Input } from "@/components/ui/input";
import { Search, FileText, FileJson } from "lucide-react";

interface Repository {
  id: string;
  name: string;
  description: string;
  repo: string;
  repo_url?: string;
  tokens: number;
  snippets: number;
}

interface SearchBarProps {
  placeholder?: string;
  className?: string;
}

export default function SearchBar({ placeholder = "搜索仓库...", className = "w-64" }: SearchBarProps) {
  const [searchQuery, setSearchQuery] = useState("");
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [repositories, setRepositories] = useState<Repository[]>([]);
  const [loading, setLoading] = useState(false);
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
            status: "active"
          }));
          
          setRepositories(formattedRepositories);
        }
      } catch (err) {
        console.error('获取仓库数据失败:', err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchRepositories();
  }, []);

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

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      router.push(`/?search=${encodeURIComponent(searchQuery)}`);
    }
  };

  return (
    <div className="relative" id="search-container">
      <form onSubmit={handleSearch} className="flex items-center">
        <div className={`relative ${className}`}>
          <Input
            className="pl-9 pr-4 bg-white border-border w-full cursor-pointer"
            placeholder={placeholder}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            type="search"
            onFocus={() => setShowSuggestions(true)}
          />
          <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3 text-muted-foreground">
            <Search size={16} strokeWidth={2} />
          </div>
          <button type="submit" className="sr-only">搜索</button>
          
          {/* 自动提示下拉菜单 */}
          {showSuggestions && searchQuery.trim() !== "" && (
            <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-gray-200 rounded-md shadow-lg z-10 max-h-60 overflow-y-auto">
              {filteredSuggestions.length > 0 ? (
                filteredSuggestions.map((repo: Repository) => (
                  <div 
                    key={repo.id} 
                    className="p-2 hover:bg-blue-50 cursor-pointer flex flex-col"
                    onClick={() => {
                      setSearchQuery(repo.repo);
                      setShowSuggestions(false);
                      router.push(`/query?table=${repo.id.replace(/\//g, '_')}&repo_name=${encodeURIComponent(repo.name)}&repo_path=${encodeURIComponent(repo.repo)}`);
                    }}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-medium text-blue-500">{repo.repo}</span>
                    </div>
                    <div className="flex items-center text-xs text-gray-500 mt-1 gap-3">
                      <span className="flex items-center gap-1">
                        <FileText className="h-3 w-3" />
                        <span className="font-bold text-gray-800">{repo.tokens.toLocaleString()}</span> tokens
                      </span>
                      <span className="flex items-center gap-1">
                        <FileJson className="h-3 w-3" />
                        <span className="font-bold text-gray-800">{repo.snippets.toLocaleString()}</span> snippets
                      </span>
                    </div>
                  </div>
                ))
              ) : (
                <div className="p-2 text-gray-500 text-center">无匹配结果</div>
              )}
            </div>
          )}
        </div>
      </form>
    </div>
  );
}
