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
from artistRC import artistRC
from discogsUtils import rockcornerUtils
from multiArtist import multiartist
import urllib
from urllib.parse import quote

class artistsRC():
    def __init__(self, discog, basedir=None):
        self.disc = discog
        self.name = "artists-rockcorner"
        
        self.artist = artistRC()
        
        ## General Imports
        self.getCodeDir          = self.disc.getCodeDir
        self.getArtistsDir       = self.disc.getArtistsDir
        self.getArtistsDBDir     = self.disc.getArtistsDBDir
        self.getDiscogDBDir      = self.disc.getDiscogDBDir
        self.discogsUtils        = rockcornerUtils()
        
        self.mulArts             = multiartist()
        
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
    ################################def oarse###############################################
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
    
    
    def getArtistSavename(self, discID, page=1):
        artistDir = self.disc.getArtistsDir()
        modValue  = self.discogsUtils.getDiscIDHashMod(discID=discID, modval=self.disc.getMaxModVal())
        if modValue is not None:
            outdir    = mkSubDir(artistDir, str(modValue))
            if isinstance(page, int) and page > 1:
                outdir = mkSubDir(outdir, "extra")
                savename  = setFile(outdir, discID+"-{0}.p".format(page))
            else:
                savename  = setFile(outdir, discID+".p")
                
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
        sleep(sleeptime)
        
        if isFile(savename):
            return True
        else:
            return False
        
        
            
    ################################################################################
    # Download Search Artist (2a)
    ################################################################################
    def searchRockCornerForArtist(self, artist, debug=True, sleeptime=2):
        if self.prevSearches.get(artist) is not None:
            return
        if self.prevSearches.get(artist.upper()) is not None:
            return
        self.prevSearches[artist] = True
        
        
        print("\n\n===================== Searching For {0} =====================".format(artist))
        baseURL = self.disc.discogSearchURL
        url = urllib.parse.urljoin(baseURL, "{0}{1}".format("search?q=", quote(artist)))
                    

        ## Download data
        data, response = self.downloadURL(url)
        if response != 200:
            print("Error downloading {0}".format(url))
            return False

        
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


        if debug:
            print("Found {0} artists".format(len(artistDB)))

        iArtist = 0
        for href, hrefData in artistDB.items():
            iArtist += 1

            name     = hrefData["Name"]
            discID   = self.discogsUtils.getArtistID(name)
            url      = self.getArtistURL(href)
            savename = self.getArtistSavename(discID)

            print(iArtist,'/',len(artistDB),'\t:',discID,'\t',url)
            
            if isFile(savename):
                continue

            self.downloadArtistURL(url, savename, sleeptime=sleeptime)
                
            




    ################################################################################
    # Parse Artist Data (3)
    ################################################################################
    def parseArtistFile(ifile):
        bsdata     = getHTML(get(ifile))
        artistData = self.parse(bsdata) 
        return artistData
    
    
    def parseArtistModValExtraFiles(self, modVal, debug=False):
        force=False
        print("Parsing Artist Extra Files For ModVal {0}".format(modVal))
        artistInfo = artistRC()

        artistDir = self.disc.getArtistsDir()
        maxModVal = self.disc.getMaxModVal()
                    
        artistDBDir = self.disc.getArtistsDBDir()        
        
        dirVal = setDir(artistDir, str(modVal))
        dirVal = setDir(dirVal, "extra")
        files  = findExt(dirVal, ext='.p')
        
        if len(files) == 0:
            return
        print("  Found {0} extra files for ModVal {1}".format(len(files), modVal))

        dbname = setFile(artistDBDir, "{0}-DB.p".format(modVal))
        
        if force is False:
            print("  Loaded ", end="")
            dbdata = getFile(dbname, version=3)
            print("{0} artist IDs.".format(len(dbdata)))
        else:
            print("Forcing Reloads of ModVal={0}".format(modVal))
            print("  Processing {0} files.".format(len(files)))
            dbdata = {}

        saveIt = 0
        
        nArtistMedia = {}
        
        for j,ifile in enumerate(files):
            if force is True:
                if j % 500 == 0:
                    print("\tProcessed {0}/{1} files.".format(j,len(files)))
                    
            
            info     = artistInfo.getData(ifile)
            artistID = info.ID.ID
            
            #print(artistID,'\t',sum([len(x) for x in dbdata[artistID].media.media.values()]),end="\t")

            keys = list(set(list(info.media.media.keys()) + list(dbdata[artistID].media.media.keys())))
            for k in keys:
                v = info.media.media.get(k)
                if v is None:
                    continue
                iVal  = {v2.code: v2 for v2 in v}
                dVal  = dbdata[artistID].media.media.get(k)
                if dVal is None:
                    Tretval = iVal
                    saveIt += len(iVal)
                else:
                    Tretval = {v2.code: v2 for v2 in dVal}
                    Tretval.update(iVal)
                    saveIt += len(iVal)
                dbdata[artistID].media.media[k] = list(Tretval.values())
                
            print(sum([len(x) for x in dbdata[artistID].media.media.values()]))
            
            
        if saveIt > 0:
            savename = setFile(artistDBDir, "{0}-DB.p".format(modVal))     
            print("Saving {0} new artist media to {1}".format(saveIt, savename))
            saveJoblib(data=dbdata, filename=savename, compress=True)
            
        return saveIt

    
    
    def parseArtistModValFiles(self, modVal, force=False, debug=False):        
        from os import path
        from datetime import datetime, timedelta

        print("Parsing Artist Files For ModVal {0}".format(modVal))
        artistInfo = artistRC()

        artistDir = self.disc.getArtistsDir()
        maxModVal = self.disc.getMaxModVal()
                    
        artistDBDir = self.disc.getArtistsDBDir()        
        
        dirVal = setDir(artistDir, str(modVal))
        files  = findExt(dirVal, ext='.p')
        dbname = setFile(artistDBDir, "{0}-DB.p".format(modVal))

        
        
        ### Check for recent files
        if isFile(dbname):
            lastModified = datetime.fromtimestamp(path.getmtime(dbname))
            now    = datetime.now()
            if force is False:
                numRecent = [ifile for ifile in files if datetime.fromtimestamp(path.getmtime(ifile)) > lastModified]
                numNew    = [ifile for ifile in files if (now-datetime.fromtimestamp(path.getmtime(ifile))).days < 1]
                if len(numRecent) == 0:
                    print("  ===> Found {0} files, but there are no new files to parse so skipping.".format(len(files)))
                    return 0
                else:
                    print("  ===> Found {0} files. There are {1} new files to parse.".format(len(files), len(numRecent)))
        else:
            force = True
            lastModified = datetime.fromtimestamp(mktime(gmtime(0)))

                
        if force is False:
            dbdata = getFile(dbname, version=3)
        else:
            print("Forcing Reloads of ModVal={0}".format(modVal))
            print("  Processing {0} files.".format(len(files)))
            dbdata = {}

        saveIt = 0
        for j,ifile in enumerate(files):
            if force is True:
                if j % 500 == 0:
                    print("\tProcessed {0}/{1} files.".format(j,len(files)))
            artistID = getBaseFilename(ifile)
            isKnown  = dbdata.get(artistID)
            recent   = datetime.fromtimestamp(path.getctime(ifile))
            if isKnown is None or recent > lastModified:
                saveIt += 1
                info   = artistInfo.getData(ifile)
                
                if info.ID.ID is None:
                    print("removeFile(\"{0}\")".format(ifile))
                    removeFile(ifile)
                    continue
                    
                if info.ID.ID != artistID:
                    print("ID From Name: {0}".format(artistID))
                    print("ID From File: {0}".format(info.ID.ID))

                    print("File: {0}".format(ifile))
                    print("Info: {0}".format(info.url.get()))
                    1/0
                
                dbdata[artistID] = info

        if saveIt > 0:
            savename = setFile(artistDBDir, "{0}-DB.p".format(modVal))     
            print("Saving {0} new artist IDs to {1}".format(saveIt, savename))
            saveJoblib(data=dbdata, filename=savename, compress=True)
            
            self.createArtistModValMetadata(modVal=modVal, db=dbdata, debug=debug)
            self.createArtistAlbumModValMetadata(modVal=modVal, db=dbdata, debug=debug)
            
        return saveIt
    

    def parseArtistFiles(self, force=False, debug=False):   
        
        totalSaves = 0
        maxModVal  = self.disc.getMaxModVal()
        for modVal in range(maxModVal):
            saveIt = self.parseArtistModValFiles(modVal, force=force, debug=debug)
            totalSaves += saveIt
            
        print("Saved {0} new artist IDs".format(totalSaves))      
        
        
    
    ################################################################################
    # Check ArtistDB Files
    ################################################################################ 
    def rmIDFromDB(self, artistID, modValue=None):
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

    
    def assertDBModValExtraData(self, modVal, maxPages=None):
        print("assertDBModValExtraData(",modVal,")")
        artistDBDir = self.disc.getArtistsDBDir()
        dbname  = setFile(artistDBDir, "{0}-DB.p".format(modVal))     
        dbdata  = getFile(dbname)
        nerrs = 0
        
        for artistID,artistData in dbdata.items():
            pages = artistData.pages
            if pages.more is True:
                npages = pages.tot
                if maxPages is not None:
                    npages = min([npages, maxPages])
                artistRef = artistData.url.url
                print(artistID,'\t',artistData.artist.name)
                multiValues = self.mulArts.getArtistNames(artistData.artist.name)
                if len(multiValues) > 1:
                    print("\tNot downloading multis: {0}".format(multiValues.keys()))
                    continue
                for p in range(2, npages+1):
                    url      = self.getArtistURL(artistRef, p)
                    savename = self.getArtistSavename(artistID, p)
                    print(artistID,'\t',url,'\t',savename)
                    if not isFile(savename):
                        self.downloadArtistURL(url=url, savename=savename, force=True, debug=True)
                        sleep(3)
                        
            
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
                    
                    rmsavename = self.getArtistSavename(artistID)


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

                        
                    if isFile(rmsavename):
                        removeFile(rmsavename)


                    if isFile(savenameArtRef):
                        removeFile(savenameArtRef)
                        self.downloadArtistURL(url=urlRef, savename=savenameArtRef, force=True, debug=True)

                    if savenameArtRef != savenameIDID:
                        if isFile(savenameIDID):
                            removeFile(savenameIDID)
                            self.downloadArtistURL(url=urlIDID, savename=savenameIDID, force=True, debug=True)


                    #print(rmsavename,'\t',savenameArtID,'\t',savenameIDID)        
        
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