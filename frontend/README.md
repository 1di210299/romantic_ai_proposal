# Frontend - React/Next.js

Este es el frontend del proyecto de propuesta romántica con IA.

## 🚀 Instalación

```bash
cd frontend
npm install
```

## 🏃‍♂️ Ejecutar en desarrollo

```bash
npm run dev
```

El frontend estará disponible en: `http://localhost:3000`

## 🔧 Configuración

Asegúrate de que el backend esté corriendo en `http://localhost:5001`

Si necesitas cambiar la URL del backend, edita el archivo `.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:5001
```

## 📦 Build para producción

```bash
npm run build
npm start
```

## 🎨 Características

- ✨ Interfaz de chat interactiva
- 💕 Diseño romántico con gradientes
- 📱 Responsive (funciona en móvil y desktop)
- ⚡ Animaciones suaves
- 🗺️ Integración con Google Maps
- 🎯 Sistema de preguntas dinámicas

## 🛠️ Tecnologías

- **Next.js 14** - Framework de React
- **TypeScript** - Tipado estático
- **Tailwind CSS** - Estilos
- **Axios** - Cliente HTTP

## 📱 Uso

1. El usuario ve un mensaje de bienvenida
2. Al responder, comienza el quiz
3. El backend genera preguntas personalizadas con OpenAI
4. El usuario responde cada pregunta
5. Al completar todas las preguntas correctamente, se revela la ubicación GPS

## 🚀 Deploy

Este proyecto está listo para desplegarse en Vercel:

```bash
npm install -g vercel
vercel
```

Sigue las instrucciones para conectar tu repositorio y desplegar.
