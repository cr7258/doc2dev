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

    // Backend now returns UTC time, parse it directly
    // If the string doesn't end with 'Z', add it to indicate UTC
    const utcTimeString = dateString.endsWith('Z') ? dateString : dateString + 'Z';
    const utcDate = new Date(utcTimeString);
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
