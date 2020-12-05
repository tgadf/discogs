from dbArtistsBase import dbArtistsBase
from dbBase import dbBase
from artistDC import artistDC
from discogsUtils import discogsUtils
import urllib
from urllib.parse import quote
from webUtils import getHTML
from fsUtils import isFile


##################################################################################################################
# Base Class
##################################################################################################################
class dbArtistsDiscogs(dbArtistsBase):
    def __init__(self, debug=False):
        self.db     = "Discogs"
        self.disc   = dbBase(self.db.lower())
        self.artist = artistDC(self.disc)
        self.dutils = discogsUtils()
        self.debug  = debug
        
        self.baseURL   = "https://www.discogs.com/"
        self.searchURL = "https://www.discogs.com/search/"
        
        super().__init__(self.db, self.disc, self.artist, self.dutils, debug=debug)


        
    ##################################################################################################################
    # Artist URL
    ##################################################################################################################
    def getArtistURL(self, artistRef, page=1, credit=False, unofficial=False):
        if artistRef.startswith("/artist/") is False:
            print("Artist Ref needs to start with /artist/")
            return None
        
        baseURL = self.baseURL
        url     = urllib.parse.urljoin(baseURL, quote(artistRef))
        url     = urllib.parse.urljoin(url, "?sort=year%2Casc&limit=500") ## Make sure we get 500 entries)
        if unofficial is True:
            url     = urllib.parse.urljoin(url, "?type=Unofficial") ## Make sure we get 500 entries)
        if credit is True:
            url     = urllib.parse.urljoin(url, "?type=Credits") ## Make sure we get 500 entries)
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

        h4s = bsdata.findAll("h4")
        
        for ih4,h4 in enumerate(h4s):
            spans = h4.findAll("span")
            ref   = None
            if len(spans) == 0:
                ref = h4.find("a")
            else:
                ref = spans[0].find("a")
                
            if ref is None:
                continue
                
            try:
                href   = ref.attrs.get('href')
                artist = ref.text.strip()
            except:
                print("Could not get artist/href from {0}".format(ref))
                continue
                
            if not href.endswith("?anv="):
                if artistDB.get(href) is None:
                    artistDB[href] = {"N": 0, "Name": artist}
                artistDB[href]["N"] += 1
                
        if self.debug:
            print("Found {0} artists".format(len(artistDB)))
                
        iArtist = 0
        for href, hrefData in artistDB.items():
            iArtist += 1
            if href.startswith("/artist") is False:
                continue
        
            discID   = self.dutils.getArtistID(href)
            url      = self.getArtistURL(href)
            savename = self.getArtistSavename(discID)

            print(iArtist,'/',len(artistDB),'\t:',len(discID),'\t',url)
            if isFile(savename):
                if force is False:
                    print("\t--> Exists.")
                    continue

            self.downloadArtistURL(url, savename, force=force, sleeptime=self.sleeptime)
            
    
    def getSearchArtistURL(self, artist):
        baseURL = self.searchURL        
        url = urllib.parse.urljoin(baseURL, "{0}{1}{2}".format("?q=", quote(artist), "&limit=25&type=artist"))
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