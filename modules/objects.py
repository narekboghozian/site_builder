# from modules.process_entry import process_entry
from modules.process_entry import process_entry
from modules.make_breadcrumbs import make_breadcrumbs
from pathlib import Path
import json
import os


class entry:
	def __init__ (self, file, root = '/'):
		self.file = file
		self.meta, self.html = process_entry(file)
		self.root = root

	def __format_entry(self):
		"""Input here is a json"""

		if self.root[0] != '/':
			self.root = '/' + self.root

		template_type = 'article' # default
		if 'template' in self.meta:
			template_type = self.meta['template']

		template_paths = {
			'article': 'templates/article_template.html',
			'home': 'templates/home_template.html'
		}
		template_path = template_paths[template_type]
		template = open(template_path).read()

		# Metadata
		for item in self.meta: # process metadata
			if "{%s}"%item in template:
				template = template.replace("{%s}"%item, self.meta[item])

		# Breadcrumbs
		crumbs_id = "{breadcrumbs}"
		if crumbs_id in template:
			path_items = self.meta['filename'].replace('.md','').split('/')
			# path = [('Home', '/')]
			# path = [('Home', '/narekb/')] # for debugging when using atom-live-server
			path = [('Home', self.root)]
			link = path[0][1]
			for item in path_items[1:]:
				link = os.path.join(link, item)
				name = item.capitalize()
				if item == path_items[-1]:
					name = self.meta['title']
				name = name.replace(' ', '&nbsp')
				path.append((name, link))
			template = template.replace(crumbs_id, make_breadcrumbs(path))


		formatted = template.replace("{entry}", self.html)
		return formatted

	def format_and_build(self):
		"""Each entry is one web page of content, with metadata and content separated"""
		formatted = {}
		config_filename = 'config.json'
		build_dir = json.load(open(config_filename))['build_folder']
		src_dir = json.load(open(config_filename))['source_folder']
		self.formatted = self.__format_entry()
		self.old_filename = self.meta['filename']
		self.new_filename = self.old_filename.replace(src_dir, build_dir).replace('.md', '.html')

	def write(self):
		output_file = Path(self.new_filename)
		output_file.parent.mkdir(exist_ok=True, parents=True)
		output_file.write_text(self.formatted)
