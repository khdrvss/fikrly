// Service Worker for Progressive Web App
const CACHE_NAME = 'fikrly-v1.0.0';
const RUNTIME_CACHE = 'fikrly-runtime';

// Assets to cache immediately
const PRECACHE_URLS = [
  '/',
  '/static/bundle.css',
  '/static/main.css',
  '/static/js/ui-enhancements.js',
  '/static/favicons/android-chrome-192x192.png',
  '/static/favicons/android-chrome-512x512.png',
  '/static/favicons/favicon.png',
  '/offline/',
];

// Install event - cache core assets
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(PRECACHE_URLS))
      .then(() => self.skipWaiting())
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames
          .filter(cacheName => cacheName !== CACHE_NAME && cacheName !== RUNTIME_CACHE)
          .map(cacheName => caches.delete(cacheName))
      );
    }).then(() => self.clients.claim())
  );
});

// Fetch event - network first, fallback to cache
self.addEventListener('fetch', event => {
  const { request } = event;
  
  // Skip non-GET requests
  if (request.method !== 'GET') return;
  
  // Skip chrome extensions
  if (request.url.startsWith('chrome-extension://')) return;
  
  // Skip admin and API endpoints from caching
  if (request.url.includes('/admin/') || request.url.includes('/api/')) {
    return;
  }
  
  event.respondWith(
    caches.match(request).then(cachedResponse => {
      // Return cached version if available
      if (cachedResponse) {
        // Update cache in background
        fetch(request).then(response => {
          if (response && response.status === 200) {
            caches.open(RUNTIME_CACHE).then(cache => {
              cache.put(request, response.clone());
            });
          }
        });
        return cachedResponse;
      }
      
      // Fetch from network
      return fetch(request).then(response => {
        // Don't cache non-successful responses
        if (!response || response.status !== 200 || response.type === 'error') {
          return response;
        }
        
        // Cache successful responses
        const responseToCache = response.clone();
        caches.open(RUNTIME_CACHE).then(cache => {
          cache.put(request, responseToCache);
        });
        
        return response;
      }).catch(() => {
        // Return offline page for navigation requests
        if (request.mode === 'navigate') {
          return caches.match('/offline/');
        }
      });
    })
  );
});

// Background sync for offline form submissions
self.addEventListener('sync', event => {
  if (event.tag === 'sync-reviews') {
    event.waitUntil(syncReviews());
  }
});

async function syncReviews() {
  // Get pending reviews from IndexedDB
  const db = await openDB();
  const pendingReviews = await db.getAll('pending-reviews');
  
  for (const review of pendingReviews) {
    try {
      const response = await fetch('/review/submit/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(review.data)
      });
      
      if (response.ok) {
        await db.delete('pending-reviews', review.id);
      }
    } catch (error) {
      console.error('Sync failed:', error);
    }
  }
}

// Push notification handler
self.addEventListener('push', event => {
  const data = event.data.json();
  
  const options = {
    body: data.body,
    icon: '/static/favicons/android-chrome-192x192.png',
    badge: '/static/favicons/favicon.png',
    vibrate: [200, 100, 200],
    data: {
      url: data.url
    },
    actions: [
      { action: 'view', title: 'Ko\'rish' },
      { action: 'close', title: 'Yopish' }
    ]
  };
  
  event.waitUntil(
    self.registration.showNotification(data.title, options)
  );
});

// Notification click handler
self.addEventListener('notificationclick', event => {
  event.notification.close();
  
  if (event.action === 'view' || !event.action) {
    const url = event.notification.data.url || '/';
    event.waitUntil(
      clients.openWindow(url)
    );
  }
});

// Helper to open IndexedDB
function openDB() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open('fikrly-db', 1);
    
    request.onerror = () => reject(request.error);
    request.onsuccess = () => resolve(request.result);
    
    request.onupgradeneeded = event => {
      const db = event.target.result;
      if (!db.objectStoreNames.contains('pending-reviews')) {
        db.createObjectStore('pending-reviews', { keyPath: 'id', autoIncrement: true });
      }
    };
  });
}
