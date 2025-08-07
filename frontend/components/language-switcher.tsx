'use client';

/**
 * Language switcher component for Doc2Dev
 */

import { useTranslation } from 'react-i18next';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

export function LanguageSwitcher() {
  const { i18n, t } = useTranslation('components');

  const handleLanguageChange = (language: string) => {
    i18n.changeLanguage(language);
  };

  const getCurrentLanguageDisplay = () => {
    switch (i18n.language) {
      case 'zh':
        return (
          <div className="flex items-center gap-1">
            <span>🇨🇳</span>
            <span className="hidden sm:inline">中文</span>
          </div>
        );
      case 'en':
        return (
          <div className="flex items-center gap-1">
            <span>🇺🇸</span>
            <span className="hidden sm:inline">EN</span>
          </div>
        );
      default:
        return (
          <div className="flex items-center gap-1">
            <span>🇨🇳</span>
            <span className="hidden sm:inline">中文</span>
          </div>
        );
    }
  };

  return (
    <Select value={i18n.language} onValueChange={handleLanguageChange}>
      <SelectTrigger className="w-20 sm:w-28 h-9 text-sm border-gray-200 hover:border-gray-300 focus:border-blue-500 transition-colors cursor-pointer bg-white shadow-sm">
        <SelectValue>
          {getCurrentLanguageDisplay()}
        </SelectValue>
      </SelectTrigger>
      <SelectContent align="end" className="min-w-32 bg-white border border-gray-200 shadow-lg">
        <SelectItem
          value="zh"
          className="cursor-pointer hover:bg-blue-50 focus:bg-blue-50 transition-colors"
        >
          <div className="flex items-center gap-2">
            <span>🇨🇳</span>
            <span>{t('languageSwitcher.chinese')}</span>
          </div>
        </SelectItem>
        <SelectItem
          value="en"
          className="cursor-pointer hover:bg-blue-50 focus:bg-blue-50 transition-colors"
        >
          <div className="flex items-center gap-2">
            <span>🇺🇸</span>
            <span>{t('languageSwitcher.english')}</span>
          </div>
        </SelectItem>
      </SelectContent>
    </Select>
  );
}
