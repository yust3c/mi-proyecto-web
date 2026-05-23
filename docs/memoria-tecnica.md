# Memoria tecnica

## 1. Objetivo del proyecto

El objetivo es demostrar un flujo completo de despliegue con Docker y CI/CD sin depender de una aplicacion compleja. La solucion implementa un chat web sencillo con IA local usando Ollama, donde se puede explicar de forma clara:

- separacion por servicios;
- comunicacion entre contenedores;
- uso de Docker Compose;
- publicacion de imagenes en GHCR;
- despliegue automatico a una VM mediante GitHub Actions.

## 2. Arquitectura usada

La aplicacion se divide en cuatro servicios:

- `frontend`: interfaz web React.
- `backend`: API FastAPI.
- `ollama`: motor local de inferencia LLM.
- `nginx`: proxy inverso y punto de entrada externo.

Flujo de una peticion:

1. El usuario accede a `http://IP_DE_LA_VM/`.
2. Nginx redirige `/` al frontend.
3. El frontend envia el prompt a `POST /api/chat`.
4. Nginx reenvia `/api/chat` al backend.
5. El backend consulta `http://ollama:11434/api/generate`.
6. Ollama devuelve la respuesta.
7. El backend responde en JSON al frontend.

## 3. Justificacion de cada contenedor

### Frontend

Se separa para mantener desacoplada la capa de presentacion. Facilita rehacer la interfaz sin tocar el backend.

### Backend

Centraliza la logica de integracion con Ollama, las validaciones y el manejo de errores. Evita exponer directamente Ollama al navegador.

### Ollama

Permite ejecutar el modelo localmente en la VM sin depender de APIs externas. El volumen persistente evita tener que descargar el modelo en cada reinicio.

### Nginx

Actua como punto unico de entrada. Simplifica la exposicion del sistema, permitiendo publicar solo el puerto `80`.

## 4. Buenas practicas Docker aplicadas

- Uso de imagenes base ligeras: `python:3.12-slim`, `node:20-alpine`, `nginx:alpine`.
- Uso de `.dockerignore` para reducir contexto de build.
- Separacion entre dependencias y codigo para aprovechar la cache.
- Ejecucion del backend como usuario no root.
- Uso de variables de entorno para modelo, URL de Ollama y tags de imagen.
- Persistencia de datos de Ollama mediante volumen Docker.
- Healthchecks para backend y Ollama.
- Reinicio automatico en produccion con `restart: unless-stopped`.

## 5. Explicacion de Docker Compose

Se usan dos archivos:

- `docker-compose.yml`: orientado a desarrollo local, construye imagenes con `build`.
- `docker-compose.prod.yml`: orientado a produccion, usa imagenes publicadas en GHCR.

Ambos archivos definen la misma topologia base:

- red interna `ollama_net`;
- volumen `ollama_data`;
- dependencia del backend respecto a Ollama;
- publicacion externa solo de Nginx.

## 6. Explicacion del pipeline CI/CD

El pipeline de GitHub Actions se ejecuta cuando hay un push a `main`:

1. Hace checkout del repositorio.
2. Prepara Python.
3. Instala dependencias del backend.
4. Ejecuta tests con `pytest`.
5. Hace login en GHCR.
6. Construye y publica imagenes de frontend y backend.
7. Conecta por SSH a la VM.
8. Ejecuta `docker compose pull` y `docker compose up -d`.
9. Limpia imagenes antiguas con `docker image prune -f`.

Este flujo permite pasar de un commit en GitHub a un despliegue actualizado en la VM.

## 7. Diferencias entre entorno local y produccion

### Local

- Las imagenes se construyen desde el codigo fuente local.
- Se usa `docker-compose.yml`.
- Es ideal para pruebas y desarrollo rapido.

### Produccion

- Las imagenes se descargan desde GHCR.
- Se usa `docker-compose.prod.yml`.
- Se activa `restart: unless-stopped`.
- El despliegue se automatiza desde GitHub Actions.

## 8. Problemas encontrados o simulados y soluciones

### Ollama no responde todavia

Problema: el contenedor esta levantado, pero el servicio aun no esta listo.

Solucion: esperar el healthcheck y revisar logs de Ollama antes de probar el chat.

### Modelo no descargado

Problema: Ollama responde error de modelo inexistente.

Solucion: ejecutar `./scripts/pull-model.sh` y verificar con `docker compose exec ollama ollama list`.

### Puerto 80 ocupado

Problema: Nginx no puede arrancar porque otro servicio usa el puerto `80`.

Solucion: liberar el puerto o cambiar `NGINX_PORT` temporalmente.

### Usuario sin permisos Docker

Problema: el usuario de la VM no puede lanzar contenedores.

Solucion: anadir el usuario al grupo `docker` o usar un usuario con permisos adecuados.

## 9. Posibles mejoras futuras

- Guardar historial en una base de datos ligera como SQLite.
- Anadir streaming de respuestas del modelo.
- Incorporar observabilidad basica con Prometheus o logs estructurados.
- Proteger el despliegue con HTTPS usando Nginx y Let's Encrypt.
- Permitir seleccionar el modelo desde la interfaz web.
