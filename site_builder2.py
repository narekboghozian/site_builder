

import modules.objects as objects
from pathlib import Path
import json
import os

def main():

	source = json.load(open('config.json'))['source_folder']
	build = json.load(open('config.json'))['build_folder']
	build = 'build/'
	site = objects.Website()

	return 0

if __name__ == '__main__':
	main()
