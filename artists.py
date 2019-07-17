from fsUtils import setFile, isFile, setDir, isDir, mkDir, mkSubDir
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
        
        self.starterDir = setDir(self.getCodeDir(), self.name)
        if not isDir(self.starterDir):
            print("Creating {0}".format(self.starterDir))
            mkDir(self.starterDir, debug=True)
        
    
    ###############################################################################
    # Find Known (Downloaded) Artists (0)
    ###############################################################################
    def findKnownArtists(self, debug=False):
        if debug:
            print("Finding Known (Downloaded) Artists")
        artistIDs = []
        artistDir = self.disc.getArtistsDir()
        maxModVal = self.disc.getMaxModVal()
        for i in range(maxModVal):
            dirVal       = setDir(artistDir, str(i))
            files        = findExt(dirVal, ext='.p')
            regArtistIDs = [getBaseFilename(x) for x in files] 
            artistIDs   += regArtistIDs

            
        if debug:
            print("Found {0} artist IDs in {1}".format(len(artistIDs), artistDir))
            
        artistDir = self.disc.getArtistsExtraDir()
        files     = findExt(artistDir, ext='.p')
        extraArtistIDs = list(set([getBaseFilename(x).split('-')[0] for x in files]))  
        if debug:
            print("Found {0} artist IDs in {1}".format(len(extraArtistIDs), artistDir))
                  
        artistIDs += extraArtistIDs
        
        savename = setFile(self.disc.getDiscogDBDir(), "KnownArtistIDs.p")
        print("Saving {0} known artists to {1}".format(len(artistIDs), savename))
        saveFile(ifile=savename, idata=artistIDs, debug=True)
        
    
    ###############################################################################
    # Find Unknown Artists (1)
    ###############################################################################
    def findUnknownArtists(self, minVal=0, debug=False):
        refCounts = Counter(self.disc.getArtistRefCountsData())
        if debug:
            print("There are {0} potential artists".format(len(refCounts)))
        
        check = {self.discogsUtils.getArtistID(k): k for k,v in refCounts.most_common() if v > minVal}
        checkSet = set(check.keys())
        if debug:
            print("There are {0} potential artists > {1} counts".format(len(checkSet), minVal))
        
        knownArtistIDs = self.disc.getKnownArtistIDsData()
        knownSet = set(knownArtistIDs)
        if debug:
            print("There are {0} known artists".format(len(knownSet)))

            
        toget = {check[k]: k for k in list(checkSet - knownSet)}
        if debug:
            print("There are {0} artists > {1} counts".format(len(toget), minVal))
        
        savename = setFile(self.disc.getDiscogDBDir(), "ToGet.p")
        print("Saving {0} known artists to {1}".format(len(toget), savename))
        saveFile(ifile=savename, idata=toget, debug=True)
        
    
    ###############################################################################
    # Download Unknown Artists (2)
    ###############################################################################
    def getArtistRef(self, artistRef):        
        baseURL = self.disc.discogURL
        url     = urllib.parse.urljoin(baseURL, quote(artistRef))
        return url
    
    
    def getArtistSavename(self, discID):
        artistDir = self.disc.getArtistsDir()
        modValue  = self.discogsUtils.getDiscIDHashMod(discID=discID, modval=self.disc.getMaxModVal())
        if modValue is not None:
            outdir    = mkSubDir(artistDir, str(modValue))
            savename  = setFile(outdir, discID+".p")
            return savename
        return None
        
    
    def downloadArtistURL(self, url, savename):
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
        print("Done. Sleeping for 2 seconds")
        sleep(2)

        
    def downloadUnknownArtists(self, forceWrite=False, debug=False):
        toget     = self.disc.getToGetData()
        if debug:
            print("There are {0} artists to download".format(len(toget)))
        
        for artistRef,discID in toget.items():
            url      = self.getArtistRef(artistRef)
            savename = self.getArtistSavename(discID)
            if isFile(savename) and not forceWrite:
                continue

            self.downloadArtistURL(url, savename)
            
            
    ################################################################################
    # Download Search Artist (2a)
    ################################################################################
    def searchDiscogForArtist(self, artist, debug=True):
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
            url      = self.getArtistRef(href)
            savename = self.getArtistSavename(discID)

            print(iArtist,'/',len(artistDB),'\t:',len(discID),'\t',url)
            if isFile(savename):
                continue

            self.downloadArtistURL(url, savename)
                
            




    ################################################################################
    # Parse Artist Data (3)
    ################################################################################
    def parseArtistFile(ifile):
        bsdata     = getHTML(get(ifile))
        artistData = self.parse(bsdata) 
        return artistData
    

    def parseArtistFiles(self, debug=False):        
        artistInfo = artist()

        artistDir = self.disc.getArtistsDir()
        maxModVal = self.disc.getMaxModVal()
                    
        artistDBDir = self.disc.getArtistsDBDir()        
        
        totalSaves = 0
        for i in range(maxModVal):
            dirVal = setDir(artistDir, str(i))
            files  = findExt(dirVal, ext='.p')
            
            dbname = setFile(artistDBDir, "{0}-DB.p".format(i))            
            dbdata = getFile(dbname, version=3)
            
            saveIt = 0
            for ifile in files:
                discID = getBaseFilename(ifile)
                if dbdata.get(discID) is None:
                    saveIt += 1
                    info   = artistInfo.getData(ifile)
                    dbdata[discID] = info

            if saveIt > 0:
                savename = setFile(artistDBDir, "{0}-DB.p".format(i))     
                print("Saving {0} new artist IDs to {1}".format(saveIt, savename))
                saveJoblib(data=dbdata, filename=savename, compress=True)
                totalSaves += saveIt
            
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