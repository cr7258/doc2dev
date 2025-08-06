import { NextRequest, NextResponse } from "next/server";

// Extract organization and repository name from Git URL (supports GitHub, GitLab, and private Git servers)
function extractRepoInfo(url: string, platform?: string): { org: string; repo: string; platform: string } | null {
  try {
    // Support multiple Git URL formats
    // HTTPS: https://domain.com/org/repo, https://domain.com/org/repo.git
    // SSH: git@domain.com:org/repo.git, git@domain.com:org/repo
    let detectedPlatform = platform || 'unknown';

    // Normalize URL by removing trailing slashes and .git
    const normalizedUrl = url.replace(/\/+$/, '').replace(/\.git$/, '');

    // Try HTTPS format first: https://domain.com/org/repo
    const httpsMatch = normalizedUrl.match(/https?:\/\/([^\/]+)\/([^\/]+)\/([^\/]+)(?:\/.*)?$/);
    if (httpsMatch && httpsMatch.length >= 4) {
      const domain = httpsMatch[1];
      const org = httpsMatch[2];
      const repo = httpsMatch[3];

      // Auto-detect platform if not specified
      if (!platform) {
        if (domain.includes('github.com')) {
          detectedPlatform = 'github';
        } else if (domain.includes('gitlab.com') || domain.includes('gitlab')) {
          detectedPlatform = 'gitlab';
        } else {
          detectedPlatform = 'git'; // Generic Git server
        }
      }

      return {
        org: org,
        repo: repo,
        platform: detectedPlatform
      };
    }

    // Try SSH format: git@domain.com:org/repo
    const sshMatch = url.match(/git@([^:]+):([^\/]+)\/([^\/]+?)(?:\.git)?$/);
    if (sshMatch && sshMatch.length >= 4) {
      const domain = sshMatch[1];
      const org = sshMatch[2];
      const repo = sshMatch[3];

      // Auto-detect platform if not specified
      if (!platform) {
        if (domain.includes('github.com')) {
          detectedPlatform = 'github';
        } else if (domain.includes('gitlab.com') || domain.includes('gitlab')) {
          detectedPlatform = 'gitlab';
        } else {
          detectedPlatform = 'git'; // Generic Git server
        }
      }

      return {
        org: org,
        repo: repo,
        platform: detectedPlatform
      };
    }

    // Fallback: try to extract org/repo from any URL pattern
    const fallbackMatch = url.match(/([^\/\s]+)\/([^\/\s]+?)(?:\.git)?(?:\/.*)?$/);
    if (fallbackMatch && fallbackMatch.length >= 3) {
      return {
        org: fallbackMatch[1],
        repo: fallbackMatch[2],
        platform: detectedPlatform
      };
    }

    return null;
  } catch (error) {
    console.error('Error extracting repo info:', error);
    return null;
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { repo_url, platform } = body;

    if (!repo_url) {
      return NextResponse.json(
        { status: "error", message: "Missing repository URL" },
        { status: 400 }
      );
    }

    // Get authentication token from request headers (optional)
    const authorization = request.headers.get('authorization');

    // Extract organization and repository name from URL
    const repoInfo = extractRepoInfo(repo_url, platform);

    if (!repoInfo) {
      return NextResponse.json(
        { status: "error", message: "Invalid Git repository URL" },
        { status: 400 }
      );
    }

    // Generate vector table name: org_repo
    const library_name = `${repoInfo.org}_${repoInfo.repo}`;

    // Use detected platform if not provided
    const finalPlatform = platform || repoInfo.platform;

    // Get client ID (if available)
    const client_id = body.client_id;

    // Call backend API
    const backendUrl = process.env.NEXT_PUBLIC_API_URL;
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
    };

    // Only add authorization header if token exists
    if (authorization) {
      headers["Authorization"] = authorization;
    }

    const response = await fetch(`${backendUrl}/download/`, {
      method: "POST",
      headers,
      body: JSON.stringify({
        repo_url: repo_url,
        library_name: library_name,
        client_id: client_id, // Pass client ID for WebSocket connection
        platform: finalPlatform, // Pass platform selection (detected or provided)
      }),
    });
    
    const data = await response.json();
    
    return NextResponse.json(data);
  } catch (error) {
    console.error("Error downloading repository:", error);
    return NextResponse.json(
      { status: "error", message: "Error downloading repository" },
      { status: 500 }
    );
  }
}
