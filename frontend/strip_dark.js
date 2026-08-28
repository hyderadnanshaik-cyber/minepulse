import fs from 'fs';
import path from 'path';

function stripDarkClasses(filePath) {
  let content = fs.readFileSync(filePath, 'utf8');
  // Match dark:class and remove it with surrounding whitespace cleanup
  const newContent = content.replace(/\bdark:[a-zA-Z0-9_\-\/\[\]#:]+/g, '').replace(/\s{2,}/g, ' ');
  
  if (newContent !== content) {
    fs.writeFileSync(filePath, newContent, 'utf8');
    console.log(`Cleaned dark classes from: ${filePath}`);
  }
}

function processDir(dir) {
  const files = fs.readdirSync(dir);
  files.forEach(file => {
    const fullPath = path.join(dir, file);
    if (fs.statSync(fullPath).isDirectory()) {
      processDir(fullPath);
    } else if (fullPath.endsWith('.tsx') || fullPath.endsWith('.ts')) {
      stripDarkClasses(fullPath);
    }
  });
}

processDir('c:/Users/sabih/OneDrive/Desktop/MinorSafetySIH2026/frontend/src');
