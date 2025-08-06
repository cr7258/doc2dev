"use client";

import React, { useState, useMemo, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { TableRowDropdown } from "@/components/ui/dropdown";
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
  Gitlab,
  Plus,
  Search,
  Database,
  FileText,
  FileJson,
} from "lucide-react";
import { Navbar } from "@/components/navbar";
import Footer from "@/components/footer";
import { formatDateTime, getRelativeTime, formatNumber } from "@/utils/date";
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
import { useAuth } from "@/lib/auth";

interface Repository {
  id: string;
  name: string;
  description: string;
  repo: string;
  repo_url?: string;
  tokens: number;
  snippets: number;
  lastUpdated: string;
  updatedAt?: string; // ISO format update time
  createdAt?: string; // ISO format creation time
  status: "active" | "archived" | "private";
  repo_status?: "in_progress" | "completed" | "failed" | "pending";
  source?: "github" | "gitlab"; // Add source type field
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
  const { token } = useAuth();
  
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
  
  // Function to refresh repository
  const handleRefreshRepo = async (repo: Repository) => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'}/repositories/${repo.id}/refresh`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        toast({
          title: "Refresh Started",
          description: data.message || `Repository ${repo.name} refresh started`,
          variant: "success",
          duration: 3000,
        });
        // Refresh page to show updated status
        setTimeout(() => window.location.reload(), 1000);
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

  // Function to delete repository
  const handleDeleteRepo = async () => {
    if (!repoToDelete) return;

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'}/repositories/${repoToDelete.id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        toast({
          title: "Delete Successful",
          description: data.message || `Repository ${repoToDelete.name} has been successfully deleted`,
          variant: "success",
          duration: 3000,
        });
        // Refresh page to update repository list
        setTimeout(() => window.location.reload(), 1000);
      } else {
        const error = await response.json();
        toast({
          title: "Delete Failed",
          description: error.detail || 'Unknown error',
          variant: "destructive",
          duration: 5000,
        });
      }
    } catch (error) {
      console.error('Error deleting repository:', error);
      toast({
        title: "Delete Failed",
        description: error instanceof Error ? error.message : 'Unknown error',
        variant: "destructive",
        duration: 5000,
      });
    } finally {
      setDeleteDialogOpen(false);
      setRepoToDelete(null);
    }
  };
  
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

        const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'}/repositories/`, {
          headers,
        });

        if (!response.ok) {
          throw new Error(`Failed to fetch repository data: ${response.status} ${response.statusText}`);
        }

        const data = await response.json();

        if (data.status === "success" && Array.isArray(data.repositories)) {
          // Convert backend data to frontend format
          const formattedRepositories = data.repositories.map((repo: {
            id: number;
            name: string;
            description?: string;
            repo: string;
            repo_url: string;
            tokens?: number;
            snippets?: number;
            updated_at: string;
            created_at: string;
            repo_status?: string;
            source?: string;
          }) => ({
            id: repo.id.toString(),
            name: repo.name,
            description: repo.description || '',
            repo: repo.repo,
            repo_url: repo.repo_url,
            tokens: repo.tokens || 0,
            snippets: repo.snippets || 0,
            // Use relative time calculation function
            lastUpdated: getRelativeTime(repo.updated_at),
            // Save original timestamp for sorting and detailed display
            updatedAt: repo.updated_at,
            createdAt: repo.created_at,
            status: "active",
            repo_status: repo.repo_status || "pending",
            source: repo.source || "github" // Add source field
          }));

          setRepositories(formattedRepositories);
        } else {
          throw new Error('Invalid repository data format');
        }
      } catch (err) {
        console.error('Failed to fetch repository data:', err);
        setError(err instanceof Error ? err.message : 'Failed to fetch repository data');
      } finally {
        setLoading(false);
      }
    };

    fetchRepositories();
  }, [token]); // Re-fetch data when token changes (login/logout)
  
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      // Navigate to query page with search query parameters
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
    
    // Search filtering
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


  // Calculate filtered and sorted repository list
  const sortedFilteredRepositories = useMemo(() => {
    return [...filteredRepositories].sort((a, b) => {
      // For lastUpdated column, use updatedAt field for sorting
      if (sortColumn === "lastUpdated") {
        const dateA = a.updatedAt ? new Date(a.updatedAt).getTime() : 0;
        const dateB = b.updatedAt ? new Date(b.updatedAt).getTime() : 0;
        return sortDirection === "asc" ? dateA - dateB : dateB - dateA;
      }
      // Sorting for other string columns
      else if (typeof a[sortColumn] === 'string' && typeof b[sortColumn] === 'string') {
        return sortDirection === "asc"
          ? (a[sortColumn] as string).localeCompare(b[sortColumn] as string)
          : (b[sortColumn] as string).localeCompare(a[sortColumn] as string);
      }
      // Sorting for number columns
      else {
        return sortDirection === "asc"
          ? (a[sortColumn] as number) - (b[sortColumn] as number)
          : (b[sortColumn] as number) - (a[sortColumn] as number);
      }
    });
  }, [filteredRepositories, sortColumn, sortDirection]);

  // Time and number formatting functions moved to utils/date-utils.ts
  // Calculate statistics
  const totalTokens = useMemo(() => {
    return repositories.reduce((sum, repo) => sum + repo.tokens, 0);
  }, [repositories]);

  const totalSnippets = useMemo(() => {
    return repositories.reduce((sum, repo) => sum + repo.snippets, 0);
  }, [repositories]);

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white flex flex-col">
      <div className="container mx-auto py-10 px-4 flex-1">
        {/* Top navigation bar - only show logo, aligned to left */}
        <div className="max-w-5xl mx-auto">
          <Navbar showSearch={false} alignment="left" />
        </div>

        <div className="mb-10 text-center max-w-5xl mx-auto">
          <h1 className="text-3xl font-bold tracking-tight mb-4">
            Up-to-date docs for AI code assistants
          </h1>
          <p className="text-muted-foreground max-w-2xl mx-auto mb-8">
            Index and query GitHub/GitLab repositories, integrating with tools like Cursor, Windsurf via MCP. Eliminate code hallucinations and make AI write more reliable code.
          </p>
        </div>
        
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 max-w-5xl mx-auto mb-6">
          <StatsCard
            title="Indexed Repositories"
            value={repositories.length}
            icon={<Database className="w-5 h-5 text-blue-500" />}
            className="border-blue-100"
          />
          <StatsCard
            title="Total Tokens"
            value={totalTokens}
            icon={<FileText className="w-5 h-5 text-green-500" />}
            className="border-green-100"
          />
          <StatsCard
            title="Total Snippets"
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
                  placeholder="Search repositories..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  type="search"
                />
                <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3 text-muted-foreground">
                  <Search size={16} strokeWidth={2} />
                </div>
                <button type="submit" className="sr-only">Search</button>
              </div>
            </form>
          </div>
          <Link href="/download">
            <Button className="bg-blue-500 hover:bg-blue-600 text-white cursor-pointer">
              <Plus className="mr-1 h-4 w-4" />
              Add Git Repository
            </Button>
          </Link>
        </div>

        {loading ? (
          <div className="flex items-center justify-center h-64 bg-white rounded-md border max-w-5xl mx-auto">
            <div className="flex flex-col items-center gap-2">
              <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent"></div>
              <p className="text-muted-foreground">Loading repository data...</p>
            </div>
          </div>
        ) : error ? (
          <div className="flex items-center justify-center h-64 bg-white rounded-md border max-w-5xl mx-auto">
            <div className="flex flex-col items-center gap-2 text-destructive">
              <div className="rounded-full bg-destructive/10 p-3">
                <ExternalLink className="h-6 w-6" />
              </div>
              <p>Failed to load repository data</p>
              <p className="text-sm text-muted-foreground">{error}</p>
              <Button
                variant="outline"
                size="sm"
                onClick={() => window.location.reload()}
              >
                Retry
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
                      Name
                      {sortColumn === "name" && (
                        sortDirection === "asc" ?
                        <ChevronUp className="ml-1 h-4 w-4" /> :
                        <ChevronDown className="ml-1 h-4 w-4" />
                      )}
                    </div>
                  </TableHead>
                  <TableHead className="w-[160px]">Repository</TableHead>
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
                      Snippets
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
                      Last Updated
                      {sortColumn === "lastUpdated" && (
                        sortDirection === "asc" ?
                        <ChevronUp className="ml-1 h-4 w-4" /> :
                        <ChevronDown className="ml-1 h-4 w-4" />
                      )}
                    </div>
                  </TableHead>
                  <TableHead className="w-[80px] text-center">Status</TableHead>
                  <TableHead className="w-[60px] text-center">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {sortedFilteredRepositories.length > 0 ? (
                  sortedFilteredRepositories.map((repo) => (
                    <TableRow key={repo.id}>
                      <TableCell className="font-medium">
                        <div className="flex flex-col">
                          <a 
                            href="#" 
                            onClick={(e) => {
                              e.preventDefault();
                              // Extract organization and repository name from repository path
                              const repoPath = repo.repo.startsWith('/') ? repo.repo.substring(1) : repo.repo;
                              const [org, repoName] = repoPath.split('/');
                              // Use underscore concatenation as table name
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
                          {repo.source === "gitlab" ? (
                            <Gitlab className="mr-2 h-4 w-4 text-orange-500" />
                          ) : (
                            <Github className="mr-2 h-4 w-4" />
                          )}
                          <a
                            href={repo.repo_url || `https://${repo.source === "gitlab" ? "gitlab.com" : "github.com"}${repo.repo}`}
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
                        <Badge 
                          variant="outline" 
                          className="font-normal"
                          title={repo.updatedAt ? formatDateTime(repo.updatedAt) : ''}
                        >
                          {repo.lastUpdated}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-center">
                        {repo.repo_status === "in_progress" && (
                          <Badge className="bg-blue-50 text-blue-600 border-blue-200 hover:bg-blue-100">
                            In Progress
                          </Badge>
                        )}
                        {repo.repo_status === "completed" && (
                          <Badge className="bg-green-50 text-green-600 border-green-200 hover:bg-green-100">
                            Completed
                          </Badge>
                        )}
                        {repo.repo_status === "failed" && (
                          <Badge className="bg-red-50 text-red-600 border-red-200 hover:bg-red-100">
                            Failed
                          </Badge>
                        )}
                        {(repo.repo_status === "pending" || !repo.repo_status) && (
                          <Badge className="bg-amber-50 text-amber-600 border-amber-200 hover:bg-amber-100">
                            Pending
                          </Badge>
                        )}
                      </TableCell>
                      <TableCell className="text-center">
                        <div className="flex justify-center gap-2">
                          {/* 使用下拉菜单组件 */}
                          <TableRowDropdown
                            onQuery={() => {
                              // Extract organization and repository name from repository path
                              const repoPath = repo.repo.startsWith('/') ? repo.repo.substring(1) : repo.repo;
                              const [org, repoName] = repoPath.split('/');
                              // Use underscore concatenation as table name
                              const tableName = `${org}_${repoName}`.toLowerCase();
                              router.push(`/query?table=${tableName}&repo_name=${repo.name}&repo_path=${repoPath}`);
                            }}
                            onRefresh={() => handleRefreshRepo(repo)}
                            onDelete={() => {
                              setRepoToDelete(repo);
                              setDeleteDialogOpen(true);
                            }}
                            isOpen={false}
                            onOpenChange={() => {}}
                            showDelete={!!token} // Only show delete for logged-in users
                          />
                        </div>
                      </TableCell>
                    </TableRow>
                  ))
                ) : (
                  <TableRow>
                    <TableCell colSpan={6} className="h-24 text-center">
                      No repositories found.
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </div>
        )}
      </div>
      
      {/* Delete confirmation dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Repository?</AlertDialogTitle>
            <AlertDialogDescription>
              {repoToDelete && (
                <>
                  Are you sure you want to delete repository <span className="font-medium">{repoToDelete.name}</span>?
                  <span className="block mt-2 text-red-500">This action cannot be undone. All related data will be permanently deleted.</span>
                </>
              )}
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel className="cursor-pointer">Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleDeleteRepo} className="bg-red-500 hover:bg-red-600 cursor-pointer">
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* Toast notification component */}
      <Toaster />

      {/* Footer */}
      <Footer />
    </div>
  );
}