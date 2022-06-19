from modules.process_entry import process_entry
from modules.generate_rss import generate_rss
from pathlib import Path
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

def __format_entry(entry):
	template_path = 'templates/article_template.html'
	template = open(template_path).read()
	for item in entry[0]: # process metadata
		if "{%s}"%item in template:
			template = template.replace("{%s}"%item, entry[0][item])

	template = template.replace("{entry}", entry[1])
	return template

def format_and_build(entries):
	formatted = {}
	for entry in entries:
		formatted = __format_entry(entry)
		filename = entry[0]['filename']
		new_filename = filename.replace('src', 'build').replace('.md', '.html')
		output_file = Path(new_filename)
		output_file.parent.mkdir(exist_ok=True, parents=True)
		output_file.write_text(formatted)

		# with open(new_filename, 'w+') as f:
		# 	f.write(entry[1])


def main():
	entries = []
	files = get_files('src')
	for file in files:
		entries.append(process_entry(file))
	format_and_build(entries)
	generate_rss(entries)
	return 0

if __name__ == '__main__':
	main()
