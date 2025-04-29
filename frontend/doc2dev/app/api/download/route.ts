import { NextRequest, NextResponse } from "next/server";

// 从 GitHub URL 中提取组织和仓库名称
function extractRepoInfo(url: string): { org: string; repo: string } | null {
  try {
    // 支持多种 GitHub URL 格式
    // https://github.com/org/repo
    // https://github.com/org/repo.git
    // git@github.com:org/repo.git
    let match;
    
    if (url.includes('github.com')) {
      // 处理 HTTPS URL
      match = url.match(/github\.com[\/:]([\w.-]+)\/([\w.-]+)(?:\.git)?$/);
    } else if (url.includes('git@github.com')) {
      // 处理 SSH URL
      match = url.match(/git@github\.com:([\w.-]+)\/([\w.-]+)(?:\.git)?$/);
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
    const { repo_url } = body;
    
    if (!repo_url) {
      return NextResponse.json(
        { status: "error", message: "Missing repository URL" },
        { status: 400 }
      );
    }
    
    // 从 URL 中提取组织和仓库名称
    const repoInfo = extractRepoInfo(repo_url);
    
    if (!repoInfo) {
      return NextResponse.json(
        { status: "error", message: "Invalid GitHub repository URL" },
        { status: 400 }
      );
    }
    
    // 生成向量表名称：org_repo
    const library_name = `${repoInfo.org}_${repoInfo.repo}`;
    
    // 调用后端 API
    const backendUrl = process.env.BACKEND_URL || "http://localhost:8000";
    const response = await fetch(`${backendUrl}/download/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        repo_url: repo_url,
        library_name: library_name,
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
