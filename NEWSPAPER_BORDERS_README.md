# Newspaper Text Borders Feature

## Overview
The newspaper text borders feature adds animated scrolling text borders around the entire application, simulating the look of newspaper headlines and text columns flowing around the edges of the screen.

## Features
- **Top Border**: Animated scrolling news headlines
- **Bottom Border**: Infosphere Herald branding and establishment info  
- **Side Borders**: Vertical scrolling newspaper text columns
- **Animations**: Smooth scrolling text in different directions and speeds

## How to Toggle On/Off

### Method 1: Using the Utility File (Recommended)
1. Open `frontend/src/utils/newspaperBorders.ts`
2. Change the `ENABLE_NEWSPAPER_BORDERS` constant:
   - `true` = Borders enabled (default)
   - `false` = Borders disabled

```typescript
export const ENABLE_NEWSPAPER_BORDERS = true;  // Change to false to disable
```

The borders will disappear instantly when set to `false`.

### Method 2: Direct CSS Removal
If you want to completely remove the CSS (more permanent):
1. Open `frontend/src/index.css`
2. Find the section: `/* Newspaper Text Border Design - Revertable Feature */`
3. Comment out or delete the entire section (lines ~140-250)

### Method 3: Component Level Removal
To remove from specific pages only:
1. Open any component file (e.g., `Dashboard.tsx`)
2. Change the import and usage:
```typescript
// Remove this import
import { getNewspaperBgClasses } from '../../utils/newspaperBorders';

// Change this
<div className={getNewspaperBgClasses()}>

// Back to this
<div className="min-h-screen newspaper-bg">
```

## Technical Details
- **Component**: `NewspaperBorders.tsx` - React component with fixed positioning
- **Animation Duration**: Top (30s), Bottom (25s), Left (20s), Right (15s)
- **Z-Index**: 50 (overlays content)
- **Content Padding**: Automatically adjusts when borders are active
- **Responsive**: Uses Tailwind CSS classes for styling

## Files Modified
- `frontend/src/components/Layout/NewspaperBorders.tsx` - Border component (NEW)
- `frontend/src/index.css` - Border animations
- `frontend/src/utils/newspaperBorders.ts` - Toggle utility
- `frontend/src/components/Dashboard/Dashboard.tsx` - Updated to use component

## Reverting Instructions
1. **Quick Toggle**: Set `ENABLE_NEWSPAPER_BORDERS = false` in `newspaperBorders.ts`
2. **Full Removal**: Delete the utility file and CSS section, then update components
3. **Git Revert**: If committed, use `git revert <commit-hash>` to undo changes

The feature is designed to be easily toggled without breaking the application.