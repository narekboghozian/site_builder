from modules.process_entry import process_entry
from modules.generate_rss import generate_rss
from modules.make_breadcrumbs import make_breadcrumbs
from modules.make_home_page import make_home_page
from modules.copy_css import copy_css
from pathlib import Path
import json
import os

def get_files(root = '.'):
	'''Returns all non-hidden .md files in target directory'''
	files = []
	dir = os.listdir(root)
	for d in dir:
		fullpath = os.path.join(root, d)
		entry = False
		if d[0] != '.':
			if os.path.isfile(fullpath) and \
				fullpath.endswith('.md'):
				files.append(fullpath)
			elif os.path.isdir(fullpath):
				entries = get_files(fullpath)
				for entry in entries:
					files.append(entry)
	return files

def __format_entry(entry, root = '/'):
	"""Input here is a json"""

	if root[0] != '/':
		root = '/' + root

	template_type = 'article' # default
	if 'template' in entry[0]:
		template_type = entry[0]['template']

	template_paths = {
		'article': 'templates/article_template.html',
		'home': 'templates/home_template.html'
	}
	template_path = template_paths[template_type]
	template = open(template_path).read()

	# Metadata
	for item in entry[0]: # process metadata
		if "{%s}"%item in template:
			template = template.replace("{%s}"%item, entry[0][item])

	# Breadcrumbs
	crumbs_id = "{breadcrumbs}"
	if crumbs_id in template:
		path_items = entry[0]['filename'].replace('.md','').split('/')
		# path = [('Home', '/')]
		# path = [('Home', '/narekb/')] # for debugging when using atom-live-server
		path = [('Home', root)]
		link = path[0][1]
		for item in path_items[1:]:
			link = os.path.join(link, item)
			name = item.capitalize()
			if item == path_items[-1]:
				name = entry[0]['title']
			name = name.replace(' ', '&nbsp')
			path.append((name, link))
		template = template.replace(crumbs_id, make_breadcrumbs(path))


	template = template.replace("{entry}", entry[1])
	return template

def format_and_build(entries, root = '/'):
	"""Each entry is one web page of content, with metadata and content separated"""
	formatted = {}
	config_filename = 'config.json'
	build_dir = json.load(open(config_filename))['build_folder']
	src_dir = json.load(open(config_filename))['source_folder']
	for entry in entries:
		formatted = __format_entry(entry, root)
		filename = entry[0]['filename']
		new_filename = filename.replace(src_dir, build_dir).replace('.md', '/index.html')
		output_file = Path(new_filename)
		output_file.parent.mkdir(exist_ok=True, parents=True)
		output_file.write_text(formatted)

		# with open(new_filename, 'w+') as f:
		# 	f.write(entry[1])


def main():
	entries = []
	root = json.load(open('config.json'))['build_folder'] # for atom-live-server
	root = '/'
	files = get_files('src')
	for file in files:
		entries.append(process_entry(file))
	format_and_build(entries, root)
	make_home_page(entries, root)
	generate_rss(entries)
	copy_css()
	return 0

if __name__ == '__main__':
	main()
