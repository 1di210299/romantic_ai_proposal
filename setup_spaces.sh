#!/bin/bash
# Script para configurar DigitalOcean Spaces
# Ejecutar desde la raíz del proyecto

echo "🚀 Configurando DigitalOcean Spaces para Romantic AI Proposal"
echo "============================================================"

# Verificar que estamos en la raíz del proyecto
if [ ! -f "backend/app.py" ]; then
    echo "❌ Error: Ejecutar desde la raíz del proyecto (donde está la carpeta backend/)"
    exit 1
fi

# Verificar que existen los archivos JSON
if [ ! -d "karemramos_1184297046409691" ]; then
    echo "❌ Error: No se encuentra la carpeta karemramos_1184297046409691"
    exit 1
fi

echo "📂 Archivos JSON encontrados:"
ls -la karemramos_1184297046409691/message_*.json

echo ""
echo "📋 PASOS A SEGUIR:"
echo ""
echo "1. Ve a DigitalOcean → Spaces Object Storage"
echo "2. Create a Space:"
echo "   - Name: romantic-ai-data"
echo "   - Region: Same as your app (NYC3, SFO3, etc.)"
echo "   - File Listing: Restricted"
echo "   - CDN: Disabled (to save money)"
echo ""
echo "3. Una vez creado, sube estos archivos:"
echo "   - karemramos_1184297046409691/message_1.json"
echo "   - karemramos_1184297046409691/message_2.json"
echo "   - karemramos_1184297046409691/message_3.json"
echo "   - karemramos_1184297046409691/message_4.json"
echo ""
echo "4. La URL será algo como:"
echo "   https://romantic-ai-data.nyc3.digitaloceanspaces.com/message_1.json"
echo ""
echo "5. Copia esa URL base y configurala como variable de entorno:"
echo "   SPACES_DATA_URL=https://romantic-ai-data.REGION.digitaloceanspaces.com"
echo ""
echo "🔍 Información de archivos:"
du -h karemramos_1184297046409691/message_*.json
echo ""
echo "📊 Total size:"
du -ch karemramos_1184297046409691/message_*.json | tail -1

echo ""
echo "✅ Una vez subidos los archivos, el sistema los descargará automáticamente"
echo "💡 Los archivos se cachearán localmente para mejor rendimiento"