# from modules.process_entry import process_entry
from modules.make_breadcrumbs import make_breadcrumbs
from datetime import datetime as dt
from pathlib import Path
import markdown
import json
import os


class ObjectBase:
	def get_template(self, type, style):
		"""Get or make the template based on params"""

		self.template_types = { # default is the last in each array
			'entry'	: [
				# 'big_thumb',
				'small_thumbnail',
				'minimal',
				'basic'
			],
			'container':[
				'basic'
			],
			'page'	: [
				'home',
				'category',
				'article'
			]
		}
		assert type in self.template_types, "objects > category > __get_template:\nInvalid type."
		if style == False or style=='default':
			style = self.template_types[type][-1]
		assert style in self.template_types[type], "objects > category > __get_template:\nInvalid style"
		template_path = "templates/%s_%s.html"%(type, style)
		template = open(template_path, 'r').read()

		return template

	def fill_template(self, template, params):
		"""Fill out a template"""

		filled = template
		for param in params:
			match = '{%s}'%param
			if match in filled:
				filled = filled.replace(match, params[param])

		return filled


class Entry(ObjectBase):
	def __init__ (self, filename, root = '/'):
		self.filename = filename
		# self.meta, self.html = process_entry(file)
		self.root = root
		self.__process_entry()

	def __open_markdown_file(self):
		'''Open and validate input file'''

		file = open(self.filename).read()
		assert type(file) == str, 'Input is not text'
		assert '\n#' in file, 'Title not in input'
		assert '\n/date' in file, 'Date not specified'
		assert file.count('\n# ') == 1, 'Only one Title allowed'

		return file

	def __split_input(self, raw_md_file):
		'''Split metadata from markdown, assuming input is validated'''

		loc = raw_md_file.find('\n#')
		self.raw_meta = raw_md_file[:loc]
		self.raw_html = raw_md_file[(loc + 1):]

	def __make_link(self):
		"""Generate the relative URL"""

		path_items = self.filename[:-len('.md')].strip('/').split('/')
		path = []
		# This next bit restricts all entries to be in a directory where the last directory name defines type
		link = "/".join(path_items[-2:])
		# for item in path_items[1:]:
		# 	link = os.path.join(link, item)
		# 	name = item.capitalize()
		# 	if item == path_items[-1]:
		# 		if type(entry) == list:
		# 			name = entry[0]['title']
		# 		else:
		# 			name = entry.meta['title']
		# 	name = name.replace(' ', '&nbsp')
		# 	path.append((name, link))

		return link

	def __get_type(self):
		"""Replace invalid spellings of metadata 'type' with valid ones"""

		default_type = 'blog'
		valid_types = [
			"blog",
			"project",
			"project-idea",
			"note"
		]
		raw = default_type
		for vt in valid_types:
			if "%s/"%vt in self.filename.split('/')[0]:
				raw = vt

		return raw

	def __get_category(self):

		category = self.__make_link().strip('/').split('/')[0]

		return category

	def __process_metadata(self):
		'''Read metadata and process parameters. Returns dict.'''

		required_inputs = [
			'date',
			'title',
			'description'
			]
		optional_inputs = [
			'thumbnail',
			'toc',
			'pin',
			'home'
		]
		deprecated_inputs = [
			'link',
			'type'
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
				assert (cmd in required_inputs or cmd in optional_inputs or cmd in deprecated_inputs), "Invalid input"
				if cmd in deprecated_inputs:
					print("Warning: %s is a deprecated command. Found in %s"%(cmd, self.filename))
				metadata[cmd] = " ".join(uncomment[1:])
				if cmd in tf_commands: # set to true if included at all
					metadata[cmd] = True
		for tf_cmd in tf_commands: # If wasnt specified, mark false
			if tf_cmd not in metadata:
				metadata[tf_cmd] = False
		if 'thumbnail' not in metadata:
			metadata['thumbnail'] = '/images/null.jpg'
		metadata['filename'] = self.filename
		if 'link' not in metadata:
			metadata['link'] = self.__make_link()
		metadata['type'] = self.__get_type()
		metadata['category'] = self.__get_category()
		metadata['monthyear'] = dt.strptime(metadata['date'], "%m.%d.%Y").strftime("%b %Y")
		metadata['timestamp'] = dt.strptime(metadata['date'], "%m.%d.%Y").timestamp()
		self.meta = metadata

	def __process_content(self):
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

		self.__split_input(self.__open_markdown_file())
		self.__process_metadata()
		self.__process_content()

	def __format_entry(self):
		"""Input here is a json"""
		#
		# if self.root[0] != '/':
		# 	self.root = '/' + self.root
		# template_type = 'article' # default
		# if 'template' in self.meta:
		# 	template_type = self.meta['template']
		# template_paths = {
		# 	'article': 'templates/article_template.html',
		# 	'home': 'templates/home_template.html'
		# }
		# template_path = template_paths[template_type]
		# template = open(template_path).read()
		# # Metadata
		# for item in self.meta: # process metadata
		# 	if "{%s}"%item in template:
		# 		template = template.replace("{%s}"%item, self.meta[item])
		#
		template = self.get_template('page', 'article')
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
			print(path)
			template = template.replace(crumbs_id, make_breadcrumbs(path))
		formatted = template.replace("{entry}", self.html)

		return formatted

	def __write_to_file(self, file_content, file_path):
		output_file = Path(file_path)
		output_file.parent.mkdir(exist_ok=True, parents=True)
		output_file.write_text(file_content)

	def build(self, build_dir='build/'):
		"""Each entry is one web page of content, with metadata and content separated"""

		formatted = {}
		config_filename = 'config.json'
		formatted = self.__format_entry()
		file_name = self.meta['link']
		if '.html' != file_name[-len('.html'):]:
			file_name += '.html'
		self.__write_to_file(formatted, file_name)

	def equals(self, cmp):
		"""Test if self object has same values as cmp object"""

		if self.file  == cmp.file and self.meta  == cmp.meta and self.html == cmp.html and self.root == cmp.root:
		 	return True
		return False

	def inside(self, arr):
		"""Check if self is in list 'arr' """
		for a in arr:
			if self.equals(a):
				return True
		return False


class Category(ObjectBase):
	def __init__ (self, category, source_dir):

		self.source = source_dir
		self.entry_list = []
		self.categories_headers = {
			"projects"			: 	"Projects",
			"project-ideas"		:	"Project Ideas",
			"blogs"				:	"Blogs",
			"notes"				:	"Notes"
		}
		assert category in self.categories_headers, "Invalid category."
		self.category = category
		self.header = self.categories_headers[category]
		self.template_types = {
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
		}
		self.site_path = "/" + self.__make_link()[len(source_dir):].strip('/')

	def __get_entries(self):

		return self.entry_list

	def __filter_entries(self, entries, pinned = False, home = False):
		"""Returns entries based on inputs as filters, ordered as added"""

		filtered = []
		for ent in entries:
			if ent.meta['pin'] == pinned and ent.meta['home'] == home:
				filtered.append(ent)

		return filtered

	def __sort_entries(self, entries, reverse = True, key = 'date'):
		"""Tool to sort all the added entries into sorted array"""

		sort_options = [
			'date',
			'alphabet',
			'order_added'
		]
		assert key in sort_options, "Invalid key."
		sort_functions = {
			sort_options[0] : lambda ent: ent.meta['timestamp'],
			sort_options[1] : lambda ent: ent.meta['title'],
 			sort_options[2] : lambda ent: entries.index(ent)
		}
		sorted_entries = sorted(entries, key=sort_functions[key])
		return sorted_entries

	def __make_params(self, ent):
		"""Build the list of parameters to put in to template"""

		params = {
			'date'			: 	ent.meta['monthyear'],
			'title'			: 	ent.meta['title'],
			'description'	: 	ent.meta['description'],
			'link'			: 	ent.meta['link'],
			'thumbnail'		: 	ent.meta['thumbnail'],
			'timestamp'		: 	ent.meta['timestamp']
			}

		return params

	def __build_posts(self, entries, pinmark = 'default', style = 'default'):
		"""Build the post list but not the actual container or page"""

		posts = []
		template = self.get_template('entry', style)
		for ent in entries:
			temp = ""
			params = self.__make_params(ent)
			filled = self.fill_template(template, params)

		return posts

	def __make_link(self, output=False):
		"""Make the link for the section"""

		links = {
			"project": "projects",
			"projects": "projects",
			"note": "notes",
			"notes": "notes",
			"project-idea": "project-ideas",
			"project-ideas": "project-ideas",
			"blogs": "blog",
			"blog": "blog"
		}
		link = links[self.category]
		if not output:
			link = os.path.join(self.source, link)

		return link

	def __build_container(self, posts, add_header = False, style = False):
		"""Buid the category container for the posts"""

		template = self.get_template('container', style)
		if add_header:
			header = self.header
		else:
			header = ''
		params = {
			"link"		: self.__make_link(),
			"header"	: header,
			"content"	: "\n".join(posts)
		}
		container = self.fill_template(template, params)

		return container

	def __make_section(self, add_header = True, pinned = False, pinmark = 'default', home = False, style = 'default'):
		"""Make the html for the posted sections on home or category page."""

		entries		= self.__get_entries()
		filtered	= self.__filter_entries(entries, pinned = pinned, home = home)
		sorted 		= self.__sort_entries(filtered)
		posts 		= self.__build_posts(entries, pinmark=pinmark, style=style)
		container	= self.__build_container(posts, add_header=add_header, style=style)

		return container

	def __write_to_file(self, file_content, file_path):

		print("category: writing to %s"%file_path)
		output_file = Path(file_path)
		output_file.parent.mkdir(exist_ok=True, parents=True)
		output_file.write_text(file_content)

	def build_category_page(self):

		breadcrumbs = []
		for item in self.site_path.strip('/').split('/'):
			breadcrumbs.append((self.categories_headers[item], item))
		params = {
			'title': self.header,
			'entry': self.__make_section(add_header=False),
			'breadcrumbs': make_breadcrumbs(breadcrumbs),
			'section': self.header
			}
		category_page_template = self.get_template('page', 'category')
		page = self.fill_template(category_page_template, params)

		self.__write_to_file(page, self.__make_link(output=True))

	def build_category_section(self, home = True, header = True, pinned = False):

		section = self.__make_section(home=home, add_header=header, pinned=pinned)

		return section

	def __add_entry(self, entry_input):
		"""Add a single entry to the entry list"""

		assert type(entry_input) == Entry,	"objects > category > __add_entry:\nIncorrect class type for entry"
		if entry_input.inside(self.entry_list):
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
			assert False, 	"objects > category > append:\nInvalid type for entry: %s"%(type(entry_input))
		return True


class Website(ObjectBase):
	def __init__(self, source = "src/", build = "build/", clear = False):
		self.source, self.build = (source, build)
		self.root = source
		self.categories = []
		self.__get_entries()
		if clear:
			self.__clear()
		self.__build_articles()
		self.__build_categories()
		self.__build_home()
		# self.__build_css()
		# self.__build_rss()
		# self.__build_htaccess()

	def __get_files(self, fullpath = None): # reads all entries
		'''Returns all non-hidden .md files in target directory'''
		if fullpath == None:
			fullpath = self.source
		files = []
		dir = os.listdir(fullpath)
		for d in dir:
			test_path = os.path.join(fullpath, d)
			entry = False
			if d[0] != '.':
				if os.path.isfile(test_path) and \
					test_path.endswith('.md'):
					files.append(test_path)
				elif os.path.isdir(test_path):
					entries = self.__get_files(test_path)
					for entry in entries:
						files.append(entry)

		return files

	def __get_entries(self): # reads all entries

		files = self.__get_files()
		entries = []
		for file in files:
			entries.append(Entry(file))

		self.entries = entries

	def __clear_build(self): # empty the build folder if exists
		# needs input validation so as not to delete anything important
		pass

	def __build_articles(self): # build all the pages

		for entry in self.entries:
			entry.build()

	def __build_categories(self): # build the category pages

		categories = {}
		for entry in self.entries:
			if entry.meta['type'] not in categories:
				categories[entry.meta['category']] = []
			categories[entry.meta['category']].append(entry)
		cat_objs = {}
		for category in categories:
			cat_objs[category] = Category(category, self.source)
			cat_objs[category].append(categories[category])
			cat_objs[category].build_category_page()

	# def __get_template(self, type, style):
	# 	"""Get or make the template based on params"""
	#
	# 	self.template_types = {
	# 		'entry'	: [
	# 			# 'big_thumb',
	# 			'small_thumbnail',
	# 			'minimal',
	# 			'basic'
	# 		],
	# 		'container':[
	# 			'basic'
	# 		],
	# 		'page'	: [
	# 			'article',
	# 			'home',
	# 			'category'
	# 		]
	# 	}
	# 	if style == False:
	# 		style = 'basic'
	#
	# 	assert type in self.template_types, "\nobjects > website > __get_template:\nInvalid type."
	# 	assert style in self.template_types[type], "\nobjects > website > __get_template:\nInvalid style"
	# 	template_path = "templates/%s_%s.html"%(type, style)
	# 	template = open(template_path, 'r').read()
	#
	# 	return template

	# def __fill_template(self, template, params):
	# 	"""Fill out a template"""
	#
	# 	filled = template
	# 	for param in params:
	# 		match = '{%s}'%param
	# 		if match in filled:
	# 			filled = filled.replace(match, params[param])
	# 	return filled

	def __write_to_file(self, file_content, file_path):

		print("website: writing to %s"%file_path)
		output_file = Path(file_path)
		output_file.parent.mkdir(exist_ok=True, parents=True)
		output_file.write_text(file_content)

	def __build_home(self): # build the home page

		categories = {}
		for entry in self.entries:
			if entry.meta['type'] not in categories:
				categories[entry.meta['category']] = []
			categories[entry.meta['category']].append(entry)
		cat_objs = {}
		cat_sections = {}
		home_template = self.get_template('page', 'home')
		for category in categories:
			cat_objs[category] = Category(category, self.build)
			cat_objs[category].append(categories[category])
			cat_sections[category] = cat_objs[category].build_category_section()
		params = {
			"entry": "\n".join(cat_sections)
		}
		home_filled = self.fill_template(home_template, params)

		self.__write_to_file(home_filled, 'index.html')

	def __build_rss(self): # build the rss
		pass

	def __build_htaccess(self): # build the htaccess
		pass











#
