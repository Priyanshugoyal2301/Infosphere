# Reader Access Feature - ADHD-Friendly Reading Mode

## Overview
The **Reader Access** feature provides a distraction-free, customizable reading experience designed specifically for people with ADHD and other accessibility needs. It's accessible from the header navbar and offers advanced reading tools.

## Features

### 🎯 ADHD-Specific Features

1. **Focus Mode**
   - Dims surrounding content
   - Highlights current reading area with gradient overlay
   - Reduces visual distractions

2. **Reading Guide Line**
   - Horizontal line that follows cursor position
   - Helps track which line you're reading
   - Prevents losing your place

3. **Text-to-Speech**
   - Built-in read-aloud functionality
   - Adjustable speech rate and pitch
   - Play/pause controls

### 📖 Customization Options

#### Font Settings
- **Font Size**: 12px - 32px (adjustable with +/- buttons)
- **Line Spacing**: 1.2 - 3.0 (slider control)
- **Font Styles**:
  - Sans-serif (Clean, modern)
  - Serif (Traditional, newspaper-style)
  - Monospace (Fixed-width for focus)
  - **OpenDyslexic** (Specially designed for dyslexia and ADHD)

#### Color Schemes
Optimized for different visual needs:

1. **Sepia (ADHD Friendly)** - Default
   - Warm beige background (#f4ecd8)
   - Dark brown text (#5c4a33)
   - Reduces eye strain, calming effect

2. **Light**
   - White background
   - Black text
   - Standard high contrast

3. **Dark**
   - Dark gray background (#1a1a1a)
   - Light gray text
   - Reduces blue light exposure

4. **Cream (Low Contrast)**
   - Soft cream background
   - Gentle text color
   - Minimizes visual stress

5. **High Contrast**
   - Black background
   - Yellow text
   - Maximum readability for visual impairments

## How to Use

### Opening Reader Mode

1. **From Navbar Header**
   - Click the **"READER ACCESS"** button (blue button with book icon)
   - Opens with empty state

2. **From News Articles**
   - Browse to **Live News** page
   - Click **"📖 READER MODE"** button on any article
   - Article loads automatically in reader

### Adjusting Settings

**Left Sidebar Controls:**
- Font size: Use +/- buttons
- Line spacing: Drag slider
- Font style: Click preferred option
- Color scheme: Select from 5 options
- ADHD features: Toggle focus mode, reading guide, or text-to-speech

### Reading Tips

For ADHD Users:
- Start with **Sepia** color scheme
- Use **18-20px** font size
- Set line spacing to **1.8-2.0**
- Enable **Focus Mode** to reduce distractions
- Try **Reading Guide** if you lose your place often
- Use **OpenDyslexic font** if regular fonts are hard to read

## Technical Implementation

### Files Created/Modified

1. **New Components:**
   - `frontend/src/components/Accessibility/ReaderMode.tsx` - Main reader component
   - `frontend/src/contexts/ReaderContext.tsx` - State management for article sharing

2. **Modified Components:**
   - `frontend/src/components/Layout/Navbar.tsx` - Added Reader Access button
   - `frontend/src/components/News/RealTimeNews.tsx` - Added "Reader Mode" buttons to articles
   - `frontend/src/App.tsx` - Wrapped app in ReaderProvider
   - `frontend/src/index.css` - Added OpenDyslexic font imports

### Context API
The `ReaderContext` allows any component to:
- Set current article for reader mode
- Open reader mode with specific article
- Share article data across components

```typescript
const { openReaderMode } = useReader();

// Open reader with article
openReaderMode({
  title: "Article Title",
  content: "Article content...",
  source: "News Source",
  published_date: "2025-12-07",
  url: "https://example.com/article"
});
```

### Accessibility Features

- **Keyboard Navigation**: Full keyboard support
- **Screen Reader Compatible**: Semantic HTML structure
- **High Contrast Options**: Multiple color schemes
- **Dyslexic-Friendly Font**: OpenDyslexic font family
- **Customizable Text Size**: 12-32px range
- **Adjustable Line Height**: 1.2-3.0x spacing

## Browser Support

- **Text-to-Speech**: Requires browser with Web Speech API
  - ✅ Chrome/Edge (full support)
  - ✅ Safari (full support)
  - ⚠️ Firefox (limited support)

- **OpenDyslexic Font**: Loaded via CDN
  - Works in all modern browsers
  - Fallback to Arial if load fails

## Future Enhancements

Potential improvements:
- [ ] Reading speed tracking
- [ ] Bookmark/save reading position
- [ ] Highlight/annotation tools
- [ ] Word highlighting during text-to-speech
- [ ] Bionic reading mode (bold first letters)
- [ ] Reading timer/break reminders
- [ ] Export article to PDF with custom settings
- [ ] Reading statistics dashboard
- [ ] Multiple reading profiles

## Benefits

### For ADHD Users:
- **Reduced Distractions**: Focus mode eliminates visual clutter
- **Better Tracking**: Reading guide prevents losing place
- **Flexible Pacing**: Text-to-speech allows passive consumption
- **Personalized**: Extensive customization for comfort

### For All Users:
- **Eye Strain Reduction**: Multiple color schemes
- **Readability**: Adjustable typography
- **Accessibility**: Dyslexia-friendly fonts
- **Convenience**: Clean, ad-free reading

## Usage Examples

### Example 1: ADHD User Setup
```
1. Open Reader Access
2. Set font size to 20px
3. Choose OpenDyslexic font
4. Select Sepia color scheme
5. Enable Focus Mode
6. Enable Reading Guide
7. Start reading with reduced distractions
```

### Example 2: Night Reading
```
1. Open Reader Access with article
2. Select Dark color scheme
3. Increase line spacing to 2.0
4. Use 18px sans-serif
5. Comfortable night reading
```

### Example 3: Quick Article Review
```
1. Click "Reader Mode" on article
2. Enable Text-to-Speech
3. Listen while doing other tasks
```

## Conclusion

The Reader Access feature makes Infosphere more inclusive and accessible. By providing tools specifically designed for ADHD and other accessibility needs, we ensure everyone can consume news comfortably and effectively.

**Accessibility is not optional—it's essential.**
