// Service Worker for Root Beer Review App
const CACHE_NAME = 'root-beer-reviews-v2';
const urlsToCache = [
  '/static/css/style.css',
  '/static/manifest.json',
];

// Routes that should NEVER be cached (admin routes, authenticated content)
const NO_CACHE_ROUTES = [
  '/admin',
  '/admin/',
  '/admin/login',
  '/admin/logout',
  '/admin/account',
  '/admin/rootbeers',
  '/admin/reviews',
  '/admin/flavor-notes',
  '/admin/metadata',
];

// Check if a URL should be cached
function shouldCache(url) {
  // Never cache admin routes
  if (NO_CACHE_ROUTES.some(route => url.pathname.startsWith(route))) {
    return false;
  }
  
  // Never cache authenticated API endpoints or admin-specific content
  if (url.pathname.startsWith('/admin/')) {
    return false;
  }
  
  // Only cache static assets and public pages
  if (url.pathname.startsWith('/static/')) {
    return true;
  }
  
  // Cache public pages (homepage, root beer pages, review pages)
  if (url.pathname === '/' || 
      url.pathname.startsWith('/rootbeers/') || 
      url.pathname.startsWith('/reviews/')) {
    return true;
  }
  
  // Don't cache anything else by default
  return false;
}

// Install event - cache resources
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('Opened cache');
        return cache.addAll(urlsToCache);
      })
  );
  // Force the waiting service worker to become the active service worker
  self.skipWaiting();
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            console.log('Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
  // Take control of all pages immediately
  return self.clients.claim();
});

// Fetch event - serve from cache, fallback to network
self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);
  
  // Never cache admin routes - always fetch from network
  if (!shouldCache(url)) {
    event.respondWith(fetch(event.request));
    return;
  }
  
  // For homepage, use network-first strategy to always get fresh data
  if (url.pathname === '/') {
    event.respondWith(
      fetch(event.request)
        .then((response) => {
          // If network request succeeds, cache it for offline use
          if (response && response.status === 200 && response.type === 'basic') {
            const responseToCache = response.clone();
            caches.open(CACHE_NAME).then((cache) => {
              cache.put(event.request, responseToCache);
            });
          }
          return response;
        })
        .catch(() => {
          // If network fails, try to return cached version
          return caches.match(event.request);
        })
    );
    return;
  }
  
  // For other cacheable routes, use cache-first strategy
  event.respondWith(
    caches.match(event.request)
      .then((response) => {
        // Cache hit - return response
        if (response) {
          return response;
        }
        
        // Clone the request because it's a stream
        const fetchRequest = event.request.clone();
        
        return fetch(fetchRequest).then((response) => {
          // Check if valid response
          if (!response || response.status !== 200 || response.type !== 'basic') {
            return response;
          }
          
          // Only cache if it's a cacheable route
          if (shouldCache(url) && event.request.method === 'GET') {
            // Clone the response because it's a stream
            const responseToCache = response.clone();
            
            caches.open(CACHE_NAME).then((cache) => {
              cache.put(event.request, responseToCache);
            });
          }
          
          return response;
        }).catch(() => {
          // If fetch fails, try to return a cached offline page (only for public pages)
          if (event.request.destination === 'document' && shouldCache(url)) {
            return caches.match('/');
          }
          // For admin routes or non-cacheable routes, fail gracefully
          return new Response('Offline - This page requires network connection', {
            status: 503,
            headers: { 'Content-Type': 'text/plain' }
          });
        });
      })
  );
});

