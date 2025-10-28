'use client';

import { useTextStreaming } from '@/hooks/useTextStreaming';

interface ChatMessageProps {
  role: 'bot' | 'user';
  content: string;
  timestamp: Date;
  enableStreaming?: boolean;
}

export default function ChatMessage({ role, content, timestamp, enableStreaming = false }: ChatMessageProps) {
  const isBot = role === 'bot';
  const { displayedText, isStreaming } = useTextStreaming(content, enableStreaming && isBot, 10);

  return (
    <div className={`flex ${isBot ? 'justify-start' : 'justify-end'} animate-fadeIn`}>
      <div
        className={`rounded-3xl p-5 max-w-2xl shadow-2xl transition-all duration-300 hover:shadow-3xl ${
          isBot
            ? 'bg-gradient-to-br from-white via-pastel-50 to-pastel-100 text-navy-900 border-2 border-pastel-400/50'
            : 'bg-gradient-to-br from-navy-700 via-navy-800 to-navy-900 text-pastel-200 border-2 border-pastel-500/40'
        }`}
      >
        {isBot && (
          <div className="flex items-center gap-3 mb-3 pb-2 border-b border-pastel-300/30">
            <span className="font-bold text-sm text-navy-700 tracking-wide">Karem AI</span>
          </div>
        )}
        
        <div className={`whitespace-pre-wrap break-words leading-relaxed ${isBot ? 'text-navy-800' : 'text-pastel-100'}`}>
          {displayedText}
          {isStreaming && (
            <span className="inline-block w-0.5 h-5 bg-pastel-500 ml-1 animate-pulse align-middle">|</span>
          )}
        </div>
        
        <div
          className={`text-xs mt-3 font-medium ${
            isBot ? 'text-navy-400' : 'text-pastel-400'
          }`}
        >
          {timestamp.toLocaleTimeString('es-ES', {
            hour: '2-digit',
            minute: '2-digit',
          })}
        </div>
      </div>
    </div>
  );
}
