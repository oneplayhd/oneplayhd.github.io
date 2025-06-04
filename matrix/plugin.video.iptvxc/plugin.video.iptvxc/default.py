#!/usr/bin/python														   #
# -*- coding: utf-8 -*-													   #
############################################################################
#							  /T /I										   #
#							   / |/ | .-~/								   #
#						   T\ Y	 I	|/	/  _							   #
#		  /T			   | \I	 |	I  Y.-~/							   #
#		 I l   /I		T\ |  |	 l	|  T  /								   #
#	  T\ |	\ Y l  /T	| \I  l	  \ `  l Y								   #
# __  | \l	 \l	 \I l __l  l   \   `  _. |								   #
# \ ~-l	 `\	  `\  \	 \ ~\  \   `. .-~	|								   #
#  \   ~-. "-.	`  \  ^._ ^. "-.  /	 \	 |								   #
#.--~-._  ~-  `	 _	~-_.-"-." ._ /._ ." ./								   #
# >--.	~-.	  ._  ~>-"	  "\   7   7   ]								   #
#^.___~"--._	~-{	 .-~ .	`\ Y . /	|								   #
# <__ ~"-.	~		/_/	  \	  \I  Y	  : |								   #
#	^-.__			~(_/   \   >._:	  | l______							   #
#		^--.,___.-~"  /_/	!  `-.~"--l_ /	   ~"-.						   #
#			   (_/ .  ~(   /'	  "~"--,Y	-=b-. _)					   #
#				(_/ .  \  Fire TV Guru/ l	   c"~o \					   #
#				 \ /	`.	  .		.^	 \_.-~"~--.	 )					   #
#				  (_/ .	  `	 /	   /	   !	   )/					   #
#				   / / _.	'.	 .':	  /		   '					   #
#				   ~(_/ .	/	 _	`  .-<_								   #
#					 /_/ . ' .-~" `.  / \  \		  ,z=.				   #
#					 ~( /	'  :   | K	 "-.~-.______//					   #
#					   "-,.	   l   I/ \_	__{--->._(==.				   #
#						//(		\  <	~"~"	 //						   #
#					   /' /\	 \	\	  ,v=.	((						   #
#					 .^. / /\	  "	 }__ //===-	 `						   #
#					/ / ' '	 "-.,__ {---(==-							   #
#				  .^ '		 :	T  ~"	ll								   #
#				 / .  .	 . : | :!		 \								   #
#				(_/	 /	 | | j-"		  ~^							   #
#				  ~-<_(_.^-~"											   #
#																		   #
############################################################################

#############################=IMPORTS=######################################
	#Kodi Specific
import sys
PY3 = sys.version_info[0] == 3
import xbmc,xbmcaddon,xbmcgui,xbmcplugin,xbmcvfs
	#Python Specific
import base64,os,re,time,sys,urllib.request
import urllib.parse,urllib.error,json,datetime,shutil
import xml.dom.minidom
from xml.dom.minidom import Node
from datetime import datetime,timedelta
	#Addon Specific
from resources.modules import control,tools,popup,speedtest
if PY3:
	from urllib.parse import quote, quote_plus, unquote_plus, unquote, urlparse	
else:
	from urllib import quote, quote_plus, unquote_plus, unquote
	from urlparse import urlparse
##########################=VARIABLES=#######################################
ADDON = xbmcaddon.Addon()
ADDONPATH = ADDON.getAddonInfo("path")
ADDON_NAME = ADDON.getAddonInfo("name")
ADDON_ID = ADDON.getAddonInfo('id')

DIALOG			  = xbmcgui.Dialog()
DP				  = xbmcgui.DialogProgress()
HOME			  = xbmcvfs.translatePath('special://home/')
ADDONS			  = os.path.join(HOME,	   'addons')
USERDATA		  = os.path.join(HOME,	   'userdata')
PLUGIN			  = os.path.join(ADDONS,   ADDON_ID)
PACKAGES		  = os.path.join(ADDONS,   'packages')
ADDONDATA		  = os.path.join(USERDATA, 'addon_data', ADDON_ID)
ADVANCED		  = os.path.join(USERDATA,	'advancedsettings.xml')
advanced_settings = os.path.join(PLUGIN,'resources', 'advanced_settings')
MEDIA			  = os.path.join(ADDONS,  PLUGIN , 'resources', 'media')
KODIV			  = float(xbmc.getInfoLabel("System.BuildVersion")[:4])
M3U_PATH		  = os.path.join(ADDONDATA,  'm3u.m3u')
##########################=ART PATHS=#######################################
icon			  = os.path.join(PLUGIN,  'icon.png')
fanart			  = os.path.join(PLUGIN,  'fanart.jpg')
background		  = os.path.join(MEDIA,   'background.jpg')
live			  = os.path.join(MEDIA,   'live.jpg')
catch			  = os.path.join(MEDIA,   'cu.jpg')
Moviesod		  = os.path.join(MEDIA,   'movie.jpg')
Tvseries		  = os.path.join(MEDIA,   'tv.jpg')
iconextras		  = os.path.join(MEDIA,   'iconextras.png')
iconsettings	  = os.path.join(MEDIA,   'iconsettings.png')
iconlive		  = os.path.join(MEDIA,   'iconlive.png')
iconcatchup		  = os.path.join(MEDIA,   'iconcatchup.png')
iconMoviesod	  = os.path.join(MEDIA,   'iconmovies.png')
iconTvseries	  = os.path.join(MEDIA,   'icontvseries.png')
iconsearch		  = os.path.join(MEDIA,   'iconsearch.png')
iconaccount		  = os.path.join(MEDIA,   'iconaccount.png')
icontvguide		  = os.path.join(MEDIA,   'iconguide.png')

#########################=XC VARIABLES=#####################################
dns				  = control.setting('DNS')
username		  = control.setting('Username')
password		  = control.setting('Password')
dns_unblock		  = control.setting('dns_unblock')
live_url = '{0}/player_api.php?username={1}&password={2}&action=get_live_categories'.format(dns, username, password)
vod_url = '{0}/player_api.php?username={1}&password={2}&action=get_vod_categories'.format(dns, username, password)
series_url = '{0}/player_api.php?username={1}&password={2}&action=get_series_categories'.format(dns, username, password)
panel_api		  = '{0}/panel_api.php?username={1}&password={2}'.format(dns,username,password)
player_api		  = '{0}/player_api.php?username={1}&password={2}'.format(dns,username,password)
play_url		  = '{0}/live/{1}/{2}/'.format(dns,username,password)
play_live		  = '{0}/{1}/{2}/'.format(dns,username,password)
play_movies		  = '{0}/movie/{1}/{2}/'.format(dns,username,password)
play_series		  = '{0}/series/{1}/{2}/'.format(dns,username,password)
#############################################################################
adult_tags = ['xxx','xXx','XXX','adult','Adult','ADULT','adults','Adults','ADULTS','porn','Porn','PORN']

def get_kversion():
    full_version_info = xbmc.getInfoLabel('System.BuildVersion')
    baseversion = full_version_info.split(".")
    intbase = int(baseversion[0])
    return intbase

def buildcleanurl(url):
	url = str(url).replace('USERNAME',username).replace('PASSWORD',password)
	return url

def start(signin):
	if username == "":
		dns = tools.keypopup('Coloque o Host ex: http://dns.com:porta')
		usern = tools.keypopup('Coloque Usuario')
		passw = tools.keypopup('Coloque Senha')
		control.setSetting('DNS',dns)
		control.setSetting('Username',usern)
		control.setSetting('Password',passw)
		xbmc.executebuiltin('Container.Refresh')
		auth_url = '{0}/player_api.php?username={1}&password={2}'.format(dns,usern,passw)
		parse = tools.OPEN_URL(auth_url)
		
		login_data = parse['user_info']['auth']
		if login_data == 0:
			line1 = "Login incorreto"
			line2 = "Por favor tente denovo" 
			line3 = "" 
			xbmcgui.Dialog().ok('Attention', line1+'\n'+line2+'\n'+line3)
			start()
		else:
			line1 = "Login com Sucesso!"
			line2 = "Bem vindo ao "+ADDON_NAME
			line3 = ('[B][COLOR white]%s[/COLOR][/B]'%usern)
			xbmcgui.Dialog().ok(ADDON_NAME, line1+'\n' + line2 +'\n' + line3)
			adult_set()
			#tvguidesetup()
			#addonsettings('ADS2','')
			xbmc.executebuiltin('Container.Refresh')
			home()
	else:
		home()

def home():
	tools.addDir('Informação da Conta','url',6,iconaccount,background,'')
	tools.addDir('TV Ao Vivo','live',1,iconlive,background,'')
	tools.addDir('Séries','live',18,iconTvseries,background,'')
	#if xbmc.getCondVisibility('System.HasAddon(pvr.iptvsimple)'):
	#	tools.addDir('TV Guide','pvr',7,icontvguide,background,'')
	#tools.addDir('Catchup TV','url',12,iconcatchup,background,'')
	tools.addDir('Filmes','vod',3,iconMoviesod,background,'')
	#tools.addDir('Pesquisa','url',5,iconsearch,background,'')
	tools.addDir('Configurações','url',8,iconsettings,background,'')
	tools.addDir('Extras','url',16,iconextras,background,'')

def livecategory():
    vod_cat = tools.OPEN_URL(live_url)
    for cat in vod_cat:
        mystring = cat['category_name'] 
        if xbmcaddon.Addon().getSetting('hidexxx')=='false':
            tools.addDir(mystring,player_api + '&action=get_live_streams&category_id=' + str(cat['category_id']), 2, icon, background, '')
        else :
            if not any(s in name for s in adult_tags):
                tools.addDir(mystring,player_api + '&action=get_live_streams&category_id=' + str(cat['category_id']), 2, icon,background, '')

def Livelist(url):
    vod_cat = tools.OPEN_URL(url)
  
    
    background = os.path.join(MEDIA, 'background.jpg')
    for cat in vod_cat:
        url = play_live + str(cat['stream_id'])
        try:
         thumb = cat['stream_icon']
        except:
         thumb =  icon
        
        if xbmcaddon.Addon().getSetting('hidexxx') == 'false':
            tools.addDir(cat['name'], url, 4, str(thumb), background, '')
        else:
            if not any(s in name for s in adult_tags):
                tools.addDir(cat['name'], url, 4, str(thumb), background, '')

def series_cats(url):
	vod_cat = tools.OPEN_URL(player_api+'&action=get_series_categories')
	
	for cat in vod_cat:
		if xbmcaddon.Addon().getSetting('hidexxx')=='false':
			tools.addDir(cat['category_name'],player_api+'&action=get_series&category_id='+str(cat['category_id']),25,icon,background,'')
		else:
			if not any(s in name for s in adult_tags):
				tools.addDir(cat['category_name'],player_api+'&action=get_series&category_id='+str(cat['category_id']),25,icon,background,'')

# categoria series
def serieslist(url): 
    ser_cat = tools.OPEN_URL(url)
    background = ''
    if not 'releaseDate'  in ser_cat:  
        cont = 0
    else: 
        cont = 1    
    
    for ser in ser_cat:
        name = ser['name']
        
        url = player_api + '&action=get_series_info&series_id=' + str(ser['series_id'])
        try:
            thumb = ser['cover']
            background = ser['backdrop_path'][0]
            plot = ser['plot']
            releaseDate = ser['releaseDate']
            cast = str(ser['cast']).split()
            rating_5based = ser['rating_5based']
            episode_run_time = str(ser['episode_run_time'])
            genre = ser['genre']
        except:
            thumb = icon
            plot = ''
            releasedate = 2023
            cast = ('', '')
            rating_5based = ''
            episode_run_time = ''
            genre = ''
          
        if not background.strip():
            background = os.path.join(MEDIA, 'background.jpg')
        if cont == 0:
            releasedate = '2022-01-01' 
        #if not releasedate.2strip(): datetime.strptime(date_time_str, '%d/%m/%y %H:%M:%S'
       
        if xbmcaddon.Addon().getSetting('meta') == 'true':
            tools.addDirMeta(name, url, 19, str(thumb), background, plot, str(releasedate), cast, rating_5based, episode_run_time,
                             genre)
        else:
            # tools.log('[FTG]--')
            tools.addDir(name, url, 19, str(thumb), background, '')

def series_seasons(url):
    ser_cat = tools.OPEN_URL(url)
    if not 'episodes'  in ser_cat:
        return
    for ser in ser_cat['episodes']:
        info = ser_cat['info']
        try:
            thumb = info['cover']
        except:
            thumb = ''
        try:
            background = info['backdrop_path'][0]
        except:
            background = ''
        if not background.strip():
            background = os.path.join(MEDIA, 'background.jpg')    
        tools.addDir('Temporada - ' + ser, url + '&season_number=' + str(ser), 20, str(thumb), background, '')

# listar seasons        
def season_list(url):
    tools.log(url)
    ser_cat = tools.OPEN_URL(url)
    
    info = ser_cat['info']
    ser_cat = ser_cat['episodes']
    
    from urllib.parse import urlparse, parse_qs
    parsed_url = urlparse(url)
    season_number = str(parse_qs(parsed_url.query)['season_number'][0])
    if not 'releaseDate'  in ser_cat[season_number]:  
        cont = 0
    else: 
        cont = 1 
    for ser in ser_cat[season_number]:
        url = play_series + str(ser['id']) + '.' + ser['container_extension']
        try:
            thumb = ser['info']['movie_image']
        except:
            thumb = ''
        try:
            background = ser['info']['movie_image']
        except:
            background = ''
        try:
            plot = ser['info']['plot']
        except:
            plot = ''
        try:
            releasedate = ser['info']['releasedate']
        except:
            releasedate = ''
        try:
            cast = str(info['cast']).split()
        except:
            cast = ('', '')
        try:
            rating_5based = info['rating_5based']
        except:
            rating_5based = ''
        try:
            duration = str(ser['info']['duration'])
        except:
            duration = ''
        try:
            genre = info['genre']
        except:
            genre = ''
        if not background:
            background = os.path.join(MEDIA, 'background.jpg')
        if cont == 0:
            releasedate = '2022-01-01'
        if xbmcaddon.Addon().getSetting('meta') == 'true':
            tools.log(cast)
            tools.addDirMeta(ser['title'], url, 4, str(thumb), background, plot, str(releasedate), cast, rating_5based, duration,
                             genre)
        else:
            tools.addDir(ser['title'], url, 4, str(thumb), background, '')	

def Vodlist(url):
        vod_cat = tools.OPEN_URL(url)
      
        background = os.path.join(MEDIA, 'background.jpg')
        for cat in vod_cat:

            try:
                thumb = cat['stream_icon']
            except:
                thumb = icon
            url = play_movies + str(cat['stream_id'])+'.' + cat['container_extension']
            if xbmcaddon.Addon().getSetting('hidexxx') == 'false':
                tools.addDir(str(cat['name']), url, 4, str(thumb), background, '')
            else:
                if not any(s in name for s in adult_tags):
                    tools.addDir(str(cat['name']), url, 4, str(thumb), background, '')
def vod(url):
    vod_cat = tools.OPEN_URL(vod_url)
    
   
    for cat in vod_cat:
        mystring = cat['category_name'] 
        if xbmcaddon.Addon().getSetting('hidexxx') == 'false':
            tools.addDir(mystring,
                         player_api + '&action=get_vod_streams&category_id=' + str(cat['category_id']), 9, icon,
                         background, '')
        else:
            if not any(s in name for s in adult_tags):
                tools.addDir(mystring,
                             player_api + '&action=get_vod_streams&category_id=' + str(cat['category_id']), 9, icon,
                             background, '')


def search():
	if mode==3:
		return False
	text = searchdialog()
	xbmc.log(str(text))
	parse = tools.OPEN_URL(panel_api)
	
	all_chans = tools.regex_get_all(open,'{"num":','}')
	for a in all_chans:
		name = tools.regex_from_to(a,'name":"','"')
		url	 = tools.regex_from_to(a,'"stream_id":"','"')
		thumb= tools.regex_from_to(a,'stream_icon":"','"').replace('\/','/')
		stream_type = tools.regex_from_to(a,'"stream_type":"','"').replace('\/','/')
		container_extension = tools.regex_from_to(a,'container_extension":"','"')
		if text in name.lower():
			if xbmcaddon.Addon().getSetting('hidexxx')=='false':
				if 'movie' in stream_type:
					tools.addDir(name,play_movies+url+'.'+container_extension,4,thumb,background,'')
				if 'live' in stream_type:
					tools.addDir(name,play_live+url,4,thumb,background,'')
			else:
				if not any(s in name for s in adult_tags):
					if 'movie' in stream_type:
						tools.addDir(name,play_movies+url+'.'+container_extension,4,thumb,background,'')
					if 'live' in stream_type:
						tools.addDir(name,play_live+url,4,thumb,background,'')
		elif text not in name.lower() and text in name:
			if xbmcaddon.Addon().getSetting('hidexxx')=='false':
				if 'movie' in stream_type:
					tools.addDir(name,play_movies+url+'.'+container_extension,4,thumb,background,'')
				if 'live' in stream_type:
					tools.addDir(name,play_live+url,4,thumb,background,'')
			else:
				if not any(s in name for s in adult_tags):
					if 'movie' in stream_type:
						tools.addDir(name,play_movies+url+'.'+container_extension,4,thumb,background,'')
					if 'live' in stream_type:
						tools.addDir(name,play_live+url,4,thumb,background,'')

def catchup():
	data = tools.OPEN_URL(panel_api+'&action=get_live_streams')

	for streams in data:
		if not streams['tv_archive']:
			continue
		try:
			thumb = streams['stream_icon']
		except:
			thumb = iconcatchup
		name = streams['name']
		stream_id = str(streams['stream_id'])
		if not name=="":
				tools.addDir(name,'url',13,str(thumb),background,stream_id)

def tvarchive(name,description):
	APIv2 = "{0}/player_api.php?username={1}&password={2}&action=get_simple_data_table&stream_id={3}".format(dns,username,password,description)
	data = tools.OPEN_URL(APIv2)
	
	for streams in data['epg_listings']:
		if not streams['has_archive']:
			continue
		if not streams['start']:
			continue
		name = base64.b64decode(streams['title']).decode('UTF-8')
		stream_id = streams['id']
		plot = base64.b64decode(streams['description']).decode('UTF-8')
		start = streams['start']
		end = streams['end']
		format = '%Y-%m-%d %H:%M:%S'
		start_obj = datetime(*(time.strptime(start, format)[0:6]))
		end_obj = datetime(*(time.strptime(end, format)[0:6]))
		start_api_obj = start_obj.strftime('%Y-%m-%d:%H-%M')
		end_api_obj = end_obj.strftime('%Y-%m-%d:%H-%M')
		difference = end_obj - start_obj
		duration = difference.total_seconds()
		duration = round(duration / 60)
		start2 = start[:-3]
		editstart = start2
		start2 = str(start2).replace(' ',' - ')
		catchupURL = "{0}/streaming/timeshift.php?username={1}&password={2}&stream={3}&start=".format(dns,username,password,description)
		ResultURL = catchupURL + str(start_api_obj) + "&duration={0}".format(duration)
		Fname = "[B][COLOR white]{0}[/COLOR][/B] - {1}".format(start2,name)
		tools.addDir(Fname,ResultURL,4,iconcatchup,background,plot)

#############################

def tvguide():
		xbmc.executebuiltin('ActivateWindow(TVGuide)')

# converter
		
def basename(p):
	"""Returns the final component of a pathname"""
	i = p.rfind('/') + 1
	return p[i:]  		

def ts_to_m3u8(url):
	try:
		url = unquote_plus(url)
	except:
		pass
	try:
		url = unquote(url)
	except:
		pass        
	if '|' in url:
		url = url.split('|')[0]
	elif '%7C' in url:
		url = url.split('%7C')[0]
	if not '.m3u8' in url and not '/hl' in url and int(url.count("/")) > 4 and not '.mp4' in url and not '.avi' in url:
		parsed_url = urlparse(url)
		try:
			host_part1 = '%s://%s'%(parsed_url.scheme,parsed_url.netloc)
			host_part2 = url.split(host_part1)[1]
			url = host_part1 + '/live' + host_part2
			file = basename(url)
			if '.ts' in file:
				file_new = file.replace('.ts', '.m3u8')
				url = url.replace(file, file_new)
			else:
				url = url + '.m3u8'
				# file_new = file + '.m3u8'
				# new_url = url.replace(file, file_new)
		except:
			pass
	return url 

# player
def stream_video(url,iconimage):
	if not iconimage:
		try:
			iconimage = xbmc.getInfoLabel('ListItem.Thumb')
		except:
			try:
				iconimage = xbmc.getInfoLabel('ListItem.Icon')
			except:
				iconimage = ''  	
	if iconimage:
		icon = iconimage
	else:
		icon = ''
	url = buildcleanurl(url)	
	headers = '|User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0'
	#url = url + headers
	try:
		name = xbmc.getInfoLabel('ListItem.Label')
	except:
		name = ''
	description = ''
	if not '.mp4' in url and not '.avi' in url and not '.rmv' in url and not 'rmvb' in url:
		check = True
	else:
		check = False
	if dns_unblock == 'true' and check == True:		
		name = 'XCUI' if not name else name
		url = ts_to_m3u8(url)
		url = url + headers
		if '.m3u8' in url and not 'plugin' in url:
			import hlsretry
			url = 'http://%s:%s/?url=%s'%(str(hlsretry.HOST_NAME),str(hlsretry.PORT_NUMBER),quote(url))
			hlsretry.XtreamProxy().start()	
			liz = xbmcgui.ListItem(name)
			liz.setArt({'icon':icon, 'thumb':icon})
			if get_kversion() > 19:
				info = liz.getVideoInfoTag()
				info.setTitle(name)
				info.setMediaType('video')
				info.setPlot(description)
			else:
				liz.setInfo(type='Video', infoLabels={'Title': name, 'Plot': description})
			#liz.setProperty('IsPlayable','true')
			liz.setPath(str(url))
			xbmc.Player().play(item=url, listitem=liz)						
		else:
			url = url + headers
			liz = xbmcgui.ListItem(name)
			liz.setArt({'icon':icon, 'thumb':icon})
			if get_kversion() > 19:
				info = liz.getVideoInfoTag()
				info.setTitle(name)
				info.setMediaType('video')
				info.setPlot(description)
			else:
				liz.setInfo(type='Video', infoLabels={'Title': name, 'Plot': description})
			#liz.setProperty('IsPlayable','true')
			liz.setPath(str(url))
			xbmc.Player().play(item=url, listitem=liz)
	elif dns_unblock == 'true' and check == False:
		name = 'XCUI' if not name else name
		import mp4retry
		url = 'http://%s:%s/?url=%s'%(str(mp4retry.HOST_NAME),str(mp4retry.PORT_NUMBER),quote(url))
		mp4retry.XtreamProxy().start()	
		liz = xbmcgui.ListItem(name)
		liz.setArt({'icon':icon, 'thumb':icon})
		if get_kversion() > 19:
			info = liz.getVideoInfoTag()
			info.setTitle(name)
			info.setMediaType('video')
			info.setPlot(description)
		else:
			liz.setInfo(type='Video', infoLabels={'Title': name, 'Plot': description})
		#liz.setProperty('IsPlayable','true')
		liz.setPath(str(url))
		xbmc.Player().play(item=url, listitem=liz)			

	else:
		url = url + headers
		liz = xbmcgui.ListItem(name)
		liz.setArt({'icon':icon, 'thumb':icon})
		if get_kversion() > 19:
			info = liz.getVideoInfoTag()
			info.setTitle(name)
			info.setMediaType('video')
			info.setPlot(description)
		else:
			liz.setInfo(type='Video', infoLabels={'Title': name, 'Plot': description})
		if not dns_unblock == 'true':
			liz.setProperty('IsPlayable','true')
		liz.setPath(str(url))
		if not dns_unblock == 'true':
			xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, liz)
		else:
			xbmc.Player().play(item=url, listitem=liz)

def searchdialog():
	search = control.inputDialog(heading='Search '+ADDON_NAME+':')
	if search=="":
		return
	else:
		return search


### alterar settings
def settingsmenu():
	if xbmcaddon.Addon().getSetting('meta')=='true':
		META = '[B][COLOR lime]ON[/COLOR][/B]'
	else:
		META = '[B][COLOR red]OFF[/COLOR][/B]'
	if xbmcaddon.Addon().getSetting('hidexxx')=='true':
		xxx = '[B][COLOR lime]ON[/COLOR][/B]'
	else:
		xxx = '[B][COLOR red]OFF[/COLOR][/B]'
	# if xbmcaddon.Addon().getSetting('f4m')=='true':
	# 	f4m_ = '[B][COLOR lime]ON[/COLOR][/B]'
	# else:
	# 	f4m_ = '[B][COLOR red]OFF[/COLOR][/B]'	
	if xbmcaddon.Addon().getSetting('dns_unblock')=='true':
		unblock = '[B][COLOR lime]ON[/COLOR][/B]'
	else:
		unblock = '[B][COLOR red]OFF[/COLOR][/B]'				
	#tools.addDir('Edit Advanced Settings','ADS',10,icon,background,'')
	tools.addDir('DNS UNBLOCK is %s'%unblock,'DNS_UNBLOCK',10,icon,background,unblock)		
	tools.addDir('META is %s'%META,'META',10,icon,background,META)
	tools.addDir('Hide Adult Content is %s'%xxx,'XXX',10,icon,background,xxx)
	tools.addDir('Log Out','LO',10,icon,background,'')

def addonsettings(url,description):
	url	 = buildcleanurl(url)
	if	 url =="clearcache":
		tools.clear_cache()
	elif url =="AS":
		xbmc.executebuiltin('Addon.OpenSettings(%s)'% ADDON_ID)
	elif url =="ADS":
		dialog = xbmcgui.Dialog().select('Edit Advanced Settings', ['Open AutoConfig','Enable Fire TV Stick AS','Enable Fire TV AS','Enable 1GB Ram or Lower AS','Enable 2GB Ram or Higher AS','Enable Nvidia Shield AS','Disable AS'])
		if dialog==0:
			advancedsettings('auto')
		elif dialog==1:
			advancedsettings('stick')
			tools.ASln()
		elif dialog==2:
			advancedsettings('firetv')
			tools.ASln()
		elif dialog==3:
			advancedsettings('lessthan')
			tools.ASln()
		elif dialog==4:
			advancedsettings('morethan')
			tools.ASln()
		elif dialog==5:
			advancedsettings('shield')
			tools.ASln()
		elif dialog==6:
			advancedsettings('remove')
			xbmcgui.Dialog().ok(ADDON_NAME, 'Advanced Settings Removed')
	elif url =="ADS2":
		dialog = xbmcgui.Dialog().select('Select Your Device Or Closest To', ['Open AutoConfig','Fire TV Stick ','Fire TV','1GB Ram or Lower','2GB Ram or Higher','Nvidia Shield'])
		if dialog==0:
			advancedsettings('auto')
			tools.ASln()
		elif dialog==1:
			advancedsettings('stick')
			tools.ASln()
		elif dialog==2:
			advancedsettings('firetv')
			tools.ASln()
		elif dialog==3:
			advancedsettings('lessthan')
			tools.ASln()
		elif dialog==4:
			advancedsettings('morethan')
			tools.ASln()
		elif dialog==5:
			advancedsettings('shield')
			tools.ASln()
	elif url =="tv":
		dialog = xbmcgui.Dialog().yesno(ADDON_NAME,'Would You like us to Setup the TV Guide for You?')
		if dialog:
			pvrsetup()
			xbmcgui.Dialog().ok(ADDON_NAME, 'PVR Integration Complete, Restart Kodi For Changes To Take Effect')
	elif url =="Itv":
			xbmc.executebuiltin('InstallAddon(pvr.iptvsimple)')
	elif url =="ST":
		speedtest.speedtest()
	elif url =="DNS_UNBLOCK":
		if 'ON' in description:
			xbmcaddon.Addon().setSetting('dns_unblock','false')
			xbmc.executebuiltin('Container.Refresh')
		else:
			xbmcaddon.Addon().setSetting('dns_unblock','true')
			xbmc.executebuiltin('Container.Refresh')
	elif url =="META":
		if 'ON' in description:
			xbmcaddon.Addon().setSetting('meta','false')
			xbmc.executebuiltin('Container.Refresh')
		else:
			xbmcaddon.Addon().setSetting('meta','true')
			xbmc.executebuiltin('Container.Refresh')
	elif url =="XXX":
		if 'ON' in description:
			pas = tools.keypopup('Enter Adult Password:')
			if pas ==control.setting('xxx_pw'):
				xbmcaddon.Addon().setSetting('hidexxx','false')
				xbmc.executebuiltin('Container.Refresh')
		else:
			xbmcaddon.Addon().setSetting('hidexxx','true')
			xbmc.executebuiltin('Container.Refresh')		
	elif url =="LO":
		xbmcaddon.Addon().setSetting('DNS','')
		xbmcaddon.Addon().setSetting('Username','')
		xbmcaddon.Addon().setSetting('Password','')
		xbmc.executebuiltin('XBMC.ActivateWindow(Videos,addons://sources/video/)')
		xbmc.executebuiltin('Container.Refresh')
	elif url =="UPDATE":
		if 'ON' in description:
			xbmcaddon.Addon().setSetting('update','false')
			xbmc.executebuiltin('Container.Refresh')
		else:
			xbmcaddon.Addon().setSetting('update','true')
			xbmc.executebuiltin('Container.Refresh')
	elif url == "RefM3U":
		DP.create(ADDON_NAME, "Please Wait")
		tools.gen_m3u(panel_api, M3U_PATH)
	elif url == "TEST":
		tester()

def adult_set():
	dialog = DIALOG.yesno(ADDON_NAME,'Você gostaria de ocultar o menu Adulto? \nVocê pode editar isso depois na configuração.')
	if dialog:
		control.setSetting('xxx_pwset','true')
		pass
	else:
		control.setSetting('xxx_pwset','false')
		pass
	dialog = DIALOG.yesno(ADDON_NAME,'Gostaria de Ativar Proteção de Conteudo Adulto? \nVocê pode editar isso depois na configuração.')
	if dialog:
		control.setSetting('xxx_pwset','true')
		adultpw = tools.keypopup('Coloque a Senha')
		control.setSetting('xxx_pw',adultpw)
	else:
		control.setSetting('xxx_pwset','false')
		pass

def advancedsettings(device):
	if device == 'stick':
		file = open(os.path.join(advanced_settings, 'stick.xml'))
	elif device =='auto':
		popup.autoConfigQ()
	elif device == 'firetv':
		file = open(os.path.join(advanced_settings, 'firetv.xml'))
	elif device == 'lessthan':
		file = open(os.path.join(advanced_settings, 'lessthan1GB.xml'))
	elif device == 'morethan':
		file = open(os.path.join(advanced_settings, 'morethan1GB.xml'))
	elif device == 'shield':
		file = open(os.path.join(advanced_settings, 'shield.xml'))
	elif device == 'remove':
		os.remove(ADVANCED)
	try:
		read = file.read()
		f = open(ADVANCED, mode='w+')
		f.write(read)
		f.close()
	except:
		pass

def accountinfo():
	# try:
	# 	parse = tools.OPEN_URL(panel_api)
	# except:
	# 	parse = tools.OPEN_URL(player_api)
	try:
		parse = tools.OPEN_URL(player_api)
	except:
		parse = tools.OPEN_URL(panel_api)

	
	expiry	   = parse['user_info']['exp_date']
	if not expiry=="":
		expiry	   = datetime.fromtimestamp(int(expiry)).strftime('%d/%m/%Y - %H:%M')
		expreg	   = re.compile('^(.*?)/(.*?)/(.*?)$',re.DOTALL).findall(expiry)
		for day,month,year in expreg:
			month	  = tools.MonthNumToName(month)
			year	  = re.sub(' -.*?$','',year)
			#expiry	  = month+' '+day+' - '+year
			expiry	  = day+' de '+month+' de '+year
	else:
		expiry = 'Ilimitado'
	max_connection = str(parse['user_info']['max_connections'])
	if max_connection == 'None':
		max_connection = 'Ilimitado'
	status = parse['user_info']['status']
	if status == 'Active':
		status = 'Ativo'
	elif status == 'Trial':
		status = 'Teste'
	tools.addDir('[B][COLOR white]Usuário: [/COLOR][/B] '+parse['user_info']['username'],'','',icon,background,'')
	tools.addDir('[B][COLOR white]Senha: [/COLOR][/B] '+parse['user_info']['password'],'','',icon,background,'')
	tools.addDir('[B][COLOR white]Expira em: [/COLOR][/B] '+expiry,'','',icon,background,'')
	tools.addDir('[B][COLOR white]Status: [/COLOR][/B] %s'%status,'','',icon,background,'')
	tools.addDir('[B][COLOR white]Conexões Atual: [/COLOR][/B] '+ str(parse['user_info']['active_cons']),'','',icon,background,'')
	tools.addDir('[B][COLOR white]Conexões Permitidas: [/COLOR][/B] '+ max_connection,'','',icon,background,'')
	tools.addDir('[B][COLOR white]IP Local: [/COLOR][/B] '+ tools.getlocalip(),'','',icon,background,'')
	tools.addDir('[B][COLOR white]IP Externo: [/COLOR][/B] '+ tools.getexternalip(),'','',icon,background,'')
	tools.addDir('[B][COLOR white]Versão Kodi: [/COLOR][/B] '+str(KODIV),'','',icon,background,'')

def waitasec(time_to_wait,title,text):
	FTGcd = xbmcgui.DialogProgress()
	ret = FTGcd.create(' '+title)
	secs=0
	percent=0
	increment = int(100 / time_to_wait)
	cancelled = False
	while secs < time_to_wait:
		secs += 1
		percent = increment*secs
		secs_left = str((time_to_wait - secs))
		remaining_display = "Still " + str(secs_left) + "seconds left"
		FTGcd.update(percent,text+'\n'+remaining_display)
		xbmc.sleep(1000)
		if (FTGcd.iscanceled()):
			cancelled = True
			break
	if cancelled == True:
		return False
	else:
		FTGcd.close()
		return False

def tester():
	FTG = ''

def pvrsetup():
	correctPVR()
	tools.killxbmc()
	return

def correctPVR():
	choice = DIALOG.yesno(ADDON_NAME, 'Does your provider allow M3U?')
	if choice:
		m3u_do = 'no'
	else:
		DP.create(ADDON_NAME, "Please Wait")
		tools.gen_m3u(panel_api, M3U_PATH)
		m3u_do = 'yes'
	try:
		addon		  = xbmcaddon.Addon(ADDON_ID)
		dns_text	  = addon.getSetting(id='DNS')
		username_text = addon.getSetting(id='Username')
		password_text = addon.getSetting(id='Password')
		PvrEnable	  = '{"jsonrpc":"2.0","method":"Addons.SetAddonEnabled","params":{"addonid":"pvr.demo","enabled":false},"id":1}'
		jsonSetPVR	  = '{"jsonrpc":"2.0", "method":"Settings.SetSettingValue", "params":{"setting":"pvrmanager.enabled", "value":true},"id":1}'
		IPTVon		  = '{"jsonrpc":"2.0","method":"Addons.SetAddonEnabled","params":{"addonid":"pvr.iptvsimple","enabled":true},"id":1}'
		nulldemo	  = '{"jsonrpc":"2.0","method":"Addons.SetAddonEnabled","params":{"addonid":"pvr.demo","enabled":false},"id":1}'
		loginurl	  = dns_text+"/get.php?username=" + username_text + "&password=" + password_text + "&type=m3u_plus&output=ts"
		EPGurl		  = dns_text+"/xmltv.php?username=" + username_text + "&password=" + password_text

		xbmc.executeJSONRPC(PvrEnable)
		xbmc.executeJSONRPC(jsonSetPVR)
		xbmc.executeJSONRPC(IPTVon)
		xbmc.executeJSONRPC(nulldemo)

		FTG = xbmcaddon.Addon('pvr.iptvsimple')
		if m3u_do == 'yes':
			FTG.setSetting(id='m3uPath', value=M3U_PATH)
			FTG.setSetting(id='m3uPathType', value="0")
		else:
			FTG.setSetting(id='m3uUrl', value=loginurl)
		FTG.setSetting(id='epgUrl', value=EPGurl)
		FTG.setSetting(id='m3uCache', value="false")
		FTG.setSetting(id='epgCache', value="false")

		xbmc.executebuiltin("Container.Refresh")
		DIALOG.ok(ADDON_NAME,"PVR Client Updated, Kodi needs to re-launch for changes to take effect, click ok to quit kodi and then please re launch")
		os._exit(1)
	except:
		DIALOG.ok(ADDON_NAME,"PVR Client: Unknown Error or PVR already Set-Up")

def tvguidesetup():
		dialog = DIALOG.yesno(ADDON_NAME,'Would You like '+ADDON_NAME+' to Setup the TV Guide for You?')
		if dialog:
			pvrsetup()
			DIALOG.ok(ADDON_NAME, 'You are all done! \n Restart Kodi For Changes To Take Effect')

def num2day(num):
	if num =="0":
		day = 'monday'
	elif num=="1":
		day = 'tuesday'
	elif num=="2":
		day = 'wednesday'
	elif num=="3":
		day = 'thursday'
	elif num=="4":
		day = 'friday'
	elif num=="5":
		day = 'saturday'
	elif num=="6":
		day = 'sunday'
	return day
	
def extras():
	tools.addDir('Run a Speed Test','ST',10,icon,background,'')
	try:
		#if xbmc.getCondVisibility('System.HasAddon(pvr.iptvsimple)'):
		#	tools.addDir('Setup PVR Guide','tv',10,icon,background,'')
		#if not xbmc.getCondVisibility('System.HasAddon(pvr.iptvsimple)'):
		#	tools.addDir('Install PVR Guide','Itv',10,icon,background,'')
		if os.path.exists(M3U_PATH):
			tools.addDir('Refresh M3U','RefM3U',10,icon,background,'')
	except:pass
	tools.addDir('Clear Cache','clearcache',10,icon,background,'')
	#tools.addDir('Tester','TEST',10,icon,background,'')

params=tools.get_params()
url=None
name=None
mode=None
iconimage=None
description=None
query=None
type=None

try:
	url=urllib.parse.unquote_plus(params["url"])
except:
	pass
try:
	name=urllib.parse.unquote_plus(params["name"])
except:
	pass
try:
	iconimage=urllib.parse.unquote_plus(params["iconimage"])
except:
	iconimage = ''
try:
	mode=int(params["mode"])
except:
	pass
try:
	description=urllib.parse.unquote_plus(params["description"])
except:
	pass
try:
	query=urllib.parse.unquote_plus(params["query"])
except:
	pass
try:
	type=urllib.parse.unquote_plus(params["type"])
except:
	pass

if mode==None or url==None or len(url)<1:
	start('false')

elif mode==1:
	livecategory()
	
elif mode==2:
	Livelist(url)
	
elif mode==3:
	vod(url)
	
elif mode==4:
	#stream_video(url)
	stream_video(url,iconimage)
	
elif mode==5:
	search()
	
elif mode==6:
	accountinfo()
	
elif mode==7:
	tvguide()
	
elif mode==8:
	settingsmenu()
	
elif mode == 9:
    Vodlist(url)	
    
elif mode==10:
	addonsettings(url,description)
	
elif mode==11:
	pvrsetup()
	
elif mode==12:
	catchup()

elif mode==13:
	tvarchive(name,description)
	
# elif mode==14:
# 	listcatchup2()
	
# elif mode==15:
# 	ivueint()
	
elif mode==16:
	extras()
	
elif mode==18:
	series_cats(url)

elif mode==25:
	serieslist(url)
	
elif mode==19:
	series_seasons(url)

elif mode==20:
	season_list(url)

# elif mode=='start':
# 	start(signin)

elif mode=='test':
	tester()

xbmcplugin.endOfDirectory(int(sys.argv[1]))