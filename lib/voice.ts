import { Platform } from 'react-native';

export interface VoiceCallbacks {
  onResult: (transcript: string, isFinal: boolean) => void;
  onError: (message: string) => void;
  onEnd: () => void;
}

export function isVoiceSupported(): boolean {
  if (Platform.OS !== 'web' || typeof window === 'undefined') return false;
  const w = window as any;
  return Boolean(w.SpeechRecognition || w.webkitSpeechRecognition);
}

export function startVoiceDictation(callbacks: VoiceCallbacks): { stop: () => void } | null {
  if (Platform.OS !== 'web' || typeof window === 'undefined') {
    callbacks.onError('Usa el icono de micrófono de tu teclado en el celular.');
    return null;
  }
  const w = window as any;
  const SpeechRecognition = w.SpeechRecognition || w.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    callbacks.onError('Tu navegador no soporta dictado directo (usa Chrome o Edge).');
    return null;
  }

  const recognition = new SpeechRecognition();
  recognition.lang = 'es-CO';
  recognition.continuous = false;
  recognition.interimResults = true;
  recognition.maxAlternatives = 1;

  recognition.onresult = (event: any) => {
    let transcript = '';
    let isFinal = false;
    for (let i = 0; i < event.results.length; i++) {
      transcript += event.results[i][0].transcript;
      if (event.results[i].isFinal) {
        isFinal = true;
      }
    }
    callbacks.onResult(transcript.trim(), isFinal);
  };

  recognition.onerror = (event: any) => {
    const code = event?.error;
    if (code === 'not-allowed' || code === 'service-not-allowed') {
      callbacks.onError('Permite el acceso al micrófono en la barra superior del navegador.');
    } else if (code === 'no-speech') {
      callbacks.onError('No se detectó voz. Intenta hablar más cerca del micrófono.');
    } else {
      callbacks.onError(`Error de micrófono: ${code || 'desconocido'}`);
    }
  };

  recognition.onend = () => {
    callbacks.onEnd();
  };

  try {
    recognition.start();
    return {
      stop: () => {
        try {
          recognition.stop();
        } catch {
          // ignore
        }
      },
    };
  } catch (e: any) {
    callbacks.onError(e?.message || 'No se pudo iniciar el micrófono.');
    return null;
  }
}
