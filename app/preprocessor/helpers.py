"""helper functions for preprocessor modules
"""

import re

def json_escape(text):
	return text.replace('"', "'").replace("\n", "</br>")

def split_keepsep(s, sep):
    return reduce(lambda acc, elem: acc[:-1] + [acc[-1] + elem] if elem == sep else acc + [elem], re.split("(%s)" % re.escape(sep), s), [])
