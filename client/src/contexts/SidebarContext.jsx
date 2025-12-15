/**
 * SidebarContext
 *
 * Manages sidebar state including collapse/expand and hover behavior.
 * Persists collapsed state to localStorage.
 */

import { createContext, useContext, useState, useCallback, useEffect } from 'react';

const SidebarContext = createContext(null);

export const useSidebar = () => {
  const context = useContext(SidebarContext);
  if (!context) {
    throw new Error('useSidebar must be used within a SidebarProvider');
  }
  return context;
};

export const SidebarProvider = ({ children }) => {
  // Always start expanded (ignore localStorage)
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [isHovered, setIsHovered] = useState(false);

  // Load navigation favorites from localStorage with validation
  const [navFavorites, setNavFavorites] = useState(() => {
    try {
      const saved = localStorage.getItem('navFavorites');
      if (!saved) return new Set();
      const parsed = JSON.parse(saved);
      // Validate: must be array of strings starting with '/'
      if (Array.isArray(parsed) && parsed.every(item => typeof item === 'string' && item.startsWith('/'))) {
        return new Set(parsed);
      }
    } catch (error) {
      console.error('Failed to load nav favorites from localStorage:', error);
    }
    return new Set();
  });

  // Load hidden pages from localStorage with validation
  const [hiddenPages, setHiddenPages] = useState(() => {
    try {
      const saved = localStorage.getItem('hiddenPages');
      if (!saved) return new Set();
      const parsed = JSON.parse(saved);
      // Validate: must be array of strings starting with '/'
      if (Array.isArray(parsed) && parsed.every(item => typeof item === 'string' && item.startsWith('/'))) {
        return new Set(parsed);
      }
    } catch (error) {
      console.error('Failed to load hidden pages from localStorage:', error);
    }
    return new Set();
  });

  // Effective collapsed state - no hover expand behavior
  const effectiveCollapsed = isCollapsed;

  // Persist favorites to localStorage whenever they change
  useEffect(() => {
    localStorage.setItem('navFavorites', JSON.stringify(Array.from(navFavorites)));
  }, [navFavorites]);

  // Persist hidden pages to localStorage whenever they change
  useEffect(() => {
    localStorage.setItem('hiddenPages', JSON.stringify(Array.from(hiddenPages)));
  }, [hiddenPages]);

  // Toggle sidebar collapse state (no localStorage)
  const toggleSidebar = useCallback(() => {
    setIsCollapsed(prev => !prev);
  }, []);

  // Collapse sidebar
  const collapseSidebar = useCallback(() => {
    setIsCollapsed(true);
  }, []);

  // Expand sidebar
  const expandSidebar = useCallback(() => {
    setIsCollapsed(false);
  }, []);

  // Handle hover events
  const handleMouseEnter = useCallback(() => {
    if (isCollapsed) {
      setIsHovered(true);
    }
  }, [isCollapsed]);

  const handleMouseLeave = useCallback(() => {
    setIsHovered(false);
  }, []);

  // Toggle navigation favorite
  const toggleNavFavorite = useCallback((path) => {
    setNavFavorites(prev => {
      const newFavorites = new Set(prev);
      if (newFavorites.has(path)) {
        newFavorites.delete(path);
      } else {
        newFavorites.add(path);
      }
      return newFavorites;
    });
  }, []);

  // Check if path is favorited
  const isNavFavorited = useCallback((path) => {
    return navFavorites.has(path);
  }, [navFavorites]);

  // Toggle hidden page
  const toggleHiddenPage = useCallback((path) => {
    setHiddenPages(prev => {
      const newHidden = new Set(prev);
      if (newHidden.has(path)) {
        newHidden.delete(path);
      } else {
        newHidden.add(path);
      }
      return newHidden;
    });
  }, []);

  // Check if page is hidden
  const isPageHidden = useCallback((path) => {
    return hiddenPages.has(path);
  }, [hiddenPages]);

  // Keyboard shortcut to toggle sidebar ([ key or Cmd+\)
  useEffect(() => {
    const handleKeyDown = (e) => {
      // [ key to toggle (when not in input)
      if (e.key === '[' && !e.metaKey && !e.ctrlKey && !e.altKey) {
        if (e.target instanceof HTMLInputElement ||
            e.target instanceof HTMLTextAreaElement ||
            e.target instanceof HTMLSelectElement) {
          return;
        }
        toggleSidebar();
      }
      // Cmd+\ or Ctrl+\ to toggle
      if (e.key === '\\' && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        toggleSidebar();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [toggleSidebar]);

  const value = {
    isCollapsed,
    isHovered,
    effectiveCollapsed,
    toggleSidebar,
    collapseSidebar,
    expandSidebar,
    handleMouseEnter,
    handleMouseLeave,
    navFavorites,
    toggleNavFavorite,
    isNavFavorited,
    hiddenPages,
    toggleHiddenPage,
    isPageHidden,
  };

  return (
    <SidebarContext.Provider value={value}>
      {children}
    </SidebarContext.Provider>
  );
};

export default SidebarContext;
