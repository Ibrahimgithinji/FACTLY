/**
 * Checks for hardcoded color values in CSS files that should use CSS variables instead.
 * Run: node scripts/check-hardcoded-colors.js
 * 
 * Exits with code 1 if violations are found.
 */
const fs = require('fs');
const path = require('path');

const SRC_DIR = path.join(__dirname, '..', 'src');
const EXCLUDE_PATTERNS = [
  'node_modules',
  'build',
];
// These files define the CSS custom properties themselves — allowed
const ALLOWED_FILES = [
  'index.css',
];

const HEX_COLOR = /#[0-9a-fA-F]{3,8}/g;
const RGB_COLOR = /rgba?\([^)]+\)/g;

// Colors in these patterns are OK (variable definitions, keyframes, dark-mode-only blocks)
const ALLOWED_CONTEXTS = [
  /^\s*--[a-z]/m,        // CSS variable definition
  /@keyframes/,           // Animation keyframes
  /prefers-color-scheme/, // Media query for color scheme
  /prefers-contrast/,     // High contrast mode
  /@media print/,         // Print styles
  /print/,                 // Any print-related
];

let hasErrors = false;

function walkDir(dir) {
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      if (!EXCLUDE_PATTERNS.includes(entry.name)) {
        walkDir(fullPath);
      }
    } else if (entry.name.endsWith('.css')) {
      checkFile(fullPath);
    }
  }
}

function isAllowedLine(line) {
  return ALLOWED_CONTEXTS.some(re => re.test(line));
}

function checkFile(filePath) {
  const relativePath = path.relative(SRC_DIR, filePath);
  if (ALLOWED_FILES.includes(path.basename(filePath))) return;

  const content = fs.readFileSync(filePath, 'utf-8');
  const lines = content.split('\n');
  
  let violations = [];
  
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const lineNum = i + 1;
    
    // Skip comments and variable definitions
    if (isAllowedLine(line)) continue;
    if (line.trim().startsWith('/*') || line.trim().startsWith('*') || line.trim().startsWith('//')) continue;
    if (line.trim().startsWith('@')) continue; // keyframes, media, etc.
    
    // Check for hex colors not inside var()
    const hexMatches = line.match(HEX_COLOR);
    if (hexMatches) {
      for (const match of hexMatches) {
        // If this hex color is not inside var(...) and not inside a CSS variable definition
        const beforeMatch = line.substring(0, line.indexOf(match));
        if (!beforeMatch.includes('var(') && !beforeMatch.trim().startsWith('--')) {
          violations.push({ lineNum, color: match, line: line.trim() });
        }
      }
    }
  }
  
  if (violations.length > 0) {
    hasErrors = true;
    console.log(`\n\x1b[31m${relativePath}\x1b[0m — ${violations.length} hardcoded color(s):`);
    for (const v of violations) {
      console.log(`  \x1b[33mLine ${v.lineNum}:\x1b[0m ${v.color}  →  ${v.line.substring(0, 80)}`);
    }
  }
}

console.log('\n\x1b[36m🔍 Scanning for hardcoded colors in CSS files...\x1b[0m');
walkDir(SRC_DIR);

if (hasErrors) {
  console.log('\n\x1b[31m❌ Found hardcoded colors! Use CSS variables (var(--...)) instead.\x1b[0m');
  process.exit(1);
} else {
  console.log('\n\x1b[32m✅ All CSS files use CSS variables. No hardcoded colors found.\x1b[0m');
}
