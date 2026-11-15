# Pendientes

## Seguridad de la autoactualización

La verificación sha256 (rama `feature/verificacion-sha256`) solo detecta descargas cortadas o dañadas. No impide que alguien haga pasar un exe falso como si fuera el publicado.

- [ ] **Pasar a HTTPS.** Hoy `MU_SERVER_URL` y `API_URL` usan `http://93.127.142.139`. Alguien en la misma red que el jugador (wifi pública, router comprometido) puede cambiar la respuesta de `/api/v2/launcher` y el exe descargado a la vez, con el sha incluido, y la verificación pasaría.
  - Se necesita un dominio que apunte al VPS (Let's Encrypt no emite certificados para una IP sola).
  - Poner un reverse proxy con certificado delante de la API, por ejemplo Caddy, que lo renueva solo. Cuando esté, configurar `TRUST_PROXY=loopback` en la API.
  - Cambiar `MU_SERVER_URL` en el `.env` de la API y `API_URL` / `MU_SERVER_URL` en el `.env` del launcher, recompilar y publicar.
  - Cerrar el puerto HTTP directo de la API, o redirigirlo a HTTPS.
  - Los launchers ya instalados tienen la URL `http` embebida: hay que mantener `http` funcionando hasta que todos se hayan actualizado a la versión con `https`.

- [ ] **Firmar los exe (code signing), opcional.** Protege incluso si alguien entra al VPS y reemplaza el exe, porque el launcher verificaría la firma y no solo el sha que da el mismo servidor. Además reduce los avisos de SmartScreen y del antivirus. Requiere comprar un certificado de firma de código.
