# NEURA - Professional AI Chat UI

A professional, dark-themed HTML and CSS UI design for an advanced AI chat application called **NEURA**. This is a pure frontend design with no JavaScript, backend, or database dependencies.

## 📁 Files Included

### 1. **index.html** - Landing Page
The main landing page featuring:
- Professional hero section with NEURA branding
- Animated logo with glow and rotation effects
- Feature highlights (Lightning Fast, Advanced Intelligence, Privacy First)
- Statistics section (100K+ Users, 99.9% Uptime, 24/7 Support)
- Professional footer with links
- Fully responsive design for desktop and mobile

**Access:** Open `index.html` in any web browser

### 2. **chat.html** - Chat Interface
Full-featured chat interface featuring:
- Conversation sidebar with history management
- Professional chat header with user profile
- Message bubbles (user and AI)
- Empty state with welcome message
- Input area with attachment support
- Responsive design for all screen sizes
- Mobile-optimized sidebar (collapsible)

**Access:** Open `chat.html` in any web browser

### 3. **mobile.html** - Mobile Optimized Interface
Mobile-first design featuring:
- Optimized header for small screens
- Bottom navigation bar (Chat, History, Settings)
- Touch-friendly buttons and input
- Safe area support for notched devices
- Efficient use of screen space
- Message bubbles optimized for mobile

**Access:** Open `mobile.html` in any web browser or view on mobile device

### 4. **styles.css** - Main Stylesheet
Comprehensive CSS file containing:
- CSS variables for dark theme colors
- Responsive design breakpoints (1024px, 768px, 480px)
- Animated logo with glow and rotation effects
- Smooth transitions and animations
- Professional typography with Inter font
- Component styles (buttons, cards, messages, etc.)
- Mobile-optimized scrollbars and interactions

## 🎨 Design Features

### Color Palette
- **Primary Color:** `#5b7fff` (Blue)
- **Accent Color:** `#00d9ff` (Cyan)
- **Background Dark:** `#0a0e27` (Deep Navy)
- **Background Card:** `#1a1f3a` (Dark Blue)
- **Text Primary:** `#e8eef7` (Light Gray)
- **Text Secondary:** `#a0aec0` (Medium Gray)

### Typography
- **Font Family:** Inter (from Google Fonts)
- **Weights:** 400, 500, 600, 700, 800
- **Responsive sizes:** Scales from 1.5rem on mobile to 3.5rem on desktop

### Animations
- **Logo Glow:** Pulsing glow effect with color transition
- **Logo Rotate:** Subtle rotating border animation
- **Message Slide:** Messages slide in smoothly
- **Button Hover:** Lift effect on hover with shadow
- **Button Press:** Scale effect on click

## 📱 Responsive Breakpoints

The design is fully responsive with optimized layouts for:

- **Desktop (1024px+):** Full sidebar, multi-column layouts
- **Tablet (768px - 1024px):** Adjusted spacing and font sizes
- **Mobile (480px - 768px):** Collapsible sidebar, single column
- **Small Mobile (<480px):** Optimized for compact screens

## 🚀 How to Use

### Option 1: Local Development
1. Clone or download all files to a folder
2. Open `index.html` in your web browser for the landing page
3. Open `chat.html` for the chat interface
4. Open `mobile.html` for the mobile view
5. All styling is contained in `styles.css`

### Option 2: Web Server
For best results, serve files through a local web server:

```bash
# Using Python 3
python -m http.server 8000

# Using Node.js (with http-server)
npx http-server

# Using PHP
php -S localhost:8000
```

Then access:
- Landing page: `http://localhost:8000/index.html`
- Chat interface: `http://localhost:8000/chat.html`
- Mobile view: `http://localhost:8000/mobile.html`

### Option 3: Deploy to Web Hosting
Upload all files to your web hosting provider:
- FTP/SFTP upload
- Git deployment
- Web hosting control panel file manager

## 🔧 Customization

### Change Colors
Edit the CSS variables at the top of `styles.css`:

```css
:root {
  --primary-color: #5b7fff;      /* Change primary blue */
  --accent-color: #00d9ff;       /* Change accent cyan */
  --background-dark: #0a0e27;    /* Change dark background */
  /* ... other colors ... */
}
```

### Change Logo
Replace the SVG code in the `<svg>` elements in HTML files with your own logo. The animated logo appears in:
- Navigation bar
- Hero section
- Chat header
- Mobile header

### Modify Text Content
All text is editable in the HTML files:
- Headlines, descriptions, and feature text
- Button labels
- Navigation links
- Footer content

### Adjust Animations
Modify animation properties in `styles.css`:
- `logoGlow` - Change glow effect timing and intensity
- `logoRotate` - Adjust rotation speed
- `messageSlide` - Modify message entrance animation
- `pulseGlow` - Change pulse effect

## 📊 File Structure

```
NEURA-UI/
├── index.html          # Landing page
├── chat.html           # Chat interface
├── mobile.html         # Mobile optimized view
├── styles.css          # All styling
└── README.md           # This file
```

## 🌐 Browser Support

- Chrome/Chromium (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## ✨ Features Highlights

✅ **Pure HTML & CSS** - No JavaScript required
✅ **Dark Theme** - Professional dark UI with cyan accents
✅ **Animated Logo** - Glow and rotation effects
✅ **Fully Responsive** - Works on all screen sizes
✅ **Modern Design** - Professional and clean aesthetic
✅ **Fast Loading** - No dependencies or frameworks
✅ **Accessible** - Semantic HTML structure
✅ **Customizable** - Easy to modify colors and content

## 📝 Notes

- All files are static HTML and CSS
- No backend server required
- No database needed
- No JavaScript dependencies
- Can be hosted on any web server
- Perfect for prototyping and UI design
- Ready for integration with any backend

## 🎯 Next Steps

To add functionality, you can:
1. Add JavaScript for interactivity
2. Connect to a backend API
3. Integrate with a real AI service
4. Add user authentication
5. Implement real-time messaging
6. Add database storage

## 📄 License

This design is provided as-is for use in your NEURA AI project.

---

**Created:** 2024
**Version:** 1.0
**Status:** Production Ready
