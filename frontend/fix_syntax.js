import fs from 'fs';
import path from 'path';

// Fix useAuth.ts
const useAuthContent = `import { useEffect } from 'react';
import {
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signOut,
  signInWithPopup,
  onAuthStateChanged,
  updateProfile,
} from 'firebase/auth';
import { auth, googleProvider } from '../services/firebase/firebase';
import { useAuthStore } from '../store/authStore';
import { User, UserRole } from '../types';

export function useAuth() {
  const { user, loading, error, setUser, setLoading, setError, clearError } = useAuthStore();

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (firebaseUser) => {
      if (firebaseUser) {
        const appUser: User = {
          uid: firebaseUser.uid,
          email: firebaseUser.email,
          displayName: firebaseUser.displayName || firebaseUser.email?.split('@')[0] || 'User',
          photoURL: firebaseUser.photoURL,
          role: (localStorage.getItem('redhack_user_role') as UserRole) || 'ENGINEER',
        };
        setUser(appUser);
      } else {
        setUser(null);
      }
    });
    return () => unsubscribe();
  }, [setUser]);

  const login = async (email: string, pass: string) => {
    setLoading(true);
    clearError();
    try {
      const userCredential = await signInWithEmailAndPassword(auth, email, pass);
      const firebaseUser = userCredential.user;
      const appUser: User = {
        uid: firebaseUser.uid,
        email: firebaseUser.email,
        displayName: firebaseUser.displayName || firebaseUser.email?.split('@')[0] || 'User',
        photoURL: firebaseUser.photoURL,
        role: (localStorage.getItem('redhack_user_role') as UserRole) || 'ENGINEER',
      };
      setUser(appUser);
      return appUser;
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Authentication failed';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const register = async (email: string, pass: string, displayName: string, role: UserRole = 'ENGINEER') => {
    setLoading(true);
    clearError();
    try {
      const userCredential = await createUserWithEmailAndPassword(auth, email, pass);
      const firebaseUser = userCredential.user;
      if (displayName) {
        await updateProfile(firebaseUser, { displayName });
      }
      localStorage.setItem('redhack_user_role', role);
      const appUser: User = {
        uid: firebaseUser.uid,
        email: firebaseUser.email,
        displayName: displayName || firebaseUser.email?.split('@')[0] || 'User',
        photoURL: firebaseUser.photoURL,
        role: role,
      };
      setUser(appUser);
      return appUser;
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Registration failed';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const loginWithGoogle = async () => {
    setLoading(true);
    clearError();
    try {
      const result = await signInWithPopup(auth, googleProvider);
      const firebaseUser = result.user;
      const appUser: User = {
        uid: firebaseUser.uid,
        email: firebaseUser.email,
        displayName: firebaseUser.displayName || 'Google User',
        photoURL: firebaseUser.photoURL,
        role: 'ENGINEER',
      };
      setUser(appUser);
      return appUser;
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Google sign-in failed';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    setLoading(true);
    try {
      await signOut(auth);
      setUser(null);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Logout failed';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return {
    user,
    loading,
    error,
    login,
    register,
    loginWithGoogle,
    logout,
    clearError,
    isAuthenticated: !!user,
  };
}
`;

fs.writeFileSync('c:/Users/sabih/OneDrive/Desktop/MinorSafetySIH2026/frontend/src/hooks/useAuth.ts', useAuthContent, 'utf8');

// Fix useConnectivity.ts
const useConnectivityContent = `import { useState, useEffect } from 'react';
import { useSystemStore } from '../store/systemStore';
import { apiClient } from '../services/api/apiClient';

export function useConnectivity() {
  const { status, setStatus } = useSystemStore();
  const [isOnline, setIsOnline] = useState(navigator.onLine);

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  useEffect(() => {
    const checkStatus = async () => {
      try {
        const res = await apiClient.get('/system/health');
        if (res.data) {
          setStatus({
            mesh_status: res.data.mesh_status || 'ONLINE',
            gateway_status: res.data.gateway_status || 'ONLINE',
            internet_status: isOnline ? 'ONLINE' : 'OFFLINE',
            cloud_status: res.data.cloud_status || 'ONLINE',
            db_status: res.data.db_status || 'ONLINE',
          });
        }
      } catch {
        setStatus({
          mesh_status: 'ONLINE',
          gateway_status: 'ONLINE',
          internet_status: isOnline ? 'ONLINE' : 'OFFLINE',
          cloud_status: 'ONLINE',
          db_status: 'ONLINE',
        });
      }
    };

    checkStatus();
    const interval = setInterval(checkStatus, 10000);
    return () => clearInterval(interval);
  }, [isOnline, setStatus]);

  return {
    status,
    isOnline,
  };
}
`;

fs.writeFileSync('c:/Users/sabih/OneDrive/Desktop/MinorSafetySIH2026/frontend/src/hooks/useConnectivity.ts', useConnectivityContent, 'utf8');

// Fix i18n/index.ts
const i18nContent = `import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import en from './locales/en.json';
import hi from './locales/hi.json';
import ur from './locales/ur.json';

export type SupportedLanguage = 'en' | 'hi' | 'ur';

export interface LanguageOption {
  code: SupportedLanguage;
  name: string;
  nativeName: string;
  dir: 'ltr' | 'rtl';
}

export const SUPPORTED_LANGUAGES: LanguageOption[] = [
  { code: 'en', name: 'English', nativeName: 'English', dir: 'ltr' },
  { code: 'hi', name: 'Hindi', nativeName: 'हिन्दी', dir: 'ltr' },
  { code: 'ur', name: 'Urdu', nativeName: 'اردو', dir: 'rtl' },
];

const savedLang = (localStorage.getItem('strata_language') as SupportedLanguage) || 'en';

i18n
  .use(initReactI18next)
  .init({
    resources: {
      en: { translation: en },
      hi: { translation: hi },
      ur: { translation: ur },
    },
    lng: savedLang,
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false,
    },
  });

export function changeLanguage(lang: SupportedLanguage) {
  i18n.changeLanguage(lang);
  localStorage.setItem('strata_language', lang);
  const selected = SUPPORTED_LANGUAGES.find((l) => l.code === lang);
  const dir = selected?.dir || 'ltr';
  document.documentElement.dir = dir;
  document.documentElement.lang = lang;
}

export default i18n;
`;

fs.writeFileSync('c:/Users/sabih/OneDrive/Desktop/MinorSafetySIH2026/frontend/src/i18n/index.ts', i18nContent, 'utf8');

// Fix services/api/apiClient.ts
const apiClientContent = `import axios from 'axios';

const BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api';

export const apiClient = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token') || 'dev-mock-token';
    if (token && config.headers) {
      config.headers.Authorization = \`Bearer \${token}\`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    return Promise.reject(error);
  }
);
`;

fs.writeFileSync('c:/Users/sabih/OneDrive/Desktop/MinorSafetySIH2026/frontend/src/services/api/apiClient.ts', apiClientContent, 'utf8');

// Fix services/firebase/firebase.ts
const firebaseContent = `import { initializeApp } from 'firebase/app';
import { getAuth, GoogleAuthProvider } from 'firebase/auth';

const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY || 'mock-api-key',
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN || 'mock-auth-domain',
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID || 'mock-project-id',
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET || 'mock-storage-bucket',
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID || 'mock-sender-id',
  appId: import.meta.env.VITE_FIREBASE_APP_ID || 'mock-app-id',
};

export const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const googleProvider = new GoogleAuthProvider();
`;

fs.writeFileSync('c:/Users/sabih/OneDrive/Desktop/MinorSafetySIH2026/frontend/src/services/firebase/firebase.ts', firebaseContent, 'utf8');

// Fix vite-env.d.ts
const viteEnvContent = `/// <reference types="vite/client" />
`;
fs.writeFileSync('c:/Users/sabih/OneDrive/Desktop/MinorSafetySIH2026/frontend/src/vite-env.d.ts', viteEnvContent, 'utf8');

console.log('Fixed helper files!');
