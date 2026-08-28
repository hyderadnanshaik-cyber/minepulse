import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import en from './en.json';
import hi from './hi.json';
import ur from './ur.json';

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

// Set initial document attributes
if (typeof document !== 'undefined') {
  const initialOption = SUPPORTED_LANGUAGES.find((l) => l.code === savedLang);
  document.documentElement.dir = initialOption?.dir || 'ltr';
  document.documentElement.lang = savedLang;
}

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
  if (typeof document !== 'undefined') {
    document.documentElement.dir = dir;
    document.documentElement.lang = lang;
  }
}

export default i18n;
