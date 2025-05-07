import Link from "next/link";
import SearchBar from "./search";
import { Github } from "lucide-react";

interface NavbarProps {
  showSearch?: boolean;
  alignment?: "center" | "left";
}

export function Navbar({ showSearch = true, alignment = "center" }: NavbarProps) {
  return (
    <>
      <div className={`flex flex-wrap items-center justify-between gap-4 ${alignment === "center" ? "max-w-4xl mx-auto" : "w-full"} mb-4`}>
        <div className="flex items-center gap-4">
          <Link href="/" className="flex items-center">
            <img src="/doc2dev.svg" alt="Doc2Dev Logo" className="h-6" />
          </Link>
          
          {showSearch && <SearchBar />}
        </div>
        
        {/* GitHub 链接 */}
        <a 
          href="https://github.com/cr7258/doc2dev" 
          target="_blank" 
          rel="noopener noreferrer"
          className="flex items-center text-black hover:text-gray-700 transition-colors"
          aria-label="GitHub repository"
        >
          <img src="/github.svg" alt="GitHub" className="h-7 w-7" />
        </a>
      </div>
      {/* 分割线 */}
      <div className={`${alignment === "center" ? "max-w-4xl mx-auto" : "w-full"} border-b border-gray-300 mb-6`}></div>
    </>
  );
}
