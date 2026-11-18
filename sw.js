const CACHE = 'corsica-lib-static-v1';
const PUBLIC_ASSETS = ['/demo.html', '/icon.svg', '/manifest.webmanifest'];
self.addEventListener('install', event => { event.waitUntil(caches.open(CACHE).then(cache => cache.addAll(PUBLIC_ASSETS))); self.skipWaiting(); });
self.addEventListener('activate', event => { event.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(key => key.startsWith('corsica-lib-static-') && key !== CACHE).map(key => caches.delete(key))))); self.clients.claim(); });
self.addEventListener('fetch', event => { const req=event.request; const url=new URL(req.url); if(req.method!=='GET' || url.origin!==self.location.origin || !PUBLIC_ASSETS.includes(url.pathname)) return; event.respondWith(fetch(req).catch(()=>caches.match(req))); });