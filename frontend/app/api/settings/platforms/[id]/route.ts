import { NextRequest, NextResponse } from 'next/server';

export async function PUT(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const authHeader = request.headers.get('authorization');
    const body = await request.json();
    const { id } = await params;

    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    if (authHeader) {
      headers.authorization = authHeader;
    }

    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/settings/platforms/${id}`, {
      method: 'PUT',
      headers,
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      let errorMessage = 'Failed to update configuration';
      try {
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
          const errorData = await response.json();
          errorMessage = errorData.detail || errorData.message || errorMessage;
        } else {
          // Handle HTML error responses
          const errorText = await response.text();
          if (errorText.includes('<!DOCTYPE')) {
            errorMessage = `Server error (${response.status}). Please check the server logs.`;
          } else {
            errorMessage = errorText || errorMessage;
          }
        }
      } catch {
        errorMessage = `Server error (${response.status}). Please check the server logs.`;
      }
      
      return NextResponse.json(
        { error: errorMessage },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error updating configuration:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const authHeader = request.headers.get('authorization');
    const { id } = await params;

    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    if (authHeader) {
      headers.authorization = authHeader;
    }

    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/settings/platforms/${id}`, {
      method: 'DELETE',
      headers,
    });

    if (!response.ok) {
      let errorMessage = 'Failed to delete platform configuration';
      try {
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
          const errorData = await response.json();
          errorMessage = errorData.detail || errorData.message || errorMessage;
        } else {
          // Handle HTML error responses
          const errorText = await response.text();
          if (errorText.includes('<!DOCTYPE')) {
            errorMessage = `Server error (${response.status}). Please check the server logs.`;
          } else {
            errorMessage = errorText || errorMessage;
          }
        }
      } catch {
        errorMessage = `Server error (${response.status}). Please check the server logs.`;
      }
      
      return NextResponse.json(
        { error: errorMessage },
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
