import subprocess

p = subprocess.Popen(["java", "Main"], stdin=subprocess.PIPE)
b = bytes("First line\r\n", 'utf-8')
p.stdin.write(3)
#p.stdin.write("Second line\r\n")
p.stdin.write("x\r\n")
