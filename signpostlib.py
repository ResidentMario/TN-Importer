# This library provides a loose collection of methods useful for tasks associated with the Wikipedia Signpost.

# Prerequisites to using this script:
# You must have the `pywikibot` package installed and set up.
# Furthermore it is recommended that you edit `user_config.py` directly to contain as many global definitions as possible, ae.:
# + usernames['wikipedia']['*'] = u'Resident Mario'
# + usernames['commons']['*'] = u'Resident Mario'
# + ...

# This script uses the following notable packages and capacities.
# pywikibot:			Handles all writing to the projects.
# requests:				Used to handles API query methods in this file.

# LIMITATION: Currently the API query methods only accept `action=query&prop=(*)` requests. Need to code in `action=query&list=(*)` requests.

import pywikibot
# import sys
import requests
import json
# import time
import datetime

# SEEKER METHOD: Finds the next Signpost issue date.
# RETURNS: A datetime object corresponding to the date of the next issue's publication.
def getNextSignpostPublicationDate():
	data = getPageHTML('User:Resident Mario/pubdate')
	data = data[data.index('BOF') + 4:data.index('EOF') - 1]
	return datetime.datetime.strptime(data, '%Y-%m-%d')

# SEEKER METHOD: Returns the formatted string at which the next Signpost issue will be published.
def getNextSignpostPublicationString():
	return 'Wikipedia:Wikipedia Signpost/' + getNextSignpostPublicationDate().strftime('%Y-%m-%d')

# SEEKER METHOD: Finds the previous Signpost issue date.
# RETURNS: A time object corresponding to the date of the previous issue's publication.
def getPreviousSignpostPublicationDate():
	return getNextSignpostPublicationDate() - datetime.timedelta(days=7)

# SEEKER METHOD: Returns the formatted string at which the previous Signpost issue was published.
def getPreviousSignpostPublicationString():
	return 'Wikipedia:Wikipedia Signpost/' + getPreviousSignpostPublicationDate().strftime('%Y-%m-%d')

# SEEKER METHOD: Sniffs and returns the contents of the Signpost issue for a certain date as a list.
def getSignpostContents():
	pass

# EXECUTION METHOD: Returns the HTML contents of a wiki page.
# PARAMATERS:
# (req) page:			Page to return the contents of.
# (opt) language:		Language of the project, en is the default.
# (opt) project:		Project, wikipedia is the default.
def getPageHTML(page, language='en', project='wikipedia'):
	return requests.get('https://' + language + '.' + project + '.org/wiki/' + page).text

# EXECUTION METHOD: Returns the wikicode contents of a wiki page.
# PARAMETERS:
# (req) page:			Page to return the contents of.
# (opt) language:		Language of the project, en is the default.
# (opt) project:		Project, wikipedia is the default.
def getPageWikicode(page, language='en', project='wikipedia'):
	return requests.get('https://' + language + '.' + project + '.org/w/index.php?&action=raw&title=' + page).text

# EXECUTION METHOD: A simple RESTBase API query method which converts HTML to Wikitext.
# PARAMETERS:
# (req) html:			HTML string to parse into wikicode.
def htmlToWikitext(html):
	return requests.post('https://rest.wikimedia.org:443/en.wikipedia.org/v1/transform/html/to/wikitext', data={'html': html}).text

# EXECUTION METHOD: A simple API query method which does not implement continuation parameters.
# PARAMETERS:
# (req) target: 		Target page of the project.
# (req) list_or_prop:	Either `prop` or `list`, depending on what kind of query is being made. eg. the `prop` in `[...]&prop=categories`
# (req) list_or_prop_param:	The body of the `prop` or `list` command. eg. the `categories` in `[...]&prop=categories`
# (opt) language:		Language of the project, en is the default.
# (opt) project:		Project, wikipedia is the default.
# (kwr) _params:		Additional parameters passed to the query.
# NOTE: This method does not implement continuation. It implements only `query` commands.
def makeSimpleAPIQuery(target, list_or_prop, list_or_prop_param, language='en', project='wikipedia', **_params):
	returnable = requests.get('https://' + language + '.' + project + '.org/w/api.php?&action=query&format=json&formatversion=2&continue=&' + list_or_prop + '=' + list_or_prop_param + '&titles=' + target, params=_params)
	returnable = json.loads(returnable.text)
	return returnable['query']['pages'][0][list_or_prop_param]

# EXECUTION WRAPPER METHOD: An API query method which implements continuation parameters. Just a wrapper for `__makeAPIQuery()`.
# PARAMETERS:
# (req) target: 		Target page of the project.
# (req) prop:			API query `prop` parameter.
# (opt) language:		Language of the project, en is the default.
# (opt) project:		Project, wikipedia is the default.
# (kwr) _params:		Additional parameters passed to the query.
# DO NOT USE: Though it works I want to generalize this function before I use it.
def makeAPIQuery(target, prop, language='en', project='wikipedia', **_params):
	return __makeAPIQuery(target, prop, _params, language, project)

# WRAPPED METHOD: Called by makeAPIQuery. Basically only here to convert away from a keyword argument, which can't be dealt with recursively.
# Implements continuation.
# See the above for parameterization.
# DO NOT USE: Though it works I want to generalize this function before I use it.
def __makeAPIQuery(target, prop, continue_information, language='en', project='wikipedia'):
	concat_string = ''
	for item in continue_information:
		concat_string += '&' + item + '=' + continue_information[item]
	returnable = requests.get('https://' + language + '.' + project + '.org/w/api.php?&action=query&format=json&formatversion=2&continue=&prop=' + prop + '&titles=' + target + concat_string)
	returnable = json.loads(returnable.text)
	if 'continue' not in returnable:
		return returnable['query']['pages'][0][prop]
	else:
		_continue_information = continue_information.copy()
		_continue_information.update(returnable['continue'])
		return returnable['query']['pages'][0][prop] + __makeAPIQuery(target, prop, _continue_information, language='en', project='wikipedia')

# EXECUTION METHOD: Writes the contents of a string to a page on a project.
# PARAMETERS:
# (req) content: 		Content to be written.
# (req) target:			Target page on the project.
# (req) editsummary:	Edit summary.
# (opt) language:		Language of the project, en is the default.
# (opt) project:		Project, wikipedia is the default.
# NOTE: pywikibot handles all writing. See also the note at the top of this file on setting up `user_config.py`.
def saveContentToPage(content, target, editsummary, language='en', project='wikipedia'):
	site = pywikibot.Site(language, project)
	page = pywikibot.Page(site, target)
	text = page.text
	page.text = content
	page.save(editsummary)

# print(makeSimpleAPIQuery('Thomas Edison', 'prop', 'categories', test='test'))
# print(makeAPIQuery('Thomas Edison', 'categories'))
# saveContentToPage(content='Test', target='User:Resident Mario/sandbox', editsummary='Test')
# print(htmlToWikitext('<b>Test</b>'))
# print(getPageData('Wikipedia:Wikipedia Signpost/Issue'))
# print(getNextSignpostPublicationDate())
# print(getPreviousSignpostPublicationDate())
# print(getNextSignpostPublicationString())
# print(getPreviousSignpostPublicationString())
# print(getPageWikicode('Paris'))
# print("Done.")
