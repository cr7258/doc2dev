"use client";

import React from 'react';
import { useTranslation } from 'react-i18next';
import { Badge } from '@/components/ui/badge';
import { formatDateTime } from '@/utils/date';

interface RelativeTimeProps {
  dateString: string;
  className?: string;
  showTooltip?: boolean;
}

export function RelativeTime({ dateString, className, showTooltip = true }: RelativeTimeProps) {
  const { t } = useTranslation('common');

  const getRelativeTimeI18n = (dateString: string): string => {
    if (!dateString) return '-';
    
    // Parse backend returned time string as UTC time
    // Add 'Z' to indicate this is UTC time
    const utcDate = new Date(dateString + 'Z');
    const now = new Date();
    
    // Calculate time difference (milliseconds)
    const timeDiff = now.getTime() - utcDate.getTime();
    const secondsDiff = Math.floor(timeDiff / 1000);
    
    // Convert to relative time with i18n support
    if (secondsDiff < 60) {
      return t('time.justNow');
    } else if (secondsDiff < 3600) {
      const minutes = Math.floor(secondsDiff / 60);
      return t('time.minutesAgo', { count: minutes });
    } else if (secondsDiff < 86400) {
      const hours = Math.floor(secondsDiff / 3600);
      return t('time.hoursAgo', { count: hours });
    } else if (secondsDiff < 2592000) {
      const days = Math.floor(secondsDiff / 86400);
      return t('time.daysAgo', { count: days });
    } else {
      // Show date if more than 30 days
      const locale = t('common.locale', { defaultValue: 'en-US' });
      return utcDate.toLocaleDateString(locale);
    }
  };

  const relativeTime = getRelativeTimeI18n(dateString);
  const tooltip = showTooltip ? formatDateTime(dateString) : undefined;

  return (
    <Badge 
      variant="outline" 
      className={`font-normal ${className || ''}`}
      title={tooltip}
    >
      {relativeTime}
    </Badge>
  );
}
