#!/usr/bin/env python3
"""
Dark Mode Theme Token Replacement Script
Replaces hardcoded color classes with CSS variable tokens
"""

import re
import os
from pathlib import Path

# Define replacement patterns
REPLACEMENTS = [
    # Background replacements
    (r'\bbg-white\b', 'bg-[var(--surface)]'),
    (r'\bbg-gray-50\b', 'bg-[var(--bg)]'),
    (r'\bbg-gray-100\b', 'bg-[var(--surface)]'),
    
    # Text replacements
    (r'\btext-gray-900\b', 'text-[var(--text-primary)]'),
    (r'\btext-gray-700\b', 'text-[var(--text-primary)]'),
    (r'\btext-gray-600\b', 'text-[var(--text-secondary)]'),
    (r'\btext-gray-500\b', 'text-[var(--text-secondary)]'),
    (r'\btext-slate-900\b', 'text-[var(--text-primary)]'),
    (r'\btext-slate-700\b', 'text-[var(--text-primary)]'),
    
    # Border replacements
    (r'\bborder-gray-100\b', 'border-[var(--border)]'),
    (r'\bborder-gray-200\b', 'border-[var(--border)]'),
    
    # Primary color replacements
    (r'\btext-primary-600\b', 'text-[var(--accent)]'),
    (r'\bhover:text-primary-600\b', 'hover:text-[var(--accent)]'),
    (r'\bhover:text-primary-700\b', 'hover:opacity-80'),
    (r'\bbg-primary-600\b', 'bg-[var(--accent)]'),
    (r'\bhover:bg-primary-700\b', 'hover:opacity-90'),
]

# Patterns to remove (gradient overlays)
REMOVE_PATTERNS = [
    r'<div class="absolute inset-0 bg-gradient-to-[tb] from-\S+/\d+ (?:via-\S+/\d+ )?to-\S+(?:/\d+)?"[^>]*></div>',
    r'<div class="absolute inset-0 bg-gradient-to-br from-\S+ to-\S+ opacity-\d+"[^>]*></div>',
]


def fix_template_file(filepath):
    """Apply dark mode token fixes to a single template file"""
    print(f"Processing: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Apply replacements
    for pattern, replacement in REPLACEMENTS:
        content = re.sub(pattern, replacement, content)
    
    # Remove gradient overlays
    for pattern in REMOVE_PATTERNS:
        content = re.sub(pattern, '', content)
    
    # Check if anything changed
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✓ Updated {filepath}")
        return True
    else:
        print(f"  - No changes needed for {filepath}")
        return False


def main():
    """Process all HTML templates in the frontend/templates directory"""
    base_dir = Path(__file__).parent.parent
    templates_dir = base_dir / 'frontend' / 'templates'
    
    if not templates_dir.exists():
        print(f"Error: Templates directory not found: {templates_dir}")
        return
    
    print(f"Scanning templates in: {templates_dir}\n")
    
    # Find all HTML files
    html_files = list(templates_dir.rglob('*.html'))
    
    # Exclude already processed files
    exclude_files = ['base.html', 'home.html', 'company_detail.html']
    html_files = [f for f in html_files if f.name not in exclude_files]
    
    print(f"Found {len(html_files)} template files to process\n")
    
    updated_count = 0
    for filepath in html_files:
        if fix_template_file(filepath):
            updated_count += 1
    
    print(f"\n{'='*60}")
    print(f"Summary: Updated {updated_count} out of {len(html_files)} files")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
