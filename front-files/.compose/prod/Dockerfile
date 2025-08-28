# Etapa 1: build
FROM docker.io/library/node:22.17.1-alpine AS builder

RUN mkdir /app

WORKDIR /app

# Actualizar npm a la última versión globalmente
RUN npm install -g npm@latest

COPY ./front-end/package*.json ./
RUN npm install

COPY ./front-end .
RUN npm run build

# Etapa 2: producción
FROM docker.io/library/nginx:alpine

ENV TZ=America/Guayaquil

# Copiar el build al directorio público de nginx
COPY --from=builder /app/dist /usr/share/nginx/html

# Copiar configuración personalizada de nginx
COPY ./front-end/.compose/prod/nginx.conf /etc/nginx/conf.d/default.conf

# Exponer el puerto 80 interno (Nginx)
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]