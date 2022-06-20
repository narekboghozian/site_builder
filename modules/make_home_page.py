from pathlib import Path
import markdown
import os


def __make_link(entry, root):

	if root[0] != '/':
		root = '/' + root

	path_items = entry[0]['filename'].replace('.md','').split('/')
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
			name = entry[0]['title']
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


def __prep_sections(entries, root = '/'):

	sorted_entries = {}

	for etype in entries:
		for entry in entries[etype]:
			desc = entry[0]['description']
			title = entry[0]['title']
			date = entry[0]['date']
			link = __make_link(entry, root)
			new_item = {
				'date': date,
				'title': title,
				'desc': desc,
				'link': link
				}
			if etype not in sorted_entries:
				sorted_entries[etype] = []
			sorted_entries[etype].append(new_item)

	return sorted_entries


def __make_sections(entries, root = '/'):

	sorted_entries = __prep_sections(entries, root)
	entry_template_path = 'templates/post_entry_template.html'
	entry_template = open(entry_template_path).read()
	listing_template = '<h2><a href="{link}" class="post_section">{typename}</a></h2><div class="post_section">{content}</div>'

	type_names = {
		"project": "Projects",
		"guide": "Cheat Sheets",
		"project_idea": "Project Ideas",
		"blog": "Blog"
	}
	etype_links = {
		"project": "projects",
		"guide": "guides",
		"project_idea": "project-ideas",
		"blog": "blog"
	}

	finished_entries = {}
	finished_listings = {}

	for etype in type_names:
		if etype in sorted_entries:
			finished_entries[etype] = ""
	for etype in sorted_entries:
		for entry in sorted_entries[etype]:
			finished_entries[etype] += entry_template.format(
				title = entry['title'],
				date = entry['date'],
				description = entry['desc'],
				link = entry['link']
			)
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
		assert 'type' in entry[0], "Entry does not have type"
		entry_type = __fix_entry_type(entry[0]['type'])
		sorted_entries[entry_type].append(entry)

	sections = __make_sections(sorted_entries, root)
	combined_sections = ""
	for section in sections:
		combined_sections += sections[section]

	template = template.format(entry = combined_sections)

	filename = os.path.join(root, 'index.html')
	output_file = Path(filename)
	output_file.parent.mkdir(exist_ok=True, parents=True)
	output_file.write_text(template)







#
