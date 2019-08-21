from fsUtils import setFile, isFile, setDir, isDir, mkDir, mkSubDir, setSubDir, removeFile, moveFile
from fileUtils import getBasename, getBaseFilename, getDirBasics, getsize
from ioUtils import getFile, saveFile, saveJoblib
from webUtils import getWebData, getHTML, getURL
from searchUtils import findExt, findPattern, findDirs
from timeUtils import clock, elapsed, update
from collections import Counter
from math import ceil
from time import sleep
from discogsUtils import discogsUtils
from album import album
from artist import artist
import urllib
from urllib.parse import quote

class albums():
    def __init__(self, discog, basedir=None):
        self.disc = discog
        self.name = "albums"
        
        self.artist = artist()
        self.album  = album()

        
        ## General Imports
        self.getCodeDir          = self.disc.getCodeDir
        self.getAlbumsDir        = self.disc.getAlbumsDir
        self.getArtistsDBDir     = self.disc.getArtistsDBDir
        self.getDiscogDBDir      = self.disc.getDiscogDBDir
        self.discogsUtils        = discogsUtils()
        
        self.prevSearches        = {}
        
        self.modVal = self.disc.getMaxModVal
        
        self.starterDir = setDir(self.getCodeDir(), self.name)
        if not isDir(self.starterDir):
            print("Creating {0}".format(self.starterDir))
            mkDir(self.starterDir, debug=True)
        
    
    ###############################################################################
    ### Album Data
    ###############################################################################
    def getData(self, ifile):
        info = self.album.getData(ifile)
        return info
    
    def getFileData(self, artistID):
        ifile = self.getArtistSavename(artistID, 1)
        info  = self.getData(ifile)
        return info
        
        
    ######################################################################
    ### Load Full Artist Data 
    ######################################################################
    def getHeaders(self):
        user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        headers={'User-Agent':user_agent,} 
        return headers
        
    def downloadAlbumURL(self, url):
        headers = self.getHeaders()
        try:
            request = urllib.request.Request(url,None,headers) #The assembled request
            response = urllib.request.urlopen(request)
            data = response.read() # The data u need
        except:
            data = None
        return data
    
    def saveDownloadedAlbumURL(self, albumdata, albumID, artistID, debug=False):
        savename = self.getAlbumSavename(artistID, albumID)
        if debug:
            print("  Saving album data to {0}".format(savename))
        saveJoblib(data=albumdata, filename=savename, compress=True)
            
        
    def downloadAlbumURLData(self, url, savename, artistID, sleeptime=2.5):
        ## Download URL Data
        print("Downloading {0}".format(url))
        albumdata = self.downloadAlbumURL(url)
        if albumdata is None:
            print("No data for {0}".format(url))
            return False
        saveIt = False
        
        ## Parse
        info    = self.album.getData(albumdata)
        albumID = info.code.code
        artists = info.artist.artists
        if artists is not None:
            for artist in artists:
                artistID = artist.ID
                savename = self.getAlbumSavename(artistID, albumID)
                if savename is None:
                    continue
                if not isFile(savename):
                    print("  Saving {0}".format(savename))
                    saveJoblib(data=albumdata, filename=savename, compress=True)
                    saveIt = True
        else:
            if savename is not None and not isFile(savename):
                print("  Saving {0}".format(savename))
                saveJoblib(data=albumdata, filename=savename, compress=True)
                saveIt = True
             
        sleep(sleeptime)
        if saveIt is False:            
            return False
        return True

        
        
    def downloadAlbumModValData(self, modval, mediaTypes=["Albums"], maxAlbums=None, debug=False):
        maxModVal = self.modVal
        
        albumsDir = self.getAlbumsDir()
        
        
        dbname = self.disc.getArtistsDBModValFilename(modVal)
        print("Loading {0}... ".format(dbname), end="")
        dbdata = getFile(dbname, version=3)
        print("Found {0} Artists".format(len(dbdata)))
        
        artistModDir = setSubDir(albumsDir, str(modval))
            
        nArtists = len(dbdata)
        iArtists = 0
        for artistID, artistData in dbdata.items():
            iArtists += 1
            
            print(iArtists,'/',nArtists,'\t:',artistData.ID.ID,'\t',artistData.artist.name)
            artistIDDir = setDir(artistModDir, artistID)
            media = artistData.media.media
            for mediaType, mediaTypeData in media.items():
                if mediaTypes is not None:
                    if mediaType not in mediaTypes:
                        continue
                nget = 0
                print("\t{0} entries of type {1}".format(len(mediaTypeData), mediaType))
                for mediaIDData in mediaTypeData:
                    mediaID     = mediaIDData.code
                    albumName   = mediaIDData.album
                    albumArtist = mediaIDData.artist[0].ID.ID
                    #print("\t\t",mediaID,'\t',albumArtist,'\t',albumName)
                    savename = setFile(artistIDDir, "{0}.p".format(mediaID))
                    if isFile(savename):
                        continue
                    if maxAlbums is not None:
                        if nget >= maxAlbums:
                            break
     
                    baseURL = self.disc.discogURL
                    url = urllib.parse.urljoin(baseURL, quote(mediaIDData.url))
                    self.downloadAlbumURLData(url, savename, artistID)
                    nget += 1
        

    def downloadAlbumsFromArtists(self, mediaTypes=["Albums"], maxAlbums=None, debug=False):
        maxModVal  = self.disc.getMaxModVal()
        #for modVal in ['NAN'] + 
        for modVal in list(range(maxModVal)):
            self.downloadAlbumModValData(modVal, mediaTypes, maxAlbums, debug)
                
        
    
    ###############################################################################
    # Album Info
    ###############################################################################
    def getAlbumURL(self, albumRef, page=1):
        baseURL = self.disc.discogURL
        url     = urllib.parse.urljoin(baseURL, quote(albumRef))
        return url
    
    
    def getAlbumSavename(self, artistID, albumID):
        albumsDir = self.getAlbumsDir()
        modValue  = self.discogsUtils.getDiscIDHashMod(discID=artistID, modval=self.disc.getMaxModVal())
        if modValue is None:
            artistDir = mkSubDir(albumsDir, 'NAN')
            outdir    = mkSubDir(artistDir, 'NAN')
        else:
            artistDir = mkSubDir(albumsDir, str(modValue))
            outdir    = mkSubDir(artistDir, str(artistID))
        savename  = setFile(outdir, albumID+".p")          
        return savename
                
                


    ################################################################################
    # Parse Album Data (3)
    ################################################################################
    def parseAlbumFile(ifile):
        bsdata     = getHTML(get(ifile))
        albumData  = self.parse(bsdata) 
        return albumData
    
    
    
    def parseAlbumModValFiles(self, modVal, force=False, debug=False):
        start, cmt = clock("Parsing Album Files For ModVal {0}".format(modVal))
        albumInfo = album()
        
        albumDir  = self.disc.getAlbumsDir()
        maxModVal = self.disc.getMaxModVal()
                    
        albumDBDir = self.disc.getAlbumsDBDir()        

        dirVal = setDir(albumDir, str(modVal))
        print("  Looking for artist albums in {0}".format(dirVal))

       
        dbname = self.disc.getAlbumsDBModValFilename(modVal)
        if force is True:
            dbdata = {}
        else:
            if isFile(dbname):
                dbdata = getFile(dbname, version=3)
            else:
                print("DB is empty")
                dbdata = {}

        artistDirs = findDirs(dirVal)
        print("  Found {0} artist directories".format(len(artistDirs)))

        saveIt = 0
        for j,artistDir in enumerate(artistDirs):
            artistID = getDirBasics(artistDir)[-1]
            if dbdata.get(artistID) is None:
                dbdata[artistID] = {}

            files = findExt(artistDir, ext='.p')
            if j % 100 == 0 or j == len(artistDirs) - 1:
                print("    Found {0: <3} albums ({1: <5}) in {2}/{3}\t{4}".format(len(files), saveIt, j, len(artistDirs), artistDir))

            if len(files) == 0:
                continue


            for ifile in files:
                if getsize(ifile) < 1000:
                    removeFile(ifile)
                    continue
                albumID = getBaseFilename(ifile)
                if dbdata[artistID].get(albumID) is None:
                    saveIt += 1
                    info   = albumInfo.getData(ifile)
                    code   = info.code.code
                    if code is None:
                        removeFile(ifile)
                        continue
                        
                    if code != albumID:
                        savename = self.getAlbumSavename(artistID, code)
                        if not isFile(savename):
                            print("Moving {0} to {1}".format(ifile, savename))
                            moveFile(ifile, savename)
                            dbdata[artistID][code] = info
                            continue
                        else:
                            removeFile(ifile)
                            continue
                            print(ifile)
                            print(savename)
                            print("rm {0}".format(ifile))
                            print("Code:   {0}".format(code))
                            print("File:   {0}".format(albumID))
                            print("Artist: {0}".format(info.artist))
                            
                            continue
                            #print("IDs:    {0}".format([x[0].ID for x in info.artist]))
                            1/0
                    dbdata[artistID][albumID] = info



        if saveIt > 0:
            savename = self.disc.getAlbumsDBModValFilename(modVal)
            print("Saving {0} new album IDs to {1}".format(saveIt, savename))
            saveJoblib(data=dbdata, filename=savename, compress=True)

        elapsed(start, cmt)
        return saveIt



    def parseAlbumFiles(self, debug=False, force=False):
        totalSaves = 0
        maxModVal  = self.disc.getMaxModVal()        
        for modVal in ['NAN'] + list(range(maxModVal)):
            saveIt = self.parseAlbumModValFiles(modVal, force=force, debug=debug)
            totalSaves += saveIt            
        print("Saved {0} new album IDs".format(totalSaves))
           
        
    
    ################################################################################
    # Find Missing Artists From Albums/Credits
    ################################################################################
    def findMissingArtistsFromAlbums(self, force=False):
        print("Finding Missing Artists From Downloaded Albums")

        artistIDs = self.disc.getArtistIDToNameData()
        
        toget    = Counter()
        togetmap = {}
        for modVal in ['NAN'] + list(range(self.disc.getMaxModVal())):
            db = self.disc.getAlbumsDBModValData(modVal)
            for artistID,artistData in db.items():
                for albumID,albumData in artistData.items():
                    artist = albumData.artist
                    if artist is None:
                        continue
                    for artistInfo in artist.artists:
                        ID  = artistInfo.ID
                        ref = artistInfo.url
                        if ID is not None and artistIDs.get(ID) is None:
                            toget[ID] += 1
                            togetmap[ID] = ref

            print("\t",modVal,'\t',len(toget))
        return {"toget": toget, "togetmap": togetmap}
        

    def findMissingArtistsFromAlbumCredits(self, force=False):
        print("Finding Missing Artists From Downloaded Album Credits")

        artistIDs = self.disc.getArtistIDToNameData()

        toget    = Counter()
        togetmap = {}

        for modVal in ['NAN'] + list(range(self.disc.getMaxModVal())):
            db = self.disc.getAlbumsDBModValData(modVal)
            for artistID,artistData in db.items():
                for albumID,albumData in artistData.items():
                    credits = albumData.credits.credit            
                    for credit,creditData in credits.items():
                        if creditData is None:
                            continue
                        for artist in creditData:
                            artistInfo = artist
                            ID  = artistInfo.ID
                            ref = artistInfo.url
                            if ID is not None and artistIDs.get(ID) is None:
                                toget[ID] += 1
                                togetmap[ID] = ref
            print(modVal,'\t',len(toget))        
        return {"toget": toget, "togetmap": togetmap}
        
        
        
    
    ################################################################################
    # Collect Metadata About Artists (4)
    ################################################################################
    def buildMetadata(self, force=False):
        start, cmt = clock("Building Album Metadata DB")
            
        if force is False:
            albumNameToID      = self.disc.getAlbumNameToIDData()
            albumIDToName      = self.disc.getAlbumIDToNameData()        
            albumRefToID       = self.disc.getAlbumRefToIDData()
            albumIDToRef       = self.disc.getAlbumIDToRefData()
            albumRefToName     = self.disc.getAlbumRefToNameData()
            albumNameToRef     = self.disc.getAlbumNameToRefData()
            albumIDToArtistID  = self.disc.getAlbumIDToNameData()        

        else:
            albumNameToID      = {}
            albumIDToName      = {}
            albumRefToID       = {}
            albumIDToRef       = {}
            albumRefToName     = {}
            albumNameToRef     = {}            
            albumIDToArtistID  = {}

        
        albumDBDir = self.disc.getAlbumsDBDir()   
        files       = findExt(albumDBDir, ext='.p')  
        for i,ifile in enumerate(files):
            if i % 25 == 0 or i == 5:
                print(i,'/',len(files),'\t',elapsed(start, cmt))
            db = getFile(ifile)
            for artistID,artistData in db.items():
                for albumID,albumData in artistData.items():
                    
                    albumRef     = albumData.url.url
                    albumName    = albumData.album.name
                    albumArtists = albumData.artist
                    
                    #print(albumRef,albumName,albumArtists.artists)
                    #1/0
                
                    if albumRefToName.get(albumRef) is None:
                        albumRefToName[albumRef] = albumName
                    if albumRefToID.get(albumRef) is None:
                        albumRefToID[albumRef]   = albumID
                    if albumIDToName.get(albumID) is None:
                        albumIDToName[albumID]   = albumName
                    if albumIDToRef.get(albumID) is None:
                        albumIDToRef[albumID]    = albumRef
                    if albumNameToRef.get(albumName) is None:
                        albumNameToRef[albumName] = {}
                    if albumNameToRef[albumName] is None:
                        albumNameToRef[albumName][albumRef] = True
                    if albumNameToID.get(albumName) is None:
                        albumNameToID[albumName] = {}
                    if albumNameToID[albumName].get(albumID) is None:
                        albumNameToID[albumName][albumID] = True

                    if albumArtists is not None:
                        if albumIDToArtistID.get(albumID) is None:
                            albumIDToArtistID[albumID] = [albumArtist.ID for albumArtist in albumArtists.artists]

        savenames = {"RefToID": albumRefToID, "NameToID": albumNameToID, "NameToRef": albumNameToRef,
                     "IDToRef": albumIDToRef, "IDToName": albumIDToName, "RefToName": albumRefToName}
        for basename,savedata in savenames.items():
            savename = setFile(self.getDiscogDBDir(), "Album{0}.p".format(basename))
            print("Saving {0} entries to {1}".format(len(savedata), savename))
            saveFile(ifile=savename, idata=savedata, debug=True)                            
                                                        
        savename = setFile(self.disc.getDiscogDBDir(), "AlbumIDToArtistID.p")
        print("Saving {0} known artists to {1}".format(len(albumIDToArtistID), savename))
        saveFile(ifile=savename, idata=albumIDToArtistID, debug=True)
        
        elapsed(start, cmt)