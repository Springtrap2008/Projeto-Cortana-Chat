const CACHE_NAME = 'cortana-pwa-v1';
const assetsToCache = [
  '/',
  '/static/style.css',
  '/static/script.js',
  '/static/icon-192.png',
  '/static/icon-512.png',
  '/static/manifest.json'
];

// Instala e guarda os arquivos estáticos no cache
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return cache.addAll(assetsToCache);
    })
  );
});

// Intercepta as requisições
self.addEventListener('fetch', event => {
  const url = event.request.url;

  // NUNCA guarde em cache as rotas da API da Cortana
  if (url.includes('/login') || 
      url.includes('/chat') || 
      url.includes('/sessao') || 
      url.includes('/rampancy') || 
      url.includes('/diario') || 
      url.includes('/proativo') ||
      url.includes('/dev/')) {
    return; // Deixa o navegador buscar da rede normalmente
  }

  // Para o resto (HTML, CSS, JS, ícones), tenta o cache primeiro, se não achar vai na rede
  event.respondWith(
    caches.match(event.request).then(response => {
      return response || fetch(event.request);
    })
  );
});

// Limpa caches antigos quando atualizar a versão
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});
