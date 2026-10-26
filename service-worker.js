const CACHE_NAME = 'cortana-pwa-v1';
const assetsToCache = [
  '/',
  '/static/style.css',
  '/static/script.js',
  '/static/icon-192.png',
  '/static/icon-512.png',
  '/static/manifest.json'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(assetsToCache))
  );
});

self.addEventListener('fetch', event => {
  const url = event.request.url;

  // NUNCA guarde em cache as rotas da API
  if (url.includes('/login') || url.includes('/chat') || url.includes('/sessao') || 
      url.includes('/rampancy') || url.includes('/diario') || url.includes('/proativo') ||
      url.includes('/subscribe') || url.includes('/dev/')) {
    return;
  }

  event.respondWith(
    caches.match(event.request).then(response => {
      return response || fetch(event.request);
    })
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) return caches.delete(cacheName);
        })
      );
    })
  );
});

// --- RECEBER A NOTIFICAÇÃO ---
self.addEventListener('push', event => {
    const data = event.data ? event.data.json() : {};
    const title = data.title || 'Cortana';
    const options = {
        body: data.body || 'Nova mensagem da Cortana.',
        icon: '/static/icon-192.png',
        badge: '/static/icon-192.png',
        vibrate: [200, 100, 200],
        data: { url: '/' }
    };

    event.waitUntil(
        self.registration.showNotification(title, options)
    );
});

self.addEventListener('notificationclick', event => {
    event.notification.close();
    event.waitUntil(
        clients.matchAll({ type: 'window' }).then(windowClients => {
            for (let client of windowClients) {
                if (client.url === '/' && 'focus' in client) return client.focus();
            }
            if (clients.openWindow) return clients.openWindow('/');
        })
    );
});