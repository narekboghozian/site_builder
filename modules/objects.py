# from modules.process_entry import process_entry
from modules.make_breadcrumbs import make_breadcrumbs
from pathlib import Path
import markdown
import json
import os


class Entry:
	def __init__ (self, filename, root = '/'):
		self.filename = filename
		# self.meta, self.html = process_entry(file)
		self.root = root
		self.__process_entry()

	def __open_markdown_file(self, filename):
		'''Open and validate input file'''

		file = open(self.filename).read()
		assert type(file) == str, 'Input is not text'
		assert '\n#' in file, 'Title not in input'
		assert '\n/date' in file, 'Date not specified'
		assert file.count('\n# ') == 1, 'Only one Title allowed'
		self.raw_md_file = file
		return True

	def __split_input(self):
		'''Split metadata from markdown, assuming input is validated'''

		loc = self.raw_md_file.find('\n#')
		self.raw_meta = raw_md_file[:loc]
		self.raw_html = raw_md_file[(loc + 1):]

	def __process_metadata(self):
		'''Read metadata and process parameters. Returns dict.'''

		required_inputs = [
			'date',
			'title',
			'link',
			'description',
			'type',
			'thumbnail'
			]
		optional_inputs = [
			'toc',
			'pin',
			'home'
		]
		tf_commands = [
			'pin',
			'home'
		]
		metadata = {}
		lines = self.raw_meta.split('\n')
		for line in lines:
			if len(line) >3 and line[0] == '/' and line[0:2] != '//':
				uncomment = line.split(' //')[0].split()
				cmd = uncomment[0][1:]
				assert (cmd in required_inputs or cmd in optional_inputs), "Invalid input"
				metadata[cmd] = " ".join(uncomment[1:])
				if cmd in tf_commands: # set to true if included at all
					metadata[cmd] = True
		for tf_cmd in tf_commands: # If wasnt specified, mark false
			if tf_cmd not in metadata:
				metadata[tf_cmd] = False
		metadata['filename'] = self.filename
		self.meta = metadata

	def __process_content():
		html = markdown.markdown(self.raw_html,
			extensions=[
				'tables',
				'attr_list',
				'toc',
				'markdown_checklist.extension'
				])
		self.html = html.replace('<a href=', '<a target="_blank" href=')

	def __process_entry(self):
		"""Split into metedata and html content"""

		self.__open_markdown_file()
		self.__split_input()
		self.__process_metadata()
		self.__process_content()

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

	def equals(self, cmp):
		"""Test if self object has same values as cmp object"""
		if  self.file 	== cmp.file
		and self.meta 	== cmp.meta
		and self.html	== cmp.html
		and self.root	== cmp.root:
		 	return True
		return False

	def in(self, arr):
		"""Check if self is in list 'arr' """
		for a in arr:
			if self.equals(a):
				return True
		return False


class Category:
	def __init__ (self, header = None):
		self.header = header
		self.entry_list = []
		self.template_types = [
			'entry'	: {
				# 'big_thumb',
				'small_thumbnail',
				'minimal',
				'basic'
			},
			'container':{
				'basic'
			},
			'page'	: {
				'article'
			}
		]

	def __get_entries(self):
		return self.entry_list

	def __filter_entries(self, entries, pinned = False, home = False):
		"""Returns entries based on inputs as filters, ordered as added"""

		filtered = []
		for ent in entries:
			if ent.meta['pin'] == pinned
			and ent.meta['home'] == home:
				filtered.append(ent)
		return filtered

	def __sort_entries(self, entries, reverse = True, key = 'date'):
		"""Tool to sort all the added entries into sorted array"""

		sorted = []
		sort_function = {
			'date'			: lambda ent:
			'alphabet'		: lambda ent:
			'order_added'	: lambda ent:
		}
		return sorted

	def __get_template(self, type, style):
		"""Get or make the template based on params"""

		assert type in self.template_types, "objects > category > __get_template:"+
											"Invalid type."
		assert style in self.template_types[type], "objects > category > __get_template:"+
											  "Invalid style"
		template_path = "templates/%s_%s.html"%(type, style)
		template = open(template_path, 'r').read()
		return template

	def __fill_template(self, template, params):
		"""Fill out a template"""

		# filled = template.format(params)
		filled = template
		for param in params:
			match = '{%s}'%param
			if match in filled:
				filled = filled.replace(match, params[param])
		return filled

	def __build_posts(self, entries, pinmark = 'default', style = 'default'):
		"""Build the post list but not the actual container or page"""

		posts = []
		post_template = self.__get_template(pinmark, style)
		for ent in entries:

		return posts

	def __build_container(self, posts, header = False, style = False):
		"""Buid the category container for the posts"""

		pass

	def make_section(self, header = True, pinned = False, pinmark = 'default', home = False, style = 'default'):
		"""Make the html for the posted sections on home or category page."""

		entries		= self.__get_entries()
		filtered	= self.__filter_entries(entries,
											pinned = pinned,
											home = home)
		sorted 		= self.__sort_entries(filtered)

		return True

	def __add_entry(self, entry_input):
		"""Add a single entry to the entry list"""
		assert type(entry_input) == entry,	"objects > category > __add_entry:"+
											"Incorrect type for entry"
		if entry_input.in(self.entry_list):
			print("objects > category > __add_entry: Blocked duplicate entry.")
		else:
			self.entry_list.append(entry_input)
		return True

	def append(self, entry_input):
		"""Add a post/entry to the array used to store them. Also sort them"""
		if type(entry_input) == list:
			for inp in entry_input:
				self.__add_entry(inp)
		elif type(entry_input) == entry:
			self.__add_entry(entry_input)
		else:
			assert False, 	"objects > category > append:"+
							"Invalid type for entry: %s"%(type(entry_input))
		return True







#
