'use client'

import React, { useState } from 'react';
import { Navbar } from '@/components/navbar';
import Footer from '@/components/footer';
import { SettingsSidebar } from '@/components/ui/settings-sidebar';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Camera } from 'lucide-react';
import { useAuth } from '@/lib/auth';

export default function ProfilePage() {
  const { user } = useAuth();
  const [displayName, setDisplayName] = useState('Se7en');
  const [username, setUsername] = useState('cr7258');
  const [useCustomUsername, setUseCustomUsername] = useState(true);
  const [bio, setBio] = useState('');
  const [website, setWebsite] = useState('');
  const [githubUrl, setGithubUrl] = useState('');
  const [twitterUrl, setTwitterUrl] = useState('');

  const bioCharacterLimit = 180;
  const remainingChars = bioCharacterLimit - bio.length;

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white flex flex-col">
      <SettingsSidebar />
      <div className="ml-60 flex flex-col flex-1">
        <div className="container mx-auto px-4 py-8 max-w-3xl flex-1">
          <Navbar showSearch={false} alignment="left" />

          <div className="space-y-8">
            {/* Header */}
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Profile</h1>
              <p className="text-gray-600 mt-1">Manage how others see you on the platform</p>
            </div>

            {/* Basic Information */}
            <div className="space-y-6">
              <div>
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Basic information</h2>

                {/* Avatar Section */}
                <div className="flex items-start gap-4 mb-6">
                  <Avatar className="w-16 h-16">
                    <AvatarImage src={user?.avatar_url} alt={user?.username || 'User'} />
                    <AvatarFallback className="text-lg">
                      {user?.username?.charAt(0) || 'U'}
                    </AvatarFallback>
                  </Avatar>

                  <div className="flex-1">
                    <Button variant="outline" className="mb-2">
                      <Camera className="w-4 h-4 mr-2" />
                      Change Avatar
                    </Button>
                    <p className="text-sm text-gray-500">Or drag and drop an image anywhere on the page</p>
                  </div>
                </div>

                {/* Display Name */}
                <div className="space-y-2 mb-4">
                  <Label htmlFor="displayName" className="text-sm font-medium">Display Name</Label>
                  <Input
                    id="displayName"
                    value={displayName}
                    onChange={(e) => setDisplayName(e.target.value)}
                    className="w-full"
                  />
                </div>

                {/* Username */}
                <div className="space-y-2 mb-4">
                  <Label htmlFor="username" className="text-sm font-medium">Username</Label>
                  <Input
                    id="username"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    className="w-full"
                  />
                </div>

                {/* Use Custom Username Checkbox */}
                <div className="flex items-center space-x-2 mb-6">
                  <input
                    type="checkbox"
                    id="useCustomUsername"
                    checked={useCustomUsername}
                    onChange={(e) => setUseCustomUsername(e.target.checked)}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <Label htmlFor="useCustomUsername" className="text-sm">Use custom username</Label>
                </div>

                {/* Bio */}
                <div className="space-y-2">
                  <Label htmlFor="bio" className="text-sm font-medium">Bio</Label>
                  <textarea
                    id="bio"
                    placeholder="Tell us about yourself"
                    value={bio}
                    onChange={(e) => setBio(e.target.value)}
                    maxLength={bioCharacterLimit}
                    className="w-full min-h-[100px] resize-none flex rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                  />
                  <p className="text-sm text-gray-500">{remainingChars} characters remaining</p>
                </div>
              </div>
            </div>

            {/* Social Links */}
            <div className="space-y-6">
              <h2 className="text-lg font-semibold text-gray-900">Social links</h2>

              {/* Website */}
              <div className="space-y-2">
                <Label htmlFor="website" className="text-sm font-medium">Website</Label>
                <div className="flex">
                  <span className="inline-flex items-center px-3 text-sm text-gray-500 bg-gray-50 border border-r-0 border-gray-300 rounded-l-md">
                    https://
                  </span>
                  <Input
                    id="website"
                    placeholder="yourwebsite.com"
                    value={website}
                    onChange={(e) => setWebsite(e.target.value)}
                    className="rounded-l-none"
                  />
                </div>
              </div>

              {/* GitHub URL */}
              <div className="space-y-2">
                <Label htmlFor="github" className="text-sm font-medium">GitHub URL</Label>
                <div className="flex">
                  <span className="inline-flex items-center px-3 text-sm text-gray-500 bg-gray-50 border border-r-0 border-gray-300 rounded-l-md">
                    https://
                  </span>
                  <Input
                    id="github"
                    placeholder="github.com/username"
                    value={githubUrl}
                    onChange={(e) => setGithubUrl(e.target.value)}
                    className="rounded-l-none"
                  />
                </div>
              </div>

              {/* Twitter URL */}
              <div className="space-y-2">
                <Label htmlFor="twitter" className="text-sm font-medium">Twitter URL</Label>
                <div className="flex">
                  <span className="inline-flex items-center px-3 text-sm text-gray-500 bg-gray-50 border border-r-0 border-gray-300 rounded-l-md">
                    https://
                  </span>
                  <Input
                    id="twitter"
                    placeholder="twitter.com/username"
                    value={twitterUrl}
                    onChange={(e) => setTwitterUrl(e.target.value)}
                    className="rounded-l-none"
                  />
                </div>
              </div>
            </div>

            {/* Save Button */}
            <div className="flex justify-end pt-6">
              <Button className="px-6">Save Changes</Button>
            </div>
          </div>
        </div>

        {/* Footer */}
        <Footer />
      </div>
    </div>
  );
}