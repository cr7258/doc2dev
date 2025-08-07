/**
 * i18next configuration for Doc2Dev
 */

import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';
import { resources } from './resources';

// Initialize i18next
i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    // Default language settings
    fallbackLng: 'zh',
    lng: 'zh', // Force default to Chinese
    
    // Language detection configuration
    detection: {
      // Only detect from localStorage, ignore browser language
      order: ['localStorage'],
      lookupLocalStorage: 'i18nextLng',
      caches: ['localStorage'],
      excludeCacheFor: ['cimode'], // Exclude cache for development mode
    },
    
    // Translation resources
    resources,
    
    // Default namespace
    defaultNS: 'common',
    
    // Namespace configuration
    ns: ['common', 'pages', 'components', 'auth'],
    
    // Interpolation settings
    interpolation: {
      escapeValue: false, // React already escapes values
    },
    
    // Development settings
    debug: process.env.NODE_ENV === 'development',
    
    // React specific settings
    react: {
      useSuspense: false, // Disable suspense for SSR compatibility
    },
    
    // Additional settings
    load: 'languageOnly', // Load only language, not region (zh instead of zh-CN)
    cleanCode: true, // Clean language codes
    
    // Fallback settings
    fallbackNS: 'common',
    
    // Key separator (use dot notation)
    keySeparator: '.',
    
    // Namespace separator
    nsSeparator: ':',
  });

export default i18n;
