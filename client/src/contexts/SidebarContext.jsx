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
  // Load initial state from localStorage
  const [isCollapsed, setIsCollapsed] = useState(() => {
    const saved = localStorage.getItem('sidebar_collapsed');
    return saved === 'true';
  });
  const [isHovered, setIsHovered] = useState(false);

  // Load navigation favorites from localStorage
  const [navFavorites, setNavFavorites] = useState(() => {
    const saved = localStorage.getItem('navFavorites');
    return saved ? new Set(JSON.parse(saved)) : new Set();
  });

  // Effective collapsed state - expanded if hovered while collapsed
  const effectiveCollapsed = isCollapsed && !isHovered;

  // Persist favorites to localStorage whenever they change
  useEffect(() => {
    localStorage.setItem('navFavorites', JSON.stringify(Array.from(navFavorites)));
  }, [navFavorites]);

  // Toggle sidebar collapse state
  const toggleSidebar = useCallback(() => {
    setIsCollapsed(prev => {
      const newValue = !prev;
      localStorage.setItem('sidebar_collapsed', String(newValue));
      return newValue;
    });
  }, []);

  // Collapse sidebar
  const collapseSidebar = useCallback(() => {
    setIsCollapsed(true);
    localStorage.setItem('sidebar_collapsed', 'true');
  }, []);

  // Expand sidebar
  const expandSidebar = useCallback(() => {
    setIsCollapsed(false);
    localStorage.setItem('sidebar_collapsed', 'false');
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
  };

  return (
    <SidebarContext.Provider value={value}>
      {children}
    </SidebarContext.Provider>
  );
};

export default SidebarContext;
