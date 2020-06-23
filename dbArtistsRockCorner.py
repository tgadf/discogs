from dbArtistsBase import dbArtistsBase
from dbBase import dbBase
from artistRC import artistRC
from discogsUtils import rockcornerUtils
import urllib
from urllib.parse import quote
from webUtils import getHTML
from fsUtils import isFile
from hashlib import md5


##################################################################################################################
# Base Class
##################################################################################################################
class dbArtistsRockCorner(dbArtistsBase):
    def __init__(self, debug=False):
        self.db     = "RockCorner"
        self.disc   = dbBase(self.db.lower())
        self.artist = artistRC(self.disc)
        self.dutils = rockcornerUtils()
        self.debug  = debug
        
        self.baseURL   = "https://www.therockcorner.com/"
        self.searchURL = "https://www.therockcorner.com/"
        
        super().__init__(self.db, self.disc, self.artist, self.dutils, debug=debug)


        
    ##################################################################################################################
    # Artist URL
    ##################################################################################################################
    def getArtistURL(self, artistRef, page=1):
        if artistRef.startswith("http"):
            url = artistRef
        else:
            baseURL = self.baseURL
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

        songs = bsdata.findAll("article", {"class": "bgl0"}) + bsdata.findAll("article", {"class": "bgl1"})
        for i,song in enumerate(songs):
            label     = song.find("label")
            if label is None:
                continue
            name      = label.text
            ref       = song.find("a").attrs['href']
            artistURL = "/".join(ref.split("/")[:2])

            #print(name,'\t',url,'\t',artistID)
            if artistDB.get(artistURL) is None:
                artistDB[artistURL] = {"N": 0, "Name": name}
            artistDB[artistURL]["N"] += 1


        if self.debug:
            print("Found {0} artists".format(len(artistDB)))

        iArtist = 0
        for href, hrefData in artistDB.items():
            iArtist += 1

            name     = hrefData["Name"]
            discID   = self.dutils.getArtistID(name)
            url      = self.getArtistURL(href)
            savename = self.getArtistSavename(discID)

            print(iArtist,'/',len(artistDB),'\t:',discID,'\t',url)
            
            if isFile(savename):
                continue

            self.downloadArtistURL(url, savename)
            
    
    def getSearchArtistURL(self, artist):
        baseURL = self.baseURL
        url = urllib.parse.urljoin(baseURL, "{0}{1}".format("search?q=", quote(artist)))
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