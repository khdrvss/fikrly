#!/usr/bin/env python3
"""
Fill Uzbek translation file with msgid values as msgstr.
This script copies msgid to msgstr for all empty translations in the Uzbek locale.
"""
import re
import sys
from pathlib import Path

def fill_translations(po_file_path):
    """Fill empty msgstr with msgid values."""
    with open(po_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove the fuzzy flag from header
    content = re.sub(r'^#, fuzzy\n', '', content, flags=re.MULTILINE)
    
    # Pattern to match msgid followed by empty msgstr
    # This handles both simple and multiline msgid
    def replace_empty_msgstr(match):
        msgid_line = match.group(1)
        # Extract the actual text from msgid
        msgid_text = msgid_line.replace('msgid ', '', 1)
        return f'{msgid_line}\nmsgstr {msgid_text}'
    
    # Replace empty msgstr with msgid value
    # Pattern: msgid "..." followed by msgstr ""
    pattern = r'(msgid ".*?")\nmsgstr ""'
    content = re.sub(pattern, replace_empty_msgstr, content)
    
    # Handle multiline msgid/msgstr
    # This is more complex, so let's do a line-by-line approach
    lines = content.split('\n')
    result = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        result.append(line)
        
        # Check if this is a msgid line
        if line.startswith('msgid "') and line != 'msgid ""':
            msgid_value = line.replace('msgid ', '', 1)
            
            # Collect multiline msgid if present
            msgid_lines = [msgid_value]
            i += 1
            while i < len(lines) and lines[i].startswith('"') and not lines[i-1].startswith('msgstr'):
                msgid_lines.append(lines[i])
                result.append(lines[i])
                i += 1
            
            # Now check if next line is msgstr ""
            if i < len(lines) and lines[i].strip() == 'msgstr ""':
                # Replace with msgid value
                if len(msgid_lines) == 1:
                    result.append(f'msgstr {msgid_lines[0]}')
                else:
                    result.append(f'msgstr {msgid_lines[0]}')
                    for msgid_line in msgid_lines[1:]:
                        result.append(msgid_line)
                i += 1
                continue
        
        i += 1
    
    # Write back
    with open(po_file_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(result))
    
    print(f"✅ Updated {po_file_path}")
    print("✅ Filled empty msgstr fields with msgid values")
    print("✅ Removed fuzzy flag")

if __name__ == '__main__':
    # Get the project root directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    uz_po_file = project_root / 'locale' / 'uz' / 'LC_MESSAGES' / 'django.po'
    
    if not uz_po_file.exists():
        print(f"❌ File not found: {uz_po_file}")
        sys.exit(1)
    
    fill_translations(uz_po_file)
