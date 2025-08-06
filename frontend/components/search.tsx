"use client";

import React, { useState, useEffect, useMemo } from "react";
import { useRouter } from "next/navigation";
import { Input } from "@/components/ui/input";
import { Search, FileText, FileJson } from "lucide-react";
import { useAuth } from "@/lib/auth";

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

export default function SearchBar({ placeholder = "Search repositories...", className = "w-64" }: SearchBarProps) {
  const [searchQuery, setSearchQuery] = useState("");
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [repositories, setRepositories] = useState<Repository[]>([]);
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [loading, setLoading] = useState(false);
  const router = useRouter();
  const { token } = useAuth();

  // Fetch repository data from backend API
  useEffect(() => {
    const fetchRepositories = async () => {
      try {
        setLoading(true);

        // Build request headers, include auth header if token exists
        const headers: Record<string, string> = {
          'Content-Type': 'application/json',
        };

        if (token) {
          headers['Authorization'] = `Bearer ${token}`;
        }

        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/repositories/`, {
          headers,
        });
        
        if (!response.ok) {
          throw new Error(`Failed to fetch repository data: ${response.status} ${response.statusText}`);
        }
        
        const data = await response.json();
        
        if (data.status === "success" && Array.isArray(data.repositories)) {
          // Convert backend data to frontend format
          const formattedRepositories: Repository[] = data.repositories.map((repo: {
            id: number;
            name: string;
            description?: string;
            repo: string;
            repo_url?: string;
            tokens?: number;
            snippets?: number;
          }) => ({
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
        console.error('Failed to fetch repository data:', err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchRepositories();
  }, [token]);

  // Close suggestion list when clicking outside
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

  // Calculate filtered search suggestions
  const filteredSuggestions = useMemo(() => {
    if (!searchQuery.trim()) return [];
    
    const query = searchQuery.toLowerCase();
    return repositories
      .filter(repo => 
        repo.name.toLowerCase().includes(query) ||
        repo.description.toLowerCase().includes(query) ||
        repo.repo.toLowerCase().includes(query)
      )
      .slice(0, 5); // Only show first 5 results
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
          <button type="submit" className="sr-only">Search</button>
          
          {/* Auto-suggestion dropdown menu */}
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
                <div className="p-2 text-gray-500 text-center">No matching results</div>
              )}
            </div>
          )}
        </div>
      </form>
    </div>
  );
}
