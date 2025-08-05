'use client';

import * as React from 'react';
import * as DropdownMenuPrimitive from '@radix-ui/react-dropdown-menu';
import { Check, ChevronRight, Circle, Github, LogOut, User, Settings, MoreHorizontal, Search, Trash2 } from 'lucide-react';
import { AnimatePresence, motion, type Transition } from 'motion/react';
import { useRouter } from 'next/navigation';

import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';

const EXIT_DELAY = 0.3;

interface DropdownMenuContextType {
  isOpen: boolean;
  activeValue: string | null;
  setActiveValue: (value: string | null) => void;
  scheduleReset: () => void;
  clearReset: () => void;
}
const DropdownMenuContext = React.createContext<DropdownMenuContextType>({
  isOpen: false,
  activeValue: null,
  setActiveValue: () => {},
  scheduleReset: () => {},
  clearReset: () => {},
});

const useDropdownMenu = (): DropdownMenuContextType => {
  const context = React.useContext(DropdownMenuContext);
  if (!context) {
    throw new Error('useDropdownMenu must be used within a DropdownMenu');
  }
  return context;
};

type DropdownMenuProps = React.ComponentPropsWithoutRef<
  typeof DropdownMenuPrimitive.Root
>;
const DropdownMenu: React.FC<DropdownMenuProps> = ({ children, ...props }) => {
  const [isOpen, setIsOpen] = React.useState(
    props?.open ?? props?.defaultOpen ?? false,
  );
  const [activeValue, setActiveValueState] = React.useState<string | null>(
    null,
  );

  const exitTimeoutRef = React.useRef<ReturnType<typeof setTimeout> | null>(
    null,
  );

  const scheduleReset = React.useCallback(() => {
    if (exitTimeoutRef.current) {
      clearTimeout(exitTimeoutRef.current);
    }
    exitTimeoutRef.current = setTimeout(() => {
      setActiveValueState(null);
      exitTimeoutRef.current = null;
    }, EXIT_DELAY * 1000);
  }, []);

  const clearReset = React.useCallback(() => {
    if (exitTimeoutRef.current) {
      clearTimeout(exitTimeoutRef.current);
      exitTimeoutRef.current = null;
    }
  }, []);

  React.useEffect(() => {
    return () => {
      if (exitTimeoutRef.current) {
        clearTimeout(exitTimeoutRef.current);
      }
    };
  }, []);

  const setActiveValue = (val: string | null) => {
    clearReset();
    setActiveValueState(val);
  };

  const handleOpenChange = React.useCallback(
    (open: boolean) => {
      setIsOpen(open);
      props.onOpenChange?.(open);
    },
    [props],
  );

  return (
    <DropdownMenuPrimitive.Root {...props} onOpenChange={handleOpenChange}>
      <DropdownMenuContext.Provider
        value={{
          isOpen,
          activeValue,
          setActiveValue,
          scheduleReset,
          clearReset,
        }}
      >
        {children}
      </DropdownMenuContext.Provider>
    </DropdownMenuPrimitive.Root>
  );
};

type DropdownMenuTriggerProps = React.ComponentPropsWithoutRef<
  typeof DropdownMenuPrimitive.Trigger
>;
const DropdownMenuTrigger = React.forwardRef<
  React.ElementRef<typeof DropdownMenuPrimitive.Trigger>,
  DropdownMenuTriggerProps
>(({ className, ...props }, ref) => (
  <DropdownMenuPrimitive.Trigger ref={ref} className={className} {...props} />
));
DropdownMenuTrigger.displayName = DropdownMenuPrimitive.Trigger.displayName;

type DropdownMenuGroupProps = React.ComponentPropsWithoutRef<
  typeof DropdownMenuPrimitive.Group
>;
const DropdownMenuGroup = DropdownMenuPrimitive.Group;

type DropdownMenuPortalProps = React.ComponentPropsWithoutRef<
  typeof DropdownMenuPrimitive.Portal
>;
const DropdownMenuPortal = DropdownMenuPrimitive.Portal;

type DropdownMenuSubProps = React.ComponentPropsWithoutRef<
  typeof DropdownMenuPrimitive.Sub
>;
const DropdownMenuSub = DropdownMenuPrimitive.Sub;

type DropdownMenuRadioGroupProps = React.ComponentPropsWithoutRef<
  typeof DropdownMenuPrimitive.RadioGroup
>;
const DropdownMenuRadioGroup = DropdownMenuPrimitive.RadioGroup;

type DropdownMenuSubTriggerProps = React.ComponentPropsWithoutRef<
  typeof DropdownMenuPrimitive.SubTrigger
> & {
  inset?: boolean;
  transition?: Transition;
};
const DropdownMenuSubTrigger = React.forwardRef<
  React.ElementRef<typeof DropdownMenuPrimitive.SubTrigger>,
  DropdownMenuSubTriggerProps
>(
  (
    {
      className,
      children,
      inset,
      disabled,
      transition = { type: 'spring', stiffness: 200, damping: 20 },
      ...props
    },
    ref,
  ) => {
    const { activeValue, setActiveValue, scheduleReset, clearReset } =
      useDropdownMenu();
    const id = React.useId();

    const handleMouseEnter = (e: React.MouseEvent<HTMLDivElement>) => {
      clearReset();
      setActiveValue(id);
      props.onMouseEnter?.(e);
    };

    const handleMouseLeave = (e: React.MouseEvent<HTMLDivElement>) => {
      scheduleReset();
      props.onMouseLeave?.(e);
    };

    return (
      <DropdownMenuPrimitive.SubTrigger
        ref={ref}
        className="relative"
        {...props}
        disabled={disabled}
        onMouseEnter={(e) => {
          handleMouseEnter(e);
          props.onMouseEnter?.(e);
        }}
        onMouseLeave={(e) => {
          handleMouseLeave(e);
          props.onMouseLeave?.(e);
        }}
      >
        <AnimatePresence>
          {activeValue === id && !disabled && (
            <motion.span
              className="absolute inset-0 h-full w-full bg-muted rounded-sm"
              layoutId="dropdown-menu-item-background"
              initial={{ opacity: 0 }}
              animate={{
                opacity: 1,
                transition,
              }}
              exit={{
                opacity: 0,
                transition: {
                  ...transition,
                  delay: EXIT_DELAY + (transition?.delay ?? 0),
                },
              }}
            />
          )}
        </AnimatePresence>

        <motion.span
          data-disabled={disabled}
          whileTap={{ scale: 0.95 }}
          className={cn(
            'relative z-[1] flex cursor-default select-none items-center gap-2 rounded-sm px-2 py-1.5 text-sm outline-none data-[state=open]:bg-accent [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0',
            inset && 'pl-8',
            className,
          )}
        >
          {children}
          <ChevronRight className="ml-auto" />
        </motion.span>
      </DropdownMenuPrimitive.SubTrigger>
    );
  },
);
DropdownMenuSubTrigger.displayName =
  DropdownMenuPrimitive.SubTrigger.displayName;

type DropdownMenuSubContentProps = React.ComponentPropsWithoutRef<
  typeof DropdownMenuPrimitive.SubContent
>;
const DropdownMenuSubContent = React.forwardRef<
  React.ElementRef<typeof DropdownMenuPrimitive.SubContent>,
  DropdownMenuSubContentProps
>(({ className, ...props }, ref) => (
  <DropdownMenuPrimitive.SubContent
    ref={ref}
    className={cn(
      'z-50 min-w-[8rem] overflow-hidden rounded-md border bg-popover p-1 text-popover-foreground shadow-lg data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[side=bottom]:slide-in-from-top-2 data-[side=left]:slide-in-from-right-2 data-[side=right]:slide-in-from-left-2 data-[side=top]:slide-in-from-bottom-2 origin-[--radix-dropdown-menu-content-transform-origin]',
      className,
    )}
    {...props}
  />
));
DropdownMenuSubContent.displayName =
  DropdownMenuPrimitive.SubContent.displayName;

type DropdownMenuContentProps = React.ComponentPropsWithoutRef<
  typeof DropdownMenuPrimitive.Content
> & {
  transition?: Transition;
};
const DropdownMenuContent = React.forwardRef<
  React.ElementRef<typeof DropdownMenuPrimitive.Content>,
  DropdownMenuContentProps
>(
  (
    {
      className,
      children,
      sideOffset = 4,
      transition = { duration: 0.2 },
      ...props
    },
    ref,
  ) => {
    const { isOpen } = useDropdownMenu();

    return (
      <AnimatePresence>
        {isOpen && (
          <DropdownMenuPrimitive.Portal forceMount>
            <DropdownMenuPrimitive.Content
              ref={ref}
              sideOffset={sideOffset}
              asChild
              {...props}
            >
              <motion.div
                key="dropdown-menu"
                className={cn(
                  'z-50 max-h-[var(--radix-dropdown-menu-content-available-height)] min-w-[8rem] overflow-y-auto overflow-x-hidden rounded-md border bg-popover p-1 text-popover-foreground shadow-md data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[side=bottom]:slide-in-from-top-2 data-[side=left]:slide-in-from-right-2 data-[side=right]:slide-in-from-left-2 data-[side=top]:slide-in-from-bottom-2 origin-[--radix-dropdown-menu-content-transform-origin]',
                  className,
                )}
                initial={{
                  opacity: 0,
                  scale: 0.95,
                  clipPath: 'inset(0 0 100% 0)',
                }}
                animate={{
                  opacity: 1,
                  scale: 1,
                  clipPath: 'inset(0 0 0 0)',
                }}
                exit={{
                  opacity: 0,
                  scale: 0.95,
                  clipPath: 'inset(0 0 100% 0)',
                }}
                transition={transition}
                style={{ willChange: 'opacity, transform, clip-path' }}
              >
                {children}
              </motion.div>
            </DropdownMenuPrimitive.Content>
          </DropdownMenuPrimitive.Portal>
        )}
      </AnimatePresence>
    );
  },
);
DropdownMenuContent.displayName = DropdownMenuPrimitive.Content.displayName;

type DropdownMenuItemProps = React.ComponentPropsWithoutRef<
  typeof DropdownMenuPrimitive.Item
> & {
  inset?: boolean;
  transition?: Transition;
};
const DropdownMenuItem = React.forwardRef<
  React.ElementRef<typeof DropdownMenuPrimitive.Item>,
  DropdownMenuItemProps
>(
  (
    {
      className,
      children,
      inset,
      disabled,
      transition = { type: 'spring', stiffness: 200, damping: 20 },
      ...props
    },
    ref,
  ) => {
    const { activeValue, setActiveValue, scheduleReset, clearReset } =
      useDropdownMenu();
    const id = React.useId();

    const handleMouseEnter = (e: React.MouseEvent<HTMLDivElement>) => {
      clearReset();
      setActiveValue(id);
      props.onMouseEnter?.(e);
    };

    const handleMouseLeave = (e: React.MouseEvent<HTMLDivElement>) => {
      scheduleReset();
      props.onMouseLeave?.(e);
    };

    return (
      <DropdownMenuPrimitive.Item
        ref={ref}
        className="relative"
        {...props}
        disabled={disabled}
        onMouseEnter={(e) => {
          handleMouseEnter(e);
          props.onMouseEnter?.(e);
        }}
        onMouseLeave={(e) => {
          handleMouseLeave(e);
          props.onMouseLeave?.(e);
        }}
      >
        <AnimatePresence>
          {activeValue === id && !disabled && (
            <motion.span
              className="absolute inset-0 h-full w-full bg-muted rounded-sm"
              layoutId="dropdown-menu-item-background"
              initial={{ opacity: 0 }}
              animate={{
                opacity: 1,
                transition,
              }}
              exit={{
                opacity: 0,
                transition: {
                  ...transition,
                  delay: EXIT_DELAY + (transition?.delay ?? 0),
                },
              }}
            />
          )}
        </AnimatePresence>

        <motion.span
          data-disabled={disabled}
          whileTap={{ scale: 0.95 }}
          className={cn(
            'relative z-[1] flex cursor-pointer select-none items-center gap-2 rounded-sm px-2 py-1.5 text-sm outline-none transition-colors focus:text-accent-foreground data-[disabled]:pointer-events-none data-[disabled]:opacity-50 [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0',
            inset && 'pl-8',
            className,
          )}
        >
          {children}
        </motion.span>
      </DropdownMenuPrimitive.Item>
    );
  },
);
DropdownMenuItem.displayName = DropdownMenuPrimitive.Item.displayName;

type DropdownMenuCheckboxItemProps = React.ComponentPropsWithoutRef<
  typeof DropdownMenuPrimitive.CheckboxItem
> & {
  transition?: Transition;
};
const DropdownMenuCheckboxItem = React.forwardRef<
  React.ElementRef<typeof DropdownMenuPrimitive.CheckboxItem>,
  DropdownMenuCheckboxItemProps
>(
  (
    {
      className,
      children,
      checked,
      disabled,
      transition = { type: 'spring', stiffness: 200, damping: 20 },
      ...props
    },
    ref,
  ) => {
    const { activeValue, setActiveValue, scheduleReset, clearReset } =
      useDropdownMenu();
    const id = React.useId();

    const handleMouseEnter = (e: React.MouseEvent<HTMLDivElement>) => {
      clearReset();
      setActiveValue(id);
      props.onMouseEnter?.(e);
    };

    const handleMouseLeave = (e: React.MouseEvent<HTMLDivElement>) => {
      scheduleReset();
      props.onMouseLeave?.(e);
    };

    return (
      <DropdownMenuPrimitive.CheckboxItem
        ref={ref}
        className="relative"
        {...props}
        checked={checked}
        disabled={disabled}
        onMouseEnter={(e) => {
          handleMouseEnter(e);
          props.onMouseEnter?.(e);
        }}
        onMouseLeave={(e) => {
          handleMouseLeave(e);
          props.onMouseLeave?.(e);
        }}
      >
        <AnimatePresence>
          {activeValue === id && !disabled && (
            <motion.span
              className="absolute inset-0 h-full w-full bg-muted rounded-sm"
              layoutId="dropdown-menu-item-background"
              initial={{ opacity: 0 }}
              animate={{
                opacity: 1,
                transition,
              }}
              exit={{
                opacity: 0,
                transition: {
                  ...transition,
                  delay: EXIT_DELAY + (transition?.delay ?? 0),
                },
              }}
            />
          )}
        </AnimatePresence>

        <motion.span
          data-disabled={disabled}
          whileTap={{ scale: 0.95 }}
          className={cn(
            'relative z-[1] flex cursor-default select-none items-center rounded-sm py-1.5 pl-8 pr-2 text-sm outline-none transition-colors focus:bg-accent focus:text-accent-foreground data-[disabled]:pointer-events-none data-[disabled]:opacity-50',
            className,
          )}
        >
          <span className="absolute left-2 flex h-3.5 w-3.5 items-center justify-center">
            <DropdownMenuPrimitive.ItemIndicator>
              <Check className="h-4 w-4" />
            </DropdownMenuPrimitive.ItemIndicator>
          </span>
          {children}
        </motion.span>
      </DropdownMenuPrimitive.CheckboxItem>
    );
  },
);
DropdownMenuCheckboxItem.displayName =
  DropdownMenuPrimitive.CheckboxItem.displayName;

type DropdownMenuRadioItemProps = React.ComponentPropsWithoutRef<
  typeof DropdownMenuPrimitive.RadioItem
> & {
  transition?: Transition;
};
const DropdownMenuRadioItem = React.forwardRef<
  React.ElementRef<typeof DropdownMenuPrimitive.RadioItem>,
  DropdownMenuRadioItemProps
>(
  (
    {
      className,
      children,
      disabled,
      transition = { type: 'spring', stiffness: 200, damping: 20 },
      ...props
    },
    ref,
  ) => {
    const { activeValue, setActiveValue, scheduleReset, clearReset } =
      useDropdownMenu();
    const id = React.useId();

    const handleMouseEnter = (e: React.MouseEvent<HTMLDivElement>) => {
      clearReset();
      setActiveValue(id);
      props.onMouseEnter?.(e);
    };

    const handleMouseLeave = (e: React.MouseEvent<HTMLDivElement>) => {
      scheduleReset();
      props.onMouseLeave?.(e);
    };

    return (
      <DropdownMenuPrimitive.RadioItem
        ref={ref}
        className="relative"
        {...props}
        disabled={disabled}
        onMouseEnter={(e) => {
          handleMouseEnter(e);
          props.onMouseEnter?.(e);
        }}
        onMouseLeave={(e) => {
          handleMouseLeave(e);
          props.onMouseLeave?.(e);
        }}
      >
        <AnimatePresence>
          {activeValue === id && !disabled && (
            <motion.span
              className="absolute inset-0 h-full w-full bg-muted rounded-sm"
              layoutId="dropdown-menu-item-background"
              initial={{ opacity: 0 }}
              animate={{
                opacity: 1,
                transition,
              }}
              exit={{
                opacity: 0,
                transition: {
                  ...transition,
                  delay: EXIT_DELAY + (transition?.delay ?? 0),
                },
              }}
            />
          )}
        </AnimatePresence>

        <motion.span
          data-disabled={disabled}
          whileTap={{ scale: 0.95 }}
          className={cn(
            'relative z-[1] flex cursor-default select-none items-center rounded-sm py-1.5 pl-8 pr-2 text-sm outline-none transition-colors focus:bg-accent focus:text-accent-foreground data-[disabled]:pointer-events-none data-[disabled]:opacity-50',
            className,
          )}
        >
          <span className="absolute left-2 flex h-3.5 w-3.5 items-center justify-center">
            <DropdownMenuPrimitive.ItemIndicator>
              <Circle className="h-2 w-2 fill-current" />
            </DropdownMenuPrimitive.ItemIndicator>
          </span>
          {children}
        </motion.span>
      </DropdownMenuPrimitive.RadioItem>
    );
  },
);
DropdownMenuRadioItem.displayName = DropdownMenuPrimitive.RadioItem.displayName;

type DropdownMenuLabelProps = React.ComponentPropsWithoutRef<
  typeof DropdownMenuPrimitive.Label
> & {
  inset?: boolean;
};
const DropdownMenuLabel = React.forwardRef<
  React.ElementRef<typeof DropdownMenuPrimitive.Label>,
  DropdownMenuLabelProps
>(({ className, inset, ...props }, ref) => (
  <DropdownMenuPrimitive.Label
    ref={ref}
    className={cn(
      'px-2 py-1.5 text-sm font-semibold',
      inset && 'pl-8',
      className,
    )}
    {...props}
  />
));
DropdownMenuLabel.displayName = DropdownMenuPrimitive.Label.displayName;

type DropdownMenuSeparatorProps = React.ComponentPropsWithoutRef<
  typeof DropdownMenuPrimitive.Separator
>;
const DropdownMenuSeparator = React.forwardRef<
  React.ElementRef<typeof DropdownMenuPrimitive.Separator>,
  DropdownMenuSeparatorProps
>(({ className, ...props }, ref) => (
  <DropdownMenuPrimitive.Separator
    ref={ref}
    className={cn('-mx-1 my-1 h-px bg-muted', className)}
    {...props}
  />
));
DropdownMenuSeparator.displayName = DropdownMenuPrimitive.Separator.displayName;

type DropdownMenuShortcutProps = React.HTMLAttributes<HTMLSpanElement>;
const DropdownMenuShortcut = React.forwardRef<
  HTMLSpanElement,
  DropdownMenuShortcutProps
>(({ className, ...props }, ref) => {
  return (
    <span
      ref={ref}
      className={cn('ml-auto text-xs tracking-widest opacity-60', className)}
      {...props}
    />
  );
});
DropdownMenuShortcut.displayName = 'DropdownMenuShortcut';

// Table Row Dropdown Component
interface TableRowDropdownProps {
  onQuery: () => void;
  onDelete: () => void;
  position?: { x: number; y: number };
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
}

const TableRowDropdown = ({ 
  onQuery, 
  onDelete, 
  position, 
  isOpen, 
  onOpenChange 
}: TableRowDropdownProps) => {
  const dropdownStyle = position 
    ? {
        position: 'fixed' as const,
        left: `${position.x}px`,
        top: `${position.y}px`,
        zIndex: 50,
      }
    : {};

  return (
    <DropdownMenu open={isOpen} onOpenChange={onOpenChange}>
      <DropdownMenuTrigger asChild>
        <Button
          variant="ghost"
          size="sm"
          className="h-8 w-8 p-0 hover:bg-gray-100 cursor-pointer"
        >
          <MoreHorizontal className="h-4 w-4" />
        </Button>
      </DropdownMenuTrigger>
      
      <DropdownMenuContent 
        className="w-40" 
        align="end"
        style={dropdownStyle}
      >
        <DropdownMenuItem onClick={onQuery}>
          <Search className="w-4 h-4" />
          <span>Query</span>
        </DropdownMenuItem>
        
        <DropdownMenuSeparator />
        
        <DropdownMenuItem 
          onClick={onDelete}
          className="text-red-600 focus:text-red-600 focus:bg-red-50"
        >
          <Trash2 className="w-4 h-4" />
          <span>Delete</span>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
};

// GitHub Avatar Dropdown Component
interface GitHubAvatarDropdownProps {
  user: {
    username: string;
    email?: string;
    avatar_url?: string;
  };
  onLogout: () => void;
}

const GitHubAvatarDropdown = ({ user, onLogout }: GitHubAvatarDropdownProps) => {
  const router = useRouter();

  const handleSettingsClick = () => {
    router.push('/settings');
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <motion.button
          className="flex items-center gap-2 rounded-full p-1 hover:bg-gray-100 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 cursor-pointer"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          {user.avatar_url ? (
            <img 
              src={user.avatar_url} 
              alt={user.username}
              className="w-8 h-8 rounded-full border-2 border-gray-200"
            />
          ) : (
            <div className="w-8 h-8 rounded-full bg-gray-300 flex items-center justify-center">
              <Github className="w-4 h-4 text-gray-600" />
            </div>
          )}
          <span className="text-sm font-medium text-gray-700 hidden sm:block">
            {user.username}
          </span>
        </motion.button>
      </DropdownMenuTrigger>
      
      <DropdownMenuContent className="w-56" align="end">
        <DropdownMenuLabel className="flex items-center gap-2">
          <div className="flex flex-col">
            <span className="font-medium">{user.username}</span>
            {user.email && (
              <span className="text-xs text-muted-foreground">{user.email}</span>
            )}
          </div>
        </DropdownMenuLabel>
        
        <DropdownMenuSeparator />
        
        <DropdownMenuItem onClick={handleSettingsClick} className="cursor-pointer">
          <Settings className="w-4 h-4" />
          <span>Settings</span>
        </DropdownMenuItem>
        
        <DropdownMenuSeparator />
        
        <DropdownMenuItem 
          onClick={onLogout}
          className="text-red-600 focus:text-red-600 focus:bg-red-50"
        >
          <LogOut className="w-4 h-4" />
          <span>Log out</span>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
};

export {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuCheckboxItem,
  DropdownMenuRadioItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuShortcut,
  DropdownMenuGroup,
  DropdownMenuPortal,
  DropdownMenuSub,
  DropdownMenuSubContent,
  DropdownMenuSubTrigger,
  DropdownMenuRadioGroup,
  type DropdownMenuProps,
  type DropdownMenuTriggerProps,
  type DropdownMenuContentProps,
  type DropdownMenuItemProps,
  type DropdownMenuCheckboxItemProps,
  type DropdownMenuRadioItemProps,
  type DropdownMenuLabelProps,
  type DropdownMenuSeparatorProps,
  type DropdownMenuShortcutProps,
  type DropdownMenuGroupProps,
  type DropdownMenuPortalProps,
  type DropdownMenuSubProps,
  type DropdownMenuSubContentProps,
  type DropdownMenuSubTriggerProps,
  type DropdownMenuRadioGroupProps,
  TableRowDropdown,
  type TableRowDropdownProps,
  GitHubAvatarDropdown,
  type GitHubAvatarDropdownProps,
};
