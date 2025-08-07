'use client'

import Link from "next/link";
import SearchBar from "./search";
import { useAuth } from "@/lib/auth";
import { GitHubLoginButton } from "./github-login";
import { GitHubAvatarDropdown } from '@/components/ui/dropdown';
import { LanguageSwitcher } from './language-switcher';

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
