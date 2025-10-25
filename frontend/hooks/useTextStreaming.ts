'use client';

import { useState, useEffect } from 'react';

/**
 * Hook para simular streaming de texto (efecto de escritura)
 */
export function useTextStreaming(text: string, enabled: boolean = true, speed: number = 30) {
  const [displayedText, setDisplayedText] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);

  useEffect(() => {
    if (!enabled || !text) {
      setDisplayedText(text);
      setIsStreaming(false);
      return;
    }

    setIsStreaming(true);
    setDisplayedText('');

    let currentIndex = 0;
    const interval = setInterval(() => {
      if (currentIndex < text.length) {
        setDisplayedText(text.slice(0, currentIndex + 1));
        currentIndex++;
      } else {
        setIsStreaming(false);
        clearInterval(interval);
      }
    }, speed);

    return () => clearInterval(interval);
  }, [text, enabled, speed]);

  return { displayedText, isStreaming };
}
