/**
 * Date and time processing utility functions
 */

/**
 * Format date time to local time
 * @param dateString Date time string (UTC time returned from backend)
 * @returns Formatted local time string
 */
export function formatDateTime(dateString: string): string {
  if (!dateString) return '-';

  // Parse backend returned time string as UTC time
  // Add 'Z' to indicate this is UTC time
  const utcDate = new Date(dateString + 'Z');

  // Use browser's localization feature to automatically convert to user timezone
  return utcDate.toLocaleString('en-US', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false // Use 24-hour format
  });
}

/**
 * Calculate relative time（如“minutes ago”、“hours ago”等）
 * @param dateString Date time string (UTC time returned from backend)
 * @returns Relative time string
 */
export function getRelativeTime(dateString: string): string {
  if (!dateString) return '-';
  
  // Parse backend returned time string as UTC time
  // Add 'Z' to indicate this is UTC time
  const utcDate = new Date(dateString + 'Z');
  const now = new Date();
  
  // Calculate time difference (milliseconds)
  const timeDiff = now.getTime() - utcDate.getTime();
  const secondsDiff = Math.floor(timeDiff / 1000);
  
  // Convert to relative time
  if (secondsDiff < 60) {
    return 'just now';
  } else if (secondsDiff < 3600) {
    return `${Math.floor(secondsDiff / 60)} minutes ago`;
  } else if (secondsDiff < 86400) {
    return `${Math.floor(secondsDiff / 3600)} hours ago`;
  } else if (secondsDiff < 2592000) {
    return `${Math.floor(secondsDiff / 86400)} days ago`;
  } else {
    // Show date if more than 30 days
    return utcDate.toLocaleDateString('en-US');
  }
}

/**
 * Format number as string with thousands separators
 * @param num Number to format
 * @returns Formatted string
 */
export function formatNumber(num: number): string {
  return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}
