#!/usr/bin/env python3
"""
Script para ejecutar el análisis completo con OpenAI desde el backend.
Este script debe ejecutarse UNA VEZ para generar las preguntas.
"""

import sys
import os

# Agregar el directorio backend al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from services.openai_analyzer import OpenAIMessageAnalyzer, main

if __name__ == "__main__":
    print("🚀 Iniciando análisis con OpenAI desde backend...")
    print("📌 Este script generará preguntas personalizadas automáticamente\n")
    main()
