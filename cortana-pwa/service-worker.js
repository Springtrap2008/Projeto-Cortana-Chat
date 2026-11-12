// Service Worker da Cortana — gerencia Web Push

self.addEventListener("install", () => {
    self.skipWaiting();
});

self.addEventListener("activate", event => {
    event.waitUntil(clients.claim());
});

self.addEventListener("push", event => {
    let data = { title: "Cortana", body: "Nova notificação." };
    if (event.data) {
        try {
            data = event.data.json();
        } catch (e) {
            data.body = event.data.text();
        }
    }

    const options = {
        body: data.body,
        icon: "icons/icon-192.png",
        badge: "icons/icon-192.png",
        vibrate: [200, 100, 200],
        tag: "cortana-" + Date.now(),
        renotify: true,
        data: { url: "./index.html" }
    };

    event.waitUntil(self.registration.showNotification(data.title, options));
});

self.addEventListener("notificationclick", event => {
    event.notification.close();
    event.waitUntil(
        clients.matchAll({ type: "window", includeUncontrolled: true }).then(list => {
            for (const c of list) {
                if (c.url.includes("index.html") && "focus" in c) return c.focus();
            }
            if (clients.openWindow) return clients.openWindow("./index.html");
        })
    );
});