import json

try:
	import importlib.resources as pkg_resources
except ImportError:
	import importlib_resources as pkg_resources

# Load aliases from item-aliases.json
#with open('osrs/item-aliases.json', 'r') as f:
#	aliases = json.loads(f.read())['aliases']
aliases = json.loads(pkg_resources.read_text('osrs','item-aliases.json'))['aliases']

def alias(term):
	if term.lower() in aliases:
		return aliases[term.lower()]
	elif term.lower()+'s' in aliases:
		return aliases[term.lower()+'s']
	else:
		return term