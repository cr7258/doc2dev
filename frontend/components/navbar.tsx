'use client'

import Link from "next/link";
import SearchBar from "./search";
import { Github, LogOut } from "lucide-react";
import { useAuth } from "@/lib/auth";
import { GitHubLoginButton } from "./github-login";
import { Button } from "./ui/button";

interface NavbarProps {
  showSearch?: boolean;
  alignment?: "center" | "left";
}

export function Navbar({ showSearch = true, alignment = "center" }: NavbarProps) {
  const { user, logout, isLoading } = useAuth();

  const handleLogout = () => {
    logout();
  };

  return (
    <>
      <div className={`flex flex-wrap items-center justify-between gap-4 ${alignment === "center" ? "max-w-4xl mx-auto" : "w-full"} mb-4`}>
        <div className="flex items-center gap-4">
          <Link href="/" className="flex items-center">
            <img src="/doc2dev.svg" alt="Doc2Dev Logo" className="h-6" />
          </Link>
          
          {showSearch && <SearchBar />}
        </div>
        
        <div className="flex items-center gap-4">
          {/* GitHub repository link */}
          <a 
            href="https://github.com/cr7258/doc2dev" 
            target="_blank" 
            rel="noopener noreferrer"
            className="flex items-center text-black hover:text-gray-700 transition-colors"
            aria-label="GitHub repository"
          >
            <img src="/github.svg" alt="GitHub" className="h-7 w-7" />
          </a>
          
          {/* Authentication section */}
          {!isLoading && (
            <div className="flex items-center gap-2">
              {user ? (
                <div className="flex items-center gap-3">
                  {/* User avatar and name */}
                  <div className="flex items-center gap-2">
                    {user.avatar_url && (
                      <img 
                        src={user.avatar_url} 
                        alt={user.username}
                        className="w-8 h-8 rounded-full"
                      />
                    )}
                    <span className="text-sm font-medium text-gray-700">
                      {user.username}
                    </span>
                  </div>
                  
                  {/* Logout button */}
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleLogout}
                    className="flex items-center gap-1"
                  >
                    <LogOut className="w-4 h-4" />
                    Logout
                  </Button>
                </div>
              ) : (
                <GitHubLoginButton />
              )}
            </div>
          )}
        </div>
      </div>
      {/* Divider */}
      <div className={`${alignment === "center" ? "max-w-4xl mx-auto" : "w-full"} border-b border-gray-300 mb-6`}></div>
    </>
  );
}
