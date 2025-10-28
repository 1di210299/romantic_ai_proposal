"use client";

import React, { useState, useEffect } from 'react';
import { Heart, MessageCircle, Calendar, Sparkles, Bot, TrendingUp, Users, Clock } from 'lucide-react';

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Cargar estadísticas del backend
    const loadStats = async () => {
      try {
        const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || window.location.origin;
        console.log('🌐 Dashboard: Loading stats from:', backendUrl);
        console.log('🔧 Environment vars:', {
          NEXT_PUBLIC_BACKEND_URL: process.env.NEXT_PUBLIC_BACKEND_URL,
          origin: window.location.origin
        });
        
        const fullUrl = `${backendUrl}/api/relationship-stats`;
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
        console.log('🏁 Dashboard: Loading finished, setting loading to false');
        setLoading(false);
      }
    };

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
    <div className="min-h-screen bg-gradient-to-br from-pink-50 via-white to-rose-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-pink-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
                <Heart className="text-pink-500" size={32} />
                Para Karem Kiyomi Ramos
              </h1>
              <p className="text-gray-600 mt-1">
                Análisis de nuestras conversaciones
                {stats.cache_hit && (
                  <span className="ml-2 inline-flex items-center px-2 py-1 rounded-full text-xs bg-green-100 text-green-800">
                    ⚡ Carga rápida
                  </span>
                )}
              </p>
            </div>
            <button
              onClick={() => window.location.href = '/chat'}
              className="bg-gradient-to-r from-pink-500 to-rose-500 text-white px-6 py-3 rounded-lg font-medium hover:from-pink-600 hover:to-rose-600 transition-all duration-200 flex items-center gap-2"
            >
              <Bot size={20} />
              Iniciar Chat
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Métricas principales */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-xl shadow-sm border border-pink-100 p-6 hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Mensajes</p>
                <p className="text-3xl font-bold text-pink-600">{stats.totalMessages.toLocaleString()}</p>
              </div>
              <MessageCircle className="text-pink-400" size={32} />
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-pink-100 p-6 hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Días Juntos</p>
                <p className="text-3xl font-bold text-rose-600">{stats.totalDays}</p>
              </div>
              <Calendar className="text-rose-400" size={32} />
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-pink-100 p-6 hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Mensajes/Día</p>
                <p className="text-3xl font-bold text-purple-600">{stats.avgMessagesPerDay}</p>
              </div>
              <TrendingUp className="text-purple-400" size={32} />
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-pink-100 p-6 hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Conexión</p>
                <p className="text-3xl font-bold text-red-600">{stats.sentimentScore}/10</p>
              </div>
              <Sparkles className="text-red-400" size={32} />
            </div>
          </div>
        </div>

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
                  <span className="text-sm font-bold text-pink-600">{stats.sentimentScore}/10</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div 
                    className="bg-gradient-to-r from-pink-400 to-rose-500 h-3 rounded-full"
                    style={{ width: `${stats.sentimentScore * 10}%` }}
                  ></div>
                </div>
              </div>

              <div>
                <h4 className="font-semibold text-gray-900 mb-3">Expresiones Frecuentes</h4>
                <div className="flex gap-3">
                  {stats.topEmojis.map((emoji, index) => (
                    <div key={index} className="text-3xl p-2 bg-pink-50 rounded-lg">
                      {emoji}
                    </div>
                  ))}
                </div>
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

        {/* Estadísticas adicionales */}
        <div className="mt-8 bg-white rounded-xl shadow-sm border border-pink-100 p-6">
          <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <Clock className="text-pink-500" size={24} />
            Estadísticas de Conversación
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center p-4 bg-gradient-to-br from-pink-50 to-rose-50 rounded-lg">
              <p className="text-3xl font-bold text-pink-600">{stats.longestConversation}</p>
              <p className="text-sm text-gray-600">mensajes en la conversación más larga</p>
            </div>
            
            <div className="text-center p-4 bg-gradient-to-br from-purple-50 to-pink-50 rounded-lg">
              <p className="text-3xl font-bold text-purple-600">{stats.mostActiveHour}:00</p>
              <p className="text-sm text-gray-600">hora más activa</p>
            </div>
            
            <div className="text-center p-4 bg-gradient-to-br from-rose-50 to-red-50 rounded-lg">
              <p className="text-3xl font-bold text-rose-600">{Math.round(stats.totalMessages / stats.totalDays * 7)}</p>
              <p className="text-sm text-gray-600">mensajes promedio semanal</p>
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