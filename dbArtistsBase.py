from fsUtils import setDir, isDir, mkDir, mkSubDir, setFile, isFile, setSubFile
from ioUtils import saveFile, getFile
from fileUtils import getBaseFilename
from searchUtils import findExt
import urllib
from time import sleep, mktime, gmtime


class dbArtistsBase():
    def __init__(self, db, disc, artist, dutils, basedir=None, debug=False):
            
        #######################
        ## General Imports
        #######################
        self.db     = db
        self.disc   = disc
        self.name   = "artists"
        self.artist = artist
        self.dutils = dutils
        self.sleeptime=2
        self.debug  = debug
        
        self.getArtistsDir       = self.disc.getArtistsDir
        self.getArtistsDBDir     = self.disc.getArtistsDBDir
        self.getDiscogDBDir      = self.disc.getDiscogDBDir
        
        self.prevSearches        = {}
        
        self.modVal = self.disc.getMaxModVal
        
        self.artistIDtoRefData = None
            
    
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
    # ModVals
    ###############################################################################
    def getModVals(self):
        return self.disc.getModValList()
        #return [str(x) for x in range(self.disc.getMaxModVal)]
    
    def getModValDirs(self):
        modVals = self.getModVals()
        retval  = [setDir(self.getArtistsDir(), str(modVal)) for modVal in modVals]
        return retval
    
    
    ###############################################################################
    # Download Information
    ###############################################################################
    def getArtistURL(self, artistRef, page=1, credit=False):
        raise ValueError("Override getArtistURL")
    
    def getArtistSavename(self, discID, page=1, credit=False):
        artistDir = self.disc.getArtistsDir()
        modValue  = self.dutils.getDiscIDHashMod(discID=discID, modval=self.disc.getMaxModVal())
        if modValue is not None:
            outdir    = mkSubDir(artistDir, str(modValue))
            if isinstance(page, int) and page > 1:
                outdir = mkSubDir(outdir, "extra")
                savename  = setFile(outdir, discID+"-{0}.p".format(page))
            elif credit is True:
                outdir = mkSubDir(outdir, "credit")
                savename  = setFile(outdir, discID+".p")
            else:
                savename  = setFile(outdir, discID+".p")
                
            return savename
        return None
    
    
    def downloadURL(self, url):
        user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        headers={'User-Agent':user_agent,} 

        if self.debug:
            print("Now Downloading {0}".format(url))

        request=urllib.request.Request(url,None,headers) #The assembled request
        response = urllib.request.urlopen(request)
        data = response.read() # The data u need
        
        return data, response.getcode()


    def downloadArtistFromID(self, artistID, artistRef, force=False):
        if self.debug:
            print("Downloading Artist Data for ID [{0}] and Ref [{1}]".format(artistID, artistRef))
        url = self.getArtistURL(artistRef)
        savename = self.getArtistSavename(artistID)
        retval = self.downloadArtistURL(url, savename, force=force)
        

    ###############################################################################
    # Download Functions
    ###############################################################################
    def downloadArtistURL(self, url, savename, force=False, sleeptime=2):
        if isFile(savename):
            if self.debug:
                print("{0} exists.".format(savename))
            if force is False:
                return False
            else:
                print("Downloading again.")
                  
        ## Download data
        data, response = self.downloadURL(url)
        if response != 200:
            print("Error downloading {0}".format(url))
            return False
            
        print("Saving {0} (force={1})".format(savename, force))
        saveFile(idata=data, ifile=savename)
        print("Done. Sleeping for {0} seconds".format(sleeptime))
        sleep(sleeptime)
        
        if isFile(savename):
            return True
        else:
            return False
    

    def downloadArtistCreditURL(self, artistData, debug=False, force=False):
        artistRef = artistData.url.url
        artistID  = artistData.ID.ID
        print("Downloading credit URL for ArtistID {0}".format(artistID))

        url      = self.getArtistURL(artistRef, credtit=True)
        savename = self.getArtistSavename(artistID, credit=True)
        if not isFile(savename) or force is True:
            retval = self.downloadArtistURL(url=url, savename=savename, force=True, debug=True)
            return retval
        return False
            
    

    def downloadArtistExtraURL(self, artistData, debug=False, force=False):
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
                if not isFile(savename) or force is True:
                    self.downloadArtistURL(url=url, savename=savename, force=True, debug=True)
                    newPages += 1
                    
        return newPages

            
    ################################################################################
    # Search For Artist
    ################################################################################
    def searchForArtist(self, artist):
        raise ValueError("Override searchForArtist")
        

    ################################################################################
    # Parse Artist Data
    ################################################################################
    def getArtistNumAlbums(self, artistData):
        numAlbums = sum([len(x) for x in artistData.media.media.values()])
        return numAlbums
    
    
    def parseArtistFile(ifile):
        bsdata     = getHTML(get(ifile))
        artistData = self.parse(bsdata) 
        return artistData
    
    
    
    def parseArtistModValCreditFiles(self, modVal, dbdata=None, debug=False, force=False):
        print("\t","="*100)
        print("\t","Parsing Artist Credit Files For ModVal {0}".format(modVal))
        artistInfo = self.artist

        artistDir = self.disc.getArtistsDir()
        maxModVal = self.disc.getMaxModVal()
                    
        artistDBDir = self.disc.getArtistsDBDir()        
        
        dirVal = setDir(artistDir, str(modVal))
        dirVal = setDir(dirVal, "credit")
        files  = findExt(dirVal, ext='.p')
        
        if len(files) == 0:
            return dbdata
        print("\t","  Found {0} credit files for ModVal {1}".format(len(files), modVal))

        dbname = setFile(artistDBDir, "{0}-DB.p".format(modVal))
        retdbdata = False

        if force is False:
            if dbdata is None:
                print("\t","  Loaded ", end="")
                dbdata = getFile(dbname, version=3)
                print("\t","{0} artist IDs.".format(len(dbdata)))
            else:
                retdbdata = True
        else:
            print("\t","Forcing Reloads of ModVal={0}".format(modVal))
            print("\t","  Processing {0} files.".format(len(files)))
            dbdata = {}

        saveIt = 0
        
        nArtistMedia = {}
        print("\t","{0} artist IDs.".format(len(dbdata)))
        
        for j,ifile in enumerate(files):
            if force is True:
                if j % 500 == 0:
                    print("\t","\tProcessed {0}/{1} files.".format(j,len(files)))
            if debug:
                print("\t","{0}/{1} -- {2}.".format(j,len(files),ifile))
            
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
                
            if debug:
                print("\t","File:",j," \tArtist:",artistID,'-->',currentMedia,'to',sum([len(x) for x in dbdata[artistID].media.media.values()]))

                
        if retdbdata is True:
            return dbdata
        #if saveAll is False:
        #    return saveIt
                
                
        if saveIt > 0:
            savename = setFile(artistDBDir, "{0}-DB.p".format(modVal))     
            print("\t","Saving {0} new (credit) artist media to {1}".format(saveIt, savename))
            dbNumAlbums = sum([self.getArtistNumAlbums(artistData) for artistData in dbdata.values()])
            print("\t","Saving {0} total (credit) artist media".format(dbNumAlbums))
            saveFile(idata=dbdata, ifile=savename)
            
            self.createArtistModValMetadata(modVal=modVal, db=dbdata, debug=debug)
            self.createArtistAlbumModValMetadata(modVal=modVal, db=dbdata, debug=debug)
            
        return saveIt
    
    
    
    def parseArtistModValExtraFiles(self, modVal, dbdata=None, debug=False, force=False):
        print("\t","="*100)
        print("\t","Parsing Artist Extra Files For ModVal {0}".format(modVal))
        artistInfo = self.artist

        artistDir = self.disc.getArtistsDir()
        maxModVal = self.disc.getMaxModVal()
                    
        artistDBDir = self.disc.getArtistsDBDir()        
        
        dirVal = setDir(artistDir, str(modVal))
        dirVal = setDir(dirVal, "extra")
        files  = findExt(dirVal, ext='.p')
        
        if len(files) == 0:
            return dbdata
        print("\t","  Found {0} extra files for ModVal {1}".format(len(files), modVal))

        dbname = setFile(artistDBDir, "{0}-DB.p".format(modVal))
        retdbdata = False

        if force is False:
            if dbdata is None:
                print("\t","  Loaded ", end="")
                dbdata = getFile(dbname, version=3)
                print("\t","{0} artist IDs.".format(len(dbdata)))
            else:
                retdbdata = True
        else:
            print("\t","Forcing Reloads of ModVal={0}".format(modVal))
            print("\t","  Processing {0} files.".format(len(files)))
            dbdata = {}

        saveIt = 0
        
        nArtistMedia = {}
        print("\t","{0} artist IDs.".format(len(dbdata)))
        
        for j,ifile in enumerate(files):
            if force is True:
                if j % 500 == 0:
                    print("\t","\tProcessed {0}/{1} files.".format(j,len(files)))
            if debug:
                print("\t","{0}/{1} -- {2}.".format(j,len(files),ifile))
            
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
                
            if debug:
                print("\t","File:",j," \tArtist:",artistID,'-->',currentMedia,'to',sum([len(x) for x in dbdata[artistID].media.media.values()]))

                
        if retdbdata is True:
            return dbdata
        #if saveAll is False:
        #    return saveIt
                
                
        if saveIt > 0:
            savename = setFile(artistDBDir, "{0}-DB.p".format(modVal))     
            print("\t","Saving {0} new (extra) artist media to {1}".format(saveIt, savename))
            dbNumAlbums = sum([self.getArtistNumAlbums(artistData) for artistData in dbdata.values()])
            print("\t","Saving {0} total (extra) artist media".format(dbNumAlbums))
            saveFile(idata=dbdata, ifile=savename)
            
            self.createArtistModValMetadata(modVal=modVal, db=dbdata, debug=debug)
            self.createArtistAlbumModValMetadata(modVal=modVal, db=dbdata, debug=debug)
            
        return saveIt

    
    
    def parseArtistModValFiles(self, modVal, force=False, debug=False, doExtra=False):        
        from os import path
        from datetime import datetime, timedelta

        print("-"*100)
        print("Parsing Artist Files For ModVal {0}".format(modVal))
        artistInfo = self.artist

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
            if isKnown is None or recent > lastModified or force is True:
                saveIt += 1
                info   = artistInfo.getData(ifile)
                
                if info.ID.ID != artistID:
                    if debug is False:
                        continue
                    print("ID From Name: {0}".format(artistID))
                    print("ID From File: {0}".format(info.ID.ID))

                    print("File: {0}".format(ifile))
                    print("Info: {0}".format(info.url.get()))
                    continue
                    #1/0
                
                dbdata[artistID] = info

               
        forceSave = False
        if saveIt > 0 and doExtra is True:
            print("\tCalling Extra Parsing")
            dbdata = self.parseArtistModValExtraFiles(modVal, dbdata=dbdata, force=force, debug=debug)
            forceSave = True
            saveIt = len(dbdata)
        

        if saveIt > 0 or forceSave is True:
            savename = setFile(artistDBDir, "{0}-DB.p".format(modVal))     
            print("Saving {0} new artist IDs to {1}".format(saveIt, savename))
            dbNumAlbums = sum([self.getArtistNumAlbums(artistData) for artistData in dbdata.values()])
            print("Saving {0} total artist media".format(dbNumAlbums))
            saveFile(idata=dbdata, ifile=savename)
            
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

    def parseArtistMetadataFiles(self, debug=False):   
        artistDBDir = self.disc.getArtistsDBDir()   
        maxModVal   = self.disc.getMaxModVal()
        for modVal in range(maxModVal):
            savename = setFile(artistDBDir, "{0}-DB.p".format(modVal))     
            dbdata   = getFile(savename)
            self.createArtistModValMetadata(modVal=modVal, db=dbdata, debug=debug)
            self.createArtistAlbumModValMetadata(modVal=modVal, db=dbdata, debug=debug)
                 
        
        
    
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
            modValue  = self.dutils.getDiscIDHashMod(discID=artistID, modval=self.disc.getMaxModVal())
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
            modValue  = self.dutils.getDiscIDHashMod(discID=artistID, modval=self.disc.getMaxModVal())
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
            saveFile(idata=dbdata, ifile=savename)
        
        
    
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
        saveFile(idata=artistIDMetadata, ifile=savename)
        
        
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
        saveFile(idata=artistIDMetadata, ifile=savename)