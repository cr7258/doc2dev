'use client'

import Link from "next/link";
import SearchBar from "./search";
import { useAuth } from "@/lib/auth";
import { GitHubLoginButton } from "./github-login";
import { GitHubAvatarDropdown } from '@/components/ui/dropdown';
import { LanguageSwitcher } from './language-switcher';
import { Button } from "@/components/ui/button";
import { Link2, Check } from "lucide-react";
import { useState } from "react";

interface NavbarProps {
  showSearch?: boolean;
  alignment?: "center" | "left";
}

export function Navbar({ showSearch = true, alignment = "center" }: NavbarProps) {
  const { user, logout, isLoading } = useAuth();
  const [copied, setCopied] = useState(false);

  const handleLogout = () => {
    logout();
  };

  const handleCopyMcpUrl = async () => {
    const mcpUrl = `${process.env.NEXT_PUBLIC_API_URL}/mcp/public`;
    try {
      await navigator.clipboard.writeText(mcpUrl);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy MCP URL:', err);
    }
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
          {/* MCP URL Copy Button - Only show for non-authenticated users */}
          {!user && !isLoading && (
            <Button
              variant="outline"
              onClick={handleCopyMcpUrl}
              className={`flex items-center gap-2 text-sm h-9 px-3 cursor-pointer transition-all duration-200 hover:shadow-md border-gray-200 hover:border-gray-300 focus:border-blue-500 bg-white shadow-sm ${
                copied
                  ? 'border-green-200 bg-green-50 text-green-700'
                  : 'hover:bg-blue-50'
              }`}
            >
              {copied ? (
                <>
                  <Check className="h-4 w-4 text-green-600" />
                  <span className="text-sm font-medium">Copied!</span>
                </>
              ) : (
                <>
                  <Link2 className="h-4 w-4 text-blue-600" />
                  <span className="text-sm font-medium">MCP URL</span>
                </>
              )}
            </Button>
          )}

          {/* Language switcher */}
          <LanguageSwitcher />

          {/* Authentication section */}
          {!isLoading && (
            <div className="flex items-center gap-2">
              {user ? (
                <GitHubAvatarDropdown
                  user={user}
                  onLogout={handleLogout}
                />
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
