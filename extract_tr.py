import re, glob

LIT = re.compile(r'"((?:[^"\\]|\\.)*)"')
SEQ = re.compile(r'(?:\s*"(?:[^"\\]|\\.)*")+')
SKIP = ('vesc_tool-master', 'build', 'QCodeEditor', 'maddy', 'android', 'ios', 'lzokay', 'heatshrink', 'minimp3', 'qmarkdowntextedit')
out = {}
for f in glob.glob('**/*.cpp', recursive=True) + glob.glob('**/*.h', recursive=True):
    if f.startswith(SKIP):
        continue
    s = open(f, encoding='utf-8', errors='replace').read()
    for m in re.finditer(r'\btr\(\s*', s):
        r = SEQ.match(s, m.end())
        if not r:
            continue
        t = ''.join(LIT.findall(r.group(0)))
        if re.search('[A-Za-z]{3}', t) and not re.search('[一-鿿]', t):
            out.setdefault(t, []).append(f + ':' + str(s.count('\n', 0, m.start()) + 1))
print(len(out))
for t, l in out.items():
    print(l[0], len(l), '|', t[:400])
