#!/usr/bin/python

import subprocess

p = subprocess.Popen(["java", "Main"], stdin=subprocess.PIPE)
p.stdin.write("First line\r\n")
p.stdin.write("Second line\r\n")
p.stdin.write("x\r\n")
