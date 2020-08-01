from dbArtistsBase import dbArtistsBase
from dbBase import dbBase
from artistAM import artistAM
from discogsUtils import allmusicUtils
import urllib
from urllib.parse import quote
from webUtils import getHTML
from fsUtils import isFile


##################################################################################################################
# Base Class
##################################################################################################################
class dbArtistsAllMusic(dbArtistsBase):
    def __init__(self, debug=False):
        self.db     = "AllMusic"
        self.disc   = dbBase(self.db.lower())
        self.artist = artistAM(self.disc)
        self.dutils = allmusicUtils()
        self.debug  = debug
        super().__init__(self.db, self.disc, self.artist, self.dutils, debug=debug)
        
        self.baseURL   = "https://www.allmusic.com/"        
        self.searchURL = "https://www.allmusic.com/search/"

        
    ##################################################################################################################
    # Artist URL
    ##################################################################################################################
    def getArtistURL(self, artistRef, page=1):
        url = "{0}/discography/all".format(artistRef)
        return url
        
        if artistRef.startswith("http"):
            return artistRef
        else:
            baseURL = self.baseURL
            url     = urllib.parse.urljoin(baseURL, quote(artistRef))
            return url

            
        if artistRef.startswith("/artist/") is False:
            print("Artist Ref needs to start with /artist/")
            return None
        
        baseURL = self.baseURL
        url     = urllib.parse.urljoin(baseURL, quote(artistRef))
        url     = urllib.parse.urljoin(url, "?sort=year%2Casc&limit=500") ## Make sure we get 500 entries)
        if isinstance(page, int) and page > 1:
            pageURL = "&page={0}".format(page)
            url = "{0}{1}".format(url, pageURL)
        return url

        
    
    ##################################################################################################################
    # Search Functions
    ##################################################################################################################
    def parseSearchArtist(self, artist, data, force=False):
        if data is None:
            return None
        
        ## Parse data
        bsdata = getHTML(data)
        
        artistDB  = {}
        
        uls = bsdata.findAll("ul", {"class": "search-results"})
        for ul in uls:
            lis = ul.findAll("li", {"class": "artist"})
            for li in lis:
                divs = li.findAll("div", {"class": "name"})
                for div in divs:
                    link     = div.find("a")
                    href     = link.attrs['href']
                    tooltip  = link.attrs['data-tooltip']
                    try:
                        from json import loads
                        tooltip = loads(tooltip)
                        artistID = tooltip['id']
                    except:
                        artistID = None
            
                    if artistDB.get(href) is None:
                        artistDB[href] = {"N": 0, "Name": artist}
                    artistDB[href]["N"] += 1
        
    
        if self.debug:
            print("Found {0} artists".format(len(artistDB)))
                
        iArtist = 0
        for href, hrefData in artistDB.items():
            iArtist += 1
        
            discID   = self.dutils.getArtistID(href)
            url      = self.getArtistURL(href)
            savename = self.getArtistSavename(discID)

            print(iArtist,'/',len(artistDB),'\t:',discID,'\t',url)
            
            if isFile(savename):
                if force is False:
                    continue

            self.downloadArtistURL(url, savename, force=force)
            
    
    def getSearchArtistURL(self, artist):
        baseURL = self.searchURL        
        url = urllib.parse.urljoin(baseURL, "{0}{1}".format("artists/", quote(artist)))                  
        return url
    
        
    def searchForArtist(self, artist, force=False):
        print("\n\n===================== Searching For {0} =====================".format(artist))
        url = self.getSearchArtistURL(artist)
        if url is None:
            raise ValueError("URL is None!")
                    
        ## Download data
        data, response = self.downloadURL(url)
        if response != 200:
            print("Error downloading {0}".format(url))
            return False

        self.parseSearchArtist(artist, data, force)