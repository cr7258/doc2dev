/**
 * Translation resources for i18next
 */

// Import Chinese translations
import zhCommon from '@/locales/zh/common.json';
import zhPages from '@/locales/zh/pages.json';
import zhComponents from '@/locales/zh/components.json';
import zhAuth from '@/locales/zh/auth.json';

// Import English translations
import enCommon from '@/locales/en/common.json';
import enPages from '@/locales/en/pages.json';
import enComponents from '@/locales/en/components.json';
import enAuth from '@/locales/en/auth.json';

export const resources = {
  zh: {
    common: zhCommon,
    pages: zhPages,
    components: zhComponents,
    auth: zhAuth,
  },
  en: {
    common: enCommon,
    pages: enPages,
    components: enComponents,
    auth: enAuth,
  },
} as const;

export default resources;
