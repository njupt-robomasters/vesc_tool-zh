import re, glob

T = {
 r'<double-click to edit>': '<双击编辑>',
 r'<font color=\"red\">Warning: </font>This is going to spin up all motors connected on the CAN-bus. Make sure that nothing is in the way.': r'<font color=\"red\">警告：</font>此操作将使 CAN 总线上连接的所有电机旋转。请确保周围没有障碍物。',
 r'<font color=\"red\">Warning: </font>This is going to spin up the motor. Make sure that nothing is in the way.': r'<font color=\"red\">警告：</font>此操作将使电机旋转。请确保周围没有障碍物。',
 r'The connected VESC-based ESC has old, but mostly compatible firmware. This is fine if your setup works properly.<br><br>Check out the firmware changelog (from the help menu or firmware page) to decide if you want to use some of the new features that have been added after your firmware version was released. Keep in mind that you only should upgrade firmware if you have time to test it after the upgrade and carefully make sure that everything works as expected.<br><br>This message can be disabled from the settings.': '已连接的基于 VESC 的电调固件较旧，但基本兼容。如果您的系统运行正常，这是没有问题的。<br><br>请查看固件更新日志（在帮助菜单或固件页面中），以决定是否使用固件发布之后新增的某些功能。请注意，只有在您有时间在升级后进行测试，并仔细确认一切正常时，才应升级固件。<br><br>可在设置中关闭此消息。',
}

LIT = re.compile(r'"((?:[^"\\]|\\.)*)"')
SEQ = re.compile(r'(?:\s*"(?:[^"\\]|\\.)*")+')
SKIP = ('vesc_tool-master', 'build', 'QCodeEditor', 'maddy', 'android', 'ios', 'lzokay', 'heatshrink', 'minimp3', 'qmarkdowntextedit')
replaced = 0
for f in glob.glob('**/*.cpp', recursive=True) + glob.glob('**/*.h', recursive=True):
    if f.startswith(SKIP):
        continue
    s = open(f, encoding='utf-8', newline='').read()
    edits = []
    for m in re.finditer(r'\btr\(\s*', s):
        r = SEQ.match(s, m.end())
        if not r:
            continue
        t = ''.join(LIT.findall(r.group(0)))
        if t in T:
            edits.append((m.end(), r.end(), T[t]))
    if edits:
        for a, b, v in reversed(edits):
            s = s[:a] + '"' + v + '"' + s[b:]
        open(f, 'w', encoding='utf-8', newline='').write(s)
        replaced += len(edits)
        print('edited', f, len(edits))
print('replacements:', replaced)
