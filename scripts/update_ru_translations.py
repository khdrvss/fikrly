#!/usr/bin/env python3
"""Update Russian translations for new Trustpilot-style UI"""

import re

# Translations mapping (Uzbek -> Russian)
TRANSLATIONS = {
    'Kompaniyalar': 'Компании',
    'Kompaniya yoki kategoriya qidiring...': 'Найти компанию или категорию...',
    'Kompaniya qidiring...': 'Найти компанию...',
    'Qidiring...': 'Поиск...',
    'kompaniya topildi': 'компаний найдено',
    'Barcha kategoriyalar': 'Все категории',
    'Barcha shaharlar': 'Все города',
    'Filtrlar': 'Фильтры',
    'Minimal baho': 'Минимальный рейтинг',
    'Faqat tasdiqlangan': 'Только подтвержденные',
    'Filtrlarni tozalash': 'Сбросить фильтры',
    'Qo\\'llash': 'Применить',
    'Tasdiqlangan': 'Подтверждено',
    'sharhlar': 'отзывов',
    'Eng mos': 'Самые подходящие',
    'Eng ko\\'p sharhlar': 'Больше всего отзывов',
    'Yangi': 'Новые',
    'A-Z': 'А-Я',
    'Ro\\'yxatdan o\\'tish': 'Регистрация',
    'Kirish': 'Войти',
    'Chiqish': 'Выйти',
    'Hech qanday natija topilmadi': 'Результаты не найдены',
    'Filtrlarni o\\'zgartiring yoki boshqa kategoriya sinab ko\\'ring.': 'Измените фильтры или попробуйте другую категорию.',
}

def update_po_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    for uz, ru in TRANSLATIONS.items():
        # Pattern to find msgid and update msgstr
        # Handle both simple and fuzzy entries
        pattern = rf'(#[^\n]*\n)*(msgid "{re.escape(uz)}"\nmsgstr ")([^"]*)"'
        
        def replacer(match):
            comments = match.group(1) or ''
            # Remove fuzzy flag if present
            comments = re.sub(r'#,\s*fuzzy\n', '', comments)
            return f'{comments}msgid "{uz}"\nmsgstr "{ru}"'
        
        content = re.sub(pattern, replacer, content)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Updated {filepath}")

if __name__ == '__main__':
    update_po_file('/app/locale/ru/LC_MESSAGES/django.po')
    print("Russian translations updated successfully!")
