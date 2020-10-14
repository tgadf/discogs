from dbArtistsBase import dbArtistsBase
from dbBase import dbBase
from artistDP import artistDP
from discogsUtils import datpiffUtils
import urllib
from urllib.parse import quote
from webUtils import getHTML
from fsUtils import isFile, setDir, setFile, isDir
from hashlib import md5
from ioUtils import saveFile, getFile
from searchUtils import findExt  
from listUtils import getFlatList
from multiArtist import multiartist


##################################################################################################################
# Base Class
##################################################################################################################
class dbArtistsDatPiff(dbArtistsBase):
    def __init__(self, debug=False):
        self.db     = "DatPiff"
        self.disc   = dbBase(self.db.lower())
        self.artist = artistDP(self.disc)
        self.dutils = datpiffUtils()
        self.dutils.setDiscogs(self.disc)
        self.debug  = debug
        
        ## MultiArtist
        self.mulArts  = multiartist()
        
        print("DatPiff ArtistsDir: {0}".format(self.disc.getArtistsDir()))
        if not isDir(self.disc.getArtistsDir()):
            raise ValueError("Could not find artist dir for DatPiff")
        self.knownDir  = setDir(self.disc.getArtistsDir(), "known")
        if not isDir(self.knownDir):
            print("Make sure that Piggy is loaded!!!")
            raise ValueError("Could not find known [{0}] dir for DatPiff".format(self.knownDir))
        self.knownFile = setFile(self.knownDir, "datPiffKnown.p")
        if not isFile(self.knownFile):
            raise ValueError("Known File [{0}] does not exist".format(self.knownFile))
        
        self.baseURL   = "https://www.datpiff.com/"
        self.searchURL = "https://www.datpiff.com/mixtapes-search?"
        
        super().__init__(self.db, self.disc, self.artist, self.dutils, debug=debug)
        
        
    ################################################################################
    # Parse Artist Data
    ################################################################################
    def parseArtistModValFiles(self, modVal=None, force=False):
        raise ValueError("Must call parseArtistFiles() instead for DatPiff")
        
    def parseArtistFiles(self, force=False, debug=False):   
        from glob import glob
        
        artistDir = self.disc.getArtistsDir()
        
        artistDBData = {}
                
        files = findExt(self.knownDir, ext='.p')        
        files = glob("/Volumes/Biggy/Discog/artists-datpiff/*/*.p")
        print("Found {0} downloaded search terms".format(len(files)))
        for i,ifile in enumerate(files):
            if ifile.endswith("datPiffKnown.p"):
                continue
            fileresults = getFile(ifile)
            if debug:
                print(i,'/',len(files),'\t',ifile)
            for j,fileresult in enumerate(fileresults):
                if debug:
                    print("  ",j,'/',len(fileresults))
                mixArtists  = fileresult["ArtistName"]
                albumName   = fileresult["AlbumName"]
                albumURL    = fileresult["AlbumURL"]
                
                mixArtistNames = self.mulArts.getArtistNames(mixArtists)
                mixArtistNames = [x.title() for x in mixArtistNames.keys()]
                
                for artistName in mixArtistNames:
                    artistID   = str(self.dutils.getArtistID(artistName))
                    albumID    = str(self.dutils.getArtistID(albumName))
                    modval     = self.dutils.getArtistModVal(artistID)
                    if artistDBData.get(modval) is None:
                        artistDBData[modval] = {}
                    if artistDBData[modval].get(artistName) is None:
                        artistDBData[modval][artistName] = {"Name": artistName, "ID": artistID, "URL": None, "Profile": None, "Media": []}
                    albumData = {"Artists": mixArtistNames, "Name": albumName, "URL": albumURL, "Code": albumID}
                    artistDBData[modval][artistName]["Media"].append(albumData)

                    
                    
                    
        maxModVal   = self.disc.getMaxModVal()
        artistDBDir = self.disc.getArtistsDBDir()     
        totalSaves  = 0
        for modVal,modvaldata in artistDBData.items():
            dbData = {}
            for artistName, artistData in modvaldata.items():
                self.artist.setData(artistData)
                artistVal = self.artist.parse()
                dbData[artistVal.ID.ID] = artistVal
                        
            savename = setFile(artistDBDir, "{0}-DB.p".format(modVal))
            print("Saving {0} artist IDs to {1}".format(len(dbData), savename))
            totalSaves += len(dbData)
            saveFile(idata=dbData, ifile=savename)
            
            self.createArtistModValMetadata(modVal=modVal, db=dbData, debug=debug)
            self.createArtistAlbumModValMetadata(modVal=modVal, db=dbData, debug=debug)
            
        print("Saved {0} new artist IDs".format(totalSaves))


        
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
    
    
    def findSearchTerms(self, minCnts=25):
        from collections import Counter
        from time import sleep
        from glob import glob

        artistsCntr = Counter()
        known = getFile(self.knownFile)
        
        files  = getFlatList([findExt(dirval, ext='.p') for dirval in self.getModValDirs()])
        for ifile in files:
        #for ifile in glob("/Volumes/Piggy/Discog/artists-datpiff/*/*.p"):
            if ifile.endswith("datPiffKnown.p"):
                continue
            tmp     = getFile(ifile)
            #print(ifile,'\t',len(tmp))
            results = [x["ArtistName"] for x in tmp]
            for artist in results:
                artists = self.mulArts.getArtistNames(artist)
                for artist in artists.keys():
                    key = artist.title()
                    if len(key) > 1 and key not in known:
                        artistsCntr[key] += 1
        searchTerms = [item[0] for item in artistsCntr.most_common() if item[1] >= minCnts]
        print("There are {0} new searches".format(len(searchTerms)))
        return searchTerms
    
        
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
        
        known = getFile(self.knownFile)
        print("  Found {0} previously searched for terms.".format(len(known)))
        known.append(artist)
        saveFile(idata=known, ifile=self.knownFile)

        self.parseSearchArtist(artist, data)