from modules.process_entry import process_entry
from modules.generate_rss import generate_rss
from modules.make_breadcrumbs import make_breadcrumbs
from modules.make_home_page3 import make_home_page
from modules.copy_css import copy_css
import modules.objects as objects
from pathlib import Path
import json
import os

# def get_files(root = '.'):
# 	'''Returns all non-hidden .md files in target directory'''
# 	files = []
# 	dir = os.listdir(root)
# 	for d in dir:
# 		fullpath = os.path.join(root, d)
# 		entry = False
# 		if d[0] != '.':
# 			if os.path.isfile(fullpath) and \
# 				fullpath.endswith('.md'):
# 				files.append(fullpath)
# 			elif os.path.isdir(fullpath):
# 				entries = get_files(fullpath)
# 				for entry in entries:
# 					files.append(entry)
# 	return files

def main():
	entries = []
	root = json.load(open('config.json'))['build_folder'] # for atom-live-server
	root = '/'
	files = get_files('src')

	categories = {
		# "blogs",
		"notes",
		# "ideas",
		"projects"
	}

	for file in files:
		entry = objects.entry(file)
		entry.format_and_build()
		entry.write()
		entries.append(entry)
		# if entry.meta['type'] not in categories:
		# 	categories[entry.meta['type']] = []

	make_home_page(entries, root)
	return 0

if __name__ == '__main__':
	main()
