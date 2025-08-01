'use client'

import { useEffect, useState, useRef } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { useAuth } from '@/lib/auth'

export default function AuthCallback() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const { login } = useAuth()
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading')
  const [error, setError] = useState<string>('')
  const processedRef = useRef(false)

  useEffect(() => {
    const handleCallback = async () => {
      if (processedRef.current) return;
      processedRef.current = true;

      const code = searchParams.get('code')
      const state = searchParams.get('state')

      if (!code) {
        setStatus('error')
        setError('No authorization code received')
        return
      }

      try {
        const redirectUri = `${window.location.origin}/auth/callback`
        const callbackUrl = `http://localhost:8000/auth/github/callback?code=${encodeURIComponent(code)}&redirect_uri=${encodeURIComponent(redirectUri)}`
        
        const response = await fetch(callbackUrl)
        
        if (!response.ok) {
          const errorText = await response.text()
          throw new Error(`Authentication failed: ${response.status} - ${errorText}`)
        }

        const data = await response.json()
        
        // Store authentication data
        login(data.access_token, {
          id: data.user_id,
          github_id: data.github_id,
          username: data.username,
          avatar_url: data.avatar_url
        })

        setStatus('success')
        
        // Redirect to home page after successful login
        setTimeout(() => {
          router.push('/')
        }, 1000)

      } catch (error) {
        console.error('Authentication error:', error)
        setStatus('error')
        setError(error instanceof Error ? error.message : 'Authentication failed')
      }
    }

    handleCallback()
  }, [searchParams, login, router])

  if (status === 'loading') {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto mb-4"></div>
          <p className="text-lg">Completing GitHub authentication...</p>
        </div>
      </div>
    )
  }

  if (status === 'success') {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="text-green-600 text-6xl mb-4">✓</div>
          <p className="text-lg text-green-600">Authentication successful!</p>
          <p className="text-sm text-gray-600">Redirecting to home page...</p>
        </div>
      </div>
    )
  }

  if (status === 'error') {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-600 text-6xl mb-4">✗</div>
          <p className="text-lg text-red-600">Authentication failed</p>
          <p className="text-sm text-gray-600 mb-4">{error}</p>
          <button 
            onClick={() => router.push('/')}
            className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
          >
            Return to Home
          </button>
        </div>
      </div>
    )
  }

  return null
}
