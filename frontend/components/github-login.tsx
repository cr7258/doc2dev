'use client'

import { useState } from 'react'
import { useAuth } from '@/lib/auth'
import { Button } from '@/components/ui/button'
import { Github } from 'lucide-react'

export function GitHubLoginButton() {
  const [isLoading, setIsLoading] = useState(false)
  const { login } = useAuth()

  const handleGitHubLogin = async () => {
    setIsLoading(true)
    
    try {
      // Get GitHub OAuth authorization URL
      const redirectUri = `${window.location.origin}/auth/callback`
      const response = await fetch(`http://localhost:8000/auth/github/login?redirect_uri=${encodeURIComponent(redirectUri)}`)
      
      if (!response.ok) {
        throw new Error('Failed to get authorization URL')
      }
      
      const data = await response.json()
      
      // Redirect to GitHub OAuth
      window.location.href = data.auth_url
      
    } catch (error) {
      console.error('GitHub login error:', error)
      setIsLoading(false)
    }
  }

  return (
    <Button 
      onClick={handleGitHubLogin} 
      disabled={isLoading}
      className="flex items-center gap-2"
    >
      <Github className="w-4 h-4" />
      {isLoading ? 'Connecting...' : 'Login with GitHub'}
    </Button>
  )
}
