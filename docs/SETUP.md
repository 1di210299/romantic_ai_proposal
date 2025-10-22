# 🚀 Setup Guide - Romantic AI Proposal System

## Requisitos Previos

- Python 3.11+
- Node.js 18+ (para frontend)
- Cuenta de OpenAI con API key
- Git (para control de versiones)

## Instalación Backend

### 1. Configurar entorno virtual Python

```bash
cd romantic_ai_proposal/backend

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En macOS/Linux:
source venv/bin/activate
# En Windows:
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configurar variables de entorno

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar .env con tus valores:
# - OPENAI_API_KEY: Tu API key de OpenAI
# - FINAL_LATITUDE/LONGITUDE: Coordenadas donde estarás esperando
# - FINAL_ADDRESS: Dirección del lugar
```

### 3. Preparar datos de la relación

```bash
cd ../data

# Copiar template de preguntas
cp questions_template.json questions.json

# Editar questions.json con tus preguntas personalizadas
# Incluir:
# - Preguntas sobre momentos especiales
# - Respuestas correctas (con variaciones)
# - Pistas si se equivoca
# - Mensajes de éxito
```

### 4. Ejecutar servidor backend

```bash
cd ../backend
python app.py

# El servidor estará corriendo en http://localhost:5000
```

## Instalación Frontend (Próximamente)

### 1. Instalar dependencias

```bash
cd romantic_ai_proposal/frontend
npm install
```

### 2. Configurar variables de entorno

```bash
cp .env.example .env.local

# Editar con la URL del backend
# NEXT_PUBLIC_API_URL=http://localhost:5000
```

### 3. Ejecutar desarrollo

```bash
npm run dev

# La app estará en http://localhost:3000
```

## Preparar Datos de Conversaciones

Si tienes mensajes de WhatsApp, iMessage, etc. con tu enamorada:

### 1. Exportar conversaciones

- **WhatsApp**: Abrir chat → Más opciones → Exportar chat → Sin multimedia
- **iMessage**: Usar app de terceros o copiar manualmente
- **Telegram**: Settings → Advanced → Export Telegram data

### 2. Procesar mensajes (script próximamente)

```bash
python scripts/process_conversations.py \
  --input data/raw_messages.txt \
  --output data/conversation_history.json
```

Este script extraerá:
- Fechas importantes mencionadas
- Lugares que visitaron
- Frases especiales o inside jokes
- Temas recurrentes
- Estilo de comunicación

### 3. Usar datos para personalizar

Los datos procesados se usarán para:
- Generar preguntas automáticamente
- Entrenar el contexto del chatbot
- Validar respuestas con mayor flexibilidad

## Testing

### Backend

```bash
cd backend
pytest tests/ -v
```

### Frontend

```bash
cd frontend
npm test
```

## Deployment (Para el día especial)

### Opción 1: Localhost (Más simple)

1. Tener laptop contigo
2. Iniciar servidor antes de que ella llegue
3. Enviarle link: `http://tu-ip-local:5000`

### Opción 2: Heroku/Render (Más profesional)

```bash
# Próximamente: Instrucciones de deployment
```

## Troubleshooting

### Error: "OpenAI API key not found"

```bash
# Verificar que .env existe
ls backend/.env

# Verificar contenido
cat backend/.env | grep OPENAI_API_KEY
```

### Error: "Module not found"

```bash
# Reinstalar dependencias
cd backend
pip install -r requirements.txt --force-reinstall
```

### El chatbot responde raro

- Verificar que `data/questions.json` tiene el formato correcto
- Revisar que el contexto en el system prompt es adecuado
- Ajustar temperatura del modelo (0.7-0.9 para más variación)

## Próximos Pasos

1. ✅ Setup completado
2. ⬜ Personalizar preguntas en `data/questions.json`
3. ⬜ Importar conversaciones (opcional)
4. ⬜ Probar el flujo completo
5. ⬜ Preparar ubicación final
6. ⬜ ¡Hacer la propuesta! 💕

---

**¿Necesitas ayuda?** Revisa los logs en `backend/app.log` o contacta al desarrollador.
