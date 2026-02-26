// Service Worker for Progressive Web App
const CACHE_NAME = 'fikrly-v1.2.0';
const RUNTIME_CACHE = 'fikrly-runtime-v1.2.0';

// Assets to cache immediately
const PRECACHE_URLS = [
  '/',
  '/static/dist/bundle.css',
  '/static/main.css',
  '/static/favicons/android-chrome-192x192.png',
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

// Allow page script to force immediate activation of an updated SW.
self.addEventListener('message', event => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});

// Fetch event - network first, fallback to cache
self.addEventListener('fetch', event => {
  const { request } = event;
  
  // Skip non-GET requests
  if (request.method !== 'GET') return;
  
  // Skip chrome extensions
  if (request.url.startsWith('chrome-extension://')) return;
  
  // Skip admin, API, auth, search, and CSRF-sensitive form endpoints from caching
  if (
    request.url.includes('/admin/') ||
    request.url.includes('/api/') ||
    request.url.includes('/accounts/') ||
    request.url.includes('/sharh-yozish/') ||
    request.url.includes('/profile/') ||
    request.url.includes('/review/') ||
    request.url.includes('search')
  ) {
    return;
  }

  // HTML navigations should be network-only to avoid stale page UI/layout.
  if (request.mode === 'navigate') {
    event.respondWith(
      fetch(request)
        .then(response => response)
        .catch(() => {
          return caches.match('/offline/');
        })
    );
    return;
  }

  // Always fetch critical UI/CSS assets from network first to prevent stale first view.
  if (
    request.url.includes('/static/js/ui-enhancements') ||
    request.url.includes('/static/dist/bundle.css') ||
    request.url.includes('/static/main.css') ||
    request.url.includes('/static/css/theme.css')
  ) {
    event.respondWith(
      fetch(request)
        .then(response => {
          if (response && response.status === 200) {
            const responseToCache = response.clone();
            caches.open(RUNTIME_CACHE).then(cache => {
              cache.put(request, responseToCache);
            });
          }
          return response;
        })
        .catch(() => caches.match(request))
    );
    return;
  }

  // Keep user-uploaded media fresh (logos/avatars/company images).
  if (request.url.includes('/media/')) {
    event.respondWith(
      fetch(request)
        .then(response => {
          if (response && response.status === 200) {
            const responseToCache = response.clone();
            caches.open(RUNTIME_CACHE).then(cache => {
              cache.put(request, responseToCache);
            });
          }
          return response;
        })
        .catch(() => caches.match(request))
    );
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
