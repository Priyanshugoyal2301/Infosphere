// Newspaper Border Toggle Utility
// This file allows easy toggling of the newspaper text borders feature
// To disable borders: change ENABLE_NEWSPAPER_BORDERS to false
// To enable borders: change ENABLE_NEWSPAPER_BORDERS to true

export const ENABLE_NEWSPAPER_BORDERS = true;

export const getNewspaperBorderClasses = (): string => {
  if (ENABLE_NEWSPAPER_BORDERS) {
    return 'newspaper-text-border newspaper-side-borders';
  }
  return '';
};

export const getNewspaperBgClasses = (): string => {
  const borderClasses = getNewspaperBorderClasses();
  return `min-h-screen newspaper-bg ${borderClasses}`.trim();
};