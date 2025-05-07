"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronDown, MoreHorizontal, Search, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";

// 定义菜单项类型
type MenuItemType = {
  id: number;
  label: string;
  icon: React.ElementType;
  onClick: () => void;
};

type DropdownProps = {
  items: MenuItemType[];
  position?: 'top' | 'bottom' | 'auto';
  index?: number;
  total?: number;
};

export function Dropdown({ items, position = 'auto', index = 0, total = 0 }: DropdownProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [isHover, setIsHover] = useState<number | null>(null);
  
  // 确定弹出方向
  const getDropdownPosition = (): 'top' | 'bottom' => {
    // 如果指定了具体方向，则使用指定的方向
    if (position === 'top') return 'top';
    if (position === 'bottom') return 'bottom';
    
    // 自动判断：如果是最后几行且总行数较少，向上弹出
    // 这里的逻辑是：如果是最后2行且总行数少于5行，向上弹出
    const isNearBottom = total > 0 && index >= total - 2 && total < 5;
    return isNearBottom ? 'top' : 'bottom';
  };
  
  const dropdownPosition = getDropdownPosition();

  const toggleDropdown = () => {
    setIsOpen(!isOpen);
  };

  const closeDropdown = () => {
    setIsOpen(false);
  };

  return (
    <div className="relative">
      <Button
        variant="ghost"
        size="icon"
        className="cursor-pointer"
        onClick={toggleDropdown}
        onBlur={() => setTimeout(closeDropdown, 100)}
      >
        <MoreHorizontal className="h-4 w-4" />
      </Button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            className={`absolute right-0 z-50 ${dropdownPosition === 'top' ? 'bottom-full mb-1' : 'mt-1'}`}
            initial={{ opacity: 0, y: dropdownPosition === 'top' ? 5 : -5 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: dropdownPosition === 'top' ? 5 : -5 }}
            transition={{ duration: 0.2 }}
          >
            <div className="bg-background border border-border rounded-md shadow-lg min-w-[120px] py-1">
              <ul>
                {items.map((item) => {
                  const Icon = item.icon;
                  return (
                    <li key={item.id}>
                      <motion.button
                        className="w-full px-3 py-2 flex items-center gap-2 cursor-pointer hover:bg-accent hover:text-accent-foreground transition-colors duration-200"
                        onClick={() => {
                          item.onClick();
                          closeDropdown();
                        }}
                        onMouseEnter={() => setIsHover(item.id)}
                        onMouseLeave={() => setIsHover(null)}
                        whileHover={{ x: 2 }}
                      >
                        <Icon className="h-4 w-4" />
                        <span className="text-sm">{item.label}</span>
                      </motion.button>
                    </li>
                  );
                })}
              </ul>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

// 使用示例
export function DropdownDemo() {
  const menuItems = [
    {
      id: 1,
      label: "查询",
      icon: Search,
      onClick: () => console.log("查询"),
    },
    {
      id: 2,
      label: "删除",
      icon: Trash2,
      onClick: () => console.log("删除"),
    },
  ];

  return <Dropdown items={menuItems} />;
}

export default DropdownDemo;
