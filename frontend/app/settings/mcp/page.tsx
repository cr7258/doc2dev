'use client'

import React, { useState } from 'react';
import { Navbar } from '@/components/navbar';
import Footer from '@/components/footer';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { SettingsSidebar } from '@/components/ui/settings-sidebar';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Copy, Check, ExternalLink, Hammer, CheckCircle, XCircle, ChevronDown, ChevronRight } from 'lucide-react';
import { useAuth } from '@/lib/auth';

export default function MCPPage() {
  const { user } = useAuth();
  const [copied, setCopied] = useState(false);
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<'success' | 'error' | null>(null);
  const [expandedTools, setExpandedTools] = useState<Record<string, boolean>>({});
  const [copiedConfig, setCopiedConfig] = useState<string | null>(null);

  const mcpUrl = user ? `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/mcp/${user.id}` : '';

  const handleCopyUrl = async () => {
    await navigator.clipboard.writeText(mcpUrl);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleTestConnection = async () => {
    if (!mcpUrl) return;

    setTesting(true);
    setTestResult(null);

    try {
      const response = await fetch(mcpUrl);
      if (response.ok) {
        setTestResult('success');
      } else {
        setTestResult('error');
      }
    } catch (error) {
      setTestResult('error');
    } finally {
      setTesting(false);
      setTimeout(() => setTestResult(null), 3000);
    }
  };

  const toggleToolExpansion = (toolName: string) => {
    setExpandedTools(prev => ({
      ...prev,
      [toolName]: !prev[toolName]
    }));
  };

  const handleCopyConfig = async (configType: 'cursor' | 'windsurf') => {
    if (!mcpUrl) return;

    let config: string;

    if (configType === 'cursor') {
      config = JSON.stringify({
        "mcpServers": {
          "doc2dev": {
            "url": mcpUrl
          }
        }
      }, null, 2);
    } else {
      config = JSON.stringify({
        "mcpServers": {
          "doc2dev": {
            "serverUrl": mcpUrl
          }
        }
      }, null, 2);
    }

    await navigator.clipboard.writeText(config);
    setCopiedConfig(configType);
    setTimeout(() => setCopiedConfig(null), 2000);
  };

  const configExample = `{
  "mcpServers": {
    "doc2dev": {
      "url": "${mcpUrl}"
    }
  }
}`;

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <SettingsSidebar />
      <div className="ml-60 flex flex-col flex-1">
        <div className="container mx-auto px-4 py-8 max-w-5xl flex-1">
          <Navbar showSearch={false} alignment="left" />

          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-lg">
                  MCP Server
                  <Badge variant="secondary">Streamable HTTP</Badge>
                  {testResult === 'success' && (
                    <Badge variant="outline" className="text-green-600 border-green-600">
                      <CheckCircle className="h-3 w-3 mr-1" />
                      Online
                    </Badge>
                  )}
                </CardTitle>
                <CardDescription>
                  Access your document libraries in AI tools through Model Context Protocol.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {user ? (
                  <>
                    <div className="space-y-2">
                      <Label htmlFor="mcp-url" className="text-base font-semibold">Your MCP URL</Label>
                      <div className="flex gap-2">
                        <Input
                          id="mcp-url"
                          value={mcpUrl}
                          readOnly
                          className="font-mono text-sm"
                        />
                        <Button
                          variant="outline"
                          size="icon"
                          onClick={handleCopyUrl}
                          className="cursor-pointer"
                        >
                          {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
                        </Button>
                        <Button
                          variant="outline"
                          size="icon"
                          onClick={handleTestConnection}
                          disabled={testing}
                          className="cursor-pointer"
                        >
                          {testing ? (
                            <Hammer className="h-4 w-4 animate-pulse" />
                          ) : testResult === 'success' ? (
                            <CheckCircle className="h-4 w-4 text-green-600" />
                          ) : testResult === 'error' ? (
                            <XCircle className="h-4 w-4 text-red-600" />
                          ) : (
                            <Hammer className="h-4 w-4" />
                          )}
                        </Button>
                      </div>
                      <p className="text-sm text-muted-foreground">
                        This is your personal MCP server URL that can be used in MCP-compatible AI tools.
                        {testResult === 'success' && (
                          <span className="text-green-600 ml-2">✓ Connection test successful</span>
                        )}
                        {testResult === 'error' && (
                          <span className="text-red-600 ml-2">✗ Connection test failed</span>
                        )}
                      </p>
                    </div>

                    <div className="space-y-2">
                      <Label className="text-base font-semibold">Integration Configuration Example</Label>
                      <div className="relative">
                        <pre className="bg-muted p-4 rounded-lg text-sm overflow-x-auto">
                          <code>{configExample}</code>
                        </pre>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="absolute top-2 right-2 cursor-pointer"
                          onClick={() => navigator.clipboard.writeText(configExample)}
                        >
                          <Copy className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </>
                ) : (
                  <div className="text-center py-8">
                    <p className="text-muted-foreground">Please sign in to get your MCP URL</p>
                  </div>
                )}

                {user && (
                  <>
                    <div className="space-y-3">
                      <Label className="text-base font-semibold">Installation</Label>
                      <p className="text-sm text-muted-foreground">Click to copy config</p>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        <div
                          className="flex items-center gap-2 p-3 border rounded-lg cursor-pointer hover:bg-muted/50 transition-colors"
                          onClick={() => handleCopyConfig('cursor')}
                        >
                          <div className="w-8 h-8 bg-black rounded flex items-center justify-center">
                            <img
                              src="/logo/cursor.svg"
                              alt="Cursor"
                              className="w-5 h-5"
                            />
                          </div>
                          <div className="flex-1">
                            <div className="font-medium">Cursor</div>
                          </div>
                          {copiedConfig === 'cursor' && (
                            <Check className="h-4 w-4 text-green-600" />
                          )}
                        </div>

                        <div
                          className="flex items-center gap-2 p-3 border rounded-lg cursor-pointer hover:bg-muted/50 transition-colors"
                          onClick={() => handleCopyConfig('windsurf')}
                        >
                          <div className="w-8 h-8 rounded flex items-center justify-center" style={{backgroundColor: '#F7F0E4'}}>
                            <img
                              src="/logo/windsurf.svg"
                              alt="Windsurf"
                              className="w-5 h-5"
                            />
                          </div>
                          <div className="flex-1">
                            <div className="font-medium">Windsurf</div>
                          </div>
                          {copiedConfig === 'windsurf' && (
                            <Check className="h-4 w-4 text-green-600" />
                          )}
                        </div>
                      </div>
                    </div>

                    <div className="space-y-2">
                      <Label className="text-base font-semibold">Available Tools</Label>
                      <div className="space-y-3">
                        <div className="p-3 bg-muted/50 rounded-lg">
                          <div
                            className="flex items-center gap-2 mb-2 cursor-pointer"
                            onClick={() => toggleToolExpansion('search-library-id')}
                          >
                            <Badge variant="outline">search-library-id</Badge>
                            <span className="text-sm font-medium">Search library IDs</span>
                            <div className="ml-auto">
                              {expandedTools['search-library-id'] ? (
                                <ChevronDown className="h-4 w-4 text-muted-foreground" />
                              ) : (
                                <ChevronRight className="h-4 w-4 text-muted-foreground" />
                              )}
                            </div>
                          </div>
                          {expandedTools['search-library-id'] && (
                            <div className="space-y-2">
                              <p className="text-xs text-muted-foreground">
                                Search for library IDs by name within your accessible repositories
                              </p>
                              <div className="text-xs">
                                <span className="font-medium">Parameters:</span>
                                <ul className="ml-4 mt-1 space-y-1">
                                  <li>• <code className="bg-muted px-1 rounded">libraryName</code> (string) - Name of the library to search for</li>
                                </ul>
                              </div>
                            </div>
                          )}
                        </div>

                        <div className="p-3 bg-muted/50 rounded-lg">
                          <div
                            className="flex items-center gap-2 mb-2 cursor-pointer"
                            onClick={() => toggleToolExpansion('get-library-docs')}
                          >
                            <Badge variant="outline">get-library-docs</Badge>
                            <span className="text-sm font-medium">Get library documentation</span>
                            <div className="ml-auto">
                              {expandedTools['get-library-docs'] ? (
                                <ChevronDown className="h-4 w-4 text-muted-foreground" />
                              ) : (
                                <ChevronRight className="h-4 w-4 text-muted-foreground" />
                              )}
                            </div>
                          </div>
                          {expandedTools['get-library-docs'] && (
                            <div className="space-y-2">
                              <p className="text-xs text-muted-foreground">
                                Get documentation for a specific library accessible to the user
                              </p>
                              <div className="text-xs">
                                <span className="font-medium">Parameters:</span>
                                <ul className="ml-4 mt-1 space-y-1">
                                  <li>• <code className="bg-muted px-1 rounded">libraryID</code> (string) - Table name in the vector database</li>
                                  <li>• <code className="bg-muted px-1 rounded">question</code> (string) - Question to ask about the library</li>
                                </ul>
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </>
                )}
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Footer */}
        <Footer />
      </div>
    </div>
  );
}