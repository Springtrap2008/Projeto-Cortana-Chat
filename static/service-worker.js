const CACHE_NAME = 'meu-site-v1';
const urlsToCache = [
  '/',
  '/static/style.css', // adicione seus arquivos CSS/JS aqui
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request).then(response => {
      return response || fetch(event.request);
    })
  );
});
