#!/bin/bash
# Script para subir archivos automáticamente a DigitalOcean Spaces
# Requiere: s3cmd o doctl

echo "🚀 Subiendo archivos JSON a DigitalOcean Spaces"
echo "=============================================="

# Configuración
SPACE_NAME="romantic-ai-data"
REGION="sfo3"
ENDPOINT="https://${REGION}.digitaloceanspaces.com"
SPACE_URL="https://${SPACE_NAME}.${REGION}.digitaloceanspaces.com"

# Verificar que existen los archivos
JSON_DIR="karemramos_1184297046409691"
if [ ! -d "$JSON_DIR" ]; then
    echo "❌ Error: No se encuentra la carpeta $JSON_DIR"
    exit 1
fi

# Archivos a subir
FILES=("message_1.json" "message_2.json" "message_3.json" "message_4.json")

echo "📂 Archivos a subir:"
for file in "${FILES[@]}"; do
    if [ -f "$JSON_DIR/$file" ]; then
        echo "  ✅ $file ($(du -h "$JSON_DIR/$file" | cut -f1))"
    else
        echo "  ❌ $file (no encontrado)"
        exit 1
    fi
done

echo ""
echo "🔧 OPCIÓN 1: Usando s3cmd (recomendado)"
echo "======================================="
echo "1. Instalar s3cmd:"
echo "   brew install s3cmd"
echo ""
echo "2. Configurar s3cmd para DigitalOcean:"
echo "   s3cmd --configure"
echo "   - Access Key: Tu Access Key de DigitalOcean"
echo "   - Secret Key: Tu Secret Key de DigitalOcean"
echo "   - S3 Endpoint: ${REGION}.digitaloceanspaces.com"
echo "   - DNS-style bucket+hostname: ${SPACE_NAME}.${REGION}.digitaloceanspaces.com"
echo ""
echo "3. Subir archivos:"
for file in "${FILES[@]}"; do
    echo "   s3cmd put $JSON_DIR/$file s3://$SPACE_NAME/$file --acl-public"
done

echo ""
echo "🔧 OPCIÓN 2: Usando doctl"
echo "========================"
echo "1. Instalar doctl:"
echo "   brew install doctl"
echo ""
echo "2. Autenticar:"
echo "   doctl auth init"
echo ""
echo "3. Subir archivos:"
for file in "${FILES[@]}"; do
    echo "   doctl spaces cp $JSON_DIR/$file spaces://$SPACE_NAME/$file --acl public-read"
done

echo ""
echo "🔧 OPCIÓN 3: Manual (más fácil)"
echo "==============================="
echo "1. Ve a: https://cloud.digitalocean.com/spaces/$SPACE_NAME"
echo "2. Arrastra los archivos desde la carpeta $JSON_DIR/"
echo "3. Los archivos estarán disponibles en:"
for file in "${FILES[@]}"; do
    echo "   $SPACE_URL/$file"
done

echo ""
echo "✅ Después de subir, verifica que los archivos estén accesibles:"
echo "curl -I $SPACE_URL/message_1.json"

echo ""
echo "🚀 Una vez subidos, el sistema los descargará automáticamente en el próximo deploy"