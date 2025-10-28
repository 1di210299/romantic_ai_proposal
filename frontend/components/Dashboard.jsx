"use client";

import React, { useState, useEffect } from 'react';
import { Heart, MessageCircle, Calendar, Sparkles, Bot, TrendingUp, Users, Clock } from 'lucide-react';

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isRegenerating, setIsRegenerating] = useState(false);

  // Función para cargar estadísticas
  const loadStats = async (forceRegenerate = false) => {
    try {
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || window.location.origin;
      console.log('🌐 Dashboard: Loading stats from:', backendUrl);
      
      let fullUrl = `${backendUrl}/api/relationship-stats`;
      if (forceRegenerate) {
        fullUrl += '?force=true';
      }
      
      console.log('📡 Dashboard: Fetching from:', fullUrl);
      
      const response = await fetch(fullUrl);
      console.log('📊 Dashboard: Response status:', response.status);
      
      if (response.ok) {
        const data = await response.json();
        console.log('✅ Dashboard: Stats loaded successfully:', data);
        setStats(data);
      } else {
        console.error('❌ Dashboard: Response not OK:', response.status, response.statusText);
      }
    } catch (error) {
      console.error('❌ Dashboard: Error loading stats:', error);
    } finally {
      setLoading(false);
      setIsRegenerating(false);
    }
  };

  // Función para regenerar estadísticas
  const regenerateStats = async () => {
    setIsRegenerating(true);
    try {
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || window.location.origin;
      const response = await fetch(`${backendUrl}/api/relationship-stats/regenerate`, {
        method: 'POST'
      });
      
      if (response.ok) {
        const result = await response.json();
        console.log('✅ Stats regenerated:', result);
        if (result.success && result.stats) {
          setStats(result.stats);
        }
      } else {
        console.error('❌ Error regenerating stats:', response.status);
      }
    } catch (error) {
      console.error('❌ Error regenerating stats:', error);
    }
    setIsRegenerating(false);
  };

  useEffect(() => {
    console.log('🚀 Dashboard: Component mounted, loading stats...');
    loadStats();
  }, []);

  if (loading || !stats) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-pink-50 via-white to-rose-50 flex items-center justify-center">
        <div className="text-center max-w-md mx-auto">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-pink-500 mx-auto mb-4"></div>
          <p className="text-gray-600 mb-2">Cargando análisis de conversaciones...</p>
          <div className="text-sm text-gray-500">
            {loading ? "Procesando datos..." : "Iniciando..."}
          </div>
          
          {/* Indicador de progreso visual */}
          <div className="mt-4 w-full bg-gray-200 rounded-full h-2">
            <div className="bg-gradient-to-r from-pink-400 to-rose-500 h-2 rounded-full animate-pulse" style={{width: "60%"}}></div>
          </div>
          
          <div className="mt-4 text-xs text-gray-400">
            💡 Tip: Las estadísticas se cargan más rápido después del primer acceso
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-navy-900 via-navy-800 to-navy-700">
      {/* Header */}
      <div className="bg-navy-800/50 backdrop-blur-sm shadow-xl border-b border-pastel-500/20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-pastel-100 flex items-center gap-2">
                <Heart className="text-romantic-400" size={32} />
                Para Karem Kiyomi Ramos
              </h1>
              <p className="text-pastel-200 mt-1 flex items-center gap-2">
                Análisis de nuestras conversaciones
                {stats.cache_hit && (
                  <span className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-pastel-500/20 text-pastel-300 border border-pastel-500/30">
                    ⚡ Carga rápida
                  </span>
                )}
                {stats.analysis_type === 'enhanced_ai_analysis' && (
                  <span className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-navy-700/50 text-pastel-400 border border-pastel-500/40">
                    🤖 IA Avanzada
                  </span>
                )}
                {stats.data_source && (
                  <span className="text-xs text-pastel-400/50">
                    {stats.data_source.replace(/_/g, ' ')}
                  </span>
                )}
              </p>
            </div>
            <div className="flex gap-3">
              <button
                onClick={regenerateStats}
                disabled={isRegenerating}
                className="bg-gradient-to-r from-pastel-500 to-pastel-600 text-navy-900 px-4 py-2 rounded-2xl font-bold hover:from-pastel-400 hover:to-pastel-500 transition-all duration-200 flex items-center gap-2 disabled:opacity-50 border-2 border-navy-900/30 shadow-xl"
              >
                {isRegenerating ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-navy-900"></div>
                    Analizando...
                  </>
                ) : (
                  <>
                    <Sparkles size={16} />
                    Mejorar Análisis
                  </>
                )}
              </button>
              <button
                onClick={() => window.location.href = '/chat'}
                className="bg-gradient-to-r from-romantic-500 to-romantic-600 text-white px-6 py-3 rounded-2xl font-bold hover:from-romantic-400 hover:to-romantic-500 transition-all duration-200 flex items-center gap-2 border-2 border-navy-900/30 shadow-xl"
              >
                <Bot size={20} />
                Iniciar Chat
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Métricas principales */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-navy-800/50 backdrop-blur-sm rounded-2xl shadow-xl border border-pastel-500/30 p-6 hover:shadow-2xl hover:scale-[1.02] transition-all duration-300">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-pastel-300">Total Mensajes</p>
                <p className="text-3xl font-bold text-pastel-400">{stats.totalMessages.toLocaleString()}</p>
              </div>
              <MessageCircle className="text-pastel-500" size={32} />
            </div>
          </div>

          <div className="bg-navy-800/50 backdrop-blur-sm rounded-2xl shadow-xl border border-pastel-500/30 p-6 hover:shadow-2xl hover:scale-[1.02] transition-all duration-300">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-pastel-300">Días Juntos</p>
                <p className="text-3xl font-bold text-romantic-400">{stats.totalDays}</p>
              </div>
              <Calendar className="text-romantic-500" size={32} />
            </div>
          </div>

          <div className="bg-navy-800/50 backdrop-blur-sm rounded-2xl shadow-xl border border-pastel-500/30 p-6 hover:shadow-2xl hover:scale-[1.02] transition-all duration-300">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-pastel-300">Mensajes/Día</p>
                <p className="text-3xl font-bold text-pastel-500">{stats.avgMessagesPerDay}</p>
                <p className="text-xs text-pastel-400/70 mt-1">¡Súper activos!</p>
              </div>
              <TrendingUp className="text-pastel-600" size={32} />
            </div>
          </div>

          <div className="bg-navy-800/50 backdrop-blur-sm rounded-2xl shadow-xl border border-pastel-500/30 p-6 hover:shadow-2xl hover:scale-[1.02] transition-all duration-300">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-pastel-300">Conexión</p>
                <p className="text-3xl font-bold text-romantic-400">
                  {stats.connectionScore || stats.sentimentScore}/10
                </p>
                {stats.avgResponseTime && (
                  <p className="text-xs text-pastel-400/70 mt-1">⚡ {stats.avgResponseTime}</p>
                )}
              </div>
              <Sparkles className="text-romantic-500" size={32} />
            </div>
          </div>
        </div>

        {/* Nueva sección: Multimedia destacada */}
        {stats.conversationPatterns && (
          <div className="mb-8 bg-gradient-to-r from-navy-800/60 to-navy-700/60 backdrop-blur-sm rounded-2xl shadow-2xl border border-pastel-500/40 p-8">
            <div className="text-center mb-6">
              <h2 className="text-2xl font-bold text-pastel-100 mb-2">🎵 Relación Multimedia</h2>
              <p className="text-pastel-300">Una historia contada en más de {stats.conversationPatterns.voiceMessages + stats.conversationPatterns.photosShared + stats.conversationPatterns.videosShared} archivos</p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center p-6 bg-navy-700/50 rounded-2xl border border-pastel-500/20">
                <div className="text-4xl mb-3">🎤</div>
                <p className="text-3xl font-bold text-pastel-400">{stats.conversationPatterns.voiceMessages.toLocaleString()}</p>
                <p className="text-sm text-pastel-300">Mensajes de voz</p>
                <p className="text-xs text-pastel-400/70 mt-1">{Math.round(stats.conversationPatterns.voiceMessages / stats.totalDays)} por día</p>
              </div>
              
              <div className="text-center p-6 bg-navy-700/50 rounded-2xl border border-pastel-500/20">
                <div className="text-4xl mb-3">📸</div>
                <p className="text-3xl font-bold text-romantic-400">{stats.conversationPatterns.photosShared.toLocaleString()}</p>
                <p className="text-sm text-pastel-300">Fotos compartidas</p>
                <p className="text-xs text-pastel-400/70 mt-1">{(stats.conversationPatterns.photosShared / stats.totalDays).toFixed(1)} por día</p>
              </div>
              
              <div className="text-center p-6 bg-navy-700/50 rounded-2xl border border-pastel-500/20">
                <div className="text-4xl mb-3">🎬</div>
                <p className="text-3xl font-bold text-pastel-500">{stats.conversationPatterns.videosShared}</p>
                <p className="text-sm text-pastel-300">Videos especiales</p>
                <p className="text-xs text-pastel-400/70 mt-1">Momentos únicos</p>
              </div>
            </div>
            
            <div className="mt-6 text-center">
              <div className="inline-flex items-center px-4 py-2 bg-pastel-500/20 rounded-full border border-pastel-500/30">
                <span className="text-pastel-200 text-sm">💫 {stats.specialMoments} momentos especiales detectados</span>
              </div>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Evolución de la relación */}
          <div className="bg-white rounded-xl shadow-sm border border-pink-100 p-6">
            <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <Users className="text-pink-500" size={24} />
              Evolución de Nuestra Relación
            </h3>
            <div className="space-y-4">
              {stats.relationshipPhases.map((phase, index) => (
                <div key={index} className="flex items-center justify-between p-4 bg-gradient-to-r from-pink-50 to-rose-50 rounded-lg">
                  <div>
                    <h4 className="font-semibold text-gray-900">{phase.phase}</h4>
                    <p className="text-sm text-gray-600">{phase.period}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-2xl font-bold text-pink-600">{phase.messages.toLocaleString()}</p>
                    <p className="text-sm text-gray-500">mensajes</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Análisis de conversaciones */}
          <div className="bg-white rounded-xl shadow-sm border border-pink-100 p-6">
            <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <Sparkles className="text-pink-500" size={24} />
              Análisis de Sentimientos
            </h3>
            
            <div className="space-y-6">
              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-sm font-medium text-gray-600">Conexión Emocional</span>
                  <span className="text-sm font-bold text-pink-600">
                    {stats.connectionScore || stats.sentimentScore}/10
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div 
                    className="bg-gradient-to-r from-pink-400 to-rose-500 h-3 rounded-full"
                    style={{ width: `${(stats.connectionScore || stats.sentimentScore) * 10}%` }}
                  ></div>
                </div>
              </div>

              <div>
                <h4 className="font-semibold text-gray-900 mb-3">
                  {stats.analysis_type === 'enhanced_ai_powered' ? 'Emojis Reales Más Usados' : 'Expresiones Frecuentes'}
                </h4>
                <div className="flex gap-3 flex-wrap">
                  {stats.topEmojis?.slice(0, 5).map((emoji, index) => (
                    <div key={index} className="text-3xl p-2 bg-pink-50 rounded-lg hover:bg-pink-100 transition-colors">
                      {emoji}
                    </div>
                  )) || ['❤️', '😘', '💜', '😍', '🥰'].map((emoji, index) => (
                    <div key={index} className="text-3xl p-2 bg-pink-50 rounded-lg opacity-50">
                      {emoji}
                    </div>
                  ))}
                </div>
                {stats.analysis_type === 'enhanced_ai_powered' && (
                  <p className="text-xs text-green-600 mt-2">✨ Análisis basado en uso real</p>
                )}
              </div>

              <div className="bg-gradient-to-r from-pink-50 to-rose-50 rounded-lg p-4">
                <div className="flex items-center gap-2 mb-2">
                  <Heart className="text-red-500" size={20} />
                  <span className="font-semibold text-gray-900">Momentos Significativos</span>
                </div>
                <p className="text-3xl font-bold text-red-600">{stats.specialMoments}</p>
                <p className="text-sm text-gray-600">conversaciones destacadas</p>
              </div>
            </div>
          </div>
        </div>

{/* Insights de IA (si están disponibles) */}
        {stats.aiInsights && (
          <div className="mt-8 bg-white rounded-xl shadow-sm border border-blue-100 p-6">
            <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <Bot className="text-blue-500" size={24} />
              Análisis Inteligente de la Relación
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {stats.aiInsights.unique_language && (
                <div className="p-4 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg">
                  <h4 className="font-semibold text-gray-900 mb-2">💝 Lenguaje Único</h4>
                  {stats.aiInsights.unique_language.pet_names?.length > 0 && (
                    <div className="mb-2">
                      <p className="text-sm text-gray-600">Apodos cariñosos:</p>
                      <p className="text-pink-600 font-medium">
                        {stats.aiInsights.unique_language.pet_names.join(', ')}
                      </p>
                    </div>
                  )}
                  {stats.aiInsights.unique_language.unique_phrases?.length > 0 && (
                    <div>
                      <p className="text-sm text-gray-600">Frases especiales:</p>
                      <p className="text-purple-600 text-sm italic">
                        &quot;{stats.aiInsights.unique_language.unique_phrases[0]}&quot;
                      </p>
                    </div>
                  )}
                </div>
              )}
              
              {stats.aiInsights.emotional_tone && (
                <div className="p-4 bg-gradient-to-br from-pink-50 to-rose-50 rounded-lg">
                  <h4 className="font-semibold text-gray-900 mb-2">💖 Tono Emocional</h4>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Sentimiento general:</span>
                      <span className="text-pink-600 font-medium capitalize">
                        {stats.aiInsights.emotional_tone.overall_sentiment}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Nivel de cariño:</span>
                      <span className="text-rose-600 font-medium capitalize">
                        {stats.aiInsights.emotional_tone.affection_level}
                      </span>
                    </div>
                  </div>
                </div>
              )}
            </div>
            
            {stats.aiInsights.main_topics && (
              <div className="mt-6 p-4 bg-gradient-to-br from-purple-50 to-pink-50 rounded-lg">
                <h4 className="font-semibold text-gray-900 mb-2">🗨️ Temas Principales</h4>
                <div className="flex flex-wrap gap-2">
                  {stats.aiInsights.main_topics.slice(0, 5).map((topic, index) => (
                    <span key={index} className="px-3 py-1 bg-white rounded-full text-sm text-purple-600 border border-purple-200">
                      {topic}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Estadísticas adicionales */}
        <div className="mt-8 bg-white rounded-xl shadow-sm border border-pink-100 p-6">
          <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <Clock className="text-pink-500" size={24} />
            Estadísticas de Conversación
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center p-4 bg-gradient-to-br from-pink-50 to-rose-50 rounded-lg">
              <p className="text-3xl font-bold text-pink-600">
                {stats.conversationPatterns?.longMessages || stats.longestConversation}
              </p>
              <p className="text-sm text-gray-600">
                {stats.conversationPatterns ? 'mensajes largos enviados' : 'mensajes en la conversación más larga'}
              </p>
            </div>
            
            <div className="text-center p-4 bg-gradient-to-br from-purple-50 to-pink-50 rounded-lg">
              <p className="text-3xl font-bold text-purple-600">
                {stats.conversationPatterns?.voiceMessages || `${stats.mostActiveHour}:00`}
              </p>
              <p className="text-sm text-gray-600">
                {stats.conversationPatterns ? 'mensajes de voz' : 'hora más activa'}
              </p>
            </div>
            
            <div className="text-center p-4 bg-gradient-to-br from-rose-50 to-red-50 rounded-lg">
              <p className="text-3xl font-bold text-rose-600">
                {stats.conversationPatterns?.photosShared || Math.round(stats.totalMessages / stats.totalDays * 7)}
              </p>
              <p className="text-sm text-gray-600">
                {stats.conversationPatterns ? 'fotos compartidas' : 'mensajes promedio semanal'}
              </p>
            </div>
          </div>
        </div>

        {/* Call to action */}
        <div className="mt-8 text-center">
          <div className="bg-gradient-to-r from-pink-500 to-rose-500 rounded-xl p-8 text-white">
            <h3 className="text-2xl font-bold mb-2">Conversación Inteligente</h3>
            <p className="text-pink-100 mb-6">Chatbot entrenado con {stats.totalMessages.toLocaleString()} mensajes reales</p>
            <button
              onClick={() => window.location.href = '/chat'}
              className="bg-white text-pink-600 px-8 py-3 rounded-lg font-medium hover:bg-pink-50 transition-all duration-200"
            >
              Iniciar Conversación
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;