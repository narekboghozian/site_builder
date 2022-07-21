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
	for i, item in enumerate(nav_list):
		if i == len(nav_list) - 1:
			li_list+=li_template_html.format(name=item[0], link=(item[1] + '.html'))
		else:
			li_list+=li_template_html.format(name=item[0], link=item[1])
	ret = ul_template_html.format(crumbs=li_list)
	return ret





	#
