from fsUtils import isDir, setDir, mkDir, setFile, isFile
from ioUtils import getFile, saveFile
from os import getcwd
from discogsUtils import discogsUtils
from fsUtils import moveFile, moveDir
from fileUtils import getFileBasics, getBasename, getDirname
from searchUtils import findExt, findPattern
from glob import glob
from os.path import join
from time import sleep
from collections import Counter


class discogs():
    def __init__(self, base='discogs'):
        self.name       = "Discog"
        self.localpath  = setDir("/Users/tgadfort/Music", self.name, forceExist=False)
        #self.savepath   = setDir("/Volumes/Music", self.name, forceExist=False)
        self.savepath   = setDir("/Volumes/Biggy", self.name, forceExist=False)

        self.codepath   = getcwd()
        
        self.maxModVal  = 100
        
        self.base = base

        if self.base == 'discogs':
            self.discogURL       = "https://www.discogs.com/"        
            self.discogSearchURL = "https://www.discogs.com/search/"        
        elif self.base == 'allmusic':
            self.discogURL       = "https://www.allmusic.com/"        
            self.discogSearchURL = "https://www.allmusic.com/search/"    
        elif self.base == 'lastfm':
            self.discogURL       = "https://www.last.fm/"
            self.discogSearchURL = "https://www.last.fm/search/" #artists?q=Ariana+Grande
        elif self.base == 'musicbrainz':
            self.discogURL       = "https://musicbrainz.org/"
            self.discogSearchURL = "https://musicbrainz.org/search?"
        elif self.base == 'acebootlegs':
            #https://ace-bootlegs.com/category/deep-purple/
            self.discogURL       = "https://ace-bootlegs.com/"
            self.discogSearchURL = "https://ace-bootlegs.com/"
        elif self.base == 'rateyourmusic':
            #https://ace-bootlegs.com/category/deep-purple/
            self.discogURL       = "https://rateyourmusic.com/"
            self.discogSearchURL = "https://rateyourmusic.com/search?"
        elif self.base == 'datpiff':
            #https://ace-bootlegs.com/category/deep-purple/
            self.discogURL       = "https://www.datpiff.com/"
            self.discogSearchURL = "https://www.datpiff.com/mixtapes-search?"
        elif self.base == 'rockcorner':
            #https://ace-bootlegs.com/category/deep-purple/
            self.discogURL       = "https://www.therockcorner.com/"
            self.discogSearchURL = "https://www.therockcorner.com/"
        elif self.base == 'cdandlp':
            self.discogURL       = "https://www.cdandlp.com/"
            self.discogSearchURL = "https://www.cdandlp.com/en/search/?"
        elif self.base == 'musicstack':
            self.discogURL       = "https://www.musicstack.com/"
            self.discogSearchURL = "https://www.musicstack.com/"
        else:
            raise ValueError("Base is illegal: {0}".format(self.base))    
                
        self.createDirectories(debug=False)
        
        #self.unitTests()
        
    ## Improve upon this later
    def unitTests(self, debug=False):
        ### Various Tests
        dbfiles = self.getArtistsDBFiles()
        assert len(dbfiles) == self.getMaxModVal()
        print("Found {0} artist DB files and that is equal to the max mod value".format(len(dbfiles)))

        
    def getModValList(self, debug=False):
        return list(range(0, self.maxModVal))
        
    def getLocalDir(self, debug=False):
        return self.localpath
    
    def getCodeDir(self, debug=False):
        return self.codepath
    
    def getSaveDir(self, debug=False):
        return self.savepath        
        
        
    def createDirectories(self, debug=False):
        if not isDir(self.getSaveDir()):
            print("Warning! Saved Discog Directory {0} is not Available".format(self.getSaveDir()))
            self.savepath = None
        else:
            if debug:
                print("Saved Discog Directory {0} is Available".format(self.getSaveDir()))
            
        if not isDir(self.getLocalDir()):
            print("Warning! Local Discog Directory {0} is not Available".format(self.getLocalDir()))
            self.localpath = None
        else:
            if self.savepath is None:
                self.savepath = self.getLocalDir()
            if debug:
                print("Local Discog Directory {0} is Available".format(self.getLocalDir()))
        
        dirnames    = []
        dbdirnames  = []
        if self.base == 'discogs':
            names = ["collections", "artists", "albums"]
            dirnames += ["{0}-{1}".format(x, self.base) for x in names]
            dirnames += ["{0}-{1}-db".format(x, self.base) for x in names]
            dirnames += ["{0}-{1}-db/metadata".format(x, self.base) for x in names]
        elif self.base in ['allmusic', 'lastfm', 'musicbrainz', 'acebootlegs', 'rateyourmusic', 'datpiff', 'rockcorner', 'cdandlp', 'musicstack']:
            names = ["artists", "albums"]
            dirnames += ["{0}-{1}".format(x, self.base) for x in names]
            dirnames += ["{0}-{1}-db".format(x, self.base) for x in names]
            dirnames += ["{0}-{1}-db/metadata".format(x, self.base) for x in names]
        else:
            raise ValueError("Base is illegal: {0}".format(self.base))

        if self.base == 'discogs':
            names = ["diagnostic"]
            dirnames += ["{0}-{1}".format(x, self.base) for x in names]  
            dirnames += ["db-{0}".format(self.base)]
        elif self.base in ['allmusic', 'lastfm', 'musicbrainz', 'acebootlegs', 'rateyourmusic', 'datpiff', 'rockcorner', 'cdandlp', 'musicstack']:
            names = ["diagnostic"]
            dirnames += ["{0}-{1}".format(x, self.base) for x in names]  
            dirnames += ["db-{0}".format(self.base)]
        else:
            raise ValueError("Base is illegal: {0}".format(self.base))



        
        self.dirnames = dict(zip(dirnames, [setDir(self.getSaveDir(), x) for x in dirnames]))
        for name, dirname in self.dirnames.items():
            if not isDir(dirname):
                print("Creating {0}".format(dirname))
                mkDir(dirname, debug=True)
            else:
                if debug:
                    print("{0} exists".format(dirname))
                    
                    
    
    ###############################################################################
    # Basic Artist Functions
    ###############################################################################
    def getArtistSavename(self, discID):
        artistDir = self.disc.getArtistsDir()
        modValue  = self.discogsUtils.getDiscIDHashMod(discID=discID, modval=self.disc.getMaxModVal())
        if modValue is not None:
            outdir    = mkSubDir(artistDir, str(modValue))
            savename  = setFile(outdir, discID+".p")
            return savename
        return None

    
    ###############################################################################
    # Artist ModVals
    ###############################################################################
    def getMaxModVal(self, debug=False):
        return self.maxModVal

    
    ###############################################################################
    # Discog Directories
    ###############################################################################
    def getDiscogDBDir(self, debug=False):
        key = "db-{0}".format(self.base)
        if self.dirnames.get(key) is not None:
            return self.dirnames[key]
        else:
            raise ValueError("Base is illegal: {0}".format(self.base))


    ###############################################################################
    # Discog Collection Directories
    ###############################################################################
    def getCollectionsDir(self, debug=False):
        key = "collections-{0}-db".format(self.base)
        if self.dirnames.get(key) is not None:
            return self.dirnames[key]
        else:
            raise ValueError("Base is illegal: {0}".format(self.base))


    ###############################################################################
    # Discog Diagnostic Directories
    ###############################################################################
    def getDiagnosticDir(self, debug=False):
        key = "diagnostic-{0}".format(self.base)
        if self.dirnames.get(key) is not None:
            return self.dirnames[key]
        else:
            raise ValueError("Base is illegal: {0}".format(self.base))


    ###############################################################################
    # Discog Artist Directories
    ###############################################################################
    def getArtistsDir(self, debug=False):
        key = "artists-{0}".format(self.base)
        if self.dirnames.get(key) is not None:
            return self.dirnames[key]
        else:
            raise ValueError("Base is illegal: {0}".format(self.base))

    def getArtistsExtraDir(self, debug=False):
        key = "artists-extra-{0}".format(self.base)
        if self.dirnames.get(key) is not None:
            return self.dirnames[key]
        else:
            raise ValueError("Base is illegal: {0}".format(self.base))

    def getArtistsDBDir(self, debug=False):
        key = "artists-{0}-db".format(self.base)
        if self.dirnames.get(key) is not None:
            return self.dirnames[key]
        else:
            raise ValueError("Base is illegal: {0}".format(self.base))
    
    def getArtistsMetadataDBDir(self, debug=False):
        key = "artists-{0}-db/metadata".format(self.base)
        if self.dirnames.get(key) is not None:
            return self.dirnames[key]
        else:
            raise ValueError("Base is illegal: {0}".format(self.base))
    
    def getArtistsDBFiles(self, debug=False):
        dbfiles = findExt(self.getArtistsDBDir(), "*-DB.p")
        return dbfiles
    
    def getArtistsDBModValFilename(self, modVal):
        dbfile = setFile(self.getArtistsDBDir(), "{0}-DB.p".format(modVal))
        return dbfile
    
    def getArtistsDBModValData(self, modVal):
        dbfile = self.getArtistsDBModValFilename(modVal)
        if not isFile(dbfile):
            raise ValueError("{0} does not exist".format(dbfile))
        dbdata = getFile(dbfile)
        return dbdata
    
    def saveArtistsDBModValData(self, modVal, dbdata):
        dbfile = self.getArtistsDBModValFilename(modVal)
        if not isFile(dbfile):
            raise ValueError("{0} does not exist".format(dbfile))
        print("Saving {0} artists to {1}... ".format(len(dbdata), dbfile), end="")
        saveFile(idata=dbdata, ifile=dbfile)
        print("Done.")


    ###############################################################################
    # Discog Albums Directories
    ###############################################################################
    def getAlbumsDir(self, debug=False):
        key = "albums-{0}".format(self.base)
        if self.dirnames.get(key) is not None:
            return self.dirnames[key]
        else:
            raise ValueError("Base is illegal: {0}".format(self.base))

    def getAlbumsDBDir(self, debug=False):
        key = "albums-{0}-db".format(self.base)
        if self.dirnames.get(key) is not None:
            return self.dirnames[key]
        else:
            raise ValueError("Base is illegal: {0}".format(self.base))
    
    def getAlbumsMetadataDBDir(self, debug=False):
        key = "albums-{0}-db/metadata".format(self.base)
        if self.dirnames.get(key) is not None:
            return self.dirnames[key]
        else:
            raise ValueError("Base is illegal: {0}".format(self.base))
    
    def getAlbumsDBFiles(self, debug=False):
        dbfiles = findExt(self.getAlbumsDBDir(), "*-DB.p")
        return dbfiles
    
    def getAlbumsMetadataFiles(self, debug=False):
        dbfiles = findExt(self.getAlbumsMetadataDBDir(), "*-AlbumMetadata.p")
        return dbfiles
    
    def getAlbumsArtistMetadataFiles(self, debug=False):
        dbfiles = findExt(self.getAlbumsMetadataDBDir(), "*-ArtistMetadata.p")
        return dbfiles
    
    def getAlbumsArtistsFiles(self, debug=False):
        dbfiles = findExt(self.getAlbumsMetadataDBDir(), "*-ArtistAlbums.p")
        return dbfiles
    
    def getAlbumsDBModValFilename(self, modVal):
        dbfile = setFile(self.getAlbumsDBDir(), "{0}-DB.p".format(modVal))
        return dbfile
    
    def getAlbumsDBModValData(self, modVal):
        dbfile = self.getAlbumsDBModValFilename(modVal)
        if not isFile(dbfile):
            raise ValueError("{0} does not exist".format(dbfile))
        dbdata = getFile(dbfile)
        return dbdata


    ###############################################################################
    # Discog Special/Search Directories
    ###############################################################################
    def getSearchDir(self, debug=False):
        return self.dirnames["search"]

    def getSearchArtistsDir(self, debug=False):
        return self.dirnames["search-artists"]

    def getSpecialDir(self, debug=False):
        return self.dirnames["special"]

    def getArtistsSpecialDir(self, debug=False):
        return self.dirnames["artist-special"]

    def getMusicDir(self, debug=False):
        return self.localpath
    
    
    ##################################  Helper ######################################
    def flip(self, db):
        return {v: k for k,v in db.items()}
    
    
    ##################################  Diagnostic ##################################
    def getDiagnosticAlbumIDs(self, debug=False):
        savename = setFile(self.getDiagnosticDir(), "albumKnownIDs.p")
        if not isFile(savename):
            raise ValueError("Could not find {0}".format(savename))
        data = getFile(savename, debug=True)
        return data
    
    def saveDiagnosticAlbumIDs(self, albumIDs):
        savename = setFile(self.getDiagnosticDir(), "albumKnownIDs.p")
        saveFile(ifile=savename, idata=albumIDs)


    ###############################################################################
    # Discog DB Names
    ###############################################################################
    def getDBData(self, dbname, prefix, returnName=False, debug=False):
        savename = setFile(self.getDiscogDBDir(), "{0}{1}.p".format(prefix, dbname))
        if debug is True:
            print("Data stored in {0}".format(savename))
        if returnName is True:
            return savename
        if not isFile(savename):
            raise ValueError("Could not find {0}".format(savename))
           
        if debug:
            print("Returning data from {0}".format(savename))
        data = getFile(savename, debug=debug)
        return data
    
    
    ###############################################################################
    # Master Discogs DB
    ###############################################################################
    def getMasterDiscogsDB(self, debug=False):
        return self.getDBData("DB", "Master")
    
    def getMasterDiscogsDBFilename(self, debug=False):
        savename = self.getDBData("DB", "Master", returnName=True)
        return savename
    
    def getMasterArtistDiscogsDB(self, debug=False):
        return self.getDBData("DB", "MasterArtist")
    
    def getMasterArtistDiscogsDBFilename(self, debug=False):
        savename = self.getDBData("DB", "MasterArtist", returnName=True)
        return savename
    
    def getMasterSlimArtistDiscogsDB(self, debug=False):
        return self.getDBData("DB", "MasterSlimArtist")
    
    def getMasterSlimArtistDiscogsDBFilename(self, debug=False):
        savename = self.getDBData("DB", "MasterSlimArtist", returnName=True)
        return savename
    
    def getMasterArtistAlbumsDiscogsDB(self, debug=False):
        return self.getDBData("DB", "MasterArtistAlbums")
    
    def getMasterArtistAlbumsDiscogsDBFilename(self, debug=False):
        savename = self.getDBData("DB", "MasterArtistAlbums", returnName=True)
        return savename
    
    def getMasterArtistMetadataDiscogsDB(self, debug=False):
        return self.getDBData("DB", "MasterArtistMetadata")
    
    def getMasterArtistMetadataDiscogsDBFilename(self, debug=False):
        savename = self.getDBData("DB", "MasterArtistMetadata", returnName=True)
        return savename
    
    def getMasterAlbumDiscogsDB(self, debug=False):
        return self.getDBData("DB", "MasterAlbum")
    
    def getMasterAlbumDiscogsDBFilename(self, debug=False):
        savename = self.getDBData("DB", "MasterAlbum", returnName=True)
        return savename
    
        
    ##################################  Artists ##################################
    def getArtistIDToNameData(self, debug=False):
        return self.getDBData("IDToName", "Artist", debug=debug)
    
    def getArtistNameToIDData(self, debug=False):        
        return self.flip(self.getArtistIDToNameData())
        
    def getArtistIDToRefData(self, debug=False):
        return self.getDBData("IDToRef", "Artist", debug=debug)
        
    def getArtistIDToVariationsData(self, debug=False):
        return self.getDBData("IDToVariations", "Artist", debug=debug)

    def getArtistIDToAlbumNamesData(self, debug=False):
        return self.getDBData("IDToAlbumNames", "Artist", debug=debug)

    def getArtistIDToAlbumRefsData(self, debug=False):
        return self.getDBData("IDToAlbumRefs", "Artist", debug=debug)

    def getArtistIDToCoreAlbumNamesData(self, debug=False):
        return self.getDBData("IDToCoreAlbumNames", "Artist", debug=debug)

    def getArtistIDToCoreAlbumRefsData(self, debug=False):
        return self.getDBData("IDToCoreAlbumRefs", "Artist", debug=debug)
        
    def getArtistIDToGenreData(self, debug=False):
        return self.getDBData("IDToGenre", "Artist", debug=debug)
        
    def getArtistIDToStyleData(self, debug=False):
        return self.getDBData("IDToStyle", "Artist", debug=debug)
        
    def getArtistIDToCollaborationData(self, debug=False):
        return self.getDBData("IDToCollaborations", "Artist", debug=debug)
    
    
    ##################################  Albums ##################################
    def getAlbumIDToNameData(self, debug=False):
        return self.getDBData("IDToName", "Album")
    
    def getAlbumIDToRefData(self, debug=False):
        return self.getDBData("IDToRef", "Album")
    
    def getAlbumIDToArtistsData(self, debug=False):
        return self.getDBData("IDToArtists", "Album")
    
    
    def getAlbumNameToIDData(self, debug=False):
        return self.getDBData("NameToID", "Album")
    
    def getAlbumNameToIDsData(self, debug=False):
        return self.getDBData("NameToIDs", "Album")
    
    def getAlbumNameToRefData(self, debug=False):
        return self.getDBData("NameToRef", "Album")

    def getAlbumRefToIDData(self, debug=False):
        return self.getDBData("RefToID", "Album")
    
    def getAlbumRefToNameData(self, debug=False):
        return self.getDBData("RefToName", "Album")
    
    def getAlbumIDToArtistIDData(self, debug=False):
        return self.getDBData("IDToArtistID", "Album")
    
    def getAlbumArtistMetaData(self, debug=False):
        return self.getDBData("ArtistMetaData", "Album")
    
    
    ##################################  Collections ##################################
    def getCollectionNameToIDData(self, debug=False):
        return self.getDBData("NameToID", "Collection")
        
    def getCollectionNameToIDsData(self, debug=False):
        return self.getDBData("NameToIDs", "Collection")
    
    def getCollectionNameToRefData(self, debug=False):
        return self.getDBData("NameToRef", "Collection")
        
    def getCollectionNameToRefsData(self, debug=False):
        return self.getDBData("NameToRefs", "Collection")

    def getCollectionRefToIDData(self, debug=False):
        return self.getDBData("RefToID", "Collection")
    
    def getCollectionRefToNameData(self, debug=False):
        return self.getDBData("RefToName", "Collection")

    def getCollectionIDToNameData(self, debug=False):
        return self.getDBData("IDToName", "Collection")
    
    def getCollectionIDToRefData(self, debug=False):
        return self.getDBData("IDToRef", "Collection")
    
    def getCollectionRefCountsData(self, debug=False):
        return self.getDBData("RefCounts", "Collection")
    
    def getCollectionAlbumRefCountsData(self, debug=False):
        return Counter(self.getDBData("AlbumRefCounts", "Collection"))
    
    def getCollectionAlbumRefArtistsData(self, debug=False):
        return self.getDBData("AlbumRefArtists", "Collection")
    
    
    
    ##################################  Core Albums ##################################
    def getArtistIDCoreAlbumNames(self, debug=False):
        return self.getDBData("IDCoreAlbumNames", "Artist", debug=debug)
    
    def getArtistIDCoreAlbumIDs(self, debug=False):
        return self.getDBData("IDCoreAlbumIDs", "Artist", debug=debug)
    
    def getArtistIDCoreAlbumRefs(self, debug=False):
        return self.getDBData("IDCoreAlbumRefs", "Artist", debug=debug)

    def getArtistIDAlbumIDs(self, debug=False):
        return self.getDBData("IDAlbumIDs", "Artist", debug=debug)

    def getArtistIDAlbumRefs(self, debug=False):
        return self.getDBData("IDAlbumRefs", "Artist", debug=debug)
    
    
    ##################################  Ascii Lookup ##################################
    def getArtistAsciiNames(self, debug=False):
        return self.getDBData("AsciiNames", "Artist", debug=debug)
    
    
    ###############################################################################
    # Moving Functions
    ###############################################################################
    def moveAlbumFilesToNewModValue(self, newModValue, oldModValue):
        filedir    = self.getAlbumsDir()
        dutils     = discogsUtils()
        for modVal in range(oldModValue):
            modValue  = dutils.getDiscIDHashMod(discID=modVal, modval=newModValue) #disc.getMaxModVal())
            if modVal == modValue:
                sleep(1)
                continue
            else:
                dirs = glob(join(filedir, str(modVal), "*"))
                print("Moving {0} directories from {1} to {2}".format(len(dirs), modVal, modValue))
                for idir in dirs:
                    dname = getDirname(idir)
                    src = idir
                    dst = join(filedir, str(modValue), dname)
                    print(src)
                    print(dst)
                    1/0
                    moveDir(src, dst)

        
    def moveArtistFilesToNewModValue(self, newModValue, oldModValue):
        filedir    = self.getArtistsDir()
        dutils     = discogsUtils()
        for modVal in range(oldModValue):
            modValue  = dutils.getDiscIDHashMod(discID=modVal, modval=newModVal) #disc.getMaxModVal())
            if modVal == modValue:
                sleep(1)
                continue
            else:
                files = glob(join(filedir, str(modVal), "*.p"))
                print("Moving {0} files from {1} to {2}".format(len(files), modVal, modValue))
                for ifile in files:
                    fbasics = getFileBasics(ifile)
                    fname = getBasename(ifile)
                    src = ifile
                    dst = join(artistsDir, str(modValue), fname)
                    moveFile(src, dst)

                            

    def moveExtArtistFilesToNewModValue(self, newModVal):
        artistsDir     = self.getArtistsDir()
        extArtistsDir  = self.getArtistsExtraDir()
        dutils         = discogsUtils()

        files = glob(join(extArtistsDir, "*.p"))
        print("Moving {0} files".format(len(files)))
        for ifile in files:
            fbasics   = getFileBasics(ifile)
            fname     = getBasename(ifile)
            discID    = fbasics[1].split('-')[0]
            modValue  = dutils.getDiscIDHashMod(discID=discID, modval=newModVal) #disc.getMaxModVal())

            src = ifile
            dst = join(artistsDir, str(modValue), fname)
            moveFile(src, dst)

    def mergeArtistDBs(self, debug=False):
        from glob import glob
        from os.path import join

        artistsDBDir = self.getArtistsDBDir()
        dutils       = discogsUtils()

        for modVal in self.getModValList():
            dbdata = {}
            files = glob(join(artistsDBDir, "old/*.p"))
            print(modVal,len(files))
            for ifile in files:
                fbasics  = getFileBasics(ifile)
                oldValue = int(fbasics[1].split('-')[0])
                modValue = dutils.getDiscIDHashMod(discID=oldValue, modval=disc.getMaxModVal())
                if modValue == modVal:
                    db = getFile(ifile)
                    dbdata.update(db)


            savename = setFile(artistsDBDir, "{0}-DB.p".format(modVal))     
            print("Saving {0} artist IDs to {1}".format(len(dbdata), savename))
            saveJoblib(data=dbdata, filename=savename, compress=True)