import signpostlib

def getLatestTechNewsLink():
	return signpostlib.makeAPIQuery(titles='Tech/News/Latest', action='query', prop='links', project='meta')[0]['title']

def getLatestTechNewsBody():
	data = signpostlib.getPageWikicode(getLatestTechNewsLink(), language='meta', project='wikimedia')
	data = data[data.index('<section begin="tech-newsletter-content"/>'):data.index('<section end="tech-newsletter-content"/>')]
	return data

def removeDelimitedString(string, front_delimiter, back_delimiter):
	return string[:string.index(front_delimiter)] + string[string.index(back_delimiter, string.index(front_delimiter)) + len(back_delimiter):]

def main():
	# Fetch the report body.
	report_content = getLatestTechNewsBody()

	# Remove meta-only strings from the content.
	report_content = report_content.replace('<translate>', '')
	report_content = report_content.replace('</translate>', '')
	while '<tvar' in report_content:
		report_content = removeDelimitedString(report_content, '<tvar', '>')
	while '</>' in report_content:
		report_content = removeDelimitedString(report_content, '</', '>')
	while '<!--T' in report_content:
		report_content = removeDelimitedString(report_content, '<!--', '-->')

	# Fix the resultant formatting errors.
	report_content = report_content.replace('* \n', '* ')
	report_content = report_content.replace('*\n', '* ')
	report_content = report_content.replace('\'\'\'\n\n', '\'\'\'')
	report_content = report_content.replace('\'\'\'\n', '\'\'\'')
	report_content = report_content.replace('\'\'\'*', '\'\'\'\n*')

	# Create and format the content string.
	content = '''{{Signpost draft}}<noinclude>{{Wikipedia:Signpost/Template:Signpost-header|||}}</noinclude>

	{{Wikipedia:Signpost/Template:Signpost-article-start|{{{1|Tech news in brief}}}|By [[meta:Tech/Ambassadors|Wikimedia tech ambassadors]]|'''
	content += signpostlib.getNextSignpostPublicationDate().strftime('%Y-%m-%d') + '''}}'''
	content += '\n{{Wikipedia:Wikipedia Signpost/Templates/Tech news}}'
	content += report_content
	content += '''\n<noinclude>{{Wikipedia:Signpost/Template:Signpost-article-comments-end||'''
	content += signpostlib.getPreviousSignpostPublicationDate().strftime('%Y-%m-%d')
	content += '|'
	content += '''}}</noinclude>'''

	return content

if __name__ == '__main__':
	content = main()
	# Publish.
	post_point = signpostlib.getNextSignpostPublicationString() + '/Technology report'
	signpostlib.saveContentToPage(content, post_point, 'Importing Tech News content via the [https://github.com/ResidentMario/TN_Importer TN_Importer] script.')
	print("Done.")
