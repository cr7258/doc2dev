'use client'

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useAuth } from '@/lib/auth';
import { Navbar } from '@/components/navbar';
import Footer from '@/components/footer';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useToast, Toaster } from '@/components/ui/toast';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Github, Gitlab, Plus, Trash2, Eye, EyeOff, Save, RefreshCw, Edit } from 'lucide-react';
import { SettingsSidebar } from '@/components/ui/settings-sidebar';

interface PlatformConfig {
  id?: string;
  name: string;
  platform: 'github' | 'gitlab';
  base_url: string;
  token: string;
  is_default?: boolean;
}

export default function SettingsPage() {
  const { token: authToken } = useAuth();
  const { toast } = useToast();
  const [configs, setConfigs] = useState<PlatformConfig[]>([]);
  const [savedConfigs, setSavedConfigs] = useState<PlatformConfig[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [showTokens, setShowTokens] = useState<{[key: string]: boolean}>({});
  const [showAddForm, setShowAddForm] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [configToDelete, setConfigToDelete] = useState<PlatformConfig | null>(null);
  const [editingConfig, setEditingConfig] = useState<string | null>(null);
  const [editingValues, setEditingValues] = useState<Partial<PlatformConfig>>({});
  const [showEditingToken, setShowEditingToken] = useState<{[key: string]: boolean}>({});

  // Load existing configurations when authToken is available
  useEffect(() => {
    if (authToken) {
      loadConfigurations();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [authToken]);

  const loadConfigurations = async () => {
    try {
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
      };

      if (authToken) {
        headers.authorization = `Bearer ${authToken}`;
      }

      const response = await fetch('/api/settings', {
        headers,
      });

      if (response.ok) {
        const data = await response.json();
        const platforms = data.platforms || [];
        // Only set savedConfigs for display, don't set configs (which is for editing)
        setSavedConfigs(platforms);
      } else {
        console.error('Failed to load configurations');
      }
    } catch (error) {
      console.error('Error loading configurations:', error);
      toast({
        title: "Error",
        description: "Failed to load platform configurations",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const addNewConfig = (platform: 'github' | 'gitlab') => {
    const newConfig: PlatformConfig = {
      name: '',
      platform,
      base_url: '',
      token: '',
    };
    setConfigs([...configs, newConfig]);
    setShowAddForm(true);
  };

  const updateConfig = (index: number, field: keyof PlatformConfig, value: string | boolean) => {
    const updatedConfigs = [...configs];
    updatedConfigs[index] = { ...updatedConfigs[index], [field]: value };
    setConfigs(updatedConfigs);
  };

  const removeConfig = (index: number) => {
    const updatedConfigs = configs.filter((_, i) => i !== index);
    setConfigs(updatedConfigs);
    // If no configs left, hide the form
    if (updatedConfigs.length === 0) {
      setShowAddForm(false);
    }
  };

  const toggleTokenVisibility = (index: number) => {
    setShowTokens(prev => ({
      ...prev,
      [index]: !prev[index]
    }));
  };

  const saveConfigurations = async () => {
    setSaving(true);
    try {
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
      };

      if (authToken) {
        headers.authorization = `Bearer ${authToken}`;
      }

      // Validate configurations before saving
      for (const config of configs) {
        // Check for duplicate name
        const duplicateName = savedConfigs.find(saved =>
          saved.name.toLowerCase() === config.name.toLowerCase()
        );
        if (duplicateName) {
          toast({
            title: "Duplicate Configuration Name",
            description: `The name "${config.name}" is already used. Please choose a different name.`,
            variant: "destructive"
          });
          return;
        }

        // Check for duplicate base URL
        const duplicateUrl = savedConfigs.find(saved =>
          saved.base_url.toLowerCase() === config.base_url.toLowerCase()
        );
        if (duplicateUrl) {
          toast({
            title: "Duplicate Base URL",
            description: `The base URL "${config.base_url}" is already configured. Please use a different URL.`,
            variant: "destructive"
          });
          return;
        }
      }

      // Save each configuration individually
      for (const config of configs) {
        const response = await fetch('/api/settings?action=platform', {
          method: 'POST',
          headers,
          body: JSON.stringify(config),
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || 'Failed to save configuration');
        }
      }

      // All configurations saved successfully
      toast({
        title: "Success",
        description: "Platform configurations saved successfully",
        variant: "success",
      });
      await loadConfigurations(); // Reload to get IDs
      setConfigs([]); // Clear the form
      setShowAddForm(false); // Hide the form
    } catch (error) {
      console.error('Error saving configurations:', error);
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to save configurations",
        variant: "destructive",
      });
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteConfig = async () => {
    if (!configToDelete?.id) return;

    try {
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
      };

      if (authToken) {
        headers.authorization = `Bearer ${authToken}`;
      }

      const response = await fetch(`/api/settings?id=${configToDelete.id}`, {
        method: 'DELETE',
        headers,
      });

      if (response.ok) {
        toast({
          title: "Success",
          description: "Configuration deleted successfully",
          variant: "success",
        });
        // Reload configurations
        await loadConfigurations();
      } else {
        let errorMessage = "Failed to delete configuration";
        try {
          const errorData = await response.json();
          errorMessage = errorData.error || errorData.detail || errorMessage;
        } catch (e) {
          console.error('Error parsing error response:', e);
        }
        toast({
          title: "Error",
          description: errorMessage,
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error('Error deleting configuration:', error);
      toast({
        title: "Error",
        description: "Failed to delete configuration",
        variant: "destructive",
      });
    } finally {
      setDeleteDialogOpen(false);
      setConfigToDelete(null);
    }
  };


  const startInlineEdit = (config: PlatformConfig) => {
    setEditingConfig(config.id || '');
    setEditingValues({
      name: config.name,
      base_url: config.base_url,
      token: config.token
    });
  };

  const cancelInlineEdit = () => {
    setEditingConfig(null);
    setEditingValues({});
    // Reset token visibility for editing
    setShowEditingToken({});
  };

  const saveInlineEdit = async (configId: string) => {
    if (!authToken || !editingValues.name || !editingValues.base_url || !editingValues.token) {
      toast({
        title: "Validation Error",
        description: "Please fill in all required fields",
        variant: "destructive"
      });
      return;
    }

    // Find the original config to get platform info
    const originalConfig = savedConfigs.find(c => c.id === configId);
    if (!originalConfig) {
      toast({
        title: "Error",
        description: "Configuration not found",
        variant: "destructive"
      });
      return;
    }

    // Validate for duplicates (excluding current config)
    const duplicateName = savedConfigs.find(saved =>
      saved.id !== configId && saved.name.toLowerCase() === editingValues.name!.toLowerCase()
    );
    if (duplicateName) {
      toast({
        title: "Duplicate Configuration Name",
        description: `The name "${editingValues.name}" is already used. Please choose a different name.`,
        variant: "destructive"
      });
      return;
    }

    const duplicateUrl = savedConfigs.find(saved =>
      saved.id !== configId && saved.base_url.toLowerCase() === editingValues.base_url!.toLowerCase()
    );
    if (duplicateUrl) {
      toast({
        title: "Duplicate Base URL",
        description: `The base URL "${editingValues.base_url}" is already configured. Please use a different URL.`,
        variant: "destructive"
      });
      return;
    }

    try {
      setSaving(true);

      const updateData = {
        name: editingValues.name,
        platform: originalConfig.platform,
        base_url: editingValues.base_url,
        token: editingValues.token,
        is_default: originalConfig.is_default
      };

      const response = await fetch(`/api/settings/platforms/${configId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${authToken}`
        },
        body: JSON.stringify(updateData)
      });

      if (!response.ok) {
        let errorMessage = 'Failed to update configuration';
        try {
          const contentType = response.headers.get('content-type');
          if (contentType && contentType.includes('application/json')) {
            const errorData = await response.json();
            errorMessage = errorData.detail || errorMessage;
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
        throw new Error(errorMessage);
      }

      toast({
        title: "Success",
        description: "Configuration updated successfully",
        variant: "success",
      });

      // Reload configurations to get updated data
      await loadConfigurations();

      // Exit edit mode
      setEditingConfig(null);
      setEditingValues({});
      setShowEditingToken({});

    } catch (error) {
      console.error('Error updating configuration:', error);
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to update configuration",
        variant: "destructive",
      });
    } finally {
      setSaving(false);
    }
  };


  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white flex flex-col">
        <SettingsSidebar />
        <div className="ml-60 flex flex-col flex-1">
          <div className="container mx-auto px-4 py-8 max-w-5xl flex-1">
            <Navbar showSearch={false} alignment="left" />
            <div className="flex items-center justify-center h-64">
              <RefreshCw className="h-8 w-8 animate-spin text-gray-400" />
            </div>
          </div>
          
          {/* Footer */}
          <Footer />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white flex flex-col">
      <SettingsSidebar />
      <div className="ml-60 flex flex-col flex-1">
        <div className="container mx-auto px-4 py-8 max-w-5xl flex-1">
          <Navbar showSearch={false} alignment="left" />

          <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                Add Git Credentials
              </CardTitle>
              <CardDescription>
                Add and manage multiple GitHub and GitLab credentials. You can configure different tokens and URLs for various Git instances.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Add buttons - always visible */}
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  onClick={() => addNewConfig('github')}
                  className="cursor-pointer"
                >
                  <Plus className="h-4 w-4 mr-0.2" />
                  <Github className="h-4 w-4 mr-0.2" />
                  Add GitHub
                </Button>
                <Button
                  variant="outline"
                  onClick={() => addNewConfig('gitlab')}
                  className="cursor-pointer"
                >
                  <Plus className="h-4 w-4 mr-0.2" />
                  <Gitlab className="h-4 w-4 mr-0.2 text-orange-500" />
                  Add GitLab
                </Button>
              </div>

              {/* Configuration forms - only show when adding/editing */}
              {showAddForm && configs.map((config, index) => (
                <div key={index} className="border rounded-lg p-4 space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      {config.platform === 'github' ? (
                        <Github className="h-5 w-5" />
                      ) : (
                        <Gitlab className="h-5 w-5 text-orange-500" />
                      )}
                      <span className="font-medium capitalize">{config.platform}</span>
                      {config.is_default && (
                        <Badge variant="secondary">Default</Badge>
                      )}
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => removeConfig(index)}
                      className="text-red-600 hover:text-red-700 hover:bg-red-50 cursor-pointer"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor={`name-${index}`}>Name</Label>
                      <Input
                        id={`name-${index}`}
                        value={config.name}
                        onChange={(e) => updateConfig(index, 'name', e.target.value)}
                        placeholder="Enter a descriptive name"
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor={`url-${index}`}>Base URL</Label>
                      <Input
                        id={`url-${index}`}
                        value={config.base_url}
                        onChange={(e) => updateConfig(index, 'base_url', e.target.value)}
                        placeholder="Enter the base URL"
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor={`token-${index}`}>Access Token</Label>
                    <div className="relative">
                      <Input
                        id={`token-${index}`}
                        type={showTokens[index] ? 'text' : 'password'}
                        value={config.token}
                        onChange={(e) => updateConfig(index, 'token', e.target.value)}
                        placeholder="Enter your access token"
                        className="pr-10"
                      />
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        className="absolute right-0 top-0 h-full px-3 cursor-pointer"
                        onClick={() => toggleTokenVisibility(index)}
                      >
                        {showTokens[index] ? (
                          <EyeOff className="h-4 w-4" />
                        ) : (
                          <Eye className="h-4 w-4" />
                        )}
                      </Button>
                    </div>
                  </div>


                </div>
              ))}

              {/* Save button - only show when form is visible and has configs */}
              {showAddForm && configs.length > 0 && (
                <div className="flex justify-end pt-4 border-t">
                  <Button
                    onClick={saveConfigurations}
                    disabled={saving}
                    className="cursor-pointer"
                  >
                    {saving ? (
                      <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                    ) : (
                      <Save className="h-4 w-4 mr-2" />
                    )}
                    {saving ? 'Saving...' : 'Save Configurations'}
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Saved Configurations Table - Always visible */}
          <Card className="mt-6">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                Saved Git Credentials
              </CardTitle>
              <CardDescription>
                Manage your existing Git Credentials
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="rounded-md border bg-white overflow-hidden">
                <Table>
                  <TableHeader className="bg-blue-50">
                    <TableRow>
                      <TableHead className="w-[120px] font-medium">Platform</TableHead>
                      <TableHead className="w-[150px] font-medium">Name</TableHead>
                      <TableHead className="w-[250px] font-medium">Base URL</TableHead>
                      <TableHead className="w-[200px] font-medium text-left">Token</TableHead>
                      <TableHead className="w-[100px] text-center font-medium">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {savedConfigs.length > 0 ? (
                      savedConfigs.map((config) => {
                        const isEditing = editingConfig === config.id;
                        return (
                          <TableRow key={config.id}>
                            <TableCell>
                              <div className="flex items-center gap-2">
                                {config.platform === 'github' ? (
                                  <Github className="h-4 w-4" />
                                ) : (
                                  <Gitlab className="h-4 w-4 text-orange-500" />
                                )}
                                <span className="capitalize">{config.platform}</span>
                              </div>
                            </TableCell>
                            <TableCell className="font-medium">
                              {isEditing ? (
                                <Input
                                  value={editingValues.name || ''}
                                  onChange={(e) => setEditingValues(prev => ({ ...prev, name: e.target.value }))}
                                  className="h-8 text-sm"
                                  placeholder="Configuration name"
                                />
                              ) : (
                                <>
                                  {config.name}
                                  {config.is_default && (
                                    <Badge variant="secondary" className="ml-2 text-xs">
                                      Default
                                    </Badge>
                                  )}
                                </>
                              )}
                            </TableCell>
                            <TableCell>
                              {isEditing ? (
                                <Input
                                  value={editingValues.base_url || ''}
                                  onChange={(e) => setEditingValues(prev => ({ ...prev, base_url: e.target.value }))}
                                  className="h-8 text-sm"
                                  placeholder="https://github.com"
                                />
                              ) : (
                                <span className="text-sm text-gray-600">{config.base_url}</span>
                              )}
                            </TableCell>
                            <TableCell className="text-left">
                              {isEditing ? (
                                <div className="relative">
                                  <Input
                                    type={showEditingToken[config.id!] ? "text" : "password"}
                                    value={editingValues.token || ''}
                                    onChange={(e) => setEditingValues(prev => ({ ...prev, token: e.target.value }))}
                                    className="h-8 text-sm pr-8"
                                    placeholder="Access token"
                                  />
                                  <Button
                                    type="button"
                                    variant="ghost"
                                    size="sm"
                                    className="absolute right-0 top-0 h-8 w-8 p-0 cursor-pointer"
                                    onClick={() => setShowEditingToken(prev => ({
                                      ...prev,
                                      [config.id!]: !prev[config.id!]
                                    }))}
                                  >
                                    {showEditingToken[config.id!] ? (
                                      <EyeOff className="h-3 w-3" />
                                    ) : (
                                      <Eye className="h-3 w-3" />
                                    )}
                                  </Button>
                                </div>
                              ) : (
                                <div className="flex items-center gap-2">
                                  <span className="text-sm text-gray-400 font-mono">
                                    {showTokens[config.id!] ? config.token : '*'.repeat(8)}
                                  </span>
                                  <Button
                                    type="button"
                                    variant="ghost"
                                    size="sm"
                                    className="h-6 w-6 p-0 cursor-pointer"
                                    onClick={() => setShowTokens(prev => ({
                                      ...prev,
                                      [config.id!]: !prev[config.id!]
                                    }))}
                                  >
                                    {showTokens[config.id!] ? (
                                      <EyeOff className="h-3 w-3" />
                                    ) : (
                                      <Eye className="h-3 w-3" />
                                    )}
                                  </Button>
                                </div>
                              )}
                            </TableCell>
                            <TableCell className="text-center">
                              <div className="flex justify-center gap-1">
                                {isEditing ? (
                                  <>
                                    <Button
                                      variant="ghost"
                                      size="sm"
                                      onClick={() => saveInlineEdit(config.id!)}
                                      disabled={saving}
                                      className="h-8 w-8 p-0 cursor-pointer text-green-600 hover:text-green-700 hover:bg-green-50"
                                      title="Save changes"
                                    >
                                      <Save className="h-4 w-4" />
                                    </Button>
                                    <Button
                                      variant="ghost"
                                      size="sm"
                                      onClick={cancelInlineEdit}
                                      disabled={saving}
                                      className="h-8 w-8 p-0 cursor-pointer text-gray-600 hover:text-gray-700 hover:bg-gray-50"
                                      title="Cancel editing"
                                    >
                                      ✕
                                    </Button>
                                  </>
                                ) : (
                                  <>
                                    <Button
                                      variant="ghost"
                                      size="sm"
                                      onClick={() => startInlineEdit(config)}
                                      className="h-8 w-8 p-0 cursor-pointer"
                                      title="Edit configuration"
                                    >
                                      <Edit className="h-4 w-4" />
                                    </Button>
                                    <Button
                                      variant="ghost"
                                      size="sm"
                                      onClick={() => {
                                        setConfigToDelete(config);
                                        setDeleteDialogOpen(true);
                                      }}
                                      className="h-8 w-8 p-0 cursor-pointer text-red-600 hover:text-red-700 hover:bg-red-50"
                                      title="Delete configuration"
                                    >
                                      <Trash2 className="h-4 w-4" />
                                    </Button>
                                  </>
                                )}
                              </div>
                            </TableCell>
                          </TableRow>
                        );
                      })
                    ) : (
                      <TableRow>
                        <TableCell colSpan={5} className="text-center py-8 text-gray-500">
                          No configurations saved yet. Click &quot;Add GitHub&quot; or &quot;Add GitLab&quot; to get started.
                        </TableCell>
                      </TableRow>
                    )}
                  </TableBody>
                </Table>
              </div>
            </CardContent>
          </Card>
          </div>

          {/* Back to homepage button */}
          <div className="flex justify-center mt-8 mb-4">
            <Button variant="outline" asChild>
              <Link href="/" className="inline-flex items-center">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M9.707 16.707a1 1 0 01-1.414 0l-6-6a1 1 0 010-1.414l6-6a1 1 0 011.414 1.414L5.414 9H17a1 1 0 110 2H5.414l4.293 4.293a1 1 0 010 1.414z" clipRule="evenodd" />
                </svg>
                Back to Homepage
              </Link>
            </Button>
          </div>
        </div>
        
        {/* Footer */}
        <Footer />
      </div>

      {/* Delete confirmation dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Git Credentials?</AlertDialogTitle>
            <AlertDialogDescription>
              {configToDelete && (
                <>
                  Are you sure you want to delete credentials <span className="font-medium">{configToDelete.name}</span> ({configToDelete.platform})?
                  <span className="block mt-2 text-red-500">This action cannot be undone. The credentials will no longer be usable after deletion.</span>
                </>
              )}
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel className="cursor-pointer">Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleDeleteConfig} className="bg-red-500 hover:bg-red-600 cursor-pointer">
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* Toast notification component */}
      <Toaster />
    </div>
  );
}
