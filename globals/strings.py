# -*- coding: utf-8 -*-

## \package globals.strings
#
#  Module for manipulating strings & string lists

# MIT licensing
# See: docs/LICENSE.txt


import sys


## Checks if a text string is empty
#
#  \param text
#		The string to be checked
def TextIsEmpty(text):
	return not text.strip(u' \t\n\r')


## Removes empty lines from a string or string list
#
#  \param text
#	\b \e String or \b \e list to be checked
#  \return
#	\b \e String or \b \e tuple with empty lines removed
def RemoveEmptyLines(text):
	fmt_string = False

	if IsString(text):
		fmt_string = True
		text = text.split(u'\n')

	elif isinstance(text, tuple):
		text = list(text)

	# Iterate in reverse to avoid skipping indexes
	for INDEX in reversed(range(len(text))):
		if TextIsEmpty(text[INDEX]):
			text.pop(INDEX)

	if fmt_string:
		return u'\n'.join(text)

	return tuple(text)


## Checks if object is a string instance
#
#  Compatibility function for legacy Python versions
def IsString(text):
	if sys.version_info[0] <= 2:
		return isinstance(text, (unicode, str))

	return isinstance(text, str)


## Converts an object to a string instance
#
#  Compatibility function for legacy Python versions
#  \param item
#	Instance to be converted to string
#  \return
#	Compatible string
def ToString(item):
	if sys.version_info[0] <= 2:
		item = unicode(item)

	else:
		item = str(item)

	return item


if sys.version_info[0] <= 2:
	GS = unicode

else:
	GS = str


## Tests if a string can be converted to int or float
#
#  \param string
#	\b \e String to be tested
def StringIsNumeric(string):
	try:
		float(string)
		return True

	except ValueError:
		return False


## Tests if a string is formatted for versioning
def StringIsVersioned(string):
	for P in string.split(u'.'):
		if not P.isnumeric():
			return False

	return True


## Retrieves a class instance's module name string
#
#  \param item
#	Object instance
#  \param className
#	If <b><i>True</i></b>, returns class object's name instead of module name
#  \param full
#	If <b><i>True</i></b>, return entire module/class string without parsing
def GetModuleString(item, className=False, full=False):
	module = ToString(item.__class__)

	# Strip extra characters
	if u'\'' in module:
		module = module[module.index(u'\'')+1:].split(u'\'')[0]

	if full:
		return module

	module = module.split(u'.')

	if className:
		return module[-1]

	return u'.'.join(module[:-1])


## Retrieves an instance's method name in the format of "Class.Method"
#
#  \param function
#	Function object
#  \param includeModule
#	Prepend module name to string for class methods
def GetFunctionString(function, includeModule=False):
	function = ToString(function).strip(u'<>')

	if function.startswith(u'bound method '):
		function = function.split(u'<')

		module = function[1].split(u';')[0]
		function = function[0].lstrip(u'bound method ').split(u' ')[0]

		if includeModule:
			class_name = function.split(u'.')[0]

			if u'.{}'.format(class_name) in module:
				module = module.replace(u'.{}'.format(class_name), u'')

			function = u'{}.{}'.format(module, function)

	else:
		function = function.split(u' ')[1]

	return function
