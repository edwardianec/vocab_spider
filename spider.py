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
import pickle



################################################################
#	Глобальные переменные
################################################################

main_link = "https://dictionary.cambridge.org/dictionary/english-russian/"
second_link = "https://dictionary.cambridge.org/dictionary/english/"
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}



def meaning_handler(meaning):
	meaning_dict = {}
	try:
		meaning_dict["short_meaning"] = meaning.find("h3").get_text().strip()
	except:
		meaning_dict["short_meaning"] = ""
	meaning_dict["levels"] = []

	if (meaning.find(class_="sense-body").findAll(class_="def-block", recursive=False)): 
		for level in meaning.find(class_="sense-body").findAll(class_="def-block", recursive=False):
			level_dict = {}
			level_dict["examples"] = []
			try:
				level_dict["ru"] = level.find(class_="def-body").find("span", class_="trans").text.strip()
			except:
				level_dict["ru"] = ""
			try:
				level_dict["name"] = level.find(class_="ddef-info").text.strip()
			except:
				level_dict["name"] = ""
			level_dict["definition"] = level.find(class_="def ddef_d").get_text().strip()
			level_examples = level.find(class_="def-body").find_all(class_="examp dexamp")
			for el in level_examples:
				for a in el.find_all('a'):
					a.replaceWithChildren()
			level_dict["examples"] = [lev.get_text().strip() for lev in level_examples]
			meaning_dict["levels"].append(level_dict)
	else:
		# phrase-block
		for level in meaning.find(class_="sense-body").findAll(class_="phrase-block", recursive=False):
			level_dict = {}
			meaning_dict["short_meaning"] = level.find(class_="phrase-head").text.strip() 
			level_dict["examples"] = []
			try:
				level_dict["ru"] = level.find(class_="def-body").find("span", class_="trans").text.strip()
			except:
				level_dict["ru"] = ""
			try:
				level_dict["name"] = level.find(class_="ddef-info").text.strip()
			except:
				level_dict["name"] = ""
			level_dict["definition"] = level.find(class_="def ddef_d").get_text().strip()
			level_examples = level.find(class_="def-body").find_all(class_="examp dexamp")
			for el in level_examples:
				for a in el.find_all('a'):
					a.replaceWithChildren()
			level_dict["examples"] = [lev.get_text().strip() for lev in level_examples]
			meaning_dict["levels"].append(level_dict)
	return 	meaning_dict


def find_extra_links(extra_links_block, word_to_find):
	print(extra_links_block)
	extra_links = []
	if (len(extra_links_block)):
		for extra_link in extra_links_block[0].find_all("a"):
			if (extra_link["title"].split(" ")[0]==word_to_find):
				extra_links.append(extra_link["href"])

def engine_v2(content, word_to_find):
	if (content): print("content: ok")
	else: print("content: none")

	items 		= []									#содержит все слова, найденные на странице - verb, noun..etc
	if (content.find(class_="di-body", recursive=False)):
		content = content.find(class_="di-body")

	for word in content.findAll(class_="entry-body__el", recursive=False):
		item = {}
		item["word"] 			= word_to_find
		item["part"] 			= word.find(class_='pos dpos').get_text()		
		item["sound"] 			= word.find(type='audio/mpeg')["src"]
		print(str(word.find(class_="pron dpron").get_text()))
		item["transcription"] 	= str(word.find("span", class_="pron dpron").get_text())
						
		item["meanings"] 		= []
		for meaning in word.select(".pr.dsense"):
			meaning_dict = meaning_handler(meaning)
			item["meanings"].append(meaning_dict)		
		items.append(item)
	return (items)



def csv_write(items):
	with open('cambridges_words.csv', "w", encoding='utf-8', newline='') as f:
		writer = csv.writer(f, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
		for item in items:
			writer.writerow([item["word"],item["part"],item["transcription"],item["image_path"], item["sound_word_path"],item["definition"],item["russian"],item["sound_def_path"], item["examples"], item["sound_ex_path"], item["tag"] ])
	with open('cambridges_pronounce.csv', "w", encoding='utf-8', newline='') as f:
		writer = csv.writer(f, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
		for item in items:
			writer.writerow([item["word"],item["sound"]])
	print("csv is writed")

def formatting_output(items):
	for word in items:
		print("\n")
		print("######################################################################")
		print(word["word"])
		print(word["part"])
		for meaning in word["meanings"]:
			print("	",meaning["short_meaning"])
			for level in meaning["levels"]:
				print("		",level["definition"])
				if (len(level["examples"])):print("		 <<",level["examples"][0],">>")
				print("		",level["ru"])
		
"""
	searching_word = "forbid"
	#page = requests.get(main_link+searching_word, headers=headers)
	found_words = engine_v2(searching_word,text)
	with open('data.pickle', 'wb') as f:
		pickle.dump(found_words, f)


	with open('data.pickle', 'rb') as f:
		data_new = pickle.load(f)
		print(data_new)
"""
def search_extra_links(searching_word, extra_links):
	found_words = []
	if (extra_links):
		for extra_link in extra_links:				
			page = requests.get(extra_link, headers=headers) 
			[found_words.append(word) for word in engine_v2(searching_word,page.text)]	
	return found_words


def check_link(searching_word, link):
	page 	= requests.get(link+searching_word, headers=headers) 
	soup 	= BeautifulSoup(page.text, 'html.parser')
	body 	= soup.select(".entry-body")
	return body	

def get_page(searching_word):
	for link in (main_link, second_link):
		html_body = check_link(searching_word, link)
		if (html_body): 
			print("working link: "+link)
			return html_body[0]
	return False

def search_words(searching_words, database_path, database_name):
	found_words = []
	for searching_word in list(dict.fromkeys(searching_words)):
		print("word: ", searching_word)
		time.sleep(random.randint(0,5))

		html_body = get_page(searching_word)
		if (html_body): 
			words = engine_v2(html_body, searching_word)
			[found_words.append(word) for word in words]
			#extra_words = search_extra_links(searching_word, extra_links)
			#if (extra_words): [found_words.append(word) for word in extra_words]
		else: 
			print("cant open word:"+searching_word)



	print(found_words)
	formatting_output(found_words)
	with open('{0}/{1}'.format(database_path, database_name), 'wb') as f:
		pickle.dump(found_words, f)
	print("found words saved in pickle file: {0}/{1}".format(database_path, database_name))

#-------------------------- dec 2019 -----------------------------------


def sense_block_parser(html):
	sense_block = {}
	if (html.find(class_="ddef_d")): sense_block["description"]	 	= html.find(class_="ddef_d").get_text().strip()
	else:
		sense_block["description"]	 = ""

	if (html.find(class_="dtrans-se")):	sense_block["translation"]	 = html.find(class_="dtrans-se").get_text().strip()
	else: sense_block["translation"] = ""

	examples = html.find_all(class_="dexamp", recursive=True)
	if (examples):
		sense_block["examples"]	= [example.get_text().strip() for example in examples]
	else:
		sense_block["examples"] = []
	return sense_block

#-------
def head_handler(html):
	head 				= {}
	head["word"]		= html.find(class_="h2").get_text().strip()
	head["speach_part"] = html.find(class_="pos").get_text().strip()
	head["sound"]		= html.find(type='audio/mpeg')["src"]
	return head

def sense_blocks_handler(sense_blocks):
	meanings = []
	for sense_block in sense_blocks:
		meanings.append(sense_block_parser(sense_block))
	return meanings

def browse(html):
	extra_links = []
	for item in html.find_all("a", recursive=True):
		
		extra_words 				= {}
		extra_words["link"] 		= item["href"]
		extra_words["title"]		= item.find(class_="base", recursive=True).get_text().strip()
		if (item.find(class_="pos", recursive=True)):
			extra_words["speach_part"] 	= item.find(class_="pos", recursive=True).get_text().strip()
		else:
			extra_words["speach_part"] 	= ""
		extra_links.append(extra_words)
	return extra_links
#--------

def render(word):
	head = "word: {0}\nsp: {1}\nsound: {2}\n".format(word["head"]["word"], word["head"]["speach_part"], word["head"]["sound"])	
	print(head)
	for meaning in word["meanings"]:
		print("	",meaning["description"])
		print("	",meaning["translation"])
		for example in meaning["examples"]:
			print("		",example)


def engine_v3(html):
	items 	= {}		#содержит все слова, найденные на странице - verb, noun..etc
	soup 	= BeautifulSoup(html, 'html.parser')
	content = soup.find(class_="entry-body__el")

	# содержит часть речи, произношение, и само слово
	items["head"]			= head_handler(content.find(class_="di-head"))

	# сдесь у нас все варианты и значения слова
	items["meanings"]		= sense_blocks_handler(content.find_all(class_="sense-block", recursive=True))

	# все дополнительные варианты слова, другие части речи и phrasal verbs

	items["see_also"]  		= browse(soup.find(class_="hax lp-10 lb lb-cm lbt0 dbrowse", recursive=True))
	
	return items


	""" 	
		for word in content.findAll(class_="entry-body__el", recursive=False):
		item = {}
		item["word"] 			= word_to_find
		item["part"] 			= word.find(class_='pos dpos').get_text()		
		item["sound"] 			= word.find(type='audio/mpeg')["src"]
		print(str(word.find(class_="pron dpron").get_text()))
		item["transcription"] 	= str(word.find("span", class_="pron dpron").get_text())
						
		item["meanings"] 		= []
		for meaning in word.select(".pr.dsense"):
			meaning_dict = meaning_handler(meaning)
			item["meanings"].append(meaning_dict)		
		items.append(item) """
	#return (items)	



###################################################################
#	Main
###################################################################

searching_words_1610 = [
	"skilful",
	"accuse",
	"say",	
	"agree",
	"claim",	
	"promise",	
	"refuse",	

	"threaten",
	"admit",
	"answer",	
	"confess",
	"get-in",

	"deny",
	"recommend",
	"remind",
	"warn",
	"blame",	
	"complain",
	"regret",	
	"insist",
	"suggest",
	"advise",
	"advice",
	"ask",
	"beg",
	"convince",
	"encourage",
	"invite",	
	"order",	
	"persuade",
	"novel",	
	"pollen",
	"goose",
	"knife",	
	"shelf",
	"matter",	
	"reluctant",
	"listen-in",
	"recall",
	"mat",
	"pen",	
	"pan",	
	"lad",	
	"latter",
	"letter",
	"flesh",
	"craft",	
	"jury",
	"needle",
	"unravel",
	"murderer",
	"journey",
	"mirror",	
	"rear",	
	"flash",	
	"escape",	

	############
	# irregular verbs

	"abide",
	"arise",
	"awake",	
	"bear",	
	"beat",	
	"become," 
	"befall",
	"beget",
	"begin",
	"behold",
	"bereave",
	"beseech",
	"beset",
	"bespeak",
	"bestride",
	"bet",
	"bid",
	"bind",
	"bite",
	"bleed",
	"blow",
	"break",
	"breed",
	"bring",
	"broadcast",
	"build",
	"burn",
	"burst",
	"buy",
	"can",
	"cast",
	"catch",
	"choose",
	"cling",
	"come",
	"cost",
	"creep",
	"cut",
	"deal",
	"dig",
	"do",
	"draw",
	##### second column
	"dream",
	"drink",
	"drive",
	"dwell",
	"eat",
	"interweave",
	"fall",
	"feed",
	"feel",
	"fight",
	"find",
	"flee",
	"fling",
	"fly",
	"forbid",
	"forecast",
	"forget",
	"forgive",
	"forsake",
	"foresee",
	"foretell",
	"freeze",
	"get",
	"give",
	"go",
	"grind",
	"grow",
	"hang",
	"have",
	"hear",
	"hide",
	"hit",
	"hold",
	"hurt",
	"keep",
	"kneel",
	"know",
	"lay",
	"lead",
	"lean",
	"leap",
	"learn",
	"leave",
	"lend",

	"let",
	"lie",
	"lose",
	"make",
	"mean",
	"meet",
	"pay",
	"mistake",
	"overhear",
	"oversleep",
	"put",
	"read",
	"rend",
	"rid",
	"ride",
	"ring",
	"rise",
	"run",
	"see",
	"seek",
	"sell",
	"send",
	"set",
	"shake",
	"shed",
	"shine",
	"shit",
	"shoot",
	"show",
	"shrink",
	"shrive",
	"shut",
	"sing",
	"sink",
	"sit",
	"slay",
	"sleep",
	"slide",
	"sling",
	"slink",
	"slit",
	"smell",
	"smite",

	"speak",
	"speed",
	"spend",
	"spin",
	"spit",
	"split",
	"spoil",
	"spread",
	"spring",
	"stand",
	"steal",
	"stick",
	"sting",
	"stink",
	"stride",
	"strike",
	"string",
	"strive",
	"swear",
	"sweep",
	"swim",
	"swing",
	"take",
	"teach",
	"tear",
	"tell",
	"think",
	"throw",
	"thrust",
	"tread",
	"understand",
	"undertake",
	"undo",
	"upset",
	"wake",
	"wear",
	"weave",
	"weep",
	"win",
	"wind",
	"withdraw",
	"withstand",
	"wring",
	"write",

	"confine",
	"revise",
	"impact",
	"postpone",
	"alleviate",
	"concise",
	"opaque",
	"implicit",
	"coherence"
]
"""


"""




#search_words(["beseech", "mean"],"database", "searching_words_1610.pickle")
log = open("log.html",  "w", encoding="utf-8")
with open("html.html", encoding="utf-8") as html_file:
	word = engine_v3(html_file)
	render(word)




log.write(str(word))





# использую это, если у тебя есть переменная,
# содержащая html страницу

#formatting_output(engine_v2("mean",mean_text)[0])
#formatting_output(engine_v2("bereave",bereave_text))


