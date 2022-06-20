import markdown


def make_breadcrumbs(nav_list):
	"""Generate breadcrumbs from list input. Return HTML"""
	# Format for input list:
	# [ ( Name, Link ), ...]

	ul_template_html = """
	<ul class="breadcrumb">
	{crumbs}
	</ul>
	"""

	li_template_html = '\t<li><a href="{link}">{name}</a></li>\n'
	li_template_html_bold = '\t<li><a href="{link}"><b>{name}</b></a></li>\n'

	li_list = ""

	for item in nav_list:
		if item == nav_list[-1] and False:
			li_list+=li_template_html_bold.format(name=item[0], link=item[1])
		else:
			li_list+=li_template_html.format(name=item[0], link=item[1])
	ret = ul_template_html.format(crumbs=li_list)
	return ret









	#
