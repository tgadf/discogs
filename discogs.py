from fsUtils import isDir, setDir, mkDir, setFile, isFile
from ioUtils import getFile, saveFile
from os import getcwd


class discogs():
    def __init__(self):        
        self.name       = "Discog"
        self.localpath  = setDir("/Users/tgadfort/Documents/music", self.name)
        self.savepath   = setDir("/Volumes/Music", self.name)
        self.codepath   = getcwd()
        
        self.maxModVal  = 500

        self.discogURL       = "https://www.discogs.com/"        
        self.discogSearchURL = "https://www.discogs.com/search/"        
                
        self.createDirectories(debug=True)

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
    def getDBData(self, dbname):
        savename = setFile(self.getDiscogDBDir(), "{0}.p".format(dbname))
        if not isFile(savename):
            raise ValueError("Could not find {0}".format(savename))
        data = getFile(savename, debug=True)
        return data
        
    def getArtistNameToIDData(self):
        return self.getDBData("NameToID")
        
    def getArtistNameToIDsData(self):
        return self.getDBData("NameToIDs")
        
    def getArtistIDToNameData(self):
        return self.getDBData("IDToName")
        
    def getArtistRefToIDData(self):
        return self.getDBData("RefToID")
        
    def getArtistIDToRefData(self):
        return self.getDBData("IDToRef")
        
    def getArtistRefToNameData(self):
        return self.getDBData("RefToName")
        
    def getArtistNameToRefData(self):
        return self.getDBData("NameToRef")
        
    def getArtistNameToRefsData(self):
        return self.getDBData("NameToRefs")
    
    def getArtistRefCountsData(self):
        return self.getDBData("RefCounts")
        
    def getKnownArtistIDsData(self):
        return self.getDBData("KnownArtistIDs")
        
    def getToGetData(self):
        return self.getDBData("ToGet")
        
    def getArtistVariationNameToIDsData(self):
        return self.getDBData("VariationNameToIDs")
    
    
    