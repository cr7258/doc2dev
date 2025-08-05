import { NextRequest, NextResponse } from "next/server";

// Extract organization and repository name from Git URL (supports GitHub and GitLab)
function extractRepoInfo(url: string): { org: string; repo: string } | null {
  try {
    // Support multiple Git URL formats
    // GitHub: https://github.com/org/repo, git@github.com:org/repo.git
    // GitLab: https://gitlab.com/org/repo, git@gitlab.com:org/repo.git
    let match;

    if (url.includes('github.com')) {
      // Handle GitHub HTTPS URL
      match = url.match(/github\.com[\/:]([\w.-]+)\/([\w.-]+)(?:\.git)?$/);
    } else if (url.includes('git@github.com')) {
      // Handle GitHub SSH URL
      match = url.match(/git@github\.com:([\w.-]+)\/([\w.-]+)(?:\.git)?$/);
    } else if (url.includes('gitlab.com')) {
      // Handle GitLab HTTPS URL
      match = url.match(/gitlab\.com[\/:]([\w.-]+)\/([\w.-]+)(?:\.git)?$/);
    } else if (url.includes('git@gitlab.com')) {
      // Handle GitLab SSH URL
      match = url.match(/git@gitlab\.com:([\w.-]+)\/([\w.-]+)(?:\.git)?$/);
    }

    if (match && match.length >= 3) {
      return {
        org: match[1],
        repo: match[2]
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

    // Get authentication token from request headers
    const authorization = request.headers.get('authorization');

    if (!authorization) {
      return NextResponse.json(
        { status: "error", message: "Authentication required" },
        { status: 401 }
      );
    }

    // Extract organization and repository name from URL
    const repoInfo = extractRepoInfo(repo_url);

    if (!repoInfo) {
      return NextResponse.json(
        { status: "error", message: "Invalid Git repository URL" },
        { status: 400 }
      );
    }

    // Generate vector table name: org_repo
    const library_name = `${repoInfo.org}_${repoInfo.repo}`;

    // Get client ID (if available)
    const client_id = body.client_id;

    // Call backend API
    const backendUrl = process.env.BACKEND_URL || "http://localhost:8000";
    const response = await fetch(`${backendUrl}/download/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": authorization, // Pass authentication header
      },
      body: JSON.stringify({
        repo_url: repo_url,
        library_name: library_name,
        client_id: client_id, // Pass client ID for WebSocket connection
        platform: platform, // Pass platform selection
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
