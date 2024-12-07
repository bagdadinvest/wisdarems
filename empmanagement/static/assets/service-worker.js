// Name of the cache
const CACHE_NAME = 'my-site-cache-v1';
// List of URLs to cache
const urlsToCache = [
  '/',
  '/styles/main.css',
  '/script/main.js'
];

self.addEventListener('install', (event) => {
  console.log('Service Worker installing.');
  // Pre-cache application shell
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('Opened cache');
        return cache.addAll(urlsToCache);
      })
      .catch((error) => {
        console.error('Failed to cache assets during install:', error);
      })
  );
});

self.addEventListener('activate', (event) => {
  console.log('Service Worker activating.');
  const cacheWhitelist = [CACHE_NAME];
  
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (!cacheWhitelist.includes(cacheName)) {
            console.log('Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request)
      .then((response) => {
        if (response) {
          return response; // Return the cached response if found
        }
        // Fetch from network if not in cache
        return fetch(event.request).then((networkResponse) => {
          // Optionally cache the new request here if desired
          return networkResponse;
        }).catch((error) => {
          console.error('Failed to fetch resource:', error);
          throw error; // Re-throw the error after logging it
        });
      })
  );
});
