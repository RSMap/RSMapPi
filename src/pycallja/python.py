import subprocess


def main():
	p = subprocess.Popen(["java", "MyClass"], stdin=subprocess.PIPE)
	p.stdin.write(b"First line\r\n")
	p.stdin.write(b"Second line\r\n")
	p.stdin.write(b"x\r\n") 

if __name__ == '__main__':
	main()
