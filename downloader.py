# -*- coding: utf-8 -*-
import sys
import codecs
import json
import csv

import requests
from bs4 import BeautifulSoup
from bs4 import element
import time
import random
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

main_url = "https://dictionary.cambridge.org/"

def csv_link_reader():
	links = {}
	with open('cambridges_pronounce.csv', newline='') as csvfile:
		spamreader = csv.reader(csvfile, delimiter=';', quotechar='|')
		for row in spamreader:
			word, source = row[0], row[1]		
			soup = BeautifulSoup(source, 'html.parser')
			link = soup.find("source")["src"]
			links[word] = link
			#file = requests.get(main_url+link, headers=headers)
			#with open(word+'.mp3','wb') as output:
			#	output.write(file.content)
	return links

ready_links = csv_link_reader()
print("Downloading...")
for (word, link) in ready_links.items():	
	file = requests.get(main_url+link, headers=headers)
	with open("pronounce/"+word+'_ed_eng.mp3','wb') as output:
		output.write(file.content)	
	print(word+" => has been dowloaded")
	time.sleep(random.randint(0,3))
print("Downloading has been finished /a")
