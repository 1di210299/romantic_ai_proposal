# 💕 Sistema de Propuesta Romántica con IA

## ¿Qué es esto?

Un chatbot personalizado que usa **Inteligencia Artificial (OpenAI GPT-4)** para crear un **rally/trivia romántico** sobre tu relación. Tu enamorada responde preguntas sobre momentos especiales que han vivido juntos, y al final se revela una ubicación GPS donde tú estarás esperando para hacerle la propuesta. 🎉

---

## ✅ Lo que ya está listo

### 1. **Backend completo** (`backend/`)
- ✅ API REST con Flask
- ✅ Integración con OpenAI GPT-4
- ✅ Sistema de validación inteligente de respuestas
- ✅ Chatbot conversacional con personalidad romántica
- ✅ Endpoints para iniciar quiz, procesar respuestas, revelar ubicación

### 2. **Scripts de procesamiento** (`scripts/`)
- ✅ `process_instagram.py` - Analiza tus mensajes de Instagram DM
- ✅ `process_messages.py` - Analiza exportaciones de WhatsApp
- ✅ Extracción automática de fechas importantes
- ✅ Identificación de lugares mencionados
- ✅ Análisis de frases especiales y apodos

### 3. **Datos y configuración** (`data/`)
- ✅ Template de preguntas personalizables
- ✅ Tus datos de Instagram ya importados
- ⏳ Pendiente: Personalizar las preguntas

### 4. **Documentación completa** (`docs/`)
- ✅ Guía de instalación paso a paso
- ✅ Instrucciones de uso
- ✅ Ejemplos y troubleshooting

---

## 🎯 Cómo funciona

```
┌─────────────────────────────────────────────────────────┐
│  1. Ella abre el link del chatbot                       │
│     "¡Hola mi amor! Tengo una sorpresa para ti..."      │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│  2. El chatbot le hace preguntas sobre su relación      │
│     "¿Recuerdas dónde nos conocimos?"                   │
│     Respuesta correcta → Siguiente pregunta             │
│     Respuesta incorrecta → Pista sutil                  │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│  3. Al responder todas correctamente...                 │
│     "¡Lo lograste! 🎉 Tengo algo especial para ti..."   │
│     [REVELA UBICACIÓN GPS]                              │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│  4. Ella llega al lugar y tú estás ahí esperando        │
│     Con flores, anillo, lo que quieras... 💍            │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 Próximos pasos (LO QUE TÚ NECESITAS HACER)

### Paso 1: Analizar tus mensajes de Instagram ⏳

```bash
cd romantic_ai_proposal
python scripts/process_instagram.py
```

Este script va a:
- ✅ Leer todos tus mensajes de Instagram con ella
- ✅ Extraer fechas importantes mencionadas
- ✅ Identificar lugares que visitaron juntos
- ✅ Analizar frases especiales y apodos
- ✅ Generar sugerencias de preguntas

**Te va a preguntar:**
- Su nombre en Instagram (como aparece en tus DMs)
- Tu nombre en Instagram

### Paso 2: Crear preguntas personalizadas 📝

Después del análisis, abre `data/questions.json` y personaliza:

```json
{
  "question": "¿En qué lugar nos conocimos por primera vez?",
  "correct_answers": [
    "Cafetería Central Universidad",
    "La cafetería de la U",
    "Café de la universidad"
  ],
  "hints": [
    "Fue en un lugar con mucho café ☕",
    "Fue en la universidad..."
  ],
  "success_message": "¡Sí! Ese día cambió mi vida 💕"
}
```

**Ejemplo de preguntas que puedes hacer:**
1. ¿Dónde nos conocimos?
2. ¿Qué día fue nuestra primera cita?
3. ¿Cuál es nuestra canción favorita?
4. ¿Cuál fue mi primer apodo para ti?
5. ¿Qué te dije cuando te confesé que me gustabas?

### Paso 3: Configurar tu API key de OpenAI 🔑

```bash
cd backend
cp .env.example .env
nano .env  # o usa cualquier editor
```

Edita el archivo `.env`:
```bash
OPENAI_API_KEY=sk-tu-api-key-de-openai-aqui
FINAL_LATITUDE=19.4326  # Tu ubicación exacta
FINAL_LONGITUDE=-99.1332
FINAL_ADDRESS="Parque Central, bajo el árbol grande"
```

**¿No tienes API key?**
1. Ve a https://platform.openai.com/
2. Crea una cuenta
3. Ve a API Keys → Create new key
4. Copia la key a tu `.env`

**Costo aproximado:** $0.50 - $2 USD por sesión completa del quiz

### Paso 4: Instalar dependencias y probar 🧪

```bash
cd backend

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En macOS

# Instalar
pip install -r requirements.txt

# Probar el servidor
python app.py
```

Si ves esto, está funcionando:
```
* Running on http://0.0.0.0:5000
```

### Paso 5: Probar el chatbot 🎮

Abre tu navegador y prueba los endpoints:

**Iniciar sesión:**
```bash
curl -X POST http://localhost:5000/api/start-quiz \
  -H "Content-Type: application/json" \
  -d '{"user_name": "María"}'
```

**Enviar mensaje:**
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "el-session-id-que-te-dio", "message": "Cafetería Central"}'
```

### Paso 6: Crear interfaz (OPCIONAL) 🎨

Si quieres una interfaz bonita en lugar de solo API:

**Opción A: Usar un frontend simple HTML/JavaScript** (fácil)
- Te puedo ayudar a crear una página web simple

**Opción B: Usar WhatsApp/Telegram Bot** (medio)
- El chatbot se integra directamente con WhatsApp

**Opción C: Crear app React/Next.js** (avanzado)
- Interfaz profesional con componentes modernos

¿Cuál prefieres?

---

## ❓ Preguntas Frecuentes

### ¿Necesito saber programar?
No mucho. Solo necesitas:
- Copiar/pegar comandos en la terminal
- Editar archivos JSON (muy simple)
- Seguir las instrucciones paso a paso

### ¿Cuánto cuesta?
- **OpenAI API:** ~$0.50-$2 por sesión completa
- **Hosting:** Gratis (puedes correrlo en tu laptop)
- **Todo lo demás:** Gratis y open source

### ¿Qué pasa si ella se equivoca mucho?
El chatbot le da pistas progresivamente más específicas. Después de 2-3 intentos, prácticamente le dice la respuesta de forma romántica.

### ¿Puedo probarlo antes?
¡SÍ! Debes probarlo completo al menos 2-3 veces antes del día real para asegurar que todo funciona.

### ¿Y si no tengo API key de OpenAI?
Puedes hacer una versión más simple sin IA, solo con respuestas predefinidas. Te ayudo a adaptarlo.

---

## 📊 Estructura del Proyecto

```
romantic_ai_proposal/
├── 📄 README_ES.md              ← ESTÁS AQUÍ
├── 📄 README.md                 (versión inglés)
│
├── 🔧 backend/                  ← CEREBRO DEL SISTEMA
│   ├── app.py                   API principal (Flask)
│   ├── requirements.txt         Dependencias Python
│   ├── .env.example             Template de configuración
│   └── services/
│       └── chatbot.py           Lógica de IA con OpenAI
│
├── 📊 data/                     ← TUS DATOS PERSONALES
│   ├── questions.json           [EDITA ESTO] Tus preguntas
│   ├── instagram_analysis.json  Análisis automático de mensajes
│   └── raw_messages.txt         Backup de conversaciones
│
├── 🛠️ scripts/                  ← HERRAMIENTAS
│   ├── process_instagram.py     Analiza mensajes de Instagram
│   └── process_messages.py      Analiza exportación WhatsApp
│
├── 📱 frontend/                 ← INTERFAZ (opcional)
│   └── (próximamente)
│
├── 📚 docs/                     ← DOCUMENTACIÓN
│   └── SETUP.md                 Guía de instalación detallada
│
└── 📁 instagram_export/         ← TUS DATOS DE INSTAGRAM
    └── your_instagram_activity/
        └── messages/
```

---

## 💡 Ideas Extra (Opcional)

### Agregar fotos en cada pregunta
Mostrar una foto especial al responder correctamente cada pregunta.

### Música de fondo
Incluir tu canción favorita que se reproduce al final.

### Video mensaje
En lugar de solo texto final, un video tuyo diciendo algo especial.

### Múltiples ubicaciones
En lugar de una ubicación final, hacer que visite varios lugares (rally más largo).

### Compartir en redes
Después de la propuesta, generar un resumen bonito para compartir en redes sociales.

---

## 🆘 ¿Necesitas Ayuda?

**Si tienes dudas:**
1. Lee `docs/SETUP.md` (más detallado)
2. Revisa los comentarios en el código
3. Pregúntame lo que necesites

**Logs útiles:**
```bash
# Ver errores del backend
cd backend
python app.py

# Los errores aparecerán en la terminal
```

---

## 📅 Timeline Sugerido

**2 semanas antes:**
- ✅ Analizar mensajes de Instagram
- ✅ Crear preguntas personalizadas
- ✅ Configurar OpenAI API

**1 semana antes:**
- Probar el sistema completo 3 veces
- Ajustar dificultad de preguntas
- Verificar coordenadas GPS

**1 día antes:**
- Prueba final completa
- Preparar backup (por si algo falla)
- Confirmar ubicación final

**El día:**
- Iniciar servidor 1 hora antes
- Enviarle el link
- ¡Estar en la ubicación final esperando! 💕

---

**¡Éxito con tu propuesta! 🎉💍**

*Este proyecto fue creado con ❤️ para ayudarte a hacer una propuesta memorable usando tecnología e inteligencia artificial.*
