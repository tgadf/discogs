from dbArtistsBase import dbArtistsBase
from dbBase import dbBase
from artistMD import artistMD
from discogsUtils import musicstackUtils
import urllib
from urllib.parse import quote
from webUtils import getHTML
from fsUtils import isFile, setDir
from ioUtils import getFile, saveFile
from searchUtils import findPatternExt
from hashlib import md5



##################################################################################################################
# Base Class
##################################################################################################################
class dbArtistsMusicStack(dbArtistsBase):
    def __init__(self, debug=False):
        self.db     = "MusicStack"
        self.disc   = dbBase(self.db.lower())
        self.artist = artistMD(self.disc)
        self.dutils = musicstackUtils()
        self.debug  = debug
        
        self.baseURL   = "https://www.musicstack.com/"
        self.searchURL = "https://www.musicstack.com/"
        
        super().__init__(self.db, self.disc, self.artist, self.dutils, debug=debug)


        
    ##################################################################################################################
    # Artist URL
    ##################################################################################################################
    def getArtistURL(self, artistRef, page=1):
        baseURL = self.disc.discogURL
        url     = urllib.parse.urljoin(baseURL, artistRef)
        return url

        
    
    ##################################################################################################################
    # Search Functions
    ##################################################################################################################
    def searchForArtist(self, artist):
        print("\n\n===================== Searching For {0} =====================".format(artist))
        return
    
    
    ##################################################################################################################
    # Parse Downloaded Files
    ##################################################################################################################
    def parseDownloadedFiles(self):
        artistDir = self.disc.getArtistsDir()
        dataDir   = setDir(artistDir, "data")
        files     = findPatternExt(dataDir, pattern="Discography and Albums", ext=".htm")
        for ifile in files:
            htmldata = getFile(ifile)
            retval   = self.getData(ifile)
            artistID = retval.ID.ID
            savename = self.getArtistSavename(artistID)
            saveFile(idata=htmldata, ifile=savename, debug=True)