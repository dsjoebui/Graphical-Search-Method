from bs4 import BeautifulSoup as bs
import requests
import csv



# pubmed only allow 10k articles per search so must make multiple searches in different time periods 

# timeperiods to be appended to the created csv/txt file names
timeperiods = [
			 # '21_01to4',
		     # '20_08to12', '20_04to7', '20_01to03',
			 # '19_08to12', '19_04to7', '19_01to03',
			 # '18_08to12', '18_04to7', '18_01to03',
			 # '17_08to12', '17_04to7', '17_01to03',
			 # '16_08to12', '16_04to7', '16_01to03',
			 # '15_08to12', '15_04to7', '15_01to03',
			 # '14_08to12', '14_04to7', '14_01to03',
			 # '13_08to12', '13_04to7', '13_01to03',
			 # '12_08to12', '12_04to7', '12_01to03',
			 # '11_08to12', '11_04to7', '11_01to03']

# time periods formatted for the URL
urltimes = [
		  # '2021%2F1-2021%2F4',
		  # '2020%2F8-2020%2F12', '2020%2F4-2020%2F7', '2020%2F1-2020%2F3',
		  # '2019%2F8-2019%2F12', '2019%2F4-2019%2F7', '2019%2F1-2019%2F3',
		  # '2018%2F8-2018%2F12', '2018%2F4-2018%2F7', '2018%2F1-2018%2F3', 
		  # '2017%2F8-2017%2F12', '2017%2F4-2017%2F7', '2017%2F1-2017%2F3', 
		  # '2016%2F8-2016%2F12', '2016%2F4-2016%2F7', '2016%2F1-2016%2F3', 
		  # '2015%2F8-2015%2F12', '2015%2F4-2015%2F7', '2015%2F1-2015%2F3',
		  # '2014%2F8-2014%2F12', '2014%2F4-2014%2F7', '2014%2F1-2014%2F3', 
		  # '2013%2F8-2013%2F12', '2013%2F4-2013%2F7', '2013%2F1-2013%2F3', 
		  # '2012%2F8-2012%2F12', '2012%2F4-2012%2F7', '2012%2F1-2012%2F3',
		  # '2011%2F8-2011%2F12', '2011%2F4-2011%2F7', '2011%2F1-2011%2F3']



# Loop through each timeperiod

for timeperiod, urltime in zip(timeperiods, urltimes): 

	# file management
	csv_filename = timeperiod + '_pubmed_scrape.csv'
	txt_filename = timeperiod + '_doilist_pubmed_scraped.txt'

	csv_file = open(csv_filename, 'w', encoding="utf-8", newline='') # create file
	csv_writer = csv.writer(csv_file) # get file writer
	csv_writer.writerow(['journal', 'title', 'date', 'authorslist', 'free', 'publicationtype', 'abstract', 'citednumber', 'doi', 'link']) # create columns

	# must create a txt file for citeddoilist (excel doesn't allow char limits > 32k in a single cell) to be appended to the final dataframe afterwards
	txt_file = open(txt_filename, 'w', encoding="utf-8", newline='')
	txt_file.write('title;;citeddoilist\n') # delimiter=';;'


	
	# Create list of URLS to be web scraped)
	preurl = 'https://pubmed.ncbi.nlm.nih.gov/?term=lung+cancer&filter=pubt.journalarticle&filter=dates.' + urltime + '&size=200&page=' # URL with specific search term (in this case, lung+cancer)
	listofurls = []

	for pagenumber in range(1, 51): # max 50 pages in pubmed per search. Loop through each page #
		listofurls.append(preurl + str(pagenumber))


	# loop through each page/URL

	for url in listofurls:
		try:
			source = requests.get(url).text
			soup = bs(source, 'lxml')
		except:
			break # for if max pages < 50


		# Get href from search list. href is the URL id for each article in pubmed.
		for article in soup.find_all('div', class_='docsum-wrap'):
			try:
				href = article.a['href']
				link = 'https://pubmed.ncbi.nlm.nih.gov' + href # URL link will also be saved in the csv file later
				articlesource = requests.get(link).text
				articlesoup = bs
			except:
				link=''


			# article page
			try:
				articlesource = requests.get(link).text
				articlesoup = bs(articlesource, 'lxml')
			except:
				pass

			# journal
			try:
				journal = articlesoup.find('span', class_="citation-journal").text.strip()
			except:
				journal = ''

			# title
			try:
				title = articlesoup.find('h1', class_='heading-title').text.strip()
			except:
				title = ''

			# date published
			try:
				date = articlesoup.find('span', class_='cit').text.partition(';')[0]

			except:
				date = ''

			# author
			try:
				authors = articlesoup.find('div', class_='authors-list').get_text().replace('\xa0', '').replace('\n', '')
				authors = ''.join([x for x in authors if not x.isdigit()]).split(',')
			except:
				authors = ''

			authorslist = []
			for author in authors:
				authorsplit = author.strip()
				authorslist.append(authorsplit)

			# free article or not
			try: 
				free = articlesoup.find('span', class_='free-label').text
			except:
				try: # two cases of different html code for free articles
					free = articlesoup.find('div', class_='full-text-links').find('span', class_='text').text

				except:
					free = ''


			# publication type (review, None (normal article), meta analysis, etc.)
			try:
				publicationtype = articlesoup.find('div', class_='publication-type').text
			except:
				publicationtype = ''

			# Abstract
			try:
				abstract = articlesoup.find('div', class_='abstract-content selected').p.text.split(':')[1].strip() 
			except: # two cases of different html code
				try:
					abstract = articlesoup.find('div', class_='abstract-content selected').p.text.strip() 
				except:
					abstract = ''

			# citednumber
			try:
				citednumber = articlesoup.find('div', class_='citedby-articles').find('em', class_='amount').text
			except: # for no citations
				citednumber = 0

			# DOI
			try: # Not all articles have DOI
				doi = articlesoup.find('span', class_='citation-doi').text.replace('doi:', '').strip()
			except:
				doi = ''


			# citedDOIlist
			# Will be a see all cited by link if there are more than 5 citers
			# make a try for articles with >5 citers and except for <5 citers

			# FOR >5 citers and up to 8000 citers
			try:
				uid = href.replace('/', '') # convert for URL syntax
				precitedlink = 'https://pubmed.ncbi.nlm.nih.gov/?size=200&linkname=pubmed_pubmed_citedin&from_uid=' + uid + '&page=' # to click the 'see all citations' hyperlink
				listofcitedlinks = []
				# max page numbers (200 citers per page)
				maxpages = int(int(citednumber)/200) + 2 # int conversion rounds down, +2 for range function below and pages start at 1
				for pagenumber in range(1, maxpages): # up to 8000 citers
					listofcitedlinks.append(precitedlink + str(pagenumber))

				citeddoilist = []
				for citedlink in listofcitedlinks:
					citedsource = requests.get(citedlink).text
					citedsoup = bs(citedsource, 'lxml')
					for citedtext in citedsoup.find_all('span', class_='docsum-journal-citation full-journal-citation'):
						citeddoi = citedtext.text.split(':')[-1]
						citeddoilist.append(citeddoi)


			# FOR <5 citers
			except:
				citeddoilist = []
				try:
					for citedtext in articlesoup.find_all('span', class_='docsum-journal-citation full-journal-citation'):
						citeddoi = citedtext.text.split(':')[-1]
						citeddoilist.append(citeddoi)
				except: # for no citers
					citeddoi = ''
					citeddoilist.append(citeddoi)



			# write scraped data into txt and csv file
			try:
				txt_file.write(title + ';;' + str(citeddoilist) + '\n') # delimiter=';;'
				csv_writer.writerow([journal, title, date, authorslist, free, publicationtype, abstract, citednumber, doi, link])
			except:
				pass


# close file after use
	csv_file.close() 
	txt_file.close()

