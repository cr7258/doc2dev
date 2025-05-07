/**
 * 日期和时间处理工具函数
 */

/**
 * 格式化日期时间为本地时间
 * @param dateString 日期时间字符串（后端返回的 UTC 时间）
 * @returns 格式化后的本地时间字符串
 */
export function formatDateTime(dateString: string): string {
  if (!dateString) return '-';
  
  // 将后端返回的时间字符串解析为 UTC 时间
  // 添加 'Z' 表示这是 UTC 时间
  const utcDate = new Date(dateString + 'Z');
  
  // 使用浏览器的本地化功能自动转换为用户时区
  return utcDate.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false // 使用24小时制
  });
}

/**
 * 计算相对时间（如“几分钟前”、“几小时前”等）
 * @param dateString 日期时间字符串（后端返回的 UTC 时间）
 * @returns 相对时间字符串
 */
export function getRelativeTime(dateString: string): string {
  if (!dateString) return '-';
  
  // 将后端返回的时间字符串解析为 UTC 时间
  // 添加 'Z' 表示这是 UTC 时间
  const utcDate = new Date(dateString + 'Z');
  const now = new Date();
  
  // 计算时间差（毫秒）
  const timeDiff = now.getTime() - utcDate.getTime();
  const secondsDiff = Math.floor(timeDiff / 1000);
  
  // 转换为相对时间
  if (secondsDiff < 60) {
    return '刚刚';
  } else if (secondsDiff < 3600) {
    return `${Math.floor(secondsDiff / 60)}分钟前`;
  } else if (secondsDiff < 86400) {
    return `${Math.floor(secondsDiff / 3600)}小时前`;
  } else if (secondsDiff < 2592000) {
    return `${Math.floor(secondsDiff / 86400)}天前`;
  } else {
    // 超过30天显示日期
    return utcDate.toLocaleDateString('zh-CN');
  }
}

/**
 * 格式化数字为带千分位的字符串
 * @param num 要格式化的数字
 * @returns 格式化后的字符串
 */
export function formatNumber(num: number): string {
  return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}
