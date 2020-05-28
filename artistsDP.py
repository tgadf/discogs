from fsUtils import setFile, isFile, setDir, isDir, mkDir, mkSubDir, setSubFile
from fsUtils import removeFile
from fileUtils import getBasename, getBaseFilename
from ioUtils import getFile, saveFile, saveJoblib
from webUtils import getWebData, getHTML, getURL
from searchUtils import findExt, findPattern
from timeUtils import clock, elapsed, update
from collections import Counter
from math import ceil
from time import sleep
from time import mktime, gmtime
from artistDP import artistDP
from discogsUtils import datpiffUtils
import urllib
from urllib.parse import quote
from hashlib import md5
import random
from multiArtist import multiartist



class artistsDP():
    def __init__(self, discog, basedir=None):
        self.disc = discog
        self.name = "artists-datpiff"
        
        self.artist = artistDP()
        
        ## MultiArtist
        self.mulArts  = multiartist()                


        
        ## General Imports
        self.getCodeDir          = self.disc.getCodeDir
        self.getArtistsDir       = self.disc.getArtistsDir
        self.getArtistsDBDir     = self.disc.getArtistsDBDir
        self.getDiscogDBDir      = self.disc.getDiscogDBDir
        self.discogsUtils        = datpiffUtils()
        self.discogsUtils.setDiscogs(discog)
        
        self.prevSearches        = {}
        
        self.modVal = self.disc.getMaxModVal
        
        self.artistIDtoRefData = None
        
        self.starterDir = setDir(self.getCodeDir(), self.name)
        if not isDir(self.starterDir):
            print("Creating {0}".format(self.starterDir))
            mkDir(self.starterDir, debug=True)
        
    
    ###############################################################################
    # Artist Data
    ###############################################################################
    def getData(self, ifile):
        info = self.artist.getData(ifile)
        return info
    
    def getFileData(self, artistID):
        ifile = self.getArtistSavename(artistID, 1)
        info  = self.getData(ifile)
        return info
        
    
    ###############################################################################
    # Artist Info
    ###############################################################################
    def getArtistURL(self, artistRef, page=1):
        baseURL = self.disc.discogURL
        url     = urllib.parse.urljoin(baseURL, artistRef)
        return url


        #url = "{0}/discography/all".format(artistRef)
        return artistRef
        
        if artistRef.startswith("http"):
            return artistRef
        else:
            baseURL = self.disc.discogURL
            url     = urllib.parse.urljoin(baseURL, quote(artistRef))
            return url

            
        if artistRef.startswith("/artist/") is False:
            print("Artist Ref needs to start with /artist/")
            return None
        
        baseURL = self.disc.discogURL
        url     = urllib.parse.urljoin(baseURL, quote(artistRef))
        url     = urllib.parse.urljoin(url, "?sort=year%2Casc&limit=500") ## Make sure we get 500 entries)
        if isinstance(page, int) and page > 1:
            pageURL = "&page={0}".format(page)
            url = "{0}{1}".format(url, pageURL)
        return url
    
    
    def getArtistSavename(self, discID, page=1):
        artistDir = self.disc.getArtistsDir()
        modValue  = self.discogsUtils.getDiscIDHashMod(discID=discID, modval=self.disc.getMaxModVal())
        if modValue is not None:
            outdir    = mkSubDir(artistDir, str(modValue))
            if page == 1:
                savename  = setFile(outdir, discID+".p")
            else:
                savename  = setFile(outdir, discID+"-{0}.p".format(page))
                
            return savename
        return None
        
    
    ###############################################################################
    # Artist Downloads
    ###############################################################################
    def downloadURL(self, url, debug=False):
        user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        headers={'User-Agent':user_agent,} 

        if debug:
            print("Now Downloading {0}".format(url))

        request=urllib.request.Request(url,None,headers) #The assembled request
        response = urllib.request.urlopen(request)
        data = response.read() # The data u need
        
        return data, response.getcode()
    
    
    def downloadArtistFromID(self, artistID, artistRef):
        print("Downloading Artist Data for ID [{0}] and Ref [{1}]".format(artistID, artistRef))
        url = self.getArtistURL(artistRef)
        savename = self.getArtistSavename(artistID)
        self.downloadArtistURL(url, savename)
        
        
    def downloadArtistURL(self, url, savename, parse=False, force=False, debug=False, sleeptime=2):
        if isFile(savename):
            if debug:
                print("{0} exists.".format(savename))
            if force is False:
                return False
            else:
                print("Downloading again.")
                  
                    
        ## Download data
        data, response = self.downloadURL(url)
        if response != 200:
            print("Response is {0}. Error downloading {0}".format(response, url))
            return False

        
        ## Parse data to check integrity
        if parse is True:
            info = self.artist.getData(str(data))
            ID = info.ID.ID
            
            if savename.find("/extra/") == -1:
                artistID = getBaseFilename(savename)
            else:
                artistID = getBaseFilename(savename).split("-")[0]
                if ID != artistID:
                    raise ValueError("Problem saving {0} with artistID {1}".format(savename, ID))
                
            if ID != artistID:
                print("  File ID != Artist ID. Renaming to {0}".format(savename))

                savename_test = self.getArtistSavename(ID)
                if force is False and isFile(savename_test):
                    print("{0} exists.".format(savename_test))
                    return False

            
        if force is False and isFile(savename):
            print("{0} exists.".format(savename))
            return True
            
            
        print("Saving {0} (force={1})".format(savename, force))
        saveJoblib(data=data, filename=savename, compress=True)
        print("Done. Sleeping for {0} seconds".format(sleeptime))
        sleep(sleeptime + random.randint(5, 10))
        
        if isFile(savename):
            return True
        else:
            return False
        
        
            
    ################################################################################
    # Download Search Artist (2a)
    ################################################################################
    def searchRateYouDPusicForArtist(self, artist, debug=True, sleeptime=2):
        if self.prevSearches.get(artist) is not None:
            return
        if self.prevSearches.get(artist.upper()) is not None:
            return
        self.prevSearches[artist] = True
        
        
        print("\n\n===================== Searching For {0} =====================".format(artist))
        baseURL = self.disc.discogSearchURL
        
        baseURL = "https://www.datpiff.com/"
        extra   = "mixtapes-search?criteria={0}&sort=relevance".format(quote(artist))

        url = urllib.parse.urljoin(baseURL, extra)
        print("\tSearch URL: {0}".format(url))
                    
        ## Download data
        data, response = self.downloadURL(url)
        if response != 200:
            print("Error downloading {0}".format(url))
            return False

        
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
                
            #artistID = self.discogsUtils.getArtistID(artistName)

            artistDB.append({"ArtistName": artistName, "AlbumName": albumName, "AlbumURL": albumURL})
        

        artistID = self.discogsUtils.getArtistID(artist)
        page     = 1
        savename = self.getArtistSavename(artistID, page)
        while isFile(savename):
            page += 1
            savename = self.getArtistSavename(artistID, page)
        print("Saving {0} new artist media to {1}".format(len(artistDB), savename))
        saveJoblib(data=artistDB, filename=savename, compress=True)

            




    ################################################################################
    # Parse Artist Data (3)
    ################################################################################
    def parseArtistFiles(self, force=False, debug=False):   
        from glob import glob
        
        artDP = artistDP()
        artistDir = self.disc.getArtistsDir()
        
        artistDBData = {}
        
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
                    artistID   = str(self.discogsUtils.getArtistID(artistName))
                    albumID    = str(self.discogsUtils.getArtistID(albumName))
                    modval     = self.discogsUtils.getArtistModVal(artistID)
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
                artDP = artistDP()
                artDP.setData(artistData)
                artistVal = artDP.parse()

                dbData[artistVal.ID.ID] = artistVal
                        
            savename = setFile(artistDBDir, "{0}-DB.p".format(modVal))
            print("Saving {0} artist IDs to {1}".format(len(dbData), savename))
            totalSaves += len(dbData)
            saveJoblib(data=dbData, filename=savename, compress=True)
            
            self.createArtistModValMetadata(modVal=modVal, db=dbData, debug=debug)
            self.createArtistAlbumModValMetadata(modVal=modVal, db=dbData, debug=debug)
            
        print("Saved {0} new artist IDs".format(totalSaves))
        
        
        
    
    ################################################################################
    # Check ArtistDB Files
    ################################################################################ 
    def DPIDFromDB(self, artistID, modValue=None):
        if modValue is None:
            modValue  = self.discogsUtils.getDiscIDHashMod(discID=artistID, modval=self.disc.getMaxModVal())
        artistDBDir = self.disc.getArtistsDBDir()
        dbname  = setFile(artistDBDir, "{0}-DB.p".format(modValue))     
        print("Loading {0}".format(dbname))
        dbdata  = getFile(dbname)
        
        saveVal = False

        if isinstance(artistID, str):
            artistID = [artistID]
        elif not isinstance(artistID, list):
            raise ValueError("Not sure what to do with {0}".format(artistID))
            
        for ID in artistID:
            try:
                del dbdata[ID]
                print("Deleted {0}".format(ID))
                saveVal = True
            except:
                print("Not there...")

            try:
                savename = self.getArtistSavename(ID)
                removeFile(savename)
                print("Removed File {0}".format(savename))
            except:
                print("Not there...")

        if saveVal:
            print("Saving {0}".format(dbname))
            saveFile(idata=dbdata, ifile=dbname)
        else:
            print("No reason to save {0}".format(dbname))

    
    def assertDBModValExtraData(self, modVal):
        
        artistDBDir = self.disc.getArtistsDBDir()
        dbname  = setFile(artistDBDir, "{0}-DB.p".format(modVal))     
        dbdata  = getFile(dbname)
        nerrs = 0
        
        for artistID,artistData in dbdata.items():
            pages = artistData.pages
            if pages.more is True:
                npages = pages.pages
                artistRef = artistData.url.url
                for p in range(2, npages+1):
                    url      = self.getArtistURL(artistRef, p)
                    savename = self.getArtistSavename(artistID, p)
                    if not isFile(savename):
                        self.downloadArtistURL(url=url, savename=savename, force=True, debug=True)
                        sleep(2 + random.randint(5, 10))
                        
            
    def assertDBModValData(self, modVal):
        
        artistDBDir = self.disc.getArtistsDBDir()
        dbname  = setFile(artistDBDir, "{0}-DB.p".format(modVal))     
        dbdata  = getFile(dbname)
        nerrs = 0
        
        if self.artistIDtoRefData is None:
            self.artistIDtoRefData = self.disc.getArtistIDToRefData()
        
        dels = []
        for artistID,artistData in dbdata.items():
            pages = artistData.pages
            if pages.redo is True and False:
                artistRef = artistData.url.url
                url       = self.getArtistURL(artistRef, 1)
                savename  = self.getArtistSavename(artistID, 1)
                self.downloadArtistURL(url=url, savename=savename, force=True, debug=True)

            ID = artistData.ID.ID
            if ID != artistID:

                nerrs += 1

                if "-" in artistID:
                    print("Extra file: {0}".format(artistID))
                    continue
                else:
                    dels.append(artistID)
                    
                    DPsavename = self.getArtistSavename(artistID)


                    ## ID = artistID                    
                    refRef      = self.artistIDtoRefData.get(artistID)
                    if refRef is None:
                        raise ValueError("Ref for ID [{0}] is None!".format(artistID))
                    else:
                        print("ArtistRef:",refRef)
                        urlRef         = self.getArtistURL(refRef)
                        savenameArtRef = self.getArtistSavename(artistID)


                    ## ID = info.ID.ID
                    try:
                        info  = self.getFileData(artistID)
                    except:
                        info  = None

                    if info is not None:
                        try:
                            refIDID      = artistIDtoRefData[info.ID.ID]
                        except:
                            refIDID      = info.url.url
                        print("ArtistID: ",refIDID)
                        urlIDID      = self.getArtistURL(refIDID)
                        savenameIDID = self.getArtistSavename(info.ID.ID)
                    else:
                        refIDID      = None
                        urlIDID      = None
                        savenameIDID = None

                        
                    if isFile(DPsavename):
                        removeFile(DPsavename)


                    if isFile(savenameArtRef):
                        removeFile(savenameArtRef)
                        self.downloadArtistURL(url=urlRef, savename=savenameArtRef, force=True, debug=True)

                    if savenameArtRef != savenameIDID:
                        if isFile(savenameIDID):
                            removeFile(savenameIDID)
                            self.downloadArtistURL(url=urlIDID, savename=savenameIDID, force=True, debug=True)


                    #print(DPsavename,'\t',savenameArtID,'\t',savenameIDID)        
        
        print("Found {0} errors with modVal {1}".format(nerrs, modVal))
        
        dbname  = setFile(artistDBDir, "{0}-DB.p".format(modVal))
        print("Found {0} artist IDs in {1}".format(len(dbdata), dbname))
        
        for artistID in dels:
            print("Deleting {0}".format(artistID))
            try:
                del dbdata[artistID]
            except:
                continue
            
        if len(dels) > 0:
            savename = setFile(artistDBDir, "{0}-DB.p".format(modVal))     
            print("Saving {0} artist IDs to {1}".format(len(dbdata), savename))
            saveJoblib(data=dbdata, filename=savename, compress=True)
        
        
    
    ################################################################################
    # Collect Metadata About Artists (4)
    ################################################################################
    def createArtistModValMetadata(self, modVal, db=None, debug=False):
        if db is None:
            db = self.disc.getArtistsDBModValData(modVal)
    
        artistIDMetadata = {k: [v.artist.name, v.url.url] for k,v in db.items()}
        
        for artistID,artistData in db.items():
            if artistData.profile.variations is not None:
                artistIDMetadata[artistID].append([v2.name for v2 in artistData.profile.variations])
            else:
                artistIDMetadata[artistID].append([artistData.artist.name])
        
        artistDBDir = self.disc.getArtistsDBDir()     
        savename    = setSubFile(artistDBDir, "metadata", "{0}-Metadata.p".format(modVal))
        
        print("Saving {0} new artist IDs name data to {1}".format(len(artistIDMetadata), savename))
        saveJoblib(data=artistIDMetadata, filename=savename, compress=True)
        
        
    def createArtistAlbumModValMetadata(self, modVal, db=None, debug=False):
        if db is None:
            db = self.disc.getArtistsDBModValData(modVal)
        
        artistIDMetadata = {}
        for artistID,artistData in db.items():
            artistIDMetadata[artistID] = {}
            for mediaName,mediaData in artistData.media.media.items():
                albumURLs  = {mediaValues.code: mediaValues.url for mediaValues in mediaData}
                albumNames = {mediaValues.code: mediaValues.album for mediaValues in mediaData}
                artistIDMetadata[artistID][mediaName] = [albumNames, albumURLs]
        
        artistDBDir = self.disc.getArtistsDBDir()     
        savename    = setSubFile(artistDBDir, "metadata", "{0}-MediaMetadata.p".format(modVal))
        
        print("Saving {0} new artist IDs media data to {1}".format(len(artistIDMetadata), savename))
        saveJoblib(data=artistIDMetadata, filename=savename, compress=True)