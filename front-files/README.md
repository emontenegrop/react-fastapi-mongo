# Información del proyecto

En el directorio del proyecto, puedes ejecutar:

### `npm start`

Ejecuta la aplicación en modo de desarrollo.\
Abre [http://localhost:3000](http://localhost:3000) para verla en tu navegador.
La página se recargará al realizar cambios.\
También puedes ver errores de lint en la consola.

### `npm test`

Inicia el ejecutor de pruebas en modo de observación interactiva.\
Consulta la sección sobre [ejecución de pruebas](https://facebook.github.io/create-react-app/docs/running-tests) para obtener más información.

### `npm run build`

Compila la aplicación para producción en la carpeta `build`.
Empaqueta React correctamente en modo de producción y optimiza la compilación para obtener el mejor rendimiento.

La compilación se minimiza y los nombres de archivo incluyen los hashes.

¡Tu aplicación está lista para implementarse!

Consulta la sección sobre [implementación](https://facebook.github.io/create-react-app/docs/deployment) para más información.


# Dependencias Esenciales

Necesitarás instalar las siguientes dependencias:
Bash

    npm install react react-dom react-router-dom axios formik yup tailwindcss

react-router-dom: Para la gestión de rutas.

axios: Para realizar peticiones HTTP a la API.

formik y yup: Para una gestión robusta de formularios y validaciones.

tailwindcss: Para estilos rápidos y modernos.


# Instalar TailwindCSS

Primero, necesitas instalar Tailwind CSS, PostCSS y Autoprefixer. Abre tu terminal en la raíz de tu proyecto React y ejecuta el siguiente comando:
Bash

    npm install -D tailwindcss postcss autoprefixer

# Inicializar TailwindCSS

Después de la instalación, genera los archivos de configuración de Tailwind CSS y PostCSS:
Bash

    npx tailwindcss init -p

Esto creará dos archivos en la raíz de tu proyecto:

    tailwind.config.js: Aquí es donde configurarás tus rutas de archivos para que Tailwind pueda escanear las clases que estás usando.

    postcss.config.js: Este archivo es necesario para que PostCSS procese los estilos de Tailwind.


# Revertir a una Versión Estable de TailwindCSS

Este es el paso más importante. Desinstalaremos tu versión actual y luego instalaremos una que sea conocida por ser estable (por ejemplo, cualquier versión de la serie 3.4.x).
Bash

# 1. Desinstala la versión actual de TailwindCSS
npm uninstall tailwindcss postcss autoprefixer

# 2. Instala una versión estable conocida (por ejemplo, ^3.4.0)
#    El ^ significa "la última versión menor compatible con 3.4.0"
npm install -D tailwindcss@^3.4.0 postcss autoprefixer

# 3. Intenta inicializar de nuevo
npx tailwindcss init -p

└> npx tailwindcss init -p

Created Tailwind CSS config file: tailwind.config.js
Created PostCSS config file: postcss.config.js


¡Claro! Configurar TailwindCSS en un proyecto React es un proceso sencillo. Te guiaré paso a paso para que puedas empezar a estilizar tus componentes con esta potente herramienta.

1. Instalar TailwindCSS

Primero, necesitas instalar Tailwind CSS, PostCSS y Autoprefixer. Abre tu terminal en la raíz de tu proyecto React y ejecuta el siguiente comando:
Bash

npm install -D tailwindcss postcss autoprefixer

2. Inicializar TailwindCSS

Después de la instalación, genera los archivos de configuración de Tailwind CSS y PostCSS:
Bash

npx tailwindcss init -p

Esto creará dos archivos en la raíz de tu proyecto:

    tailwind.config.js: Aquí es donde configurarás tus rutas de archivos para que Tailwind pueda escanear las clases que estás usando.

    postcss.config.js: Este archivo es necesario para que PostCSS procese los estilos de Tailwind.

# Configurar Rutas en tailwind.config.js

Abre tailwind.config.js y configura la propiedad content. Esto le dice a Tailwind dónde buscar tus archivos HTML/JSX para generar las clases CSS necesarias.
JavaScript

// tailwind.config.js
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}", // Esto es importante: escaneará todos los archivos JS, TS, JSX, TSX en la carpeta src
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
