import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { table_name, query, k = 5, summarize = true } = body;
    
    if (!table_name || !query) {
      return NextResponse.json(
        { status: "error", message: "Missing required parameters" },
        { status: 400 }
      );
    }
    
    // 调用后端 API
    const backendUrl = process.env.BACKEND_URL || "http://localhost:8000";
    const response = await fetch(`${backendUrl}/query/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        table_name: table_name,
        query: query,
        k: k,
        summarize: summarize,
      }),
    });
    
    const data = await response.json();
    
    return NextResponse.json(data);
  } catch (error) {
    console.error("Error querying vector database:", error);
    return NextResponse.json(
      { status: "error", message: "Error querying vector database" },
      { status: 500 }
    );
  }
}
