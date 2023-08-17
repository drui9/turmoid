'''
@author: sp3rtah
@email: ngaira14nelson@gmail.com

Desc: This is a build script for Droid module.

Usage:
Package .backup-ignore, Makefile, requirements.txt and **/*.py into a zipfile.
...maintaining directory structure. 
Unpack zipfile on termux device through ssh.

todo: check .backup-ignore idea
'''
import os

base = ['Makefile', 'requirements.txt']

def main(directory ='Droid'):
	files = os.listdir('.')
	#
	for _file in base:
		if _file not in files:
			raise RuntimeError(f'{_file} is missing!')
	#
	files = [f for f in os.walk(directory)]
	seen = list()
	for f in files:
		print(f)

if __name__ == '__main__':
	main()
