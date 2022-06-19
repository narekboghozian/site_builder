import markdown

def __open_markdown_file(filename):
	'''Open and validate input file'''

	file = open(filename).read()
	assert type(file) == str, 'Input is not text'
	assert '\n#' in file, 'Title not in input'
	assert '\n/date' in file, 'Date not specified'
	assert file.count('\n# ') == 1, 'Only one Title allowed'

	return file

def __split_input(x):
	'''Split metadata from markdown, assuming input is validated'''
	loc = x.find('\n#')

	return x[:loc], x[(loc + 1):]

def __process_metadata(x):
	'''Read metadata and process parameters. Returns dict.'''

	required_inputs = [
		'date',
		'title'
		]
	optional_inputs = [
		'toc',
		'description'
	]

	metadata = {}

	lines = x.split('\n')
	for line in lines:
		if len(line) >3 and line[0] == '/':
			uncomment = line.split('//')[0].split()
			cmd = uncomment[0][1:]
			assert (cmd in required_inputs or cmd in optional_inputs), "Invalid input"
			metadata[cmd] = " ".join(uncomment[1:])

	return metadata

def __process_content(x):
	return markdown.markdown(x)

def process_entry(filename):
	raw = __open_markdown_file(filename)
	raw_meta, content = __split_input(raw) #
	meta = __process_metadata(raw_meta) # Metadata JSON
	conv = __process_content(content) # HTML
	meta['filename'] = filename
	return meta, conv
