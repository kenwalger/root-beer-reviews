# Progressive Web App (PWA) Setup Guide

Your Root Beer Review App is now configured as a Progressive Web App (PWA), which means it can be installed on mobile devices and desktop browsers for a native app-like experience.

## What's Included

✅ **Manifest File** (`app/static/manifest.json`)
- Defines app metadata, icons, display mode, and theme colors
- Enables "Add to Home Screen" functionality

✅ **Service Worker** (`app/static/service-worker.js`)
- Provides offline functionality
- Caches static assets for faster loading
- Enables the app to work without internet connection (for cached pages)

✅ **PWA Meta Tags**
- Added to both public and admin templates
- Configured for iOS (Apple) devices
- Sets theme colors and display preferences

## Installing the App

### On Mobile (iOS/Android)

1. **Open the app in your mobile browser** (Safari on iOS, Chrome on Android)
2. **Look for the install prompt:**
   - **iOS Safari**: Tap the Share button → "Add to Home Screen"
   - **Android Chrome**: You'll see an "Install" banner, or go to Menu → "Install App"
3. **Follow the prompts** to add the app to your home screen
4. **Launch the app** from your home screen like a native app

### On Desktop (Chrome/Edge)

1. **Open the app in Chrome or Edge**
2. **Look for the install icon** in the address bar (usually a "+" or download icon)
3. **Click "Install"** when prompted
4. **The app will open in its own window** without browser chrome

## Creating App Icons

The app needs icon files for proper PWA installation. Currently, placeholder paths are configured.

### Quick Setup Options

1. **Use an Online Generator:**
   - Visit [PWA Asset Generator](https://github.com/onderceylan/pwa-asset-generator)
   - Upload a 512x512px image
   - Download the generated icons
   - Place them in `app/static/icons/` with the names:
     - `icon-72x72.png`
     - `icon-96x96.png`
     - `icon-128x128.png`
     - `icon-144x144.png`
     - `icon-152x152.png`
     - `icon-192x192.png` (required)
     - `icon-384x384.png`
     - `icon-512x512.png` (required)

2. **Create Your Own:**
   - Design a 512x512px icon (root beer themed)
   - Export at all required sizes
   - Use a tool like ImageMagick or online resizers to create all sizes

3. **Temporary Solution:**
   - The app will work without icons, but installation won't be as polished
   - You can use a simple colored square or emoji-based icon temporarily

## Testing PWA Features

### Check Installation Readiness

1. Open Chrome DevTools (F12)
2. Go to the "Application" tab
3. Check "Manifest" section - should show your app details
4. Check "Service Workers" section - should show registered worker

### Test Offline Functionality

1. Open the app
2. Open DevTools → Network tab
3. Check "Offline" checkbox
4. Navigate around - cached pages should still work

### Test on Mobile

1. Deploy to a server (or use ngrok for local testing)
2. Open on your phone
3. Test the "Add to Home Screen" functionality
4. Launch from home screen and verify it opens in standalone mode

## PWA Features Enabled

- ✅ **Installable** - Can be added to home screen/desktop
- ✅ **Offline Support** - Cached pages work without internet
- ✅ **App-like Experience** - Standalone display mode
- ✅ **Fast Loading** - Service worker caches assets
- ✅ **Theme Colors** - Matches your root beer color scheme

## Troubleshooting

### App Won't Install

- **Check HTTPS**: PWAs require HTTPS (except localhost)
- **Verify Manifest**: Check DevTools → Application → Manifest for errors
- **Service Worker**: Ensure service worker is registered (DevTools → Application → Service Workers)
- **Icons**: Make sure icon files exist and are accessible

### Service Worker Not Registering

- Check browser console for errors
- Verify `/service-worker.js` is accessible
- Ensure you're not in private/incognito mode (some browsers block SW)
- Clear browser cache and try again

### Icons Not Showing

- Verify icon files exist in `app/static/icons/`
- Check file permissions
- Ensure icon paths in `manifest.json` are correct
- Clear browser cache

## Next Steps

1. **Create custom icons** for a polished experience
2. **Test on real devices** to ensure everything works
3. **Deploy to production** with HTTPS enabled
4. **Consider adding more offline features** (like caching API responses)

## Resources

- [MDN PWA Guide](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps)
- [Web.dev PWA Checklist](https://web.dev/pwa-checklist/)
- [PWA Builder](https://www.pwabuilder.com/) - Tools and testing

