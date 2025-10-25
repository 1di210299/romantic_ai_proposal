'use client';

import { useState, KeyboardEvent } from 'react';

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
}

export default function ChatInput({ onSend, disabled = false }: ChatInputProps) {
  const [input, setInput] = useState('');

  const handleSend = () => {
    if (input.trim() && !disabled) {
      onSend(input);
      setInput('');
    }
  };

  const handleKeyPress = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex gap-3">
      <textarea
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyPress={handleKeyPress}
        placeholder="O escribe tu respuesta aquí..."
        disabled={disabled}
        rows={1}
        className="flex-1 resize-none border-2 border-pastel-500/50 bg-navy-800/50 backdrop-blur-sm rounded-2xl px-6 py-4 focus:outline-none focus:ring-2 focus:ring-pastel-500 focus:border-pastel-500 disabled:bg-navy-900/30 disabled:cursor-not-allowed text-pastel-100 placeholder-pastel-400/50 transition-all duration-200 shadow-lg"
      />
      <button
        onClick={handleSend}
        disabled={disabled || !input.trim()}
        className="bg-gradient-to-r from-pastel-400 via-pastel-500 to-pastel-600 text-navy-900 px-8 py-4 rounded-2xl font-bold hover:shadow-2xl hover:scale-[1.02] transition-all duration-300 disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:shadow-lg disabled:hover:scale-100 border-2 border-navy-900/30 shadow-xl hover:from-pastel-500 hover:via-pastel-600 hover:to-pastel-700"
      >
        ✉️ Enviar
      </button>
    </div>
  );
}
