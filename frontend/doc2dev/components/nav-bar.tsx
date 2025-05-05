import Link from "next/link";
import SearchWithSuggestions from "./search-with-suggestions";

interface NavBarProps {
  showSearch?: boolean;
  alignment?: "center" | "left";
}

export function NavBar({ showSearch = true, alignment = "center" }: NavBarProps) {
  return (
    <div className={`flex flex-wrap items-center justify-between gap-4 ${alignment === "center" ? "max-w-4xl mx-auto" : "w-full"} mb-8`}>
      <div className="flex items-center gap-4">
        <Link href="/" className="flex items-center">
          <img src="/doc2dev.svg" alt="Doc2Dev Logo" className="h-6" />
        </Link>
        
        {showSearch && <SearchWithSuggestions />}
      </div>
    </div>
  );
}
