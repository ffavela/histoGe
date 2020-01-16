import os
import subprocess

try:
	os.system('pip3 install -r requirements.txt')
	path = subprocess.getoutput("pwd")+"/histoGe.py"
	os.system("mkdir -p ~/.myPrograms")
	a = "cd ~/.myPrograms && ln -s "+ path + "   histoGe"
	os.system(a)
	os.system("echo 'export PATH=$PATH:~/.myPrograms' >> ~/.bashrc")
except:
	print('Error')
