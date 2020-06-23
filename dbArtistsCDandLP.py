from dbArtistsBase import dbArtistsBase
from dbBase import dbBase
from artistCL import artistCL
from discogsUtils import cdandlpUtils
import urllib
from urllib.parse import quote
from webUtils import getHTML
from fsUtils import isFile
from hashlib import md5


##################################################################################################################
# Base Class
##################################################################################################################
class dbArtistsCDandLP(dbArtistsBase):
    def __init__(self, debug=False):
        self.db     = "CDandLP"
        self.disc   = dbBase(self.db.lower())
        self.artist = artistCL(self.disc)
        self.dutils = cdandlpUtils()
        self.debug  = debug
        
        self.baseURL   = "https://www.cdandlp.com/"
        self.searchURL = "https://www.cdandlp.com/en/search/?"
        
        super().__init__(self.db, self.disc, self.artist, self.dutils, debug=debug)


        
    ##################################################################################################################
    # Artist URL
    ##################################################################################################################
    def getArtistURL(self, artistRef, page=1):
        #print("getArtistURL(",artistRef,")")
        if artistRef.startswith("http"):
            url = artistRef
        else:
            baseURL = self.disc.discogURL
            if artistRef.startswith("/") is True:
                #print("Join", end="\t")
                url     = urllib.parse.urljoin(baseURL, quote(artistRef[1:]))
                #print(url)
            else:
                url     = urllib.parse.urljoin(baseURL, quote(artistRef))
        
        if isinstance(page, int) and page > 1:
            pageURL = "&page={0}".format(page)
            url = "{0}{1}".format(url, pageURL)
        return url

        
    
    ##################################################################################################################
    # Search Functions
    ##################################################################################################################
    def parseSearchArtist(self, artist, data):
        if data is None:
            return None
        
        ## Parse data
        bsdata = getHTML(data)
        
        artistDB  = {}
        
        descrs = bsdata.findAll("div", {"class": "listingDescription"})
        for descr in descrs:
            refs = descr.findAll("a", {"class": "listingTitle"})
            for ref in refs:
                url      = ref.attrs['href']
                fullurl  = "/".join(url.split("/")[:-4])
                fullurl  = "{0}/artist".format(fullurl)
                artistID = self.dutils.getArtistID(fullurl)
                if artistDB.get(fullurl) is None:
                    artistDB[fullurl] = {"N": 0, "ID": artistID}
                artistDB[fullurl]["N"] += 1
        
    
        if self.debug:
            print("Found {0} artists".format(len(artistDB)))
                
        iArtist = 0
        for href, hrefData in artistDB.items():
            iArtist += 1
        
            discID   = hrefData["ID"]
            url      = href
            savename = self.getArtistSavename(discID)

            print(iArtist,'/',len(artistDB),'\t:',discID,'\t',url,'\t',savename)
            
            if isFile(savename):
                continue

            self.downloadArtistURL(url, savename)
            
    
    def getSearchArtistURL(self, artist):
        baseURL = self.baseURL
        url = urllib.parse.urljoin(baseURL, "{0}{1}".format("?q=", quote(artist)))
        return url
    
        
    def searchForArtist(self, artist):
        print("\n\n===================== Searching For {0} =====================".format(artist))
        url = self.getSearchArtistURL(artist)
        if url is None:
            raise ValueError("URL is None!")
                    
        ## Download data
        data, response = self.downloadURL(url)
        if response != 200:
            print("Error downloading {0}".format(url))
            return False

        self.parseSearchArtist(artist, data)