from dbArtistsBase import dbArtistsBase
from dbBase import dbBase
from artistRM import artistRM
from discogsUtils import rateyourmusicUtils
import urllib
from urllib.parse import quote
from webUtils import getHTML
from fsUtils import isFile
from hashlib import md5


##################################################################################################################
# Base Class
##################################################################################################################
class dbArtistsRateYourMusic(dbArtistsBase):
    def __init__(self, debug=False):
        self.db     = "RateYourMusic"
        self.disc   = dbBase(self.db.lower())
        self.artist = artistRM(self.disc)
        self.dutils = rateyourmusicUtils()
        self.debug  = debug
        
        self.baseURL   = "https://rateyourmusic.com/"
        self.searchURL = "https://rateyourmusic.com/search?"
        
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
    def searchForArtist(self, artist):
        print("\n\n===================== Searching For {0} =====================".format(artist))
        return