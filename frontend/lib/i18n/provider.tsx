'use client';

/**
 * I18n Provider component for client-side i18n initialization
 */

import { useEffect, useState } from 'react';
import { I18nextProvider } from 'react-i18next';
import i18n from './index';

interface I18nProviderProps {
  children: React.ReactNode;
}

export function I18nProvider({ children }: I18nProviderProps) {
  const [isInitialized, setIsInitialized] = useState(false);

  useEffect(() => {
    // Check if i18n is already initialized
    if (i18n.isInitialized) {
      setIsInitialized(true);
    } else {
      // Wait for initialization to complete
      const checkInitialization = () => {
        if (i18n.isInitialized) {
          setIsInitialized(true);
        } else {
          setTimeout(checkInitialization, 50);
        }
      };
      checkInitialization();
    }
  }, []);

  // Show loading state while i18n is initializing
  if (!isInitialized) {
    // Use default language (Chinese) for loading text since i18n is not ready yet
    const loadingText = '加载中...'; // Default to Chinese as per our app settings

    return (
      <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto mb-4"></div>
          <p className="text-lg">{loadingText}</p>
        </div>
      </div>
    );
  }

  return (
    <I18nextProvider i18n={i18n}>
      {children}
    </I18nextProvider>
  );
}
