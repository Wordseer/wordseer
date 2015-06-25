"""helper functions for preprocessor modules
"""

def json_escape(text):
	return text.replace('"', "'").replace("\n", "</br>")