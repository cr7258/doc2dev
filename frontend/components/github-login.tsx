'use client'

import { useState } from 'react'
import { useAuth } from '@/lib/auth'
import { Button } from '@/components/ui/button'
import { SignInModal } from '@/components/ui/clean-minimal-sign-in'


export function GitHubLoginButton() {
  const [isLoading, setIsLoading] = useState(false)
  const [showModal, setShowModal] = useState(false)
  const { } = useAuth()

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

  const handleGoogleLogin = () => {
    // Placeholder for Google login
    alert('Google login coming soon!')
  }

  return (
    <>
      <Button
        onClick={() => setShowModal(true)}
        disabled={isLoading}
        className="cursor-pointer"
      >
        {isLoading ? 'Connecting...' : 'Sign in'}
      </Button>

      <SignInModal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        onGitHubLogin={handleGitHubLogin}
        onGoogleLogin={handleGoogleLogin}
      />
    </>
  )
}
