const CACHE_NAME = 'caike-news-v1';
const urlsToCache = [
  '/My-news-app/',
  '/My-news-app/index.html',
  '/My-news-app/style.css',
  '/My-news-app/script.js',
  '/My-news-app/news.json'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => response || fetch(event.request))
  );
});
