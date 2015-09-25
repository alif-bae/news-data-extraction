#!/usr/bin/env python
""" 
Takes a list of URLS or a URL from the Boston Chronicle
and appends the data to a JSON file
"""

import json
import urllib2
import httplib
import datetime
from bs4 import BeautifulSoup

__author__ = "Ali Fawad"

class HoustonChronCrawler():
	def __init__(self, Url):
		self.url = Url


	def validateURL(self):
		if "www.chron.com/" in self.url:
			return True
		else:
			return False


	def getHtmlBuffer(self):
		try:
			htmlBuffer = urllib2.urlopen(self.url).read()
			return htmlBuffer
		except urllib2.HTTPError, err:
			print "HTTP Error: " + str(err)
			return -1
		except httplib.IncompleteRead, err:
			print "Incomplete Read Error: " + str(err)
			return -1


	def extractContentFromHtml(self, htmlBuffer):
		if htmlBuffer == -1:
			return -1
		else:		
			articleInfo = {}
			pageSoup = BeautifulSoup(htmlBuffer)
			articleInfo['Link'] = self.url
			articleInfo['Author'] = self.authorFilter(pageSoup)
			articleInfo['Title'] = self.titleFilter(pageSoup)
			articleInfo['Content'] = self.contentFilter(pageSoup)
			articleInfo['Date'] = self.dateFilter(pageSoup)
			return articleInfo


	def contentFilter(self, pageSoup):
		contentSoup = BeautifulSoup(str(pageSoup.find_all(
			'div', {'class': 'article-body'})))

		contentFilter = (BeautifulSoup(str(
			contentSoup.find_all('p'))).get_text()).encode('ascii',errors='ignore')

		filter1 = contentFilter.replace("., ", ". , ") # Add Space after new paragraph
		filter2 = filter1.replace("\n", '')
		filter3 = filter2.replace('[, , ', '')
		filter4 = filter3.encode('string-escape').replace("\\'", '')
		filter5 = filter4.replace('[[', '[')
		filter6 = filter5.replace("\t", '')

		if '___' in filter6: #if true, get content till start of footer
			stringEnd = filter6.find("___")
			return filter6[:stringEnd]
		else:
			return filter6

	def titleFilter(self, pageSoup):
		title = BeautifulSoup(str(pageSoup.find_all(
			'h1', {'class': 'headline entry-title'}))).get_text().encode(
			'ascii',errors='ignore')
		title = title.replace("\n", "")
		title = title.replace("      ", "")
		return title


	#TODO: Some author tags have extra info, cater for that case.
	def authorFilter(self, pageSoup):
		author = BeautifulSoup(str(pageSoup.find_all(
			'p', {'class': 'byline'}))).get_text().encode('ascii', errors='ignore')

		author = author.replace("\n", '')

		if author == '[]':
			if "editorials" in self.url:
				author = "NULL"
				return author
			else: 
				author == "NULL"
				return author
		else:
			return author


	def dateFilter(self, pageSoup):
		dateFilter = pageSoup.find_all('h5', {"title":True})
		for date in dateFilter:
			dateLineString = date['title'][:10]
			dateLineFormated = str(datetime.datetime.strptime(dateLineString, "%Y-%m-%d").date()).replace('-','')
			return dateLineFormated


	def dumpToJsonFile(self, content, filename, filemode):
		with open(filename, filemode) as f:
			f.write(json.dumps(content)+'\n')


def main():
	articleCounter = 0
	with open("houston-chron-articleLinks.txt") as f:
		for link in f:
			print (">> " + link)
			crawlerObj = HoustonChronCrawler(link)
			htmlBuffer = crawlerObj.getHtmlBuffer()
			articleData = crawlerObj.extractContentFromHtml(htmlBuffer)
			crawlerObj.dumpToJsonFile(articleData,'houstonChron-data-all-v3.json', 'a+')
			articleCounter += 1
			print articleData	
main()
