import { createContext, useContext, useState, useEffect } from 'react';

const ThemeContext = createContext();

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

export const ThemeProvider = ({ children }) => {
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem('theme') || 'light';
  });

  const [textSize, setTextSize] = useState(() => {
    return localStorage.getItem('textSize') || 'medium';
  });

  const isDark = theme === 'dark';

  useEffect(() => {
    const root = document.documentElement;
    if (theme === 'dark') {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }
    localStorage.setItem('theme', theme);
  }, [theme]);

  useEffect(() => {
    const root = document.documentElement;
    // Remove existing text size classes
    root.classList.remove('text-size-small', 'text-size-medium', 'text-size-large');
    // Add current text size class
    root.classList.add(`text-size-${textSize}`);
    localStorage.setItem('textSize', textSize);
  }, [textSize]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === 'light' ? 'dark' : 'light'));
  };

  const cycleTextSize = () => {
    setTextSize((prev) => {
      if (prev === 'small') return 'medium';
      if (prev === 'medium') return 'large';
      return 'small';
    });
  };

  const value = {
    theme,
    setTheme,
    toggleTheme,
    isDark,
    textSize,
    setTextSize,
    cycleTextSize,
  };

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
};

export default ThemeContext;
