import urllib,urllib2,re,xbmcplugin,xbmcgui,urlresolver,xbmc,xbmcplugin,xbmcgui,xbmcaddon,os
from metahandler import metahandlers
from t0mm0.common.addon import Addon
from t0mm0.common.net import Net
from universal import favorites
from universal import _common as univ_common


#www.thedarewall.com (The Dare TV) - by The_Silencer 2013 v0.1


grab = metahandlers.MetaData(preparezip = False)
addon_id = 'plugin.video.thedaretv'
local = xbmcaddon.Addon(id=addon_id)
daretvpath = local.getAddonInfo('path')
addon = Addon(addon_id, sys.argv)
datapath = addon.get_profile()
art = daretvpath+'/art'
net = Net()
fav = favorites.Favorites('plugin.video.thedaretv', sys.argv)


#Metahandler
def GRABMETA(name,types):
        type = types
        EnableMeta = local.getSetting('Enable-Meta')
        if EnableMeta == 'true':
                if 'Movie' in type:
                        meta = grab.get_meta('movie',name,'',None,None,overlay=6)
                        infoLabels = {'rating': meta['rating'],'duration': meta['duration'],'genre': meta['genre'],'mpaa':"rated %s"%meta['mpaa'],
                          'plot': meta['plot'],'title': meta['title'],'writer': meta['writer'],'cover_url': meta['cover_url'],
                          'director': meta['director'],'cast': meta['cast'],'backdrop_url': meta['backdrop_url'],'tmdb_id': meta['tmdb_id'],'year': meta['year']}
                elif 'tvshow' in type:
                        meta = grab.get_meta('tvshow',name,'','',None,overlay=6)
                        infoLabels = {'rating': meta['rating'],'genre': meta['genre'],'mpaa':"rated %s"%meta['mpaa'],
                              'plot': meta['plot'],'title': meta['title'],'cover_url': meta['cover_url'],
                              'cast': meta['cast'],'studio': meta['studio'],'banner_url': meta['banner_url'],
                              'backdrop_url': meta['backdrop_url'],'status': meta['status']}
        return infoLabels
                
#Main menu
def CATEGORIES():
        addDir('Movies','http://www.thedarewall.com/tv/new-movies',18,'',None,'')
        fav.add_my_fav_directory(img=os.path.join(art,''))
        addDir('Search','http://www.thedarewall.com/tv/',15,'',None,'')

def MOVIES():
        addDir('Latest Updated','http://www.thedarewall.com/tv/new-movies',5,'',None,'')
        addDir('BoxOffice','http://www.thedarewall.com/tv/movie-tags/boxoffice',5,'',None,'')
        #addDir('A-Z','',10,'',None,'')
        addDir('Genres','http://www.thedarewall.com/tv/',9,'',None,'')
        addDir('Search','http://www.thedarewall.com/tv/',15,'',None,'')

#regex for A-Z list
def MOVIEAZ(url):
        match=re.compile('<a href="(.+?)" class="letterFilter ">(.+?)</a>').findall(net.http_GET(url).content)
        for url,name in match:
                        addDir(name,url,5,'',None,'')

#regex for genres movies  
def MOVIEGEN(url):
        data=re.compile('<li class="dropdown"><a href="http://www.thedarewall.com/tv/movies" class="dropdown-toggle"><b class="caret"></b>&nbsp;&nbsp;Movies</a>.+?<ul class="dropdown-menu">(.+?)</ul>.+?</li>',re.DOTALL).findall(net.http_GET(url).content)
        pattern = '<li><a href="(.+?)">(.+?)</a></li>'
        match = re.findall(pattern,str(data))
        for url,name in match:
                        addDir(name,url,5,'',None,'')

#Routine to search for Movies
def SEARCH(url):
        EnableMeta = local.getSetting('Enable-Meta')
        keyb = xbmc.Keyboard('', 'Search The Dare TV for Movies')
        keyb.doModal()
        if (keyb.isConfirmed()):
                search = keyb.getText()
                encode=urllib.quote(search)
                encode = encode.replace('%20', '+')
                print encode
                surl='http://www.thedarewall.com/tv/index.php?menu=search&query='+encode
                #data = net.http_POST(url,{'search' : encode}).content
                match=re.compile('</div>.+?<h5 class=".+?">.+?<a class="link" href="(.+?)" title="(.+?)">',re.DOTALL).findall(net.http_GET(surl).content)  
                for url,name in match:
                        if EnableMeta == 'true':
                               addDir(name.encode('UTF-8','ignore'),url,6,'','Movie','Movies')
                        if EnableMeta == 'false':
                               addDir(name.encode('UTF-8','ignore'),url,6,'',None,'Movies')

#regex for Movies            
def INDEX1(url):
        EnableMeta = local.getSetting('Enable-Meta')
        match=re.compile('</div>.+?<h5 class=".+?">.+?<a class="link" href="(.+?)" title="(.+?)">',re.DOTALL).findall(net.http_GET(url).content)
        nextpage=re.search('<li class=\'current\'>.+?<li><a href="(.+?)">&raquo;</a></li>',(net.http_GET(url).content))
        for url,name in match:
                if EnableMeta == 'true':
                        addDir(name.encode('UTF-8','ignore'),url,6,'','Movie','Movies')
                if EnableMeta == 'false':
                        addDir(name.encode('UTF-8','ignore'),url,6,'',None,'Movies')
        if nextpage:
                url = nextpage.group(1)
                addDir('[B][COLOR yellow]Next Page >>>[/COLOR][/B]',url,5,'',None,'')

#regex for Hoster links
def VIDEOLINKS(url):
        match=re.compile('id="selector(.+?)"><span>(.+?)</span></a>',re.DOTALL).findall(net.http_GET(url).content)
        for click,name in match:
                ONCLICK(url,name,click)

def ONCLICK(url,name,click):
        print click
        match=re.compile('embeds\[(.+?)\] =.+?src="(.+?)"',re.DOTALL).findall(net.http_GET(url).content)
        for embed,url in match:
                print embed
                specialhost = ['iShared','VK']
                print url
                if name not in specialhost:
                        if embed == click:
                                url = url.replace('/embed/','/file/')#switch putlocker & sockshare embed to file
                                addDir(name,url,7,'',None,'')
                else:
                        if embed == click:
                                addDir(name,url,8,'',None,'')
                                
#Routine to resolve host not in metahandlers (VK, iShared)
def SPECIALHOST(url,name):
        #Get VK final links with quality
        if 'VK' in name:
                #fix oid= reversed by javascript
                url = re.sub('oid=(.+?)&', lambda match: "oid=" + match.group(1)[::-1] + "&",url)
                print url
                match720=re.search('url720=(.+?)&amp;',(net.http_GET(url).content))
                match480=re.search('url480=(.+?)&amp;',(net.http_GET(url).content))
                match360=re.search('url360=(.+?)&amp;',(net.http_GET(url).content))
                match260=re.search('url260=(.+?)&amp;',(net.http_GET(url).content))
                match240=re.search('url240=(.+?)&amp;',(net.http_GET(url).content))
                if match720:
                        url = match720.group(1)
                        url = url.replace('amp;', '')
                        addLink('VK Quality : 720',url,'')
                if match480:
                        url = match480.group(1)
                        url = url.replace('amp;', '')
                        addLink('VK Quality : 480',url,'')
                if match360:
                        url = match360.group(1)
                        url = url.replace('amp;', '')
                        addLink('VK Quality : 360',url,'')
                if match260:
                        url = match260.group(1)
                        url = url.replace('amp;', '')
                        addLink('VK Quality : 260',url,'')
                if match240:
                        url = match240.group(1)
                        url = url.replace('amp;', '')
                        addLink('VK Quality : 240',url,'')
                
        #Get iShared final link
        if 'iShared' in name:
                match=re.compile('file:"(.+?)", label: ".+?", type:".+?"').findall(net.http_GET(url).content)
                for url in match:
                        addLink('Play',url,'')

#Pass url to urlresolver
def STREAM(url):
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        streamlink = urlresolver.resolve(urllib2.urlopen(req).url)
        print streamlink
        addLink(name,streamlink,'')

def get_params():
        param=[]
        paramstring=sys.argv[2]
        if len(paramstring)>=2:
                params=sys.argv[2]
                cleanedparams=params.replace('?','')
                if (params[len(params)-1]=='/'):
                        params=params[0:len(params)-2]
                pairsofparams=cleanedparams.split('&')
                param={}
                for i in range(len(pairsofparams)):
                        splitparams={}
                        splitparams=pairsofparams[i].split('=')
                        if (len(splitparams))==2:
                                param[splitparams[0]]=splitparams[1]
                                
        return param

def addLink(name,url,iconimage):
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz,isFolder=False)
        return ok


def addDir(name,url,mode,iconimage,types,favtype):
        ok=True
        type = types
        if type != None:
                infoLabels = GRABMETA(name,types)
        else: infoLabels = {'title':name}
        try: img = infoLabels['cover_url']
        except: img= iconimage
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=img)
        liz.setInfo( type="Video", infoLabels= infoLabels)

        contextMenuItems = []
        contextMenuItems.append(('Movie Information', 'XBMC.Action(Info)'))
        liz.addContextMenuItems(contextMenuItems, replaceItems=False)
        #Universal Favorites
        if 'Movies' in favtype:
                contextMenuItems.append(('Add to Favorites', fav.add_directory(name, u, section_title='Movies')))
                liz.addContextMenuItems(contextMenuItems, replaceItems=True)
        elif 'TV-Shows' in favtype:
                contextMenuItems.append(('Add to Favorites', fav.add_directory(name, u, section_title='TV-Shows')))
                liz.addContextMenuItems(contextMenuItems, replaceItems=True)
        else:
                contextMenuItems.append(('Add to Favorites', fav.add_directory(name, u, section_title='Other Favorites')))
                liz.addContextMenuItems(contextMenuItems, replaceItems=True)
        ####################
        
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok
    
params=get_params()
url=None
name=None
mode=None

try:
        url=urllib.unquote_plus(params["url"])
except:
        pass
try:
        name=urllib.unquote_plus(params["name"])
except:
        pass
try:
        mode=int(params["mode"])
except:
        pass

print "Mode: "+str(mode)
print "URL: "+str(url)
print "Name: "+str(name)


if mode==None or url==None or len(url)<1:
        print ""
        CATEGORIES()
        
elif mode==1:
        MOVIES()

elif mode==2:
        MOVIESAZ()

elif mode==3:
        MOVIESGEN()

elif mode==4:
        TVSHOWS()

elif mode==5:
        print ""+url
        INDEX1(url)

elif mode==6:
        print ""+url
        VIDEOLINKS(url)

elif mode==7:
        print ""+url
        STREAM(url)

elif mode==8:
        print ""+url
        SPECIALHOST(url,name)

elif mode==9:
        print ""+url
        MOVIEGEN(url)

elif mode==10:
        print ""+url
        MOVIEAZ(url)

elif mode==11:
        print ""+url
        ACTORS(url)

elif mode==12:
        print ""+url
        COUNTRIES(url)

elif mode==13:
        ACTORSDIR()

elif mode==14:
        DIRECTORDIR()

elif mode==15:
        print ""+url
        SEARCH(url)

elif mode==16:
        print ""+url
        ACTORSEARCH(url)

elif mode==17:
        print ""+url
        INDEX2(url)
        
elif mode==18:
        MOVIES()

elif mode==19:
        TVSHOWS()
        
elif mode==20:
        print ""+url
        TVGEN(url)

elif mode==21:
        print ""+url
        COUNTRIESTV(url)

elif mode==22:
        print ""+url
        SEARCHTV(url)

elif mode==23:
        print ""+url
        SEASONS(url,name)

elif mode==24:
        print ""+url
        EPISODES(url,name)

elif mode==25:
        print ""+url
        EPISODELINKS(url,name)
        
xbmcplugin.endOfDirectory(int(sys.argv[1]))
