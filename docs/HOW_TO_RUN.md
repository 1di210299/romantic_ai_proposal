# 🚀 Cómo Ejecutar el Proyecto Completo

## ✅ Prerequisitos

Ya tienes todo configurado:
- ✅ Backend con Flask
- ✅ Frontend con React/Next.js
- ✅ OpenAI API configurada
- ✅ Dependencias instaladas

---

## 🎯 Paso 1: Iniciar el Backend

Abre una terminal y ejecuta:

```bash
cd /Users/juandiegogutierrezcortez/romantic_ai_proposal/backend
python3 app.py
```

Deberías ver:
```
 * Running on http://127.0.0.1:5001
```

✅ **Backend listo en:** `http://localhost:5001`

---

## 🎨 Paso 2: Iniciar el Frontend

Abre **OTRA terminal** (nueva pestaña) y ejecuta:

```bash
cd /Users/juandiegogutierrezcortez/romantic_ai_proposal/frontend
npm run dev
```

Deberías ver:
```
  ▲ Next.js 14.x.x
  - Local:        http://localhost:3000
  - Ready in Xms
```

✅ **Frontend listo en:** `http://localhost:3000`

---

## 🧪 Paso 3: Probar la Aplicación

1. **Abre tu navegador** en: `http://localhost:3000`

2. **Verás el mensaje de bienvenida** del bot:
   ```
   ¡Hola! 💕 Bienvenida a esta sorpresa especial. 
   Voy a hacerte algunas preguntas sobre nuestra historia juntos. 
   ¿Lista para comenzar?
   ```

3. **Escribe cualquier cosa** (ej: "Sí", "Lista", etc.) para iniciar

4. **El bot generará 7 preguntas personalizadas** usando OpenAI y tus mensajes

5. **Responde cada pregunta:**
   - ✅ Si es correcta → Siguiente pregunta
   - ❌ Si es incorrecta → Pista después de 2 intentos
   - 💡 Sistema de pistas inteligente

6. **Al completar todas las preguntas:**
   - 🎉 Mensaje de felicitación
   - 📍 Coordenadas GPS reveladas
   - 🗺️ Link a Google Maps

---

## 📱 Cómo se ve

### Pantalla Principal
```
┌──────────────────────────────────────┐
│ 💕 Una Sorpresa Especial             │
│ Pregunta 1 de 7                      │
├──────────────────────────────────────┤
│                                      │
│  🤖 Bot:                             │
│  ¡Hola! 💕 Bienvenida...            │
│                                      │
│  👤 Tú:                              │
│  Sí! Estoy lista 😊                  │
│                                      │
│  🤖 Bot:                             │
│  Pregunta 1/7:                       │
│  ¿Cómo me llamabas cariñosamente?    │
│                                      │
├──────────────────────────────────────┤
│  [Escribe tu respuesta...] [Enviar] │
└──────────────────────────────────────┘
```

### Cuando Completa el Quiz
```
┌──────────────────────────────────────┐
│ 🎉 ¡Felicidades!                     │
│ Has completado todas las preguntas   │
│                                      │
│ 📍 Ubicación revelada:               │
│ Latitud: -12.0xxx                    │
│ Longitud: -77.0xxx                   │
│                                      │
│ 🗺️ Ver en Google Maps:               │
│ [Link a Google Maps]                 │
└──────────────────────────────────────┘
```

---

## 🔧 Solución de Problemas

### El backend no inicia
```bash
# Verifica que el puerto 5001 esté libre
lsof -i :5001

# Si está ocupado, mata el proceso
kill -9 <PID>
```

### El frontend no se conecta al backend
1. Verifica que el backend esté corriendo
2. Revisa el archivo `.env.local` en frontend:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:5001
   ```

### Error de CORS
El backend ya tiene CORS configurado. Si hay problemas:
- Reinicia el backend
- Limpia el caché del navegador (Cmd+Shift+R)

---

## 💰 Costos

Cada vez que alguien inicia el quiz:
- **Análisis de mensajes:** ~$0.03 USD
- **Generación de preguntas:** ~$0.03 USD
- **Total por sesión:** ~$0.06 USD

Para 10 sesiones de prueba: **~$0.60 USD**

---

## 🎬 Flujo Completo

1. Usuario abre `http://localhost:3000`
2. Ve mensaje de bienvenida
3. Escribe "Sí" o similar → **Backend genera preguntas con OpenAI**
4. Usuario responde pregunta 1
5. Backend valida con OpenAI
6. Si es correcta → Pregunta 2
7. Si es incorrecta → Pista o reintentar
8. Repite hasta completar 7 preguntas
9. Backend revela coordenadas GPS
10. Usuario ve ubicación en Google Maps
11. 🎊 **¡Propuesta romántica lista!**

---

## 📸 Screenshots (para debuggear)

Abre las **DevTools del navegador** (F12):

### Console Tab
- Verás los requests a la API
- Errores de JavaScript si los hay

### Network Tab
- Verás las llamadas HTTP al backend
- POST /api/start-quiz
- POST /api/chat
- POST /api/get-location

---

## ✅ Checklist de Prueba

- [ ] Backend inicia sin errores
- [ ] Frontend inicia sin errores
- [ ] Página carga en el navegador
- [ ] Mensaje de bienvenida aparece
- [ ] Al escribir "Sí" → Genera preguntas (espera ~5 segundos)
- [ ] Pregunta 1 aparece
- [ ] Al responder → Bot valida la respuesta
- [ ] Contador de preguntas funciona (1/7, 2/7, etc.)
- [ ] Sistema de pistas funciona
- [ ] Al completar → Muestra coordenadas GPS
- [ ] Link a Google Maps funciona

---

## 🚀 Siguiente Paso: Deploy

Una vez que funcione localmente, puedes desplegarlo:

1. **Backend:** Railway, Render, o Heroku
2. **Frontend:** Vercel (gratis y fácil)

¿Quieres que te ayude con el deploy?

---

## 🆘 Si algo falla

1. **Lee los mensajes de error** en la terminal
2. **Verifica los logs** en la consola del navegador
3. **Prueba reiniciar** ambos servidores
4. **Pregúntame** con el error específico

---

## 🎉 ¡Listo!

Ahora tienes:
- ✅ Backend funcionando con OpenAI
- ✅ Frontend con React/Next.js
- ✅ Sistema de chat interactivo
- ✅ Generación dinámica de preguntas
- ✅ Revelación de ubicación GPS

**¡Todo configurado para tu propuesta romántica! 💕**
