"use client"

import * as React from "react"
import { useState, useEffect } from "react";
import { createPortal } from "react-dom";
import { useTranslation } from 'react-i18next';
import { LogIn, Lock, Mail, X } from "lucide-react";

interface SignInModalProps {
  isOpen: boolean;
  onClose: () => void;
  onGitHubLogin: () => void;
  onGoogleLogin?: () => void;
}

const SignInModal = ({ isOpen, onClose, onGitHubLogin, onGoogleLogin }: SignInModalProps) => {
  const { t } = useTranslation('auth'); // Specify the namespace directly
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const validateEmail = (email: string) => {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  };

  const handleSignIn = () => {
    if (!email || !password) {
      setError(t('enterEmailPassword'));
      return;
    }
    if (!validateEmail(email)) {
      setError(t('enterValidEmail'));
      return;
    }
    setError("");
    alert(t('signInSuccessDemo'));
  };

  if (!isOpen || !mounted) return null;

  const modalContent = (
    <>
      {/* Background overlay to dim the page and prevent clicks */}
      <div className="fixed inset-0 bg-gray-200 bg-opacity-50 z-[9998]" onClick={onClose}></div>

      {/* Modal content */}
      <div className="fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-[9999]">
        <div className="w-96 min-h-[520px] bg-gradient-to-b from-sky-50/50 to-white rounded-3xl shadow-2xl p-8 flex flex-col items-center border border-blue-100 text-black relative">
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 transition-colors cursor-pointer"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex items-center justify-center w-14 h-14 rounded-2xl bg-white mb-6 shadow-lg">
          <LogIn className="w-7 h-7 text-black" />
        </div>
        
        <h2 className="text-2xl font-semibold mb-2 text-center">
          {t('signInWithEmail')}
        </h2>
        <p className="text-gray-500 text-sm mb-6 text-center">
          {t('signInDescription')}
        </p>
        
        <div className="w-full flex flex-col gap-3 mb-2">
          <div className="relative">
            <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
              <Mail className="w-4 h-4" />
            </span>
            <input
              placeholder={t('email')}
              type="email"
              value={email}
              className="w-full pl-10 pr-3 py-2 rounded-xl border border-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-200 bg-gray-50 text-black text-sm"
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>
          <div className="relative">
            <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
              <Lock className="w-4 h-4" />
            </span>
            <input
              placeholder={t('password')}
              type="password"
              value={password}
              className="w-full pl-10 pr-10 py-2 rounded-xl border border-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-200 bg-gray-50 text-black text-sm"
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>
          <div className="w-full flex justify-between items-center">
            {error && (
              <div className="text-sm text-red-500">{error}</div>
            )}
            <button className="text-xs hover:underline font-medium ml-auto cursor-pointer">
              {t('forgotPassword')}
            </button>
          </div>
        </div>
        
        <button
          onClick={handleSignIn}
          className="w-full bg-gradient-to-b from-gray-700 to-gray-900 text-white font-medium py-2 rounded-xl shadow hover:brightness-105 cursor-pointer transition mb-4 mt-2"
        >
          {t('getStarted')}
        </button>

        <div className="flex items-center w-full my-2">
          <div className="flex-grow border-t border-dashed border-gray-200"></div>
          <span className="mx-2 text-xs text-gray-400">{t('orSignInWith')}</span>
          <div className="flex-grow border-t border-dashed border-gray-200"></div>
        </div>
        
        <div className="flex gap-3 w-full justify-center mt-2">
          {onGoogleLogin && (
            <button
              onClick={onGoogleLogin}
              className="flex items-center justify-center w-12 h-12 rounded-xl border bg-white hover:bg-gray-100 transition grow cursor-pointer"
            >
              <img
                src="https://www.svgrepo.com/show/475656/google-color.svg"
                alt="Google"
                className="w-6 h-6"
              />
            </button>
          )}
          <button
            onClick={onGitHubLogin}
            className="flex items-center justify-center w-12 h-12 rounded-xl border bg-white hover:bg-gray-100 transition grow cursor-pointer"
          >
            <img
              src="/github.svg"
              alt="GitHub"
              className="w-6 h-6"
            />
          </button>
        </div>
        </div>
      </div>
    </>
  );

  return createPortal(modalContent, document.body);
};

export { SignInModal };
