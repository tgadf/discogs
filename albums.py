from fsUtils import setFile, isFile, setDir, isDir, mkDir, mkSubDir, setSubDir, removeFile, moveFile, setSubFile
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
            
        
    def downloadAlbumURLData(self, url, savename, artistID, sleeptime=1.75):
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
            print("  Found album code {0} with {1} artists".format(albumID, len(artists)))
        else:
            print("  Found album code {0}".format(albumID))
            
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
                    print("  Exists {0}".format(savename))
        else:
            if savename is not None and not isFile(savename):
                print("  Saving {0}".format(savename))
                saveJoblib(data=albumdata, filename=savename, compress=True)
                saveIt = True
            else:
                print("  Exists {0}".format(savename))
             
        print("  Done and sleeping...")
        sleep(sleeptime)
        if saveIt is False:            
            return False
        return True
    
    
    def downloadAlbumFromArtistData(self, artistID, artistData, iArtists=None, mediaTypes=["Albums"], maxAlbums=None, knownAlbums=None, debug=False):
        if knownAlbums is None:
            knownAlbums = self.disc.getDiagnosticAlbumIDs()
        nKnown = len(knownAlbums)
            
        albumsDir    = self.getAlbumsDir()        
        modVal       = self.discogsUtils.getDiscIDHashMod(discID=artistID, modval=self.disc.getMaxModVal())
        artistModDir = setSubDir(albumsDir, str(modVal))
        artistIDDir  = setDir(artistModDir, artistID)
        nDownloads   = 0

        downloadedFiles = findExt(artistIDDir, ext=".p")
        #print(type(artistData))
        #print(type(artistData.media))
        #print(type(artistData.media.media))
        allFiles        = sum([len(x) for x in artistData.media.media.values()])

        
        print("\n","="*30,"Artist ID --- {0}".format(artistID),"="*30)
        print("  ",len(downloadedFiles),'/',allFiles,'  ','\t',nKnown,'\t',artistData.ID.ID,'\t',artistData.artist.name)

        media = artistData.media.media
        for mediaType, mediaTypeData in media.items():
            if mediaTypes is not None:
                if mediaType not in mediaTypes:
                    continue

            nget = 0        
            toGetMediaIDs = {mediaIDData.code: mediaIDData.url for mediaIDData in mediaTypeData}

            toGet = {}
            known = {}
            print("\t","Getting {0} media IDs".format(len(toGetMediaIDs)))
            for albumID,albumURL in toGetMediaIDs.items():
                savename = self.getAlbumSavename(artistID, albumID)                    
                if not isFile(savename):
                    toGet[albumURL] = savename
                else:
                    known[albumURL] = savename

            nToGet = len(toGetMediaIDs)-len(toGet)
            #print("\tDownloaded {0}/{1} entries of type {2}".format(nToGet, len(toGetMediaIDs), mediaType))
            for albumURL,savename in toGet.items():
                if maxAlbums is not None:
                    if len(known) >= maxAlbums:
                        break               
                known[albumURL] = savename

                baseURL = self.disc.discogURL
                url = urllib.parse.urljoin(baseURL, quote(albumURL))
                if knownAlbums.get(url) is True:
                    print("\t  Already known and previously downloaded.")
                    continue
                retval = self.downloadAlbumURLData(url, savename, artistID)
                nDownloads += 1

                if retval is False:
                    knownAlbums[url] = True
                    if len(knownAlbums) % 50 == 0:
                        print("!"*100)
                        print("Saving {0} known albums...".format(len(knownAlbums)))
                        print("!"*100)
                        self.disc.saveDiagnosticAlbumIDs(knownAlbums)
                        sleep(2)



        if len(knownAlbums) > nKnown:
            print("!"*100)
            print("Saving {0} known albums...".format(len(knownAlbums)))
            print("!"*100)
            self.disc.saveDiagnosticAlbumIDs(knownAlbums)
        return nDownloads
        
        
    def downloadAlbumModValData(self, modVal, mediaTypes=["Albums"], maxAlbums=None, debug=False):
        
        from datetime import datetime as dt
        
        maxModVal = self.modVal
        
        albumsDir = self.getAlbumsDir()
        
        
        dbname = self.disc.getArtistsDBModValFilename(modVal)
        print("Loading {0}... ".format(dbname), end="")
        dbdata = getFile(dbname, version=3)
        print("Found {0} Artists".format(len(dbdata)))
        
        artistModDir = setSubDir(albumsDir, str(modVal))        
            
        nArtists = len(dbdata)
        iArtists = 0
        
        startTime  = dt.now()
        nDownloads = 0
        
        knownAlbums = self.disc.getDiagnosticAlbumIDs()
        
        for artistID, artistData in dbdata.items():
            iArtists   += 1
            nDownloads += self.downloadAlbumFromArtistData(artistID, artistData, iArtists, mediaTypes, maxAlbums, knownAlbums, debug)
            if nDownloads % 5 == 0 and nDownloads > 0:
                deltaT = ((dt.now() - startTime).seconds)/60.0
                if deltaT <= 0:
                    deltaT = 1
                rate = nDownloads / deltaT
                print("")
                print("=============================================================================================")
                print("== Download Rate: {0} / {1} = {2}".format(nDownloads, round(deltaT,1), round(rate,1)))
                print("=============================================================================================")
                print("")
    
        
        

    def downloadAlbumsFromArtists(self, mediaTypes=["Albums"], maxAlbums=None, debug=False, rev=False, rand=False):
        maxModVal  = self.disc.getMaxModVal()
        #for modVal in ['NAN'] + 
        if rand:
            from random import shuffle
            modList = list(range(maxModVal))
            shuffle(modList)
            for modVal in modList:
                self.downloadAlbumModValData(modVal, mediaTypes, maxAlbums, debug)
        elif rev:
            for modVal in list(reversed(list(range(maxModVal)))):
                self.downloadAlbumModValData(modVal, mediaTypes, maxAlbums, debug)
        else:
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
            print("  Forcing a parse of all files.")
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
            
            self.createAlbumModValMetadata(modVal, db=dbdata)

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

        files = self.disc.getAlbumsArtistMetadataFiles()
        for ifile in files:
            db = getFile(ifile)
            for artistData in db.values():
                try:
                    artists = artistData["ArtistsURL"]
                    for artistID,artistURL in artists.items():
                        if artistID is not None and artistIDs.get(artistID) is None:
                            toget[artistID] += 1
                            togetmap[artistID] = artistURL
                except:
                    continue

            print("\t",ifile,'\t',len(toget))
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
    def createAlbumModValMetadata(self, modVal, db=None, debug=False):
        if db is None:
            db = self.disc.getAlbumsDBModValData(modVal)
            
        artistIDMetadata = {}
        albumIDMetadata = {}
        
        artistIDAlbums  = {}
        albumIDArtists  = {}


        
        ############## Artist MetaData ##############
        for artistID,artistData in db.items():
            artistIDMetadata[artistID] = {"Genre": Counter(), "Artists": Counter(), "Style": Counter(), "ArtistsURL": {}}
            artistIDAlbums[artistID]   = {}

            
            for albumID,albumData in artistData.items():
                artistIDAlbums[artistID][albumID] = [albumData.album.name, albumData.url.url, Counter(), Counter()]
                
                countries = albumData.profile.country
                if not isinstance(countries, list):
                    countries = [countries]
                for country in countries:
                    artistIDAlbums[artistID][albumID][2][country] += 1
                
                releaseds = albumData.profile.released
                if not isinstance(releaseds, list):
                    releaseds = [releaseds]
                for released in releaseds:
                    artistIDAlbums[artistID][albumID][3][released] += 1
                    
                    
                genres = albumData.profile.genre
                if not isinstance(genres, list):
                    genres = [genres]
                for genre in genres:
                    if genre is not None:
                        artistIDMetadata[artistID]['Genre'][genre.name] += 1

                artists = albumData.artist.artists
                for artist in artists:
                    if artist is not None:
                        artistIDMetadata[artistID]['Artists'][artist.name] += 1
                        artistIDMetadata[artistID]['ArtistsURL'][artist.ID] = artist.url


                styles = albumData.profile.style
                if not isinstance(styles, list):
                    styles = [styles]
                for style in styles:
                    if style is not None:
                        artistIDMetadata[artistID]['Style'][style.name] += 1

        
        albumDBDir = self.disc.getAlbumsMetadataDBDir()     
        savename    = setFile(albumDBDir, "{0}-ArtistMetadata.p".format(modVal))
        print("Saving {0} new artist IDs to {1}".format(len(artistIDMetadata), savename))
        saveJoblib(data=artistIDMetadata, filename=savename, compress=True)
          
        savename    = setFile(albumDBDir, "{0}-ArtistAlbums.p".format(modVal))
        print("Saving {0} new artist IDs to {1}".format(len(artistIDAlbums), savename))
        saveJoblib(data=artistIDAlbums, filename=savename, compress=True)
        
        
    def buildMetadata(self, force=False):
        start, cmt = clock("Building Album Metadata DB")
            
        if force is False:
            albumNameToID      = self.disc.getAlbumNameToIDData()
            albumIDToName      = self.disc.getAlbumIDToNameData()        
            albumRefToID       = self.disc.getAlbumRefToIDData()
            albumIDToRef       = self.disc.getAlbumIDToRefData()
            albumRefToName     = self.disc.getAlbumRefToNameData()
            albumNameToRef     = self.disc.getAlbumNameToRefData()
            albumIDToArtistID  = self.disc.getAlbumIDToArtistIDData()            
        else:
            albumNameToID      = {}
            albumIDToName      = {}
            albumRefToID       = {}
            albumIDToRef       = {}
            albumRefToName     = {}
            albumNameToRef     = {}            
            albumIDToArtistID  = {}

        artistAlbumMetaData = {}



        
        albumDBDir = self.disc.getAlbumsDBDir()   
        files       = findExt(albumDBDir, ext='.p')  
        for i,ifile in enumerate(files):
            if i % 25 == 0 or i == 5:
                print(i,'/',len(files),'\t',elapsed(start, cmt))
            db = getFile(ifile)
            for artistID,artistData in db.items():
                artistAlbumMetaData[artistID] = {"Genre": Counter(), "Artists": Counter(), "Style": Counter()}

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


                    ####### Artist MetaData #######
                    genres = albumData.profile.genre
                    if not isinstance(genres, list):
                        genres = [genres]
                    for genre in genres:
                        if genre is not None:
                            artistAlbumMetaData[artistID]['Genre'][genre.name] += 1

                    artists = albumData.artist.artists
                    for artist in artists:
                        if artist is not None:
                            artistAlbumMetaData[artistID]['Artists'][artist.name] += 1

                    styles = albumData.profile.style
                    if not isinstance(styles, list):
                        styles = [styles]
                    for style in styles:
                        if style is not None:
                            artistAlbumMetaData[artistID]['Style'][style.name] += 1
                            
                            
                            
        savenames = {"RefToID": albumRefToID, "NameToID": albumNameToID, "NameToRef": albumNameToRef,
                     "IDToRef": albumIDToRef, "IDToName": albumIDToName, "RefToName": albumRefToName}
        for basename,savedata in savenames.items():
            savename = setFile(self.getDiscogDBDir(), "Album{0}.p".format(basename))
            print("Saving {0} entries to {1}".format(len(savedata), savename))
            saveFile(ifile=savename, idata=savedata, debug=True)                            
                                                        
        savename = setFile(self.disc.getDiscogDBDir(), "AlbumIDToArtistID.p")
        print("Saving {0} known artists to {1}".format(len(albumIDToArtistID), savename))
        saveFile(ifile=savename, idata=albumIDToArtistID, debug=True)                       
                                                        
        savename = setFile(self.disc.getDiscogDBDir(), "AlbumArtistMetaData.p")
        print("Saving {0} known artists to {1}".format(len(artistAlbumMetaData), savename))
        saveFile(ifile=savename, idata=artistAlbumMetaData, debug=True)
        
        elapsed(start, cmt)