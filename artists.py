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
from artist import artist
from discogsUtils import discogsUtils
import urllib
from urllib.parse import quote

class artists():
    def __init__(self, discog, basedir=None):
        self.disc = discog
        self.name = "artists"
        
        self.artist = artist()
        
        ## General Imports
        self.getCodeDir          = self.disc.getCodeDir
        self.getArtistsDir       = self.disc.getArtistsDir
        self.getArtistsDBDir     = self.disc.getArtistsDBDir
        self.getDiscogDBDir      = self.disc.getDiscogDBDir
        self.discogsUtils        = discogsUtils()
        
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
    def downloadArtistFromID(self, artistID, artistRef):
        print("Downloading Artist Data for ID [{0}] and Ref [{1}]".format(artistID, artistRef))
        url = self.getArtistURL(artistRef)
        savename = self.getArtistSavename(artistID)
        self.downloadArtistURL(url, savename)
        

    def downloadArtistURL(self, url, savename, parse=True, force=False, debug=False, sleeptime=2):
        if isFile(savename):
            if debug:
                print("{0} exists.".format(savename))
            if force is False:
                return False
            else:
                print("Downloading again.")
                        
        user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        headers={'User-Agent':user_agent,} 

        if debug:
            print("Now Downloading in Artists(): {0}".format(url))
            print("                   Saving as: {0}".format(savename))

        request=urllib.request.Request(url,None,headers) #The assembled request
        response = urllib.request.urlopen(request)
        data = response.read() # The data u need

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
                
            ## Check For Additional Pages
            newPages = self.downloadArtistExtraURL(info)
            print("  Downloaded {0} Additional URLs".format(newPages))

            
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
        
            
    def downloadArtistExtraURL(self, artistData, debug=False):
        newPages = 0
        pages = artistData.pages
        if pages.more is True:
            npages = pages.pages
            artistRef = artistData.url.url
            artistID  = artistData.ID.ID
            print("Downloading an additional {0} URLs for ArtistID {1}".format(npages-1, artistID))

            for p in range(2, npages+1):
                url      = self.getArtistURL(artistRef, p)
                savename = self.getArtistSavename(artistID, p)
                if not isFile(savename):
                    self.downloadArtistURL(url=url, savename=savename, force=True, debug=True)
                    newPages += 1
                    
        return newPages



        
            
    ################################################################################
    # Download Search Artist (2a)
    ################################################################################
    def searchDiscogForArtist(self, artist, debug=True, sleeptime=2):
        if self.prevSearches.get(artist) is not None:
            return
        if self.prevSearches.get(artist.upper()) is not None:
            return
        self.prevSearches[artist] = True
        
        
        print("\n\n===================== Searching For {0} =====================".format(artist))
        baseURL = self.disc.discogSearchURL
        
        url = urllib.parse.urljoin(baseURL, "{0}{1}{2}".format("?q=", quote(artist), "&limit=250&type=artist"))

        
        user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        headers={'User-Agent':user_agent,} 

        sleep(1)

        print("Downloading: {0}".format(url))

        request=urllib.request.Request(url,None,headers) #The assembled request
        response = urllib.request.urlopen(request)
        data = response.read() # The data u need

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
                
        if debug:
            print("Found {0} artists".format(len(artistDB)))
                
        iArtist = 0
        for href, hrefData in artistDB.items():
            iArtist += 1
            if href.startswith("/artist") is False:
                continue
        
            discID   = self.discogsUtils.getArtistID(href)
            url      = self.getArtistURL(href)
            savename = self.getArtistSavename(discID)

            print(iArtist,'/',len(artistDB),'\t:',len(discID),'\t',url)
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
    
    
    def parseArtistModValExtraFiles(self, modVal, debug=False, force=False):
        print("Parsing Artist Extra Files For ModVal {0}".format(modVal))
        artistInfo = artist()

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
            
            currentMedia = sum([len(x) for x in dbdata[artistID].media.media.values()])
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
                
            
            print("File:",j," \tArtist:",artistID,'-->',currentMedia,'to',sum([len(x) for x in dbdata[artistID].media.media.values()]))
            
            
        if saveIt > 0:
            savename = setFile(artistDBDir, "{0}-DB.p".format(modVal))     
            print("Saving {0} new artist media to {1}".format(saveIt, savename))
            saveJoblib(data=dbdata, filename=savename, compress=True)
            
            self.createArtistModValMetadata(modVal=modVal, db=dbdata, debug=debug)
            self.createArtistAlbumModValMetadata(modVal=modVal, db=dbdata, debug=debug)
            
        return saveIt

    
    
    def parseArtistModValFiles(self, modVal, force=False, debug=False):        
        from os import path
        from datetime import datetime, timedelta

        print("Parsing Artist Files For ModVal {0}".format(modVal))
        artistInfo = artist()

        artistDir = self.disc.getArtistsDir()
        maxModVal = self.disc.getMaxModVal()
                    
        artistDBDir = self.disc.getArtistsDBDir()        
        
        dirVal = setDir(artistDir, str(modVal))
        files  = findExt(dirVal, ext='.p')
        dbname = setFile(artistDBDir, "{0}-DB.p".format(modVal))

        
        
        ### Check for recent files
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
    def rmIDFiles(self, artistID):
        print("Removing files artistID {0}".format(artistID))
        savename = self.getArtistSavename(artistID)
        if isFile(savename):
            files = [savename]
        else:
            files = []
        from glob import glob
        from os.path import join
        from fileUtils import getDirname
        files += glob(join(getDirname(savename), "extra", "{0}-*.p".format(artistID)))
        print("Found {0} files to delete.".format(len(files)))
        from fsUtils import removeFile
        for ifile in files:
            removeFile(ifile)
            print("Removed File {0}".format(ifile))

                
    def rmIDsFromDBs(self, artistIDs, modValue=None):
        modvals = {}
        for artistID in artistIDs:
            modValue  = self.discogsUtils.getDiscIDHashMod(discID=artistID, modval=self.disc.getMaxModVal())
            if modvals.get(modValue) is None:
                modvals[modValue] = []
            modvals[modValue].append(artistID)
            
        for modval in modvals.keys():
            dbdata = self.disc.getArtistsDBModValData(modval)
            for artistID in modvals[modval]:
                try:
                    del dbdata[artistID]
                    print("  Removed ArtistID {0}".format(artistID))
                except:
                    print("  Could not remove ArtistID {0}".format(artistID))
                    
            self.disc.saveArtistsDBModValData(modval, dbdata)
                


    def rmIDFromDB(self, artistID, modValue=None):
        print("Trying to remove data from ArtistID {0}".format(artistID))
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

            self.rmIDFiles(ID)

        if saveVal:
            print("Saving {0}".format(dbname))
            saveFile(idata=dbdata, ifile=dbname)
        else:
            print("No reason to save {0}".format(dbname))

            
    
    def assertDBModValExtraData(self, modVal):
        
        artistDBDir = self.disc.getArtistsDBDir()
        dbdata  = self.disc.getArtistsDBModValData(modVal)
        nerrs   = 0
        
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
                        sleep(2)
                        
            
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



        
    def buildMetadata(self, force=False, doAlbums=False):
        start, cmt = clock("Building Artist Metadata DB")
        
        if force is False:
            artistNameToID    = self.disc.getArtistNameToIDData()
            artistNameToIDs   = self.disc.getArtistNameToIDsData()
            artistIDToName    = self.disc.getArtistIDToNameData()        
            artistRefToID     = self.disc.getArtistRefToIDData()
            artistIDToRef     = self.disc.getArtistIDToRefData()
            artistRefToName   = self.disc.getArtistRefToNameData()
            artistNameToRef   = self.disc.getArtistNameToRefData()
            artistNamesToName = {}

        else:
            artistNameToID    = {}
            artistNameToIDs   = {}
            artistIDToName    = {}
            artistRefToID     = {}
            artistIDToRef     = {}
            artistRefToName   = {}
            artistNameToRef   = {}
            artistNamesToName = {}
            

        albumNameToID   = {}
        albumIDToName   = {}
        albumRefToID    = {}
        albumIDToRef    = {}
        albumRefToName  = {}
        albumNameToRef  = {}

        artistIDCoreAlbumIDs   = {}
        artistIDAlbumIDs       = {}
        artistIDCoreAlbumRefs  = {}
        artistIDAlbumRefs      = {}
        artistIDCoreAlbumNames = {}
        artistIDAlbumNames     = {}

        
        core = ["Singles & EPs", "Albums", "Compilations"]
        
        
        artistNames = {}
        artistYears = {}
        artistDBDir = self.disc.getArtistsDBDir()   
        files       = findExt(artistDBDir, ext='.p')
        for i,ifile in enumerate(files):
            if i % 25 == 0 or i == 5:
                print(i,'/',len(files),'\t',elapsed(start, cmt))
            db = getFile(ifile)
            for artistID,artistData in db.items():
                
                #if artistIDToName
                
                years = None
                artist      = artistData.artist.name
                artistName  = self.discogsUtils.getArtistName(artist)
                artistRef   = artistData.url.url
                
                if artist is None or artistName is None or artistRef is None:
                    continue
                
                if artistRefToName.get(artistRef) is None:
                    artistRefToName[artistRef] = artist
                if artistRefToID.get(artistRef) is None:
                    artistRefToID[artistRef] = artistID
                if artistNameToRef.get(artist) is None:
                    artistNameToRef[artist] = artistRef
                if artistNameToID.get(artist) is None:
                    artistNameToID[artist] = artistID
                if artistIDToName.get(artistID) is None:
                    artistIDToName[artistID] = artist
                if artistIDToRef.get(artistID) is None:
                    artistIDToRef[artistID] = artistRef

                
                if artistNames.get(artistName) is None:
                    artistNames[artistName] = {}
                artistNames[artistName][artistID] = 1
                
                if artistNamesToName.get(artistName) is None:
                    artistNamesToName[artistName] = set()
                artistNamesToName[artistName].add(artistName)

                    
                artistVariations = artistData.profile.variations
                
                if False:
                    artistMedia      = artistData.media.media
                    if artistMedia is not None:
                        for mediaName,mediaData in artistMedia.items():
                            if not isinstance(mediaData, list):
                                raise ValueError("MediaData is a {0}".format(type(mediaData)))
                            for mediaValues in mediaData:
                                year = mediaValues.year
                                try:
                                    year = int(year)
                                except:
                                    continue
                                if years is None:
                                    years = [year, year]
                                else:
                                    years[0] = min([year, years[0]])
                                    years[1] = max([year, years[1]])
                        
                if artistVariations is not None:
                    for artistURLData in artistVariations:
                        varname = artistURLData.name
                        if artistNames.get(varname) is None:
                            artistNames[varname] = {}
                        artistNames[varname][artistID] = 1
                        if artistNamesToName.get(varname) is None:
                            artistNamesToName[varname] = set()
                        artistNamesToName[varname].add(artistName)

                        
                ##### Albums For Artists #####
                if doAlbums:
                    artistIDCoreAlbumIDs[artistID]  = []
                    artistIDAlbumIDs[artistID]      = []
                    artistIDCoreAlbumRefs[artistID] = {}
                    artistIDAlbumRefs[artistID]     = {}


                    media = artistData.media.media
                    if media is not None:
                        for mediaName,mediaData in media.items():
                            if not isinstance(mediaData, list):
                                raise ValueError("MediaData is a {0}".format(type(mediaData)))

                            albumKeys = [mediaValues.code for mediaValues in mediaData]
                            albumURLs = {mediaValues.code: mediaValues.url for mediaValues in mediaData}

                            #albumCntr[mediaName] += 1
                            if mediaName in core:
                                artistIDCoreAlbumIDs[artistID] += albumKeys
                                artistIDCoreAlbumRefs[artistID].update(albumURLs)
                            artistIDAlbumIDs[artistID] += albumKeys
                            artistIDAlbumRefs[artistID].update(albumURLs)


                            for mediaValues in mediaData:
                                albumID   = mediaValues.code
                                albumName = mediaValues.album
                                albumRef  = mediaValues.url

                                if albumNameToID.get(albumName) is None:
                                    albumNameToID[albumName] = {}
                                albumNameToID[albumName][albumID] = True

                                if albumNameToRef.get(albumName) is None:
                                    albumNameToRef[albumName] = {}
                                albumNameToRef[albumName][albumRef] = True

                                if albumIDToName.get(albumID) is None:
                                    albumIDToName[albumID] = {}
                                albumIDToName[albumID][albumName] = True

                                if albumIDToRef.get(albumID) is None:
                                    albumIDToRef[albumID] = {}
                                albumIDToRef[albumID][albumRef] = True

                                if albumRefToName.get(albumRef) is None:
                                    albumRefToName[albumRef] = {}
                                albumRefToName[albumRef][albumName] = True

                                if albumRefToID.get(albumRef) is None:
                                    albumRefToID[albumRef] = {}
                                albumRefToName[albumRef][albumID] = True
                                                    
                            

        savenames = {"RefToID": artistRefToID, "NameToID": artistNameToID, "NameToRef": artistNameToRef,
                     "IDToRef": artistIDToRef, "IDToName": artistIDToName, "RefToName": artistRefToName}
        for basename,savedata in savenames.items():
            savename = setFile(self.getDiscogDBDir(), "Artist{0}.p".format(basename))
            print("Saving {0} entries to {1}".format(len(savedata), savename))
            saveFile(ifile=savename, idata=savedata, debug=True)                            
                            
                                                        
        for artistName in artistNames.keys():
            artistNames[artistName] = list(artistNames[artistName].keys())
                        
        for varName in artistNamesToName.keys():
            artistNamesToName[varName] = list(artistNamesToName[varName])
                            
        savename = setFile(self.disc.getDiscogDBDir(), "ArtistVariationNameToIDs.p")
        print("Saving {0} known artists to {1}".format(len(artistNames), savename))
        saveFile(ifile=savename, idata=artistNames, debug=True)

        
        from string import ascii_uppercase, digits, punctuation
        vals = "{0}{1}{2}".format(ascii_uppercase, digits, punctuation)
        asciiToName = {val: [x for x in artistNames.keys() if (x.startswith(val) or x.startswith(val.lower()))] for val in vals}
        savename = setFile(self.disc.getDiscogDBDir(), "ArtistAsciiNames.p")
        print("Saving {0} known artists ascii characters to {1}".format(len(asciiToName), savename))
        saveFile(ifile=savename, idata=asciiToName, debug=True)


        
        if doAlbums:
            artistIDCoreAlbumNames = {}
            for artistID,albumIDs in artistIDCoreAlbumIDs.items():
                artistIDCoreAlbumNames[artistID] = []
                for albumID in albumIDs:
                    albumNames = albumIDToName[albumID]
                    artistIDCoreAlbumNames[artistID] += albumNames

            artistIDAlbumNames = {}
            for artistID,albumIDs in artistIDAlbumIDs.items():
                artistIDAlbumNames[artistID] = []
                for albumID in albumIDs:
                    albumNames = albumIDToName[albumID]
                    artistIDAlbumNames[artistID] += albumNames



            for artistID in artistIDCoreAlbumIDs.keys():
                artistIDCoreAlbumIDs[artistID] = list(set(artistIDCoreAlbumIDs[artistID]))
            for artistID in artistIDAlbumIDs.keys():
                artistIDAlbumIDs[artistID] = list(set(artistIDAlbumIDs[artistID]))

            for artistID in artistIDCoreAlbumNames.keys():
                artistIDCoreAlbumNames[artistID] = list(set(artistIDCoreAlbumNames[artistID]))
            for artistID in artistIDAlbumNames.keys():
                artistIDAlbumNames[artistID] = list(set(artistIDAlbumNames[artistID]))    

            savenames = {"ArtistIDCoreAlbumIDs": artistIDCoreAlbumIDs, "ArtistIDAlbumIDs": artistIDAlbumIDs,
                         "ArtistIDCoreAlbumRefs": artistIDCoreAlbumRefs, "ArtistIDAlbumRefs": artistIDAlbumRefs,
                         "ArtistIDCoreAlbumNames": artistIDCoreAlbumNames, "ArtistIDAlbumNames": artistIDAlbumNames}
            for basename,savedata in savenames.items():
                savename = setFile(self.getDiscogDBDir(), "{0}.p".format(basename))
                print("Saving {0} entries to {1}".format(len(savedata), savename))
                print("  --> There are {0} albums in this file".format(sum([len(v) for k,v in savedata.items()])))
                saveFile(ifile=savename, idata=savedata, debug=True)
                print("")


            savenames = {"RefToID": albumRefToID, "NameToID": albumNameToID, "NameToRef": albumNameToRef,
                         "IDToRef": albumIDToRef, "IDToName": albumIDToName, "RefToName": albumRefToName}
            for basename,savedata in savenames.items():
                savename = setFile(self.getDiscogDBDir(), "ArtistAlbum{0}.p".format(basename))
                print("Saving {0} entries to {1}".format(len(savedata), savename))
                saveFile(ifile=savename, idata=savedata, debug=True)
                print("")        

        
        elapsed(start, cmt)