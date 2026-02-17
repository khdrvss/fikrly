#!/usr/bin/env python3
"""
Final cleanup for business_list.html
"""

import re

filepath = '/home/ubuntu/projects/fikrly/frontend/templates/pages/business_list.html'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix remaining hardcoded classes
replacements = [
    (r'bg-secondary p-1 rounded-lg', r'bg-[var(--surface)] p-1 rounded-lg'),
    (r'bg-emerald-50 text-emerald-600 dark:bg-emerald-900/30 dark:text-emerald-300', r'bg-green-50 text-green-600'),
    (r'border-border-light dark:border-border-dark text-\[var\(--text-primary\)\] dark:text-slate-200', r'border-[var(--border)] text-[var(--text-primary)]'),
    (r'hover:border-primary-600', r'hover:border-[var(--accent)]'),
    (r'group-hover:bg-primary-50/50', r''),
    (r'focus-visible:ring-2 focus-visible:ring-emerald-500 focus-visible:ring-offset-2', ''),
    (r'text-xl font-semibold mb-2', r'text-xl font-semibold text-[var(--text-primary)] mb-2'),
    (r'px-3 py-1\.5 rounded-full bg-emerald-50 text-emerald-700', r'px-3 py-1.5 rounded-full bg-green-50 text-green-600'),
    (r'hover:bg-emerald-100', r'hover:bg-green-100'),
    (r'bg-emerald-500 text-white hover:bg-emerald-600', r'bg-[var(--accent)] text-white hover:opacity-90'),
]

for pattern, replacement in replacements:
    content = re.sub(pattern, replacement, content)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"✓ Cleaned up {filepath}")
