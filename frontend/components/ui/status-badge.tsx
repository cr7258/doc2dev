"use client";

import React from 'react';
import { useTranslation } from 'react-i18next';
import { Badge } from '@/components/ui/badge';

interface StatusBadgeProps {
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  className?: string;
}

export function StatusBadge({ status, className }: StatusBadgeProps) {
  const { t } = useTranslation('common');

  const getStatusConfig = () => {
    switch (status) {
      case 'completed':
        return {
          text: t('status.completed'),
          className: 'bg-green-50 text-green-600 border-green-200 hover:bg-green-100'
        };
      case 'in_progress':
        return {
          text: t('status.inProgress'),
          className: 'bg-blue-50 text-blue-600 border-blue-200 hover:bg-blue-100'
        };
      case 'failed':
        return {
          text: t('status.failed'),
          className: 'bg-red-50 text-red-600 border-red-200 hover:bg-red-100'
        };
      case 'pending':
      default:
        return {
          text: t('status.pending'),
          className: 'bg-amber-50 text-amber-600 border-amber-200 hover:bg-amber-100'
        };
    }
  };

  const config = getStatusConfig();

  return (
    <Badge className={`px-3 py-1 text-xs ${config.className} ${className || ''}`}>
      {config.text}
    </Badge>
  );
}
