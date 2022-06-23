import xml.etree.ElementTree as ET
from datetime import datetime as dt
import os
import json

# Allowable values in rss xml are:
# author
# category
# comments
# description
# enclosure
# guid
# link
# pubDate
# source
# title
#
# Although only title, description, link are required

def __process_json_item(raw_key, raw_val):

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

	swap = {
		"date": "pubDate",
		"desc": "description"
	}

	if raw_key in swap:
		new_key = swap[raw_key]
	else:
		new_key = raw_key

	if (new_key in required_rss_items or new_key in optional_rss_items):
		validity = True
	else:
		validity = False

	if new_key == 'pubDate':
		time_val = dt.strptime(raw_val, "%m.%d.%Y")
		new_val = time_val.strftime("%a, %d %b %Y %H:%M:%S %z")
	else:
		new_val = raw_val

	return validity, new_key, new_val


def generate_rss(item_list):
	'''Convert list of dicts to RSS XML'''

	output_dir = json.load(open('config.json'))['build_folder']
	filename = "rss.xml"
	# filename = "feed/rss.xml"
	filename = "rss"
	main_title = "Nareks Blog"
	main_link = "http://www.narekb.com"
	main_description = "Nareks Blog"

	rss = ET.Element("rss", version="2.0")
	channel = ET.SubElement(rss, "channel")

	ET.SubElement(channel, "title").text = main_title
	ET.SubElement(channel, "link").text = main_link
	ET.SubElement(channel, "description").text = main_description

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
