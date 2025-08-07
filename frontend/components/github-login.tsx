'use client'

import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useAuth } from '@/lib/auth'
import { Button } from '@/components/ui/button'
import { SignInModal } from '@/components/ui/sign-in'


export function GitHubLoginButton() {
  const { t } = useTranslation()
  const [isLoading, setIsLoading] = useState(false)
  const [showModal, setShowModal] = useState(false)
  const { } = useAuth()

  const handleGitHubLogin = async () => {
    setIsLoading(true)
    
    try {
      // Get GitHub OAuth authorization URL
      const redirectUri = `${window.location.origin}/auth/callback`
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/github/login?redirect_uri=${encodeURIComponent(redirectUri)}`)
      
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
    alert(t('auth:googleComingSoon'))
  }

  return (
    <>
      <Button
        onClick={() => setShowModal(true)}
        disabled={isLoading}
        className="cursor-pointer"
      >
        {isLoading ? t('auth:connecting') : t('components:authButton.login')}
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
