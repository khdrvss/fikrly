#!/usr/bin/env python3
import sys
import os
import struct

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
    try:
        # eval on bytes literal returns bytes (e.g. b'"foo"' -> b'foo')
        res = eval(s)
        if not isinstance(res, bytes):
             if isinstance(res, str):
                 return res.encode('utf-8')
        return res
    except Exception as e:
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
    msgid = b''
    msgstr = b''
    messages = {}

    for l in lines:
        l_stripped = l.strip()
        if not l_stripped:
            continue
        if l_stripped.startswith('#'):
            if l_stripped.startswith('#,') and 'fuzzy' in l_stripped:
                fuzzy = 1
            if section == STR:
                add(messages, msgid, msgstr, fuzzy)
                section = None
                fuzzy = 0
            continue

        if l_stripped.startswith('msgid') and not l_stripped.startswith('msgid_plural'):
            if section == STR:
                add(messages, msgid, msgstr, fuzzy)
            section = ID
            l_content = l_stripped[5:].strip()
            msgid = unescape(l_content.encode('utf-8'))
            msgstr = b''
            fuzzy = 0

        elif l_stripped.startswith('msgid_plural'):
            if section == STR:
                add(messages, msgid, msgstr, fuzzy)
            section = ID
            l_content = l_stripped[12:].strip()
            msgid += b'\0' + unescape(l_content.encode('utf-8'))

        elif l_stripped.startswith('msgstr'):
            if l_stripped.startswith('msgstr['):
                if section == ID:
                    section = STR
                    msgstr = b''
                idx = l_stripped.find('"')
                if idx != -1:
                    s = unescape(l_stripped[idx:].encode('utf-8'))
                    if msgstr:
                        msgstr += b'\0' + s
                    else:
                        msgstr = s
            else:
                section = STR
                l_content = l_stripped[6:].strip()
                msgstr = unescape(l_content.encode('utf-8'))

        elif l_stripped.startswith('"'):
            l_content = l_stripped.encode('utf-8')
            if section == ID:
                msgid += unescape(l_content)
            elif section == STR:
                msgstr += unescape(l_content)

    if section == STR:
        add(messages, msgid, msgstr, fuzzy)

    output = generate_mo(messages)

    try:
        with open(outfile, 'wb') as f:
            f.write(output)
        print(f"Compiled {filename} to {outfile}")
    except Exception as e:
        print(f"Error writing file {outfile}: {e}", file=sys.stderr)
        sys.exit(1)

def add(messages, msgid, msgstr, fuzzy):
    if not fuzzy and msgstr:
        messages[msgid] = msgstr

def generate_mo(messages):
    magic = 0x950412de
    version = 0
    num_strings = len(messages)
    keys = sorted(messages.keys())

    header_size = 28
    otable_offset = header_size
    ttable_offset = otable_offset + num_strings * 8
    data_offset = ttable_offset + num_strings * 8

    otable = []
    ttable = []
    ids_data = bytearray()
    strs_data = bytearray()

    current_offset = data_offset

    for k in keys:
        l = len(k)
        otable.append((l, current_offset))
        ids_data.extend(k)
        ids_data.append(0)
        current_offset += l + 1

    for k in keys:
        v = messages[k]
        l = len(v)
        ttable.append((l, current_offset))
        strs_data.extend(v)
        strs_data.append(0)
        current_offset += l + 1

    output = bytearray()
    output.extend(struct.pack('I', magic))
    output.extend(struct.pack('I', version))
    output.extend(struct.pack('I', num_strings))
    output.extend(struct.pack('I', otable_offset))
    output.extend(struct.pack('I', ttable_offset))
    output.extend(struct.pack('I', 0))
    output.extend(struct.pack('I', 0))

    for l, o in otable:
        output.extend(struct.pack('II', l, o))
    for l, o in ttable:
        output.extend(struct.pack('II', l, o))

    output.extend(ids_data)
    output.extend(strs_data)

    return output

if __name__ == '__main__':
    generate()
