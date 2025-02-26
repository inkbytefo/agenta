import * as React from 'react';
import { createContext, useContext, useEffect, useState } from 'react';
import { create, StateCreator } from 'zustand';
import { persist, PersistOptions } from 'zustand/middleware';

// Theme Types
export type ThemeMode = 'light' | 'dark' | 'high-contrast';

interface ThemeState {
  theme: ThemeMode;
  setTheme: (theme: ThemeMode) => void;
}

type ThemeStorePersist = (
  config: StateCreator<ThemeState>,
  options: PersistOptions<ThemeState>
) => StateCreator<ThemeState>;

// Create Zustand store with persistence
const useThemeStore = create<ThemeState>()(
  (persist as ThemeStorePersist)(
    (set) => ({
      theme: 'light' as ThemeMode,
      setTheme: (theme: ThemeMode) => set({ theme }),
    }),
    {
      name: 'theme-storage',
    }
  )
);

// Theme Context Type
interface ThemeContextType {
  theme: ThemeMode;
  setTheme: (theme: ThemeMode) => void;
  toggleTheme: () => void;
  systemTheme: ThemeMode;
}

// Create Theme Context
export const ThemeContext = createContext<ThemeContextType | null>(null);

// Custom Hook for Using Theme
export const useTheme = (): ThemeContextType => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

// System Theme Detection
const getSystemTheme = (): ThemeMode => {
  if (typeof window !== 'undefined') {
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    return prefersDark ? 'dark' : 'light';
  }
  return 'light';
};

interface ThemeProviderProps {
  children: React.ReactNode;
}

export const ThemeProvider: React.FC<ThemeProviderProps> = ({ children }) => {
  const { theme, setTheme } = useThemeStore();
  const [systemTheme, setSystemTheme] = useState<ThemeMode>(getSystemTheme());

  // Listen for system theme changes
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    
    const handleChange = (e: MediaQueryListEvent) => {
      setSystemTheme(e.matches ? 'dark' : 'light');
    };

    mediaQuery.addEventListener('change', handleChange);
    
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, []);

  // Apply theme to document
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    document.documentElement.classList.add('theme-transition');
    
    // Remove transition class after animation completes
    const timeoutId = setTimeout(() => {
      document.documentElement.classList.remove('theme-transition');
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [theme]);

  const toggleTheme = () => {
    const nextTheme = theme === 'light' ? 'dark' : 'light';
    setTheme(nextTheme);
  };

  const contextValue: ThemeContextType = {
    theme,
    setTheme,
    toggleTheme,
    systemTheme,
  };

  return (
    <ThemeContext.Provider value={contextValue}>
      {children}
    </ThemeContext.Provider>
  );
};

// Utility Hook for Theme Values
export const useThemeValue = (
  lightValue: string,
  darkValue: string,
  highContrastValue?: string
): string => {
  const { theme } = useTheme();
  
  if (theme === 'high-contrast' && highContrastValue) {
    return highContrastValue;
  }
  
  return theme === 'dark' ? darkValue : lightValue;
};

// Export types for components
export type { ThemeContextType, ThemeProviderProps };
