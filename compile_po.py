#!/usr/bin/env python3
import sys
import os
import struct
import ast

def usage():
    print("Usage: compile_po.py [options] inputfile", file=sys.stderr)
    print("Options:", file=sys.stderr)
    print("  -o outputfile   Specify the output file (default is inputfile.mo)", file=sys.stderr)

def generate():
    if len(sys.argv) < 2:
        usage()
        sys.exit(1)

    outfile = None
    infile = None

    args = sys.argv[1:]
    while args:
        arg = args.pop(0)
        if arg == '-o':
            if args:
                outfile = args.pop(0)
            else:
                usage()
                sys.exit(1)
        else:
            infile = arg

    if not infile:
        usage()
        sys.exit(1)

    if outfile is None:
        if infile.endswith('.po'):
            outfile = infile[:-3] + '.mo'
        else:
            outfile = infile + '.mo'

    make(infile, outfile)

def unescape(s):
    """Convert a string in PO format to a byte string."""
    # s is bytes containing the quoted string, e.g. b'"foo\n"'
    try:
        # ast.literal_eval is safer than eval
        # We need to decode to string for literal_eval if we want to handle it as string literal
        # But we want bytes.
        # If we use eval on bytes, it works for b'...' literals.
        # But the input is like b'"foo"'.
        # In Python 3, eval(b'"foo"') returns b'foo'.
        res = eval(s)
        if not isinstance(res, bytes):
             # If it's not bytes, force it to bytes if it's string
             if isinstance(res, str):
                 return res.encode('utf-8')
        return res
    except Exception as e:
        # print(f"Error unescaping {s}: {e}", file=sys.stderr)
        return s

def make(filename, outfile):
    ID = 1
    STR = 2

    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading file {filename}: {e}", file=sys.stderr)
        sys.exit(1)

    section = None
    fuzzy = 0

    # Parse the catalog
    msgid = b''
    msgstr = b''
    messages = {}

    for l in lines:
        l_stripped = l.strip()

        # Skip empty lines
        if not l_stripped:
            continue

        # Skip comments
        if l_stripped.startswith('#'):
            if l_stripped.startswith('#,') and 'fuzzy' in l_stripped:
                fuzzy = 1
            # If we get a comment line after a msgstr, this is a new entry
            if section == STR:
                add(messages, msgid, msgstr, fuzzy)
                section = None
                fuzzy = 0
            continue

        # Now we are in a msgid section, output previous section
        if l_stripped.startswith('msgid') and not l_stripped.startswith('msgid_plural'):
            if section == STR:
                add(messages, msgid, msgstr, fuzzy)
            section = ID
            # Remove 'msgid' and whitespace
            l_content = l_stripped[5:].strip()
            msgid = unescape(l_content.encode('utf-8'))
            msgstr = b''
            fuzzy = 0 # Reset fuzzy if not set by comment immediately preceding

        # This is a message with plural forms
        elif l_stripped.startswith('msgid_plural'):
            if section == STR:
                add(messages, msgid, msgstr, fuzzy)
            section = ID
            l_content = l_stripped[12:].strip()
            msgid += b'\0' + unescape(l_content.encode('utf-8'))

        # Now we are in a msgstr section
        elif l_stripped.startswith('msgstr'):
            if l_stripped.startswith('msgstr['):
                # Plural form
                if section == ID:
                    section = STR
                    msgstr = b''

                # Find the string part
                idx = l_stripped.find('"')
                if idx != -1:
                    s = unescape(l_stripped[idx:].encode('utf-8'))
                    if msgstr:
                        msgstr += b'\0' + s
                    else:
                        msgstr = s
            else:
                # Singular
                section = STR
                l_content = l_stripped[6:].strip()
                msgstr = unescape(l_content.encode('utf-8'))

        # Continuation line
        elif l_stripped.startswith('"'):
            l_content = l_stripped.encode('utf-8')
            if section == ID:
                msgid += unescape(l_content)
            elif section == STR:
                msgstr += unescape(l_content)

    # Add last entry
    if section == STR:
        add(messages, msgid, msgstr, fuzzy)

    # Compute output
    output = generate_mo(messages)

    try:
        with open(outfile, 'wb') as f:
            f.write(output)
        print(f"Compiled {filename} to {outfile}")
    except Exception as e:
        print(f"Error writing file {outfile}: {e}", file=sys.stderr)
        sys.exit(1)

def add(messages, msgid, msgstr, fuzzy):
    "Add a non-fuzzy translation to the dictionary."
    if not fuzzy and msgstr:
        messages[msgid] = msgstr

def generate_mo(messages):
    "Return the generated mo file as a byte string."
    magic = 0x950412de
    version = 0
    num_strings = len(messages)

    keys = sorted(messages.keys())

    # Offsets
    header_size = 28
    otable_offset = header_size
    ttable_offset = otable_offset + num_strings * 8
    data_offset = ttable_offset + num_strings * 8

    otable = []
    ttable = []

    ids_data = bytearray()
    strs_data = bytearray()

    # We'll build data buffers and calculate offsets
    # But we need absolute offsets in the file.

    # Let's build the data block first
    # We can put keys then values

    current_offset = data_offset

    # Process keys
    for k in keys:
        l = len(k)
        otable.append((l, current_offset))
        ids_data.extend(k)
        ids_data.append(0) # Null terminator
        current_offset += l + 1

    # Process values
    for k in keys:
        v = messages[k]
        l = len(v)
        ttable.append((l, current_offset))
        strs_data.extend(v)
        strs_data.append(0) # Null terminator
        current_offset += l + 1

    # Construct binary
    output = bytearray()

    # Header
    output.extend(struct.pack('I', magic))
    output.extend(struct.pack('I', version))
    output.extend(struct.pack('I', num_strings))
    output.extend(struct.pack('I', otable_offset))
    output.extend(struct.pack('I', ttable_offset))
    output.extend(struct.pack('I', 0)) # Hash table size
    output.extend(struct.pack('I', 0)) # Hash table offset

    # OTable
    for l, o in otable:
        output.extend(struct.pack('II', l, o))

    # TTable
    for l, o in ttable:
        output.extend(struct.pack('II', l, o))

    # Data
    output.extend(ids_data)
    output.extend(strs_data)

    return output

if __name__ == '__main__':
    generate()
