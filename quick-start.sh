#!/bin/bash

# Quick Start Guide - Romantic AI Proposal System
# Guía rápida para deployar tu sistema

set -e

echo "🎯 ROMANTIC AI PROPOSAL - QUICK START"
echo "====================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  PASO 1: Configurar credenciales"
    echo "   cp .env.example .env"
    echo "   # Edita .env y agrega tu OPENAI_API_KEY"
    echo ""
    echo "❌ Por favor completa este paso primero"
    exit 1
fi

# Check if API key is configured
if grep -q "your_openai_api_key_here" .env; then
    echo "⚠️  OPENAI_API_KEY no configurado en .env"
    echo "   Edita el archivo .env y agrega tu API key real"
    exit 1
fi

echo "✅ Credenciales configuradas"
echo ""

# Show deployment options
echo "🚀 OPCIONES DE DEPLOYMENT:"
echo ""
echo "1. Railway (GRATIS) - Recomendado para producción"
echo "   • Costo: $0/mes"
echo "   • Setup: 5 minutos"
echo "   • URL pública automática"
echo "   Comando: ./deploy-railway.sh"
echo ""

echo "2. Local (GRATIS) - Para desarrollo"
echo "   • Costo: $0"
echo "   • Setup: 2 minutos"
echo "   • Solo tu computadora"
echo "   Comando: ./start-system.sh"
echo ""

echo "3. Docker (GRATIS) - Para desarrollo avanzado"
echo "   • Costo: $0"
echo "   • Setup: 10 minutos"
echo "   • Requiere Docker instalado"
echo "   Comando: ./deploy-docker.sh"
echo ""

# Ask user what they want to do
echo "¿Qué quieres hacer?"
echo "1) Deploy en Railway (Recomendado)"
echo "2) Ejecutar localmente"
echo "3) Ejecutar con Docker"
echo "4) Solo mostrar información"
read -p "Elige una opción (1-4): " choice

case $choice in
    1)
        echo "🚆 Iniciando deployment en Railway..."
        ./deploy-railway.sh
        ;;
    2)
        echo "💻 Iniciando sistema localmente..."
        if [ ! -d "backend/venv" ]; then
            echo "Ejecutando setup inicial..."
            ./setup.sh
        fi
        ./start-system.sh
        ;;
    3)
        echo "🐳 Iniciando con Docker..."
        ./deploy-docker.sh
        ;;
    4)
        echo ""
        echo "📊 INFORMACIÓN DEL SISTEMA:"
        echo "=========================="
        echo "• Backend: Flask + OpenAI + RAG"
        echo "• Frontend: Next.js + React"
        echo "• Cache: 45MB (embeddings + índice FAISS)"
        echo "• RAM requerida: ~512MB"
        echo "• Storage: ~100MB"
        echo ""
        echo "📂 ARCHIVOS IMPORTANTES:"
        echo "• .env - Credenciales (configura primero)"
        echo "• backend/cache/ - Embeddings y chunks"
        echo "• karemramos_1184297046409691/ - Datos originales"
        echo ""
        echo "💰 COSTOS DE DEPLOYMENT:"
        echo "• Railway: $0/mes (recomendado)"
        echo "• Local: $0 (para desarrollo)"
        echo "• VPS: $6-12/mes (si necesitas más control)"
        ;;
    *)
        echo "❌ Opción inválida"
        exit 1
        ;;
esac