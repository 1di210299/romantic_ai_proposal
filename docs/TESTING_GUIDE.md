# 🚀 Guía de Pruebas con OpenAI

## 📋 Paso 1: Obtener tu API Key de OpenAI

### Opción A: Ya tienes cuenta en OpenAI
1. Ve a: https://platform.openai.com/api-keys
2. Inicia sesión
3. Clic en "Create new secret key"
4. Copia la key (¡guárdala! no podrás verla después)

### Opción B: Nueva cuenta
1. Ve a: https://platform.openai.com/signup
2. Crea tu cuenta (puedes usar Gmail)
3. Verifica tu email
4. Ve a: https://platform.openai.com/api-keys
5. Crea una API key
6. **IMPORTANTE:** Agrega créditos a tu cuenta
   - Ve a: https://platform.openai.com/account/billing
   - Agrega $5-10 USD (suficiente para todo el proyecto)

---

## 📝 Paso 2: Configurar el archivo .env

### 2.1 Abrir el archivo
```bash
code .env
```

### 2.2 Pegar tu API key
```bash
# OpenAI API Configuration
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxx  # ← PEGA TU KEY AQUÍ

# Flask Configuration
FLASK_DEBUG=True
FLASK_ENV=development
SECRET_KEY=dev-secret-key-romantic-ai-2025

# Final Location Configuration
FINAL_LATITUDE=19.4326
FINAL_LONGITUDE=-99.1332
FINAL_ADDRESS=Lugar especial donde estaré esperando
```

### 2.3 Guardar el archivo
`Cmd + S` (Mac) o `Ctrl + S` (Windows/Linux)

---

## 🧪 Paso 3: Ejecutar Prueba (RECOMENDADO)

### Prueba pequeña primero (500 mensajes, ~$0.10)

```bash
cd /Users/juandiegogutierrezcortez/romantic_ai_proposal
python3 scripts/test_openai.py
```

**Esto va a:**
1. ✅ Verificar que tu API key funcione
2. ✅ Analizar solo 500 mensajes (rápido)
3. ✅ Generar 7 preguntas de prueba
4. ✅ Mostrarte el costo real
5. ✅ Crear archivos de prueba

**Costo aproximado:** $0.05 - $0.15 USD

---

## 🚀 Paso 4: Análisis Completo (Opcional)

Si la prueba funciona bien, ejecuta el análisis completo:

```bash
python3 scripts/run_openai_analysis.py
```

**Esto va a:**
- Analizar TODOS los 33,622 mensajes
- Generar preguntas más precisas
- Costo: ~$2-5 USD

---

## 📊 Qué esperar

### Durante el análisis verás:
```
🚀 ANÁLISIS COMPLETO CON OPENAI
======================================================================
📂 Cargando mensajes...
   ✓ 10,000 mensajes
   ✓ 10,000 mensajes
   ...

📦 Creando chunks de 100 mensajes...
✅ 5 chunks creados

🤖 Analizando chunk 1 con OpenAI...
   ✓ Chunk 1 analizado (1,234 tokens)
🤖 Analizando chunk 2 con OpenAI...
   ✓ Chunk 2 analizado (1,156 tokens)
...

💡 Generando preguntas personalizadas con OpenAI...
✅ 7 preguntas generadas (2,345 tokens)
💰 Costo aproximado: $0.0234
```

### Al finalizar obtendrás:
```
📄 ARCHIVOS GENERADOS:
   1. data/openai_analysis.json - Análisis completo
   2. data/questions_generated.json - Preguntas listas
```

---

## 🔍 Verificar Resultados

### Revisar las preguntas generadas:
```bash
cat data/questions_generated.json | less
```

O abrir en VS Code:
```bash
code data/questions_generated.json
```

### Ejemplo de pregunta generada:
```json
{
  "id": 1,
  "question": "¿Dónde pasamos más tiempo juntos según nuestros mensajes?",
  "category": "lugares",
  "difficulty": "medium",
  "correct_answers": [
    "la universidad",
    "la U",
    "universidad"
  ],
  "hints": [
    "Es un lugar donde aprendemos cosas nuevas...",
    "Es donde nos vemos casi todos los días...",
    "Es la universidad"
  ],
  "success_message": "¡Exacto! La U es nuestro lugar. Ahí empezó todo... 💕",
  "context": "Mencionaron 'universidad' o 'U' más de 15,000 veces",
  "why_important": "Es el lugar más significativo de su relación"
}
```

---

## 💰 Costos Estimados

| Análisis | Mensajes | Costo Aproximado |
|----------|----------|------------------|
| **Prueba** | 500 | $0.05 - $0.15 |
| **Completo** | 33,622 | $2.00 - $5.00 |
| **Uso del chatbot** | Por sesión | $0.10 - $0.30 |

**Total para todo el proyecto:** ~$5-10 USD

---

## ❓ Troubleshooting

### Error: "OPENAI_API_KEY not found"
**Solución:**
```bash
# Verifica que el archivo .env existe
ls -la .env

# Verifica que tiene tu key
cat .env | grep OPENAI_API_KEY

# Asegúrate de estar en la carpeta correcta
pwd
# Debe mostrar: /Users/juandiegogutierrezcortez/romantic_ai_proposal
```

### Error: "Insufficient credits"
**Solución:**
1. Ve a: https://platform.openai.com/account/billing
2. Agrega $5-10 USD de créditos
3. Espera 1-2 minutos
4. Intenta de nuevo

### Error: "Rate limit exceeded"
**Solución:**
- Espera 1 minuto
- Intenta de nuevo
- El script automáticamente tiene pausas entre requests

### Error: "Invalid API key"
**Solución:**
1. Verifica que copiaste la key completa
2. Asegúrate de que no tenga espacios al inicio/final
3. Genera una nueva key en: https://platform.openai.com/api-keys

---

## ✅ Checklist de Prueba

Antes de ejecutar, verifica:

- [ ] Archivo `.env` creado
- [ ] API key de OpenAI pegada en `.env`
- [ ] Créditos agregados a tu cuenta de OpenAI
- [ ] Estás en la carpeta correcta del proyecto
- [ ] Python 3.9+ instalado
- [ ] Dependencias instaladas (`pip install openai python-dotenv`)

---

## 🎯 Siguiente Paso

Una vez que las pruebas funcionen:

```bash
# Ver las preguntas generadas
code data/questions_generated.json

# Si te gustan, cópialas al archivo principal
cp data/questions_generated.json data/questions.json

# Luego configura el backend para usar las preguntas
cd backend
python app.py
```

---

## 💡 Pro Tips

1. **Empieza con la prueba pequeña** (500 mensajes)
2. **Revisa los resultados** antes del análisis completo
3. **Las preguntas se pueden editar** manualmente después
4. **Guarda tus archivos de análisis** como respaldo
5. **Puedes re-ejecutar** cuantas veces quieras

---

## 📞 Si necesitas ayuda

**Errores comunes y soluciones:**
- API key inválida → Genera una nueva
- Sin créditos → Agrega $5 en OpenAI
- Import errors → Instala dependencias con `pip install openai`

**Listo para empezar!** 🚀

```bash
python3 scripts/test_openai.py
```
