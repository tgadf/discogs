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





class discogs():
    def __init__(self):        
        self.name       = "Discog"
        self.localpath  = setDir("/Users/tgadfort/Documents/music", self.name)
        self.savepath   = setDir("/Volumes/Music", self.name)
        self.codepath   = getcwd()
        
        self.maxModVal  = 100

        self.discogURL       = "https://www.discogs.com/"        
        self.discogSearchURL = "https://www.discogs.com/search/"        
                
        self.createDirectories(debug=True)
        
        self.unitTests()
        
    ## Improve upon this later
    def unitTests(self):
        ### Various Tests
        dbfiles = self.getArtistsDBFiles()
        assert len(dbfiles) == self.getMaxModVal()
        print("Found {0} artist DB files and that is equal to the max mod value".format(len(dbfiles)))

        
    def getModValList(self):
        return list(range(0, self.maxModVal))
        
    def getLocalDir(self):
        return self.localpath
    
    def getCodeDir(self):
        return self.codepath
    
    def getSaveDir(self):
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
            if debug:
                print("Local Discog Directory {0} is Available".format(self.getLocalDir()))
        
        dirnames    = []
        dbdirnames  = []
        names = ["base", "collections", "artists", "albums"]
        dirnames += ["{0}".format(x) for x in names]
        dirnames += ["{0}-db".format(x) for x in names]
        
        names = ["artists-extra"]
        dirnames += ["{0}".format(x) for x in names]

        names = ["search", "search-artists"]
        dirnames += ["{0}".format(x) for x in names]
        
        names = ["special", "artist-special"]
        dirnames += ["{0}".format(x) for x in names]
        
        dirnames += ["db"]
        
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
    def getMaxModVal(self):
        return self.maxModVal

    
    ###############################################################################
    # Discog Directories
    ###############################################################################
    def getDiscogDBDir(self):
        return self.dirnames["db"]


    ###############################################################################
    # Discog Collection Directories
    ###############################################################################
    def getCollectionsDir(self):
        return self.dirnames["collections"]

    def getCollectionsDBDir(self):
        return self.dirnames["collections-db"]


    ###############################################################################
    # Discog Artist Directories
    ###############################################################################
    def getArtistsDir(self):
        return self.dirnames["artists"]

    def getArtistsExtraDir(self):
        return self.dirnames["artists-extra"]

    def getArtistsDBDir(self):
        return self.dirnames["artists-db"]
    
    def getArtistsDBFiles(self):
        dbfiles = findExt(self.getArtistsDBDir(), "*.p")
        return dbfiles


    ###############################################################################
    # Discog Albums Directories
    ###############################################################################
    def getAlbumsDir(self):
        return self.dirnames["albums"]

    def getAlbumsDBDir(self):
        return self.dirnames["albums-db"]


    ###############################################################################
    # Discog Special/Search Directories
    ###############################################################################
    def getSearchDir(self):
        return self.dirnames["search"]

    def getSearchArtistsDir(self):
        return self.dirnames["search-artists"]

    def getSpecialDir(self):
        return self.dirnames["special"]

    def getArtistsSpecialDir(self):
        return self.dirnames["artist-special"]

    def getMusicDir(self):
        return self.localpath
    
    


    ###############################################################################
    # Discog DB Names
    ###############################################################################
    def getDBData(self, dbname, prefix):
        savename = setFile(self.getDiscogDBDir(), "{0}{1}.p".format(prefix, dbname))
        if not isFile(savename):
            raise ValueError("Could not find {0}".format(savename))
        data = getFile(savename, debug=True)
        return data
        
        
    ##################################  Artists ##################################
    def getArtistNameToIDData(self):
        return self.getDBData("NameToID", "Artist")
        
    def getArtistNameToIDsData(self):
        return self.getDBData("VariationNameToIDs", "Artist")
        
    def getArtistIDToNameData(self):
        return self.getDBData("IDToName", "Artist")
        
    def getArtistRefToIDData(self):
        return self.getDBData("RefToID", "Artist")
        
    def getArtistIDToRefData(self):
        return self.getDBData("IDToRef", "Artist")
        
    def getArtistRefToNameData(self):
        return self.getDBData("RefToName", "Artist")
        
    def getArtistNameToRefData(self):
        return self.getDBData("NameToRef", "Artist")
        
    def getArtistNameToRefsData(self):
        return self.getDBData("NameToRefs", "Artist")
    
    def getArtistRefCountsData(self):
        return self.getDBData("RefCounts", "artist")
        
    def getKnownArtistIDsData(self):
        return self.getDBData("KnownArtistIDs", "Artist")
        
    def getToGetData(self):
        return self.getDBData("ToGet")
    
    def getArtistVariationNameToIDsData(self):
        return self.getDBData("VariationNameToIDs", "Artist")
    
    
    ##################################  Albums ##################################
    def getAlbumNameToIDData(self):
        return self.getDBData("NameToID", "Album")
    
    def getAlbumNameToRefData(self):
        return self.getDBData("NameToRef", "Album")

    def getAlbumRefToIDData(self):
        return self.getDBData("RefToID", "Album")
    
    def getAlbumRefToNameData(self):
        return self.getDBData("RefToName", "Album")

    def getAlbumIDToNameData(self):
        return self.getDBData("IDToName", "Album")
    
    def getAlbumIDToRefData(self):
        return self.getDBData("IDToRef", "Album")
    
    
    ##################################  Collections ##################################
    def getCollectionNameToIDData(self):
        return self.getDBData("NameToID", "Collection")
        
    def getCollectionNameToIDsData(self):
        return self.getDBData("NameToIDs", "Collection")
    
    def getCollectionNameToRefData(self):
        return self.getDBData("NameToRef", "Collection")
        
    def getCollectionNameToRefsData(self):
        return self.getDBData("NameToRefs", "Collection")

    def getCollectionRefToIDData(self):
        return self.getDBData("RefToID", "Collection")
    
    def getCollectionRefToNameData(self):
        return self.getDBData("RefToName", "Collection")

    def getCollectionIDToNameData(self):
        return self.getDBData("IDToName", "Collection")
    
    def getCollectionIDToRefData(self):
        return self.getDBData("IDToRef", "Collection")
    
    def getCollectionRefCountsData(self):
        return self.getDBData("RefCounts", "Collection")
    
    
    ##################################  Core Albums ##################################
    def getArtistIDCoreAlbumNames(self):
        return self.getDBData("IDCoreAlbumNames", "Artist")

    def getArtistIDAlbumNames(self):
        return self.getDBData("IDAlbumNames", "Artist")

    
    
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

    def mergeArtistDBs(self):
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