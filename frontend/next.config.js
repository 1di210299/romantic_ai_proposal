/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  
  // Configuración de URLs
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_BACKEND_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000',
  },
  
  // Configuración para producción
  output: 'standalone', // ⭐ NUEVO - Mejor para deployment en DigitalOcean
  trailingSlash: false,
  generateEtags: false,
  
  // Asegurar que los assets se sirvan correctamente
  compress: true, // ⭐ NUEVO - Compresión para mejor performance
  poweredByHeader: false, // ⭐ NUEVO - Seguridad básica
}

module.exports = nextConfig