# -*- coding: UTF-8 -*-
####################################################################################################

PREFIX = "/video/orftvthek"
URL = "http://tvthek.orf.at"
URLprograms = "http://tvthek.orf.at/programs"
SEARCH_URL = 'http://tvthek.orf.at/search?q=%s'
#htmlPage = HTML.ElementFromURL(URL, cacheTime=3600)

TITLE = 'ORF TVThek'
ART = 'tvthek_bg.jpg'
ICON = 'icon-default.png'

####################################################################################################
def Start():
	ObjectContainer.art = R(ART)
	ObjectContainer.title1 = TITLE
	DirectoryObject.thumb = R(ICON)
	DirectoryObject.art = R(ART)
		
def CreatePrefs():
	Prefs.Add(id='orf1', type='bool', default=True, label='ORF1')
	Prefs.Add(id='orf2', type='bool', default=True, label='ORF2')

def ValidatePrefs():
	orf1 = Prefs.Get('orf1')
	orf2 = Prefs.Get('orf2')

@handler(PREFIX, TITLE, art=ART, thumb=ICON)
@route(PREFIX + '/mainmenu')
def MainMenu():
	Log.Debug("Entering MainMenu …")
	mainMenu = ObjectContainer()
	
	htmlPage = HTML.ElementFromURL(URL, cacheTime=7200)
	# Find items in the menu bar		
	menuItems = htmlPage.xpath('//ul[@id="menu"]/li')
	for menuItem in menuItems:
		title = menuItem.xpath('./a')[0].get("title")
		kind = menuItem.xpath('./a')[0].get("href")
		
		if kind == "/":
			kind = kind + "start"
		kind = kind[1:]
		
		#if subtitle.find("Startseite"):
		subPageURL = URL + menuItem.xpath('./a')[0].get("href")
		Log.Debug("Item: " + title + " url: " + subPageURL)
		# mainMenu.add(DirectoryObject(key=Callback(SubMenu, subPageURL = subPageURL, title = title), title=title))
		mainMenu.add(DirectoryObject(key=Callback(SubMenu, subPageURL = subPageURL, kind = kind), title=title))
	#SearchMenuItem(dir=mainMenu)
	#dir.Append(PrefsItem("Preferences..."))

	Log.Debug("Leaving MainMenu …")	
	return mainMenu
	
@route(PREFIX + '/submenu')
# def SubMenu(subPageURL,title):
def SubMenu(subPageURL,kind):
	Log.Debug("Entering SubMenu for " + kind)

	htmlPage = HTML.ElementFromURL(subPageURL, cacheTime=3600)
	# menuItems = htmlPage.xpath('//div[@id="content"]//div[contains(@class, "row")]//div[contains(@class, "block")]')
	xPath = '//div[@id="content"]//div[contains(@class, "row")]'
	
	if kind == "live":
		xPath = '//div[@id="content"]//div[not(contains(@class,"form")) and contains(@class,"row")]'
	menuItems = htmlPage.xpath(xPath)

	# menuItems = htmlPage.xpath('//div[@id="content"]//div[contains(@class, "row")]//div[@class="content"]')	
	# menuItems = htmlPage.xpath('//div[@id="content"]//div[contains(@class, "row")]//div[@class="content"]/..')
		
	subMenu = ObjectContainer()

	i = 0 # initialize for-loop counter
	for menuItem in menuItems:
		
		i = i + 1 # increase loop counter
		Log.Debug("URL: " + subPageURL + ", loop counter:" + str(i))
		if kind == "start" and i == 1:
			subMenu = SubMenuTab(subPageURL)
			continue
		if kind == "live" and i > 2:
			continue
		
		try:
			title = menuItem.xpath('.//h3/span')[0].text
		except:
			title = " "
			
		# title = menuItem.xpath('.//h3/a')[0].text

		Log.Debug("subPageURL = " + subPageURL + " / loop counter: " + str(i) + " Title: " + title)

		try:
			moreShows = menuItem.xpath('.//h3/a[@class="more"]')[0].get('href')
			Log.Debug("There are more " + title + " Shows …")
	
		except:
			moreShows = None
			Log.Debug("No more shows in " + title + " Shows ...")
		
		try:
			topic = menuItem.xpath('.//div[contains(@id, "topic_")]')[0].get('id')
			# showType = "Topic"
		except:
			topic = title
			# showType = "Genre"
			
		# topic = topic[6:]
		Log.Debug("Topic: " + topic)
		
		subMenu.add(DirectoryObject(
			key = Callback(
				Shows,
				title = title,
				topic = topic,
				subPageURL = subPageURL,
				moreShows = moreShows,
				kind = kind),
			title = title
		))	
	Log.Debug("Leaving SubMenu …")	
	return subMenu

@route(PREFIX + '/submenutab')
def SubMenuTab(subPageURL):
	Log.Debug("Entering SubMenuTab …")
	htmlPage = HTML.ElementFromURL(subPageURL, cacheTime=3600)
	# menuItems = htmlPage.xpath('//div[@id="content"]//div[contains(@class, "row")]//div[@class="content"]')
	menuItems = htmlPage.xpath('//div[@id="content"]//div[contains(@class, "row")]//div[@class="tabcontrol"]//div[contains(@id, "-tab")]')
	subMenu = ObjectContainer()

	i = 0 # initialize for-loop counter
	for menuItem in menuItems:
		i = i + 1 # increase loop counter

		title = menuItem.xpath('h3/a')[0].get('title')
		topic = menuItem.get('id')
		
		Log.Debug("Title: " + title + " / Topic: " + topic)
		
		subMenu.add(DirectoryObject(
			key = Callback(
				Shows,
				title = title,
				topic = topic,
				subPageURL = subPageURL,
				moreShows = None,
				kind = "start"),
			title = title
		))	
	Log.Debug("Leaving SubMenuTab …")	
	return subMenu

@route(PREFIX + '/shows')
def Shows(title, topic, subPageURL, moreShows = None, kind = "Topic"):	
	Log.Debug("Entering Shows for " + title + " (Kind: " + kind + ")")
	
	xPath = '//div[@id="content"]//div[contains(@class, "row")]//div[@class="content"]'

		
	if moreShows:
		subPageURL = URL+moreShows

	elif kind == "start":
		xPath = '//div[@id="' + topic + '"]'

	elif (kind == "programs") or (kind == "live"):
		topic = unicode(topic, "utf8")
		Log.Debug("Topic (encoded): " + topic)
		xPath = '//div[@id="content"]//div[contains(@class, "row")]//div[contains(@class, "block") and ./h3/span[contains(text(),"' + topic + '")]]'

	elif kind == "topics":
		xPath = '//div[@id="content"]//div[contains(@class, "row")]//div[@id="' + topic + '"]//div[@class="content"]'
	
	Log.Debug("Title: " + title + " URL: " + subPageURL)
	
	if kind == "live":
		xPath = xPath + '//li'
	else:
		xPath = xPath + '//li/a'
		
	Log.Debug("XPath: " + xPath)
	
	htmlPage = HTML.ElementFromURL(subPageURL, cacheTime=None)
	
	# shows =[]
	shows = htmlPage.xpath(xPath)
	Log.Debug("Nr. of Shows: " + str(len(shows)))
	
	showMenu = ObjectContainer()
	
	for show in shows:
		showTitle = show.xpath('.//strong')[0].text
		if (not showTitle):
			showTitle = show.xpath('.//strong/span')[0].text
			if (not showTitle):
				showTitle = show.get("title")
		# showTitle = showTitle.lstrip()		

		try:
			showURL = show.get("href")
		except:
			showURL = " "
			
		showThumb = show.xpath(".//img")[0].get("src")
		
		try:
			showDateTime = show.xpath('.//span[@class="desc_time genre"]')[0].text
			showDateTime = showDateTime.lstrip()
			showDateTime = showDateTime.rstrip()
		except:
			showDateTime = " "
		try:
			showDesc = show.xpath('.//span[@class="desc"]')[0].text
		except:
			showDesc = " "
		
		if kind == "live":
			showDesc = ""
			showDescs = show.xpath('.//span[@class="desc"]')
			for descLine in showDescs:
				showDesc = showDesc + descLine.text + "\n"
		try:
			showDuration = show.xpath('.//span[contains(@class, "duration")]')[0].text
		except:
			showDuration = " "

		showDesc = showDateTime + " " + showDuration + "\n" + showDesc
		
		#Log.Debug("Title: " + showTitle)
		#Log.Debug("URL: " + showURL)
		#Log.Debug("Thumb: " + showThumb)
		#Log.Debug("DatTime: " + showDateTime)
		#Log.Debug("Duration: " + showDuration)
		#Log.Debug("Desc: " + showDesc)

		showMenu.add(VideoClipObject(
			title = showTitle,
			summary = showDesc,
			thumb = showThumb,
			url = URL + showURL			
			)
		)
		
		#showMenu.add(DirectoryObject(
		#	key = Callback(
		#		VideoItems,
		#		title = showTitle,
		#		date = showDateTime,
		#		dur = showDuration,
		#		summary = showDesc,
		#		thumb = showThumb,
		#		url = showURL,
		#		kind = kind
		#		),
		#	title = showTitle,
		#	tagline = (showDateTime + " / " + showDuration),
		#	summary = showDesc,
		#	thumb = showThumb
		#	)
		#)
		
	Log.Debug("Leaving Shows …")		
	return showMenu

@route(PREFIX + '/videoitems')
def VideoItems(title,date,dur,summary,thumb,url,kind):
	Log.Debug("Entering VideoItems for kind: " + kind)
	
	title = unicode(title, "utf8")

	if kind == "live":
		message = PopupDirectoryObject()
		message.header = title
		message.message = summary
		return message
	
	video = VideoClipObject(
		title = title,
		summary = summary,
		# originally_available_at = date,
		thumb = thumb,
		url = URL + url
		)
	
	oc = ObjectContainer()
	oc.add(video)
	
	return oc

