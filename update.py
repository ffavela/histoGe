import os

try:
	os.system('git pull')
	os.system('pip3 install -r requirements.txt')
except:
	
	print('Error')
