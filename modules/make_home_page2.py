from pathlib import Path
import markdown
from datetime import datetime as dt
from modules.make_breadcrumbs import make_breadcrumbs
import os
import json


def __make_link(entry, root):

	if root[0] != '/':
		root = '/' + root

	if type(entry) == list:
		path_items = entry[0]['filename'].replace('.md','').split('/')
	else:
		path_items = entry.meta['filename'].replace('.md','').split('/')
	# path = [('Home', '/')]
	# path = [('Home', '/narekb/')] # for debugging when using atom-live-server
	# path = [('Home', root)]
	# link = path[0][1]
	path = []
	link = root
	for item in path_items[1:]:
		link = os.path.join(link, item)
		name = item.capitalize()
		if item == path_items[-1]:
			if type(entry) == list:
				name = entry[0]['title']
			else:
				name = entry.meta['title']
		name = name.replace(' ', '&nbsp')
		path.append((name, link))
	return link


def __fix_entry_type(entry_type):
	swaps = {
		"projects": "project",
		"cheat": "guide",
		"cheat_sheet": "guide",
		"cheat-sheet": "guide",
		"cheat sheet": "guide",
		"blogs": "blog",
		"idea" : "project_idea",
		"project idea": "project_idea",
		"project-idea": "project_idea",
		"project_idea": "project_idea"
	}
	if entry_type.lower() in swaps:
		entry_type = swaps[entry_type.lower()]
	return entry_type

def __date_to_monthyear(raw_val):
	time_val = dt.strptime(raw_val, "%m.%d.%Y")
	new_val = time_val.strftime("%b %Y")
	return new_val

def __date_to_timestamp(raw_val):
	time_val = dt.strptime(raw_val, "%m.%d.%Y")
	new_val = time_val.timestamp()
	return new_val

def __getEntryTimestamp(entry):
	return entry['timestamp']

def __prep_sections(entries, root = '/'):

	sorted_entries = {}

	for etype in entries:
		for entry in entries[etype]:
			desc = entry.meta['description']
			title = entry.meta['title']
			date = entry.meta['date']
			link = __make_link(entry, root)
			thumbnail = entry.meta['thumbnail']
			new_item = {
				'date': __date_to_monthyear(date),
				'title': title,
				'desc': desc,
				'link': link,
				'thumbnail': thumbnail,
				'timestamp': __date_to_timestamp(date)
				}
			if etype not in sorted_entries:
				sorted_entries[etype] = []
			sorted_entries[etype].append(new_item)

	# actually sort them
	for etype in sorted_entries:
		sorted_entries[etype] = sorted_entries[etype].sort(key=__getEntryTimestamp)

	return sorted_entries


def __proj_proc(sorted_entries_etype):
	finished_entries = ""
	entry_template_path = 'templates/proj_entry_template.html'
	entry_template = open(entry_template_path).read()
	for entry in sorted_entries_etype:
		finished_entries += entry_template.format(
			title = entry['title'],
			date = entry['date'],
			description = entry['desc'],
			link = entry['link'],
			thumbnail = entry['thumbnail']
		)
	return finished_entries

def __guide_proc(sorted_entries_etype):
	finished_entries = ""
	entry_template_path = 'templates/guide_entry_template.html'
	entry_template = open(entry_template_path).read()
	for entry in sorted_entries_etype:
		finished_entries += entry_template.format(
			title = entry['title'],
			description = entry['desc'],
			link = entry['link']
		)
	return finished_entries

def __basic_proc(sorted_entries_etype):
	finished_entries = ""
	entry_template_path = 'templates/basic_entry_template.html'
	entry_template = open(entry_template_path).read()
	for entry in sorted_entries_etype:
		finished_entries += entry_template.format(
			title = entry['title'],
			date = entry['date'],
			description = entry['desc'],
			link = entry['link']
		)
	return finished_entries

def __make_sections(entries, root = '/'):

	sorted_entries = __prep_sections(entries, root)
	# entry_template_path = 'templates/post_entry_template.html'
	# entry_template = open(entry_template_path).read()
	listing_template = '<h2><a href="{link}" class="post_section">{typename}</a></h2><div class="post_section">{content}</div>'

	type_names = {
		"project": "Projects",
		"guide": "Guides",
		"project_idea": "Project Ideas",
		"blog": "Blog"
	}
	etype_links = {
		"project": "projects",
		"guide": "guides",
		"project_idea": "project-ideas",
		"blog": "blog"
	}
	etype_processors = {
		"project": __proj_proc,
		"guide": __guide_proc,
		"project_idea": __basic_proc,
		"blog": __basic_proc
	}

	finished_entries = {}
	finished_listings = {}

	# Make section pages... probably shouldn't go here
	for etype in sorted_entries:
		finished_page_entries = ""
		entry_template_paths = {
			"basic"	: "templates/basic_entry_template.html",
			"guide" : "templates/guide_entry_template.html",
			"proj" 	: "templates/proj_entry_template.html"
		}
		if etype not in entry_template_paths:
			entry_template_path = entry_template_paths['basic']
		else:
			entry_template_path = entry_template_paths[etype]
		entry_template = open(entry_template_path).read()
		section_page_template_path = 'templates/section_page_template.html'
		section_page_template = open(section_page_template_path).read()
		for entry in sorted_entries[etype]:
			finished_page_entries += entry_template.format(
				title = entry['title'],
				date = entry['date'],
				description = entry['desc'],
				link = entry['link']
			)


		crumbs_id = "{breadcrumbs}"
		if crumbs_id in section_page_template:
			path_items = ['Home', etype_links[etype]]
			# path = [('Home', '/')]
			# path = [('Home', '/narekb/')] # for debugging when using atom-live-server
			path = [('Home', root)]
			link = path[0][1]
			for item in path_items[1:]:
				link = os.path.join(link, item)
				name = item.capitalize()
				if item == path_items[-1]:
					name = type_names[etype]
				name = name.replace(' ', '&nbsp')
				path.append((name, link))
			section_page_template = section_page_template.replace(crumbs_id, make_breadcrumbs(path))
		finished_page = section_page_template.format(
			title = type_names[etype],
			section = type_names[etype],
			entry = finished_page_entries
			# link = __make_link([{'filename':"src/", 'title': etype_links[etype]}], root)
		)



		page_root = json.load(open('config.json'))['build_folder']
		page_filename = os.path.join(page_root, etype_links[etype], 'index.html')
		page_output_file = Path(page_filename)
		page_output_file.parent.mkdir(exist_ok=True, parents=True)
		page_output_file.write_text(finished_page)



	# for etype in type_names:
	# 	if etype in sorted_entries:
	# 		finished_entries[etype] = ""
	for etype in sorted_entries:

		finished_entries[etype] = etype_processors[etype](sorted_entries[etype])
		# for entry in sorted_entries[etype]:
		# 	finished_entries[etype] += entry_template.format(
		# 		title = entry['title'],
		# 		date = entry['date'],
		# 		description = entry['desc'],
		# 		link = entry['link'],
		# 		thumbnail = entry['thumbnail']
		# 	)
		entry={'title':'hi'}
		finished_listings[etype] = listing_template.format(
			typename = type_names[etype],
			content = finished_entries[etype],
			link = __make_link([{'filename':"src/%s"%etype_links[etype], 'title': entry['title']}], root)
		)

	return finished_listings



def make_home_page(entries, root):


	template_path = 'templates/home_template.html'
	template = open(template_path).read()

	sorted_entries = {
		"project": [],
		"guide": [],
		"project_idea": [],
		"blog" : []
	}

	for entry in entries:
		assert 'type' in entry.meta, "Entry does not have type"
		entry_type = __fix_entry_type(entry.meta['type'])
		sorted_entries[entry_type].append(entry)

	sections = __make_sections(sorted_entries, root)
	combined_sections = ""
	for section in sections:
		combined_sections += sections[section]

	template = template.format(entry = combined_sections)


	root = json.load(open('config.json'))['build_folder']
	filename = os.path.join(root, 'index.html')
	output_file = Path(filename)
	output_file.parent.mkdir(exist_ok=True, parents=True)
	output_file.write_text(template)







#
