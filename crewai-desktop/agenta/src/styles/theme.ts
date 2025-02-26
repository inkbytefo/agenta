export type ThemeMode = 'light' | 'dark';

export interface Theme {
  colors: {
    primary: string;
    secondary: string;
    background: string;
    surface: string;
    textPrimary: string;
    textSecondary: string;
    border: string;
  };
}

export const lightTheme: Theme = {
  colors: {
    primary: '#4a90e2',
    secondary: '#357bd8',
    background: '#f0f2f5',
    surface: '#ffffff',
    textPrimary: '#333333',
    textSecondary: '#666666',
    border: '#dddddd',
  },
};

export const darkTheme: Theme = {
  colors: {
    primary: '#4a90e2',
    secondary: '#357bd8',
    background: '#1a1a1a',
    surface: '#2d2d2d',
    textPrimary: '#ffffff',
    textSecondary: 'rgba(255, 255, 255, 0.7)',
    border: '#404040',
  },
};