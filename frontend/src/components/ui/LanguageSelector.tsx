import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { SUPPORTED_LANGUAGES, SupportedLanguage, changeLanguage } from '../../i18n';
import { Globe, Check, ChevronDown } from 'lucide-react';

interface LanguageSelectorProps {
  variant?: 'segmented' | 'dropdown';
  className?: string;
}

export const LanguageSelector: React.FC<LanguageSelectorProps> = ({
  variant = 'segmented',
  className = '',
}) => {
  const { i18n } = useTranslation();
  const [isOpen, setIsOpen] = useState(false);
  const currentLang = (i18n.language as SupportedLanguage) || 'en';

  if (variant === 'segmented') {
    return (
      <div className={`inline-flex items-center p-1 bg-slate-100 rounded-xl border border-slate-200 ${className}`}>
        {SUPPORTED_LANGUAGES.map((lang) => {
          const isSelected = currentLang === lang.code;
          return (
            <button
              key={lang.code}
              type="button"
              onClick={() => changeLanguage(lang.code)}
              className={
                isSelected
                  ? 'px-3 py-1 text-xs font-bold rounded-lg transition-all bg-white text-blue-700 shadow-xs'
                  : 'px-3 py-1 text-xs font-bold rounded-lg transition-all text-slate-600 hover:text-slate-900 hover:bg-slate-200/60'
              }
            >
              {lang.nativeName}
            </button>
          );
        })}
      </div>
    );
  }

  return (
    <div className={`relative ${className}`}>
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-slate-200 bg-white text-xs font-semibold text-slate-700 hover:bg-slate-50 transition"
      >
        <Globe className="h-4 w-4 text-slate-500" />
        <span>{SUPPORTED_LANGUAGES.find((l) => l.code === currentLang)?.nativeName}</span>
        <ChevronDown className="h-3.5 w-3.5 text-slate-400" />
      </button>

      {isOpen && (
        <div className="absolute right-0 rtl:right-auto rtl:left-0 mt-2 w-36 rounded-2xl bg-white border border-slate-200 shadow-xl py-1 z-50">
          {SUPPORTED_LANGUAGES.map((lang) => {
            const isSelected = currentLang === lang.code;
            return (
              <button
                key={lang.code}
                type="button"
                onClick={() => {
                  changeLanguage(lang.code);
                  setIsOpen(false);
                }}
                className={
                  isSelected
                    ? 'w-full px-3.5 py-2 text-left rtl:text-right text-xs font-bold text-blue-600 bg-blue-50 flex items-center justify-between'
                    : 'w-full px-3.5 py-2 text-left rtl:text-right text-xs text-slate-700 hover:bg-slate-50 flex items-center justify-between'
                }
              >
                <span>{lang.nativeName}</span>
                {isSelected && <Check className="h-3.5 w-3.5 text-blue-600" />}
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default LanguageSelector;
