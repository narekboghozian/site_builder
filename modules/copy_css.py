import os
import shutil
import json


def copy_css():
	src = "css/main.css"
	root = json.load(open('config.json'))['build_folder']
	dst = os.path.join(root, src)
	if 'css' not in os.listdir(root):
		os.mkdir(os.path.join(root, 'css'))
	shutil.copyfile(src, dst)
