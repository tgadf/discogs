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
from artistAB import artistAB
from discogsUtils import acebootlegsUtils
import urllib
from urllib.parse import quote
from hashlib import md5

class artistsAB():
    def __init__(self, discog, basedir=None):
        self.disc = discog
        self.name = "artists-acebootlegs"
        
        self.artist = artistAB()
        
        ## General Imports
        self.getCodeDir          = self.disc.getCodeDir
        self.getArtistsDir       = self.disc.getArtistsDir
        self.getArtistsDBDir     = self.disc.getArtistsDBDir
        self.getDiscogDBDir      = self.disc.getDiscogDBDir
        self.discogsUtils        = acebootlegsUtils()
        self.discogsUtils.setDiscogs(self.disc)
        
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
    
    
    def getMainSavename(self):
        artistDir = self.disc.getArtistsDir()
        savename  = setFile(artistDir, "main.p")
        return savename
    
    
    def getArtistSavename(self, discID, page=1):
        artistDir = self.disc.getArtistsDir()
        modValue  = self.discogsUtils.getDiscIDHashMod(discID=discID, modval=self.disc.getMaxModVal())
        if modValue is not None:
            outdir    = mkSubDir(artistDir, str(modValue))
            if isinstance(page, int) and page > 1:
                outdir = mkSubDir(outdir, "extra")
                savename  = setFile(outdir, discID+"-{0}.p".format(page))
            else:
                savename  = setFile(outdir, "{0}.p".format(discID))
                
            return savename
        return None
        
    
    ###############################################################################
    # Artist Downloads
    ###############################################################################
    def downloadMain(self, force=False, debug=False, sleeptime=2):
        url = "https://ace-bootlegs.com"
        
        ## Download data
        data, response = self.downloadURL(url)
        if response != 200:
            print("Response is {0}. Error downloading {0}".format(response, url))
            return False

        savename = self.getMainSavename()
            
        print("Saving {0} (force={1})".format(savename, force))
        saveJoblib(data=data, filename=savename, compress=True)
        print("Done. Sleeping for {0} seconds".format(sleeptime))
        sleep(sleeptime)
        
        if isFile(savename):
            return True
        else:
            return False
        
        
    def downloadMainArtists(self, force=False, debug=False, sleeptime=2):        
        savename = self.getMainSavename()
        
        ## Parse data
        bsdata = getHTML(savename)        
        artistDB  = {}
        
        
        ## Find and Download Artists
        categories = bsdata.find("div", {"class": "sidebar-widget widget_categories"})
        if categories is None:
            raise ValueError("Cannot find categories!")
        uls = categories.findAll("ul")
        for ul in uls:
            lis = ul.findAll("li")
            for i, li in enumerate(lis):
                try:
                    catitem = li.attrs["class"][1]
                except:
                    raise ValueError("Cannot find list class item: {0}".format(li))
                ref  = li.find("a")
                if ref is None:
                    raise ValueError("Cannot find list link!")
                try:
                    href = ref.attrs['href']
                except:
                    raise ValueError("Cannot find list href!")

                # check for artist
                artistName = href.split('/')[-2]
                try:
                    int(artistName)
                    continue
                except:
                    if artistName.find("parent-category-ii") == -1:
                        pass
                    else:
                        continue

                # get artist ID
                artistID = catitem.split('-')[-1]
                try:
                    int(artistID)
                except:
                    continue


                if force is False and isFile(savename):
                    print("{0} exists.".format(savename))
                    continue
            
                url = href
                savename = self.getArtistSavename(artistID)
                print(i,'\t',artistID,'\t',artistName,'\t',savename)
                self.downloadArtistURL(url=url, savename=savename, parse=False)

                
        
        
        
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
    def searchAceBootlegsForArtist(self, artist, debug=True, sleeptime=2):
        print("This is not possible. Returning")
        return 



    ################################################################################
    # Parse Artist Data (3)
    ################################################################################
    def parseArtistFiles(self, force=False, debug=False):           
        dbdata = {}
        from glob import glob
        
        artAB = artistAB()
        artistDir = self.disc.getArtistsDir()
        
        for ifile in glob("/Volumes/Biggy/Discog/artists-acebootlegs/*/*.p"):
            print(ifile)
            info       = artAB.getData(ifile)
            err        = info.err
            if isinstance(err, str):
                continue
            artistName = info.artist.name
            artistID   = str(self.discogsUtils.getArtistID(artistName))
            modval     = self.discogsUtils.getArtistModVal(artistID)

            if dbdata.get(modval) is None:
                dbdata[modval] = {}
            if dbdata[modval].get(artistID) is None:
                dbdata[modval][artistID] = info
            else:
                keys = list(set(list(info.media.media.keys()) + list(dbdata[modval][artistID].media.media.keys())))
                for k in keys:
                    v = info.media.media.get(k)
                    if v is None:
                        continue
                    iVal  = {v2.code: v2 for v2 in v}
                    dVal  = dbdata[modval][artistID].media.media.get(k)
                    if dVal is None:
                        Tretval = iVal
                    else:
                        Tretval = {v2.code: v2 for v2 in dVal}
                        Tretval.update(iVal)
                    dbdata[modval][artistID].media.media[k] = list(Tretval.values())

       


        maxModVal   = self.disc.getMaxModVal()
        artistDBDir = self.disc.getArtistsDBDir()        

        totalSaves  = 0
        for modVal in sorted(dbdata.keys()):
            modValData = dbdata[modVal]
            dirVal = setDir(artistDir, str(modVal))
            savename = setFile(artistDBDir, "{0}-DB.p".format(modVal))
            print("Saving {0} artist IDs to {1}".format(len(modValData), savename))
            totalSaves += len(modValData)
            saveJoblib(data=modValData, filename=savename, compress=True)
            
            self.createArtistModValMetadata(modVal=modVal, db=modValData, debug=debug)
            self.createArtistAlbumModValMetadata(modVal=modVal, db=modValData, debug=debug)
            
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
            db = self.disc.getArtistsDBModValDat
            a(modVal)
    
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