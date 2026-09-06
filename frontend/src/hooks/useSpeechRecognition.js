import { useState, useEffect, useRef, useCallback } from 'react';

export default function useSpeechRecognition({
  onResult,
  onError,
  onEnd,
  lang = 'tr-TR',
  continuous = false,
  interimResults = false
} = {}) {
  const [isListening, setIsListening] = useState(false);
  const [error, setError] = useState(null);
  const recognitionRef = useRef(null);

  const callbacksRef = useRef({ onResult, onError, onEnd });
  useEffect(() => {
    callbacksRef.current = { onResult, onError, onEnd };
  });

  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setError('not_supported');
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = continuous;
    recognition.interimResults = interimResults;
    recognition.lang = lang;

    recognition.onstart = () => {
      setIsListening(true);
      setError(null);
    };

    recognition.onerror = (event) => {
      setError(event.error);
      setIsListening(false);
      if (callbacksRef.current.onError) {
        callbacksRef.current.onError(event.error);
      }
    };

    recognition.onend = () => {
      setIsListening(false);
      if (callbacksRef.current.onEnd) {
        callbacksRef.current.onEnd();
      }
    };

    recognition.onresult = (event) => {
      let transcript = '';
      for (let i = event.resultIndex; i < event.results.length; i++) {
        transcript += event.results[i][0].transcript;
      }
      if (callbacksRef.current.onResult) {
        callbacksRef.current.onResult(transcript);
      }
    };

    recognitionRef.current = recognition;

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.abort();
      }
    };
  }, [lang, continuous, interimResults]);

  const startListening = useCallback(() => {
    if (!recognitionRef.current) return;
    if (!isListening) {
      try {
        recognitionRef.current.start();
      } catch {
        // already started
      }
    }
  }, [isListening]);

  const stopListening = useCallback(() => {
    if (recognitionRef.current && isListening) {
      try {
        recognitionRef.current.stop();
      } catch {
        // already stopped
      }
    }
  }, [isListening]);

  return {
    isSupported: !!(window.SpeechRecognition || window.webkitSpeechRecognition),
    isListening,
    error,
    startListening,
    stopListening
  };
}
