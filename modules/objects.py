# from modules.process_entry import process_entry
from modules.make_breadcrumbs import make_breadcrumbs
from datetime import datetime as dt
import xml.etree.ElementTree as ET
from modules.scan_notes import ScanNotes
from pathlib import Path
import markdown
import json
import os
import re




class ObjectBase:
	def get_template(self, type, style):
		"""Get or make the template based on params"""

		self.template_types = { # default is the last in each array
			'entry'	: [
				# 'big_thumb',
				'toc',
				'toc_wrapper',
				'toc_prefix',
				'date_subtitle',
				'small_thumbnail',
				'minimal',
				'basic'
			],
			'container':[
				'toc',
				'basic'
			],
			'page'	: [
				'home',
				'category',
				'contact',
				'article'
			],
			'element' : [
				'show_more_button'
			]
		}
		# assert type in self.template_types, "objects > ObjectBase > __get_template:\nInvalid type."
		if style == False or style=='default':
			style = self.template_types[type][-1]
		# assert style in self.template_types[type], "objects > ObjectBase > __get_template:\nInvalid style"
		template_path = "templates/%s_%s.html"%(type, style)
		template = open(template_path, 'r').read()

		return template

	def fill_template(self, template, params):
		"""Fill out a template"""

		filled = template
		for param in params:
			match = '{%s}'%str(param)
			if match in filled:
				filled = filled.replace(match, str(params[param]))

		return filled

	def write_to_file(self, file_content, file_path, build_dir="narekb/"):

		file_path = build_dir + file_path
		output_file = Path(file_path)
		output_file.parent.mkdir(exist_ok=True, parents=True)
		output_file.write_text(file_content)


class TOC_Node(ObjectBase):
	def __init__(self, raw_entry='', depth=0, root=False, repeated=False):
		self.raw = raw_entry
		self.depth = depth
		self.__parent = None
		self.__children = []
		self.__child_number = None
		self.__root = root
		if root:
			self.raw = "__ROOT__"
		self.repeated = repeated

	def __build_header_id(self):
		'''Create the html id for this TOC item, used for links'''

		remove = '''!()[]{};:'"\,<>./?@#$%^&*~'''
		newline_id = self.raw.lower()
		for i in remove:
			newline_id = newline_id.replace(i, '')
		newline_id = newline_id.replace(' ', '-')
		while('--' in newline_id):
			newline_id = newline_id.replace('--', '-')
		if self.repeated:
			newline_id += "_" + str(self.repeated)
		return newline_id

	def header_id(self):
		return self.__build_header_id()

	def __build_prefix(self):
		numbers = []
		node = self
		for i in range(self.depth):
			numbers.append(node.child_number() + 1)
			node = node.get_parent()
		numbers = numbers[::-1]
		return numbers

	def __build_header(self):
		'''Return the header with a tiered number in front'''

		numbers = self.__build_prefix()
		prefix = ".".join([str(number) for number in numbers])
		toc_prefix_template = self.get_template('entry', 'toc_prefix')
		prefix_params =  {
			'prefix': prefix,
			'header': self.raw
		}
		return self.fill_template(toc_prefix_template,prefix_params)

	def root(self):
		return self.__root

	def add_child(self, new_child):
		assert type(new_child) == type(self), 'TOC_Node.add_child(): Wrong type'
		self.__children.append(new_child)
		return len(self.__children) - 1

	def get_children(self):
		return self.__children

	def child_number(self):
		return self.__child_number

	def set_parent(self, parent):
		assert type(parent) == type(self), 'TOC_Node.set_parent(): Wrong type'
		self.__parent = parent
		# Set this node as the child of the new parent
		self.__child_number = parent.add_child(self)

	def get_parent(self):
		return self.__parent

	def build(self):
		children = "\n".join([child.build() for child in self.__children])
		if self.__root:
			root_template = self.get_template('container', 'toc')
			node_params = {'content': children}
			return self.fill_template(root_template, node_params)
		elif len(children) > 0:
			wrap_template = self.get_template('entry', 'toc_wrapper')
			node_params = {
				'section-label': self.__build_header(),
				'section-id': self.__build_header_id(),
				'content': children,
			}
			return self.fill_template(wrap_template, node_params)
		else:
			node_template = self.get_template('entry', 'toc')
			node_params = {
				'section-label': self.__build_header(),
				'section-id': self.__build_header_id()
			}
			return self.fill_template(node_template, node_params)


class Citation(ObjectBase):
	def __init__(self, label, name, link):
		self.__label = label.strip()
		if type(name) == str:
			self.__name = name.strip()
		elif type(name) == list:
			self.__name = " ".join(name).strip()
		else:
			self.__name = False
		if type(link) == str:
			self.__link = link.strip()
		else:
			self.__link = False
		self.__place = None # Place within the order that cites are mentioned

	def match(self):
		return "\cite{" + self.__label + "}"

	def make_ref(self):
		# out = "[%s - %s](%s)"%(self.__name, self.__link, self.__link)
		template = self.get_template('entry', 'bib_basic')
		if self.__link and self.__name:
			content = "%s: <br><br>&nbsp&nbsp&nbsp%s"%(self.__name, self.__link)
		elif self.__link:
			content = self.__link
		else:
			content = self.__name
		id = 'bib-item-%s'%str(self.__place)
		link = self.get_id()
		if self.__link:
			link = self.__link
		params = {
			'link': link,
			'content': content,
			'id': id
		}
		out = self.fill_template(template, params)
		return out

	def set_place(self, place, force=False):
		if force or self.__place == None:
			self.__place = place

	def link(self):
		return self.__link

	def get_id(self):
		return '#bib-item-%s'%str(self.__place + 1)


class Entry(ObjectBase):
	def __init__ (self, filename, root = '/', build_dir = "build/"):
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

	def __make_link(self, html=False):
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
		if html:
			link+='.html'

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
			'home',
			'bib'
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
		for rawline in lines:
			line = rawline.rstrip(' ')
			if len(line) >3 and line[0] == '/' and line[0:2] != '//':
				uncomment = line.split(' //')[0].split()
				cmd = uncomment[0][1:]
				assert (cmd in required_inputs or cmd in optional_inputs or cmd in deprecated_inputs), "Invalid input"
				# if cmd in deprecated_inputs:
					# print("Warning: %s is a deprecated command. Found in %s"%(cmd, self.filename))
				if cmd == 'bib':
					# label = uncomment[1]
					# name = uncomment[2:-1]
					# url = uncomment[-1]
					items = {
						'name': False,
						'link': False,
						'label': False
					}
					item_keys = ['label', 'name', 'link']
					for val, item in enumerate(list(re.finditer('{.*?}', " ".join(uncomment)))):
						items[item_keys[val]] = item.group()[1:-1]
					if 'bib' not in metadata:
						metadata['bib']  = {}
					metadata['bib'][items['label']] = Citation(
						items['label'],
						items['name'],
						items['link']
					)
				else:
					metadata[cmd] = " ".join(uncomment[1:])
				if cmd in tf_commands: # set to true if included at all
					metadata[cmd] = True
		if 'toc' not in metadata:
			metadata['toc'] = False
		for tf_cmd in tf_commands: # If wasnt specified, mark false
			if tf_cmd not in metadata:
				metadata[tf_cmd] = False
		if 'bib' not in metadata:
			metadata['bib']  = False
		if 'thumbnail' not in metadata:
			metadata['thumbnail'] = '/images/null.jpg'
		metadata['filename'] = self.filename
		if 'link' not in metadata or True:
			metadata['link'] = self.__make_link(html=True)
		metadata['type'] = self.__get_type()
		metadata['category'] = self.__get_category()
		metadata['monthyear'] = dt.strptime(metadata['date'], "%m.%d.%Y").strftime("&nbsp&nbsp&nbsp%b&nbsp%Y")
		metadata['timestamp'] = int(dt.strptime(metadata['date'], "%m.%d.%Y").timestamp())
		metadata['pubDate'] = dt.strptime(metadata['date'], "%m.%d.%Y").strftime("%a, %d %b %Y %H:%M:%S %z")
		metadata['date_subtitle'] = dt.strptime(metadata['date'], "%m.%d.%Y").strftime("%b %d, %Y")
		self.meta = metadata

	def __process_content(self):
		# raw_html = self.raw_html.replace('/','/<wbr>')
		self.__build_cites()
		raw_html = self.raw_html
		html = markdown.markdown(raw_html,
			extensions=[
				'tables',
				'attr_list',
				'toc',
				'markdown_checklist.extension'
				])
		html = html.replace('<a href=', '<a target="_blank" href=')
		self.html = html

	def __process_entry(self):
		"""Split into metedata and html content"""

		self.__split_input(self.__open_markdown_file())
		self.__process_metadata()
		self.__process_content()

	def __build_toc(self, depth):
		'''
		Use nodes/linked lists to generate the heirarchy as a tree
		Keep the list in an array that has the same sorting order
		If a previous node has...
			- lower depth: set parent of this node to prev node
			- same depth: set parent of this node to parent of prev node
			- higher depth: go up the linked lists until you find a node of same depth, then, add that to whatever the parent of that is
 		Then, with the complete tree, use a member function to build each of those headers into html using a template, leaving a formatting space for any child content
		Recursively flatten it using a member function
		'''
		depth = int(depth)
		assert depth >= 1 and depth < 6, 'Invalid depth for Entry.__build_toc()'
		depth = int(depth) + 2
		toc_template = self.get_template('container', 'toc')
		entries_template = self.get_template('entry', 'toc')
		sub_tree_template = self.get_template('entry', 'toc_wrapper')
		entries = []

		# Generate the primary array of bare headers
		header_pattern = '#'
		for line in self.raw_html.split('\n'):
			if any(header_pattern * dep + ' ' in line[0:depth] \
				for dep in range(2, depth)):
				raw_entry = " ".join(line.split(' ')[1:])
				entry_depth = line.split(' ')[0].count(header_pattern) - 1
				entries.append((raw_entry, entry_depth))

		if len(entries) == 0:
			self.toc = ''
			return
		if self.meta['bib']:
			entries.append(('References', 1))
			# Replace those with a node object that stores the header
		nodes = []
		node_counter = {}
		for entry in entries:
			new_node = TOC_Node(entry[0], entry[1])
			if not new_node.header_id() in node_counter:
				node_counter[new_node.header_id()] = 0
			else:
				node_counter[new_node.header_id()] += 1
				new_node.repeated = node_counter[new_node.header_id()]
			nodes.append(new_node)
			# print(new_node.header_id())

		# Process through the array to link each member to their parents
		root_node = TOC_Node(root=True)
		nodes[0].set_parent(root_node)
		for i, node in enumerate(nodes[1:]):
			prev_node = nodes[i]
			if node.depth > prev_node.depth:
				parent = prev_node
			elif node.depth == prev_node.depth:
				parent = prev_node.get_parent()
			else:
				# print('')
				diff = prev_node.depth - node.depth + 1
				parent = prev_node
				for j in range(diff):
					parent = parent.get_parent()
			node.set_parent(parent)

		# Recursively flatten everything
		self.toc = root_node.build()

	def __build_date(self):

		date_template = self.get_template('entry', 'date_subtitle')
		date_params = {
			'date': self.meta['date_subtitle']
		}
		date = self.fill_template(date_template, date_params)
		self.date_subtitle = date

	def __get_match_locations(self, match, data):
		'''Find indicies of 'match' withing 'data'.'''

		assert len(match) < len(data), 'Entry.__get_match_locations() > Match string must be smaller than input data'
		locs = []
		for i, letter in enumerate(data[:-len(match)]):
			if match == data[i:i+len(match)]:
				locs.append(i)
		return locs

	def __build_bib(self):
		'''Build the bibliography at the end'''

		if not self.meta['bib']:
			self.bib = ''
		else:
			bib = self.meta['bib']
			bib_html  = ''
			for entry in bib:
				bib_html += bib[entry].make_ref()
			full_bib_template = self.get_template('container','bib')
			bib_params = {
				'content': bib_html
			}
			self.bib = self.fill_template(full_bib_template, bib_params)

	def __build_cites(self):
		'''Process the /cite tags like how latex does it'''

		# Go through all patterns to find all types of cites
		pattern = '\\\cite{.+?}'
		match_dict = {}
		cites = list(re.finditer(pattern, self.raw_html))
		counter = 0
		for cite in cites:
			label = re.search('{.+?}', cite.group()).group()[1:-1]
			if label not in match_dict:
				match_dict[label] = counter
				self.meta['bib'][label].set_place(counter)
				pattern = '\\\cite{' + label + '}'
				link = ''
				# repl = '[['+str(counter+1)+']](%s)'%self.meta['bib'][label].get_id()
				repl = '<a  href="%s">[%s]</a>'%(
					self.meta['bib'][label].get_id(),
					str(counter+1)
					)
				self.raw_html = repl.join(re.split(pattern, self.raw_html))
				counter += 1
		self.__build_bib()

	def __format_entry(self):
		"""Input here is a json"""

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
			template = template.replace(crumbs_id, make_breadcrumbs(path))
		if self.meta['toc']:
			self.__build_toc(self.meta['toc'])
			self.html = self.html.replace('</h1>', '</h1>\n%s'%self.toc)
		if self.meta['bib'] is not False:
			self.html += self.bib
			# print('</article>' in self.html)
			# print(self.html)
		self.__build_date()
		self.html = self.html.replace('</h1>', '</h1>\n%s'%self.date_subtitle)
		params = {
			'entry': self.html,
			'title': self.meta['title']
		}
		formatted = self.fill_template(template, params)
		# formatted = template.replace("{entry}", self.html)

		return formatted

	def build(self, build_dir='build/'):
		"""Each entry is one web page of content, with metadata and content separated"""

		formatted = {}
		config_filename = 'config.json'
		formatted = self.__format_entry()
		file_name = self.meta['link']
		if '.html' != file_name[-len('.html'):]:
			file_name += '.html'
		self.write_to_file(formatted, file_name)

	def equals(self, cmp):
		"""Test if self object has same values as cmp object"""

		if self.filename  == cmp.filename and self.meta  == cmp.meta and self.html == cmp.html and self.root == cmp.root:
		 	return True
		return False

	def inside(self, arr):
		"""Check if self is in list 'arr' """
		for a in arr:
			if self.equals(a):
				return True
		return False


class Category(ObjectBase):
	def __init__ (self, category, source_dir, build_dir = "build/"):

		self.build_dir = build_dir
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
		self.has_pins = False
		self.has_homes = False
		self.num_pins = 0
		self.num_homes = 0
		self.count = 0

	def __get_entries(self):

		return self.entry_list

	def __filter_entries(self, entries, pinned = False, home = False):
		"""Returns entries based on inputs as filters, ordered as added"""

		filtered = []
		for ent in entries:
			add = True
			if pinned and not ent.meta['pin']:
				add = False
			if home and not ent.meta['home']:
				add = False
			if add:
				filtered.append(ent)
		return filtered

	def __sort_entries(self, entries, reverse = False, key = 'date'):
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
		if not reverse:
			sorted_entries.reverse()
		return sorted_entries

	def __make_params(self, ent):
		"""Build the list of parameters to put in to template"""

		params = {
			'date'			: 	ent.meta['monthyear'],
			'title'			: 	ent.meta['title'],
			'description'	: 	ent.meta['description'],
			'link'			: 	"/"+ent.meta['link'].lstrip('/'),
			'thumbnail'		: 	ent.meta['thumbnail'],
			'timestamp'		: 	ent.meta['timestamp']
			}

		return params

	def __build_posts(self, entries, pinmark = 'default', style = 'default'):
		"""Build the post list but not the actual container or page"""

		styles = {
			'projects' : 'small_thumbnail',
			'notes' : 'minimal',
			'blog' : 'basic'
		}
		posts = []
		template = self.get_template('entry', styles[self.category])
		for ent in entries:
			temp = ""
			params = self.__make_params(ent)
			filled = self.fill_template(template, params)
			posts.append(filled)

		return posts

	def __make_link(self, output=False):
		"""Make the link for the section"""

		self.links = {
			"project": "projects",
			"projects": "projects",
			"note": "notes",
			"notes": "notes",
			"project-idea": "project-ideas",
			"project-ideas": "project-ideas",
			"blogs": "blog",
			"blog": "blog"
		}
		link = self.links[self.category]
		if not output:
			link = os.path.join(self.source, link)

		return link

	def __build_container(self, posts, add_header = False, style = False, show_more = False):
		"""Buid the category container for the posts"""

		template = self.get_template('container', style)
		if add_header:
			head = '<h2><a href="{link}" class="post_section">{header}</a></h2>'
			header = head.replace('{link}', "/"+self.__make_link(output=True))
			header = header.replace('{header}', self.header)
		else:
			header = ''
		more = ""
		if show_more and self.count > self.num_homes:
			more = self.get_template('element', 'show_more_button')
			mpar = {
				"header" : self.header,
				"remaining_count" : (self.count - self.num_homes),
				"total_count" : self.count,
				"category_link" : "/"+self.__make_link(output=True)
			}
			more = self.fill_template(more, mpar)
		params = {
			"link"		: "/"+self.__make_link(output=True),
			"header"	: header,
			"content"	: "\n".join(posts),
			"show_more"		: more
		}
		container = self.fill_template(template, params)

		return container

	def __make_section(self, add_header = True, pinned = False, pinmark = 'default', home = False, style = 'default', show_more=False):
		"""Make the html for the posted sections on home or category page."""

		entries		= self.__get_entries()
		filtered	= self.__filter_entries(entries, pinned = pinned, home = home)
		sorted 		= self.__sort_entries(filtered)
		posts 		= self.__build_posts(sorted, pinmark=pinmark, style=style)
		container	= self.__build_container(posts, add_header=add_header, style=style, show_more=show_more)

		return container

	def build_category_page(self):

		breadcrumbs = [('Home', '/')]
		site_path = self.site_path.strip('/').split('/')
		for i, item in enumerate(site_path):
			breadcrumbs.append((self.categories_headers[item], "/"+"/".join(site_path[:i]) + self.category))
		params = {
			'title': self.header,
			'entry': self.__make_section(add_header=False),
			'breadcrumbs': make_breadcrumbs(breadcrumbs),
			# 'section': self.header
			'section': self.header
			}
		category_page_template = self.get_template('page', 'category')
		page = self.fill_template(category_page_template, params)

		self.write_to_file(page, self.__make_link(output=True)+'/index.html')

	def build_category_section(self, home = False, header = True, pinned = False):

		# Pinned keeps at the top
		# Home includes it in the home page
		section = self.__make_section(home=self.has_homes, add_header=header, pinned=pinned, show_more=self.has_homes)

		return section

	def __add_entry(self, entry_input):
		"""Add a single entry to the entry list"""

		assert type(entry_input) == Entry,	"objects > category > __add_entry:\nIncorrect class type for entry"
		if entry_input.inside(self.entry_list):
			print("objects > category > __add_entry: Blocked duplicate entry.")
		else:
			if entry_input.meta['pin']:
				self.has_pins = True
				self.num_pins += 1
			if entry_input.meta['home']:
				self.has_homes = True
				self.num_homes += 1
			self.entry_list.append(entry_input)
			self.count = len(self.entry_list)
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
	def __init__(self, source = "src/", build = "build/", clear = False, apnotes = False):
		self.source, self.build_dir = (source, build)
		self.root = source
		self.categories = []
		self.__get_entries()
		if clear:
			self.__clear()
		self.__build_articles()
		self.__build_categories()
		self.__build_home()
		self.__build_css()
		self.__build_assets()
		self.__build_contact()
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
		# if apnotes is not False:
		# 	dirs = ['']
		# 	folders = ['Reports']
		# 	notes = ScanNotes(folders)


		for file in files:
			entries.append(Entry(file, build_dir=self.build_dir))

		self.entries = entries

	def __clear_build(self): # empty the build folder if exists
		# needs input validation so as not to delete anything important
		pass

	def __build_articles(self): # build all the pages

		for entry in self.entries:
			entry.build(build_dir = self.build_dir)

	def __build_categories(self): # build the category pages

		categories = {}
		for entry in self.entries:
			if entry.meta['category'] not in categories:
				categories[entry.meta['category']] = []
			categories[entry.meta['category']].append(entry)
		cat_objs = {}
		for category in categories:
			cat_objs[category] = Category(category, self.source)
			cat_objs[category].append(categories[category])
			cat_objs[category].build_category_page()

	def __build_home(self): # build the home page

		categories = {}
		for entry in self.entries:
			if entry.meta['category'] not in categories:
				categories[entry.meta['category']] = []
			categories[entry.meta['category']].append(entry)
		cat_objs = {}
		cat_sections = {}
		home_template = self.get_template('page', 'home')
		for category in categories:
			cat_objs[category] = Category(category, self.source)
			cat_objs[category].append(categories[category])
			cat_sections[category] = cat_objs[category].build_category_section()
		cat_section = ""
		for item in cat_sections.keys():
			cat_section+=cat_sections[item]
		params = {
			"entry": "".join(cat_section)
		}
		home_filled = self.fill_template(home_template, params)

		self.write_to_file(home_filled, 'index.html')

	def __build_rss(self): # build the rss
		pass

	def __build_htaccess(self): # build the htaccess
		pass

	def __build_css(self):

		css_paths = ['css/main.css', 'css/contact.css']
		for item in css_paths:
			css = open(item, 'r').read()
			self.write_to_file(css, item)

	def __build_assets(self):

		images_path = 'images/'
		new_path = self.build_dir + images_path
		os.system('cp -r %s %s'%(images_path, new_path))

		js_path = 'js/'
		new_path = self.build_dir + js_path
		os.system('cp -r %s %s'%(js_path, new_path))

	def __build_contact(self):

		# template = self.get_template('page', 'contact')
		# params = {
		# }
		# filled = self.fill_template(template, params)
		# filename = "contact.html"
		# self.write_to_file(filled, filename)

		path = 'contact/'
		new_path = self.build_dir + path
		os.system('cp -r %s %s'%(path, new_path))

	def __build_rss(self):

		required_rss_items = [
			'link',
			'title',
			'description'
		]
		optional_rss_items = [
			"author",
			"category",
			"comments",
			"enclosure",
			"guid",
			"pubDate",
			"source"
		]
		filename = "rss.xml"
		main_title = "Nareks Blog"
		main_link = "http://www.narekb.com"
		main_description = "Nareks Blog"
		rss = ET.Element("rss", version="2.0")
		channel = ET.SubElement(rss, "channel")
		ET.SubElement(channel, "title").text = main_title
		ET.SubElement(channel, "link").text = main_link
		ET.SubElement(channel, "description").text = main_description
		item_list = []
		for ent in self.entries:
			item_list.append({
				"link" : ent.meta['link'],
				"title" : ent.meta['title'],
				"description" : ent.meta['description'],
				"pubDate" : ent.meta['pubDate']
			})
		for item_json in item_list:
			item = ET.SubElement(channel, 'item')
			for attr in item_json[0]:
				validity, attr_key, attr_val = __process_json_item(attr, item_json[0][attr])
				if validity:
					ET.SubElement(item, attr_key).text = attr_val
		tree = ET.ElementTree(rss)
		rss_path = os.path.join(output_dir, filename)
		tree.write(rss_path, encoding='utf8', xml_declaration=True)







#
