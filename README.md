# 💕 Romantic AI Proposal System

Sistema de propuesta romántica interactivo usando inteligencia artificial - Un chatbot personalizado que guía a tu enamorada a través de un rally/trivia sobre su relación.

## 🎯 Concepto

Un chatbot conversacional que:
- Hace preguntas sobre momentos especiales de la relación
- Valida respuestas y da pistas si son incorrectas
- Progresa secuencialmente solo con respuestas correctas
- Revela una ubicación GPS al final donde estarás esperando

## 📁 Estructura del Proyecto

```
romantic_ai_proposal/
├── backend/                # API Flask/FastAPI con OpenAI
│   ├── app.py             # Aplicación principal
│   ├── models.py          # Modelos de datos
│   ├── services/          # Lógica de negocio
│   │   ├── chatbot.py     # Integración OpenAI
│   │   ├── quiz.py        # Sistema de preguntas
│   │   └── validation.py  # Validación de respuestas
│   └── requirements.txt   # Dependencias Python
│
├── frontend/              # Interfaz web (React/Next.js)
│   ├── components/        # Componentes UI
│   │   ├── ChatInterface.tsx
│   │   ├── QuestionCard.tsx
│   │   └── LocationReveal.tsx
│   └── package.json
│
├── data/                  # Datos de la relación
│   ├── conversation_history.json  # Mensajes con tu enamorada
│   ├── questions.json     # Preguntas del quiz
│   └── training_data.json # Datos para entrenar el contexto
│
└── docs/
    ├── SETUP.md          # Instrucciones de instalación
    └── API.md            # Documentación de API

```

## 🚀 Estado del Proyecto

- [x] Estructura de carpetas creada
- [ ] Backend API implementado
- [ ] Sistema de chatbot con OpenAI
- [ ] Base de datos de preguntas
- [ ] Interfaz frontend
- [ ] Sistema de validación de respuestas
- [ ] Integración con ubicación GPS
- [ ] Importar datos de conversaciones

## 🔧 Próximos Pasos

1. **Importar datos**: Procesar mensajes con tu enamorada
2. **Crear preguntas**: Definir el quiz personalizado
3. **Implementar backend**: API con Flask + OpenAI
4. **Construir frontend**: Interfaz de chat interactiva
5. **Probar y desplegar**: Verificar todo funciona antes del día especial

## 🎨 Características Planeadas

- ✨ Respuestas conversacionales naturales con OpenAI GPT-4
- 🎯 Validación inteligente (acepta variaciones de respuestas correctas)
- 📍 Revelación progresiva de pistas
- 🗺️ Integración con Google Maps para ubicación final
- 💾 Guardado de progreso (puede pausar y continuar)
- 🎵 Posibilidad de incluir música de fondo
- 📸 Opción de mostrar fotos en cada pregunta correcta

## 📝 Notas

Este es un proyecto personal y privado. Los datos de conversaciones serán procesados localmente y solo se usarán para entrenar el contexto del chatbot de manera privada y segura.

---

**Creado con ❤️ para una propuesta especial**
