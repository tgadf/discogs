from dbArtistsBase import dbArtistsBase
from dbBase import dbBase
from artistDP import artistDP
from discogsUtils import datpiffUtils
import urllib
from urllib.parse import quote
from webUtils import getHTML
from fsUtils import isFile
from hashlib import md5


##################################################################################################################
# Base Class
##################################################################################################################
class dbArtistsDatPiff(dbArtistsBase):
    def __init__(self, debug=False):
        self.db     = "DatPiff"
        self.disc   = dbBase(self.db.lower())
        self.artist = artistDP(self.disc)
        self.dutils = datpiffUtils()
        self.debug  = debug
        
        self.baseURL   = "https://www.datpiff.com/"
        self.searchURL = "https://www.datpiff.com/mixtapes-search?"
        
        super().__init__(self.db, self.disc, self.artist, self.dutils, debug=debug)


        
    ##################################################################################################################
    # Artist URL
    ##################################################################################################################
    def getArtistURL(self, artistRef, page=1):
        baseURL = self.baseURL
        url     = urllib.parse.urljoin(baseURL, artistRef)
        return url

        
    
    ##################################################################################################################
    # Search Functions
    ##################################################################################################################
    def parseSearchArtist(self, artist, data):
        if data is None:
            return None
        
        ## Parse data
        bsdata = getHTML(data)
        
        artistDB  = []

        contentdivs = bsdata.findAll("div", {"class": "contentItem"})
        for i,contentdiv in enumerate(contentdivs):
            artistDiv = contentdiv.find("div", {"class": "artist"})
            if artistDiv is None:
                continue
            artistName = artistDiv.text

            albumDiv = contentdiv.find("div", {"class": "title"})
            if albumDiv is None:
                continue
            albumName = albumDiv.text
            try:
                albumURL  = albumDiv.find("a").attrs['href']
            except:
                albumURL  = None
                
            artistDB.append({"ArtistName": artistName, "AlbumName": albumName, "AlbumURL": albumURL})
        

        artistID = self.dutils.getArtistID(artist)
        page     = 1
        savename = self.getArtistSavename(artistID, page)
        while isFile(savename):
            page += 1
            savename = self.getArtistSavename(artistID, page)
        print("Saving {0} new artist media to {1}".format(len(artistDB), savename))
        saveFile(idata=artistDB, ifile=savename)
            
    
    def getSearchArtistURL(self, artist):      
        baseURL = self.baseURL
        extra   = "mixtapes-search?criteria={0}&sort=relevance".format(quote(artist))
        url = urllib.parse.urljoin(baseURL, extra)
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