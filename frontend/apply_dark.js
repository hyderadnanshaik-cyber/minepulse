import fs from 'fs';
import path from 'path';

const replacements = [
  { regex: /\bbg-white\b(?! dark:)/g, replace: 'bg-white dark:bg-slate-800' },
  { regex: /\bbg-slate-50\b(?! dark:)/g, replace: 'bg-slate-50 dark:bg-slate-900' },
  { regex: /\btext-slate-900\b(?! dark:)/g, replace: 'text-slate-900 dark:text-white' },
  { regex: /\btext-slate-800\b(?! dark:)/g, replace: 'text-slate-800 dark:text-slate-200' },
  { regex: /\btext-slate-700\b(?! dark:)/g, replace: 'text-slate-700 dark:text-slate-300' },
  { regex: /\btext-slate-600\b(?! dark:)/g, replace: 'text-slate-600 dark:text-slate-300' },
  { regex: /\btext-slate-500\b(?! dark:)/g, replace: 'text-slate-500 dark:text-slate-400' },
  { regex: /\btext-slate-400\b(?! dark:)/g, replace: 'text-slate-400 dark:text-slate-500' },
  { regex: /\bborder-slate-200\b(?! dark:)/g, replace: 'border-slate-200 dark:border-slate-700' },
  { regex: /\bborder-slate-100\b(?! dark:)/g, replace: 'border-slate-100 dark:border-slate-700/50' },
  { regex: /\bbg-slate-100\b(?! dark:)/g, replace: 'bg-slate-100 dark:bg-slate-700' },
  { regex: /\bhover:bg-slate-100\b(?! dark:)/g, replace: 'hover:bg-slate-100 dark:hover:bg-slate-700' },
  { regex: /\bhover:bg-slate-50\b(?! dark:)/g, replace: 'hover:bg-slate-50 dark:hover:bg-slate-700/50' },
  { regex: /\bdivide-slate-100\b(?! dark:)/g, replace: 'divide-slate-100 dark:divide-slate-700/50' },
  { regex: /\bdivide-slate-200\b(?! dark:)/g, replace: 'divide-slate-200 dark:divide-slate-700' },
];

function processFile(filePath) {
  let content = fs.readFileSync(filePath, 'utf8');
  let changed = false;
  
  replacements.forEach(({ regex, replace }) => {
    const newContent = content.replace(regex, replace);
    if (newContent !== content) {
      content = newContent;
      changed = true;
    }
  });

  if (changed) {
    fs.writeFileSync(filePath, content, 'utf8');
    console.log(`Updated ${filePath}`);
  }
}

function processDir(dir) {
  const files = fs.readdirSync(dir);
  files.forEach(file => {
    const fullPath = path.join(dir, file);
    if (fs.statSync(fullPath).isDirectory()) {
      processDir(fullPath);
    } else if (fullPath.endsWith('.tsx') || fullPath.endsWith('.ts')) {
      processFile(fullPath);
    }
  });
}

processDir('c:/Users/sabih/OneDrive/Desktop/MinorSafetySIH2026/frontend/src/components');
processDir('c:/Users/sabih/OneDrive/Desktop/MinorSafetySIH2026/frontend/src/pages');
