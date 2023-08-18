'''
@author: sp3rtah
@email: ngaira14nelson@gmail.com

Desc: This script builds `Droid` module as a zipfile and does
`scp .build/build.zip _gateway:` to deploy to termux.

_gateway is specified in ~/.ssh/config as:

Host _gateway
	Port 2221
'''
import os
import zipfile
import subprocess

base = ('Makefile', 'requirements.txt', 'start.py')

def main(directory ='Droid'):
	build_dir = '.build'
	zipname = os.path.join(build_dir, 'build.zip')
	files = os.listdir('.')
	#
	for _file in base:
		if _file not in files:
			raise RuntimeError(f'{_file} is missing!')
	#
	files = [f for f in os.walk(directory)]
	seen = [b for b in base	]
	for f in files:
		cwd, dirs, scripts = f
		seen.extend([os.path.join(cwd, i) for i in scripts if i[-3:] == '.py'])
	#
	os.system(f'mkdir -p {build_dir}')
	with zipfile.ZipFile(zipname, 'w') as zf:
		for item in seen:
			zf.write(item, compress_type=zipfile.ZIP_DEFLATED)
	#
	print(f'Deploying [{zipname}]')
	deploy = subprocess.run(['scp', zipname, '_gateway:'])
	try:
		deploy.check_returncode()
		print('Deployment successful.')
		return
	except subprocess.CalledProcessError:
		pass
	print('Deployment failed.')

if __name__ == '__main__':
	main()
