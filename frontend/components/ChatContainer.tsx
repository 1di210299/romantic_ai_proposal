'use client';

import { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';
import QuickResponses from './QuickResponses';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5001';

interface Message {
  role: 'bot' | 'user';
  content: string;
  timestamp: Date;
  enableStreaming?: boolean;
}

interface QuizState {
  sessionId: string | null;
  currentQuestion: number;
  totalQuestions: number;
  completed: boolean;
  location: { lat: number; lng: number } | null;
  currentOptions: string[];
  attemptsLeft: number;
}

export default function ChatContainer() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'bot',
      content: 'Hola Karem, soy Karem AI. He aprendido mucho sobre ti y nuestra historia a través de nuestras conversaciones. Me encantaría platicar contigo y recordar algunos momentos especiales. ¿Te parece si empezamos?',
      timestamp: new Date(),
    },
  ]);
  const [quizState, setQuizState] = useState<QuizState>({
    sessionId: null,
    currentQuestion: 0,
    totalQuestions: 0,
    completed: false,
    location: null,
    currentOptions: [],
    attemptsLeft: 3,
  });
  const [isLoading, setIsLoading] = useState(false);
  const [waitingForStart, setWaitingForStart] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const startQuiz = async () => {
    setIsLoading(true);
    try {
      const response = await axios.post(`${API_URL}/api/start-quiz`, {
        user_name: 'Karem',
      });

      const { session_id, question, options, current_question, total_questions, attempts_left } = response.data;

      setQuizState({
        sessionId: session_id,
        currentQuestion: current_question,
        totalQuestions: total_questions,
        completed: false,
        location: null,
        currentOptions: options || [],
        attemptsLeft: attempts_left || 3,
      });

      setMessages((prev) => [
        ...prev,
        {
          role: 'bot',
          content: `¡Perfecto! Tengo ${total_questions} preguntas especiales para ti. ✨\n\nPregunta ${current_question}/${total_questions}:\n${question}`,
          timestamp: new Date(),
          enableStreaming: true,
        },
      ]);

      setWaitingForStart(false);
    } catch (error) {
      console.error('Error starting quiz:', error);
      setMessages((prev) => [
        ...prev,
        {
          role: 'bot',
          content: '❌ Hubo un error al iniciar. Por favor, intenta de nuevo.',
          timestamp: new Date(),
          enableStreaming: false,
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const sendMessage = async (content: string) => {
    if (!content.trim() || isLoading) return;

    // Si estamos esperando que comience, iniciar el quiz
    if (waitingForStart) {
      setMessages((prev) => [
        ...prev,
        {
          role: 'user',
          content,
          timestamp: new Date(),
        },
      ]);
      await startQuiz();
      return;
    }

    // Agregar mensaje del usuario
    const userMessage: Message = {
      role: 'user',
      content,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);

    setIsLoading(true);

    try {
      const response = await axios.post(`${API_URL}/api/chat`, {
        session_id: quizState.sessionId,
        message: content,
      });

      const {
        message: botResponse,
        is_correct: correct,
        current_question,
        total_questions,
        completed,
        options,
        attempts_left,
      } = response.data;

      // Actualizar estado del quiz
      setQuizState((prev) => ({
        ...prev,
        currentQuestion: current_question,
        totalQuestions: total_questions,
        completed: completed || false,
        currentOptions: options || prev.currentOptions, // Mantener opciones si no vienen nuevas
        attemptsLeft: attempts_left !== undefined ? attempts_left : prev.attemptsLeft,
      }));

      // Agregar respuesta del bot
      let botMessage = botResponse;
      
      // El mensaje ya viene formateado desde el backend
      botMessage = botResponse;
      
      if (completed) {
        // Obtener ubicación cuando completa el quiz
        try {
          const locationResponse = await axios.post(`${API_URL}/api/get-location`, {
            session_id: quizState.sessionId,
          });
          
          const { latitude, longitude, message: locationMessage } = locationResponse.data;
          
          setQuizState((prev) => ({
            ...prev,
            location: { lat: latitude, lng: longitude },
          }));

          botMessage += `\n\n📍 ${locationMessage}\n\nCoordenadas: ${latitude}, ${longitude}\n\n🗺️ Puedes verlo en Google Maps: https://www.google.com/maps?q=${latitude},${longitude}`;
        } catch (error) {
          console.error('Error getting location:', error);
        }
      }

      setMessages((prev) => [
        ...prev,
        {
          role: 'bot',
          content: botMessage,
          timestamp: new Date(),
          enableStreaming: true,
        },
      ]);
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages((prev) => [
        ...prev,
        {
          role: 'bot',
          content: '❌ Hubo un error al procesar tu respuesta. Por favor, intenta de nuevo.',
          timestamp: new Date(),
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-gray-900 via-navy-900 to-black">
      {/* Header - Más elegante */}
      <div className="bg-gradient-to-r from-navy-600 via-navy-700 to-navy-900 text-pastel-200 p-6 shadow-2xl border-b border-pastel-500/20 backdrop-blur-sm">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-3xl font-bold flex items-center gap-3 tracking-tight">
            <span className="text-pastel-400">💕</span>
            <span className="bg-gradient-to-r from-pastel-300 to-pastel-500 bg-clip-text text-transparent">
              Una Sorpresa Especial
            </span>
          </h1>
          {!waitingForStart && (
            <div className="flex items-center justify-between mt-3 text-sm">
              <p className="text-pastel-300 font-medium flex items-center gap-2">
                <span className="inline-block w-2 h-2 bg-pastel-400 rounded-full animate-pulse"></span>
                Pregunta {quizState.currentQuestion} de {quizState.totalQuestions}
              </p>
              <p className="text-pastel-300 font-medium bg-navy-800/50 px-3 py-1 rounded-full border border-pastel-500/30">
                ❤️ Intentos: {quizState.attemptsLeft}/3
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Chat Messages - Fondo más elegante */}
      <div className="flex-1 overflow-y-auto chat-container p-6">
        <div className="max-w-4xl mx-auto space-y-6">
          {messages.map((message, index) => (
            <ChatMessage
              key={index}
              role={message.role}
              content={message.content}
              timestamp={message.timestamp}
              enableStreaming={message.enableStreaming}
            />
          ))}
          {isLoading && (
            <div className="flex justify-start animate-fadeIn">
              <div className="bg-gradient-to-br from-white to-pastel-50 border-2 border-pastel-400 rounded-3xl p-5 shadow-xl max-w-md backdrop-blur-sm">
                <div className="flex gap-2 items-center">
                  <div className="w-3 h-3 bg-gradient-to-r from-pastel-500 to-pastel-600 rounded-full animate-bounce"></div>
                  <div className="w-3 h-3 bg-gradient-to-r from-pastel-500 to-pastel-600 rounded-full animate-bounce" style={{ animationDelay: '0.15s' }}></div>
                  <div className="w-3 h-3 bg-gradient-to-r from-pastel-500 to-pastel-600 rounded-full animate-bounce" style={{ animationDelay: '0.3s' }}></div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input and Quick Responses - Más elegante */}
      {!quizState.completed && (
        <div className="bg-gradient-to-r from-navy-800 via-navy-900 to-black border-t border-pastel-500/20 p-6 shadow-2xl backdrop-blur-md">
          <div className="max-w-4xl mx-auto">
            {/* Quick Response Options */}
            {quizState.currentOptions.length > 0 && (
              <div className="mb-4">
                <p className="text-pastel-300 text-sm font-semibold mb-3 flex items-center gap-2">
                  <span className="inline-block w-1.5 h-1.5 bg-pastel-400 rounded-full"></span>
                  Opciones rápidas:
                </p>
                <QuickResponses
                  options={quizState.currentOptions}
                  onSelect={sendMessage}
                  disabled={isLoading}
                />
              </div>
            )}
            
            {/* Text Input */}
            <ChatInput onSend={sendMessage} disabled={isLoading} />
          </div>
        </div>
      )}

      {/* Completion Message - Más elegante */}
      {quizState.completed && quizState.location && (
        <div className="bg-gradient-to-r from-pastel-400 via-pastel-500 to-pastel-600 text-navy-900 p-8 text-center border-t-4 border-pastel-300 shadow-2xl">
          <p className="text-2xl font-bold mb-3 flex items-center justify-center gap-2">
            <span>🎊</span> ¡Quiz Completado! <span>🎊</span>
          </p>
          <p className="text-base font-semibold">
            Revisa el último mensaje para ver la ubicación especial 💕
          </p>
        </div>
      )}
    </div>
  );
}
