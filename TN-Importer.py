import signpostlib

def getLatestTechNewsLink():
	# return signpostlib.makeSimpleAPIQuery('Tech/News/Latest', 'prop', 'links', language='meta', project='wikimedia')[0]['title']
	return signpostlib.makeAPIQuery(titles='Tech/News/Latest', action='query', prop='links', project='meta')[0]['title']

def getLatestTechNewsBody():
	data = signpostlib.getPageWikicode(getLatestTechNewsLink(), language='meta', project='wikimedia')
	data = data[data.index('<section begin="tech-newsletter-content"/>'):data.index('<section end="tech-newsletter-content"/>')]
	return data

def removeDelimitedString(string, front_delimiter, back_delimiter):
	return string[:string.index(front_delimiter)] + string[string.index(back_delimiter, string.index(front_delimiter)) + len(back_delimiter):]

# Create and format the content string.
content = '''{{Signpost draft}}<noinclude>{{Wikipedia:Signpost/Template:Signpost-header|||}}</noinclude>

{{Wikipedia:Signpost/Template:Signpost-article-start|{{{1|(Your article's descriptive subtitle here)}}}|By [[meta:Tech/Ambassadors|Wikimedia tech ambassadors]]|'''
content += signpostlib.getNextSignpostPublicationDate().strftime('%Y-%m-%d') + '''}}'''
content += '\n{{Wikipedia:Wikipedia Signpost/Templates/Tech news}}'
content += getLatestTechNewsBody()
content += '''\n<noinclude>{{Wikipedia:Signpost/Template:Signpost-article-comments-end||2015-06-24|2015-07-01}}</noinclude>'''

# Remove meta-only strings from the content.
content = content.replace('<translate>', '')
content = content.replace('</translate>', '')
while '<tvar' in content:
	content = removeDelimitedString(content, '<tvar', '>')
while '</>' in content:
	content = removeDelimitedString(content, '</', '>')
while '<!--T' in content:
	content = removeDelimitedString(content, '<!--', '-->')

# Fix the resultant formatting errors.
content = content.replace('* \n', '* ')
content = content.replace('*\n', '* ')
content = content.replace('\'\'\'\n\n', '\'\'\'')
content = content.replace('\'\'\'\n', '\'\'\'')
content = content.replace('\'\'\'*', '\'\'\'\n*')

post_point = signpostlib.getNextSignpostPublicationString() + '/Technology report'
signpostlib.saveContentToPage(content, post_point, 'Importing Tech News content via the TN-Importer script.')
print("Done.")
