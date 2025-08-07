/**
 * TypeScript types for i18n
 */

export type Language = 'zh' | 'en';

export interface TranslationResources {
  common: {
    nav: {
      home: string;
      query: string;
      settings: string;
    };
    buttons: {
      save: string;
      cancel: string;
      delete: string;
      edit: string;
      add: string;
      search: string;
      submit: string;
      back: string;
      next: string;
      previous: string;
      confirm: string;
      close: string;
    };
    messages: {
      success: string;
      error: string;
      loading: string;
      noData: string;
      confirmDelete: string;
    };
    status: {
      active: string;
      inactive: string;
      pending: string;
      completed: string;
      failed: string;
    };
  };
  pages: {
    home: {
      title: string;
      description: string;
      searchPlaceholder: string;
      addRepository: string;
    };
    query: {
      title: string;
      description: string;
      placeholder: string;
      noResults: string;
      searchButton: string;
    };
    download: {
      title: string;
      description: string;
      urlLabel: string;
      urlPlaceholder: string;
      libraryNameLabel: string;
      libraryNamePlaceholder: string;
      platformLabel: string;
      downloadButton: string;
    };
    settings: {
      title: string;
      description: string;
      platformConfigs: string;
      mcpSettings: string;
    };
  };
  components: {
    languageSwitcher: {
      chinese: string;
      english: string;
    };
    repositoryCard: {
      viewDocs: string;
      lastUpdated: string;
      tokens: string;
      snippets: string;
    };
    authButton: {
      login: string;
      logout: string;
      profile: string;
    };
  };
  auth: {
    signInWithEmail: string;
    signInDescription: string;
    email: string;
    password: string;
    forgotPassword: string;
    getStarted: string;
    orSignInWith: string;
    enterEmailPassword: string;
    enterValidEmail: string;
    signInSuccessDemo: string;
    connecting: string;
    googleComingSoon: string;
    noAuthCode: string;
    completing: string;
    success: string;
    redirecting: string;
    failed: string;
    returnHome: string;
  };
}

// Extend react-i18next module to include our custom types
declare module 'react-i18next' {
  interface CustomTypeOptions {
    defaultNS: 'common';
    resources: TranslationResources;
  }
}
