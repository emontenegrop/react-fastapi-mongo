FROM node:22.17.1-alpine

RUN mkdir /app

WORKDIR /app

# Copiamos solo package.json primero para cachear instalación
COPY ./front-end/package*.json ./

RUN npm install

# Copiamos el resto del proyecto
COPY ./front-end .

# Hot reload
ENV CHOKIDAR_USEPOLLING=true
ENV WATCHPACK_POLLING=true

EXPOSE 5173

CMD ["npm", "run", "dev"]
