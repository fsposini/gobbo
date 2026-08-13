/* Gobbo — service worker
   La versione della cache DEVE coincidere con VERSIONE in index.html.
   Le due righe le allinea da sole PUBBLICA.bat: non modificarle a mano. */
const CACHE = "gobbo-v13";

const GUSCIO = [
  "./",
  "./index.html",
  "./manifest.webmanifest",
  "./icon-192.png",
  "./icon-512.png",
  "./icon-512-maskable.png",
  "./apple-touch-icon.png"
];

self.addEventListener("install", ev => {
  ev.waitUntil(
    caches.open(CACHE)
      .then(c => c.addAll(GUSCIO))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", ev => {
  ev.waitUntil(
    caches.keys()
      .then(nomi => Promise.all(nomi.filter(n => n !== CACHE).map(n => caches.delete(n))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", ev => {
  const req = ev.request;
  if (req.method !== "GET") return;

  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;

  // Prima la rete, sempre. La cache resta come rete di sicurezza quando non c'è
  // campo. Prima il guscio dell'app veniva servito dalla cache e le correzioni
  // non arrivavano mai al telefono: sembrava che i difetti non fossero riparati.
  ev.respondWith(
    fetch(req)
      .then(r => {
        const copia = r.clone();
        caches.open(CACHE).then(c => c.put(req, copia)).catch(() => {});
        return r;
      })
      .catch(() => caches.match(req, { ignoreSearch: true }))
  );
});
