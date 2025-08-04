import { NextRequest, NextResponse } from "next/server";

// 从 Git URL 中提取组织和仓库名称（支持 GitHub 和 GitLab）
function extractRepoInfo(url: string): { org: string; repo: string } | null {
  try {
    // 支持多种 Git URL 格式
    // GitHub: https://github.com/org/repo, git@github.com:org/repo.git
    // GitLab: https://gitlab.com/org/repo, git@gitlab.com:org/repo.git
    let match;

    if (url.includes('github.com')) {
      // 处理 GitHub HTTPS URL
      match = url.match(/github\.com[\/:]([\w.-]+)\/([\w.-]+)(?:\.git)?$/);
    } else if (url.includes('git@github.com')) {
      // 处理 GitHub SSH URL
      match = url.match(/git@github\.com:([\w.-]+)\/([\w.-]+)(?:\.git)?$/);
    } else if (url.includes('gitlab.com')) {
      // 处理 GitLab HTTPS URL
      match = url.match(/gitlab\.com[\/:]([\w.-]+)\/([\w.-]+)(?:\.git)?$/);
    } else if (url.includes('git@gitlab.com')) {
      // 处理 GitLab SSH URL
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

    // 从请求头中获取认证token
    const authorization = request.headers.get('authorization');

    if (!authorization) {
      return NextResponse.json(
        { status: "error", message: "Authentication required" },
        { status: 401 }
      );
    }

    // 从 URL 中提取组织和仓库名称
    const repoInfo = extractRepoInfo(repo_url);

    if (!repoInfo) {
      return NextResponse.json(
        { status: "error", message: "Invalid Git repository URL" },
        { status: 400 }
      );
    }

    // 生成向量表名称：org_repo
    const library_name = `${repoInfo.org}_${repoInfo.repo}`;

    // 获取客户端 ID（如果有）
    const client_id = body.client_id;

    // 调用后端 API
    const backendUrl = process.env.BACKEND_URL || "http://localhost:8000";
    const response = await fetch(`${backendUrl}/download/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": authorization, // 传递认证头
      },
      body: JSON.stringify({
        repo_url: repo_url,
        library_name: library_name,
        client_id: client_id, // 传递客户端 ID 用于 WebSocket 连接
        platform: platform, // 传递平台选择
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
