import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  try {
    const authHeader = request.headers.get('authorization');
    const { searchParams } = new URL(request.url);
    const action = searchParams.get('action');

    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    if (authHeader) {
      headers.authorization = authHeader;
    }

    // Determine endpoint based on action parameter
    let endpoint = 'http://localhost:8000/settings/platforms';
    if (action === 'platform') {
      endpoint = 'http://localhost:8000/settings/platform';
    }

    const response = await fetch(endpoint, {
      method: 'GET',
      headers,
    });

    if (!response.ok) {
      const errorData = await response.json();
      return NextResponse.json(
        { error: errorData.message || errorData.detail || 'Failed to fetch configurations' },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error fetching configurations:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const authHeader = request.headers.get('authorization');
    const body = await request.json();
    const { searchParams } = new URL(request.url);
    const action = searchParams.get('action');

    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    if (authHeader) {
      headers.authorization = authHeader;
    }

    // Determine endpoint based on action parameter
    let endpoint = 'http://localhost:8000/settings/platforms';
    if (action === 'platform') {
      endpoint = 'http://localhost:8000/settings/platform';
    }

    const response = await fetch(endpoint, {
      method: 'POST',
      headers,
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const errorData = await response.json();
      return NextResponse.json(
        { error: errorData.detail || errorData.message || 'Failed to save configuration' },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error saving configuration:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}


export async function DELETE(request: NextRequest) {
  try {
    const authHeader = request.headers.get('authorization');
    const { searchParams } = new URL(request.url);

    // Get ID from query parameter
    const id = searchParams.get('id');

    if (!id) {
      return NextResponse.json(
        { error: 'Platform ID is required' },
        { status: 400 }
      );
    }

    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    if (authHeader) {
      headers.authorization = authHeader;
    }

    const response = await fetch(`http://localhost:8000/settings/platforms/${id}`, {
      method: 'DELETE',
      headers,
    });

    if (!response.ok) {
      const errorData = await response.json();
      return NextResponse.json(
        { error: errorData.detail || 'Failed to delete platform configuration' },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error deleting platform configuration:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}