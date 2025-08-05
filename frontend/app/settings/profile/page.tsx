'use client'

import React from 'react';
import { Navbar } from '@/components/navbar';
import Footer from '@/components/footer';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { SettingsSidebar } from '@/components/ui/settings-sidebar';

export default function ProfilePage() {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <SettingsSidebar />
      <div className="ml-60 flex flex-col flex-1">
        <div className="container mx-auto px-4 py-8 max-w-5xl flex-1">
          <Navbar showSearch={false} alignment="left" />

          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Profile Settings</CardTitle>
                <CardDescription>
                  Manage your profile information and preferences.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-gray-500 py-8 text-center">
                  Profile settings coming soon...
                </div>
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