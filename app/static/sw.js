// Minimal service worker — enables "Add to Home Screen" without offline caching
const CACHE_NAME = 'mtg-tracker-v1';

self.addEventListener('install', (event) => {
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(clients.claim());
});

// No fetch handler — all requests go straight to the network
