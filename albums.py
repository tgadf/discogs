from fsUtils import setFile, isFile, setDir, isDir, mkDir, mkSubDir, setSubDir, removeFile
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

class albums():
    def __init__(self, discog, basedir=None):
        self.disc = discog
        self.name = "albums"
        
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
        
        
    ######################################################################
    ### Load Full Artist Data 
    ######################################################################
    def downloadAlbumURL(self, url, savename, sleeptime=2.5):
        if isFile(savename):
            return
        
        user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        headers={'User-Agent':user_agent,} 

        sleep(1)

        print("Downloading: {0}".format(url))

        request=urllib.request.Request(url,None,headers) #The assembled request
        response = urllib.request.urlopen(request)
        data = response.read() # The data u need

        print("Saving {0}".format(savename))
        saveJoblib(data=data, filename=savename, compress=True)
        print("Done. Sleeping for {0} seconds".format(sleeptime))
        sleep(sleeptime)
        
        
    def downloadAlbumDataData(self, modval, mediaTypes=["Albums"], maxAlbums=None, debug=False):
        maxModVal = self.modVal
        
        albumsDir = self.getAlbumsDir()
        
        dbname = setFile(self.getArtistsDBDir(), "{0}-DB.p".format(modval))
        dbdata = getFile(dbname, version=3)
        
        artistModDir = setSubDir(albumsDir, str(modval))
            
        nArtists = len(dbdata)
        iArtists = 0
        for artistID, artistData in dbdata.items():
            iArtists += 1
            if artistID in ['712500', '1745000']:
                continue
            #retval = {}
            #retval["Artist"]      = self.getArtistName(bsdata, debug)
            #retval["URL"]         = self.getArtistURL(bsdata, debug)
            #retval["ID"]          = self.getArtistDiscID(retval["URL"], debug)
            #retval["Pages"]       = self.getArtistPages(bsdata, debug)
            ##retval["Variations"]  = self.getArtistVariations(bsdata, debug)
            #retval["MediaCounts"] = self.getArtistMediaCounts(bsdata, debug)
            #retval["Media"]       = self.getArtistMedia(bsdata, debug)
            
            print(iArtists,'/',nArtists,'\t:',artistData["ID"],'\t',artistData["Artist"])
            artistIDDir = setDir(artistModDir, artistID)
            media = artistData["Media"]
            for mediaType, mediaTypeData in media.items():
                if mediaTypes is not None:
                    if mediaType not in mediaTypes:
                        continue
                nget = 0
                for mediaID, mediaIDData in mediaTypeData.items():
                    albumName = mediaIDData["Album"]
                    albumArtist = mediaIDData["Artist"][0][0]
                    print("\t",mediaID,'\t',albumArtist,'\t',albumName)
                    savename = setFile(artistIDDir, "{0}.p".format(mediaID))
                    if isFile(savename):
                        continue
                    if maxAlbums is not None:
                        if nget >= maxAlbums:
                            break
     
                    baseURL = self.disc.discogURL
                    url = urllib.parse.urljoin(baseURL, quote(mediaIDData["URL"]))                    
                    self.downloadAlbumURL(url, savename)
                
                


    ################################################################################
    # Parse Album Data (3)
    ################################################################################
    def parseAlbumFile(ifile):
        bsdata     = getHTML(get(ifile))
        albumData  = self.parse(bsdata) 
        return albumData
    

    def parseAlbumFiles(self, debug=False):        
        albumInfo = album()

        albumDir  = self.disc.getAlbumsDir()
        maxModVal = self.disc.getMaxModVal()
                    
        albumDBDir = self.disc.getAlbumsDBDir()        
        
        totalSaves = 0
        for i in ['NAN'] + list(range(maxModVal)):
            
            start, cmt = clock("Analyzing Modval {0}".format(i))
            
            dirVal = setDir(albumDir, str(i))
            print("Looking for artist albums in {0}".format(dirVal))
            
            dbname = setFile(albumDBDir, "{0}-DB.p".format(i))
            if isFile(dbname):
                dbdata = getFile(dbname, version=3)
            else:
                print("DB is empty")
                dbdata = {}
            
            artistDirs = findDirs(dirVal)
            print("Found {0} artist directories".format(len(artistDirs)))

            saveIt = 0
            for j,artistDir in enumerate(artistDirs):
                artistID = getDirBasics(artistDir)[-1]
                if dbdata.get(artistID) is None:
                    dbdata[artistID] = {}
                
                files = findExt(artistDir, ext='.p')
                if j % 100 == 0 or j == len(artistDirs) - 1:
                    print("  Found {0: <3} albums ({1: <5}) in {2}/{3}\t{4}".format(len(files), saveIt, j, len(artistDirs), artistDir))

                if len(files) == 0:
                    continue
                    

                for ifile in files:
                    if getsize(ifile) < 1000:
                        removeFile(ifile)
                        continue
                    discID = getBaseFilename(ifile)
                    if dbdata[artistID].get(discID) is None:
                        try:
                            saveIt += 1
                            info   = albumInfo.getData(ifile)
                            dbdata[artistID][discID] = info
                        except:
                            continue
                    


            if saveIt > 0:
                savename = setFile(albumDBDir, "{0}-DB.p".format(i))     
                print("Saving {0} new album IDs to {1}".format(saveIt, savename))
                saveJoblib(data=dbdata, filename=savename, compress=True)
                totalSaves += saveIt
                
            elapsed(start, cmt)
            sleep(1)


        print("Saved {0} new artist IDs".format(totalSaves))
        
    
    ################################################################################
    # Collect Metadata About Artists (4)
    ################################################################################
    def buildMetadata(self):
        start, cmt = clock("Building Artist Metadata DB")
        
        artistNameToID   = self.disc.getArtistNameToIDData()
        artistNameToIDs  = self.disc.getArtistNameToIDsData()
        artistIDToName   = self.disc.getArtistIDToNameData()        
        artistRefToID    = self.disc.getArtistRefToIDData()
        artistIDToRef    = self.disc.getArtistIDToRefData()
        artistRefToName  = self.disc.getArtistRefToNameData()
        artistNameToRef  = self.disc.getArtistNameToRefData()
        artistNameToRefs = self.disc.getArtistNameToRefsData()

        albumNameToID   = {}
        albumIDToName   = {}
        albumRefToID    = {}
        albumIDToRef    = {}
        albumRefToName  = {}
        albumNameToRef  = {}

        artistIDCoreAlbumIDs   = {}
        artistIDAlbumIDs       = {}
        artistIDCoreAlbumNames = {}
        artistIDAlbumNames     = {}

        
        
        
        artistNames = {}
        artistYears = {}
        artistDBDir = self.disc.getArtistsDBDir()   
        files       = findExt(artistDBDir, ext='.p')  
        for i,ifile in enumerate(files):
            if i % 25 == 0 or i == 5:
                print(i,'/',len(files),'\t',elapsed(start, cmt))
            db = getFile(ifile)
            for discID,artistData in db.items():
                
                #if artistIDToName
                
                years = None
                artist      = artistData['Artist']
                artistName  = self.discogsUtils.getArtistName(artist)
                artistRef   = artistData['URL']
                
                if artistRefToName.get(artistRef) is None:
                    artistRefToName[artistRef] = artist
                if artistRefToID.get(artistRef) is None:
                    artistRefToID[artistRef] = discID
                if artistNameToRef.get(artist) is None:
                    artistNameToRef[artist] = artistRef
                if artistNameToID.get(artist) is None:
                    artistNameToID[artist] = discID
                if artistIDToName.get(discID) is None:
                    artistIDToName[discID] = artist
                if artistIDToRef.get(discID) is None:
                    artistIDToRef[discID] = artistRef

                
                if artistNames.get(artistName) is None:
                    artistNames[artistName] = {}
                artistNames[artistName][discID] = 1

                    
                artistVariations = artistData['Variations']
                artistMedia      = artistData['Media']
                if artistMedia is not None:
                    for mediaName,mediaData in artistMedia.items():
                        for mediaID, mediaValues in mediaData.items():
                            year = mediaValues['Year']
                            try:
                                year = int(year)
                            except:
                                continue
                            if years is None:
                                years = [year, year]
                            else:
                                years[0] = min([year, years[0]])
                                years[1] = max([year, years[1]])
                        
                if len(artistVariations) > 0:
                    vardata = artistVariations.values()
                    for var in vardata:
                        for varval in var:
                            varname = varval[0]
                            if artistNames.get(varname) is None:
                                artistNames[varname] = {}
                            artistNames[varname][discID] = 1


                artistIDCoreAlbumIDs[artistID] = []
                artistIDAlbumIDs[artistID]    = []

                media = artistData['Media']
                if media is not None:
                    for mediaName,mediaData in media.items():
                        albumCntr[mediaName] += 1
                        albumKeys = list(mediaData.keys())
                        if mediaName in core:
                            artistIDCoreAlbumIDs[artistID] += albumKeys
                        artistIDAlbumIDs[artistID] += albumKeys

                        for mediaID, mediaValues in mediaData.items():
                            for mediaType, mediaTypeData in mediaValues.items():
                                albumID   = mediaID
                                albumName = mediaValues["Album"]
                                albumRef  = mediaValues["URL"]

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
                            
        savename = setFile(self.disc.getDiscogDBDir(), "ArtistVariationNameToIDs.p")
        print("Saving {0} known artists to {1}".format(len(artistNames), savename))
        saveFile(ifile=savename, idata=artistNames, debug=True)

        
        

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
                     "ArtistIDCoreAlbumNames": artistIDCoreAlbumNames, "ArtistIDAlbumNames": artistIDAlbumNames}
        for basename,savedata in savenames.items():
            savename = setFile(disc.getDiscogDBDir(), "{0}.p".format(basename))
            print("Saving {0} entries to {1}".format(len(savedata), savename))
            print("  --> There are {0} albums in this file".format(sum([len(v) for k,v in savedata.items()])))
            saveFile(ifile=savename, idata=savedata, debug=True)
            print("")


        savenames = {"RefToID": albumRefToID, "NameToID": albumNameToID, "NameToRef": albumNameToRef,
                     "IDToRef": albumIDToRef, "IDToName": albumIDToName, "RefToName": albumRefToName}
        for basename,savedata in savenames.items():
            savename = setFile(disc.getDiscogDBDir(), "Album{0}.p".format(basename))
            print("Saving {0} entries to {1}".format(len(savedata), savename))
            saveFile(ifile=savename, idata=savedata, debug=True)
            print("")        
        
        
        
        
        
        
        elapsed(start, cmt)