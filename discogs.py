from fsUtils import isDir, setDir, mkDir
from ioUtils import getFile, saveFile
from os import getcwd


class discogs():
    def __init__(self):        
        self.name       = "Discog"
        self.localpath  = setDir("/Users/tgadfort/Documents/music", self.name)
        self.savepath   = setDir("/Volumes/Music", self.name)
        self.codepath   = getcwd()
        

    def getLocalDir(self):
        return self.localpath
    
    def getCodeDir(self):
        return self.codepath
    
    def getSaveDir(self):
        return self.savepath        
        
        
    def createDirectories(self):
        if not isDir(self.getSaveDir()):
            print("Warning! Saved Discog Directory {0} is not Available".format(self.getSaveDir()))
            self.savepath = None
        else:
            print("Saved Discog Directory {0} is Available".format(self.getSaveDir()))
            
        if not isDir(self.getLocalDir()):
            print("Warning! Local Discog Directory {0} is not Available".format(self.getLocalDir()))
            self.localpath = None
        else:
            print("Local Discog Directory {0} is Available".format(self.getLocalDir()))
        
        dirnames    = []
        dbdirnames  = []
        names = ["base", "collections", "artists", "albums"]
        dirnames += ["{0}".format(x) for x in names]
        dirnames += ["{0}-db".format(x) for x in names]
        
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
                print("{0} exists".format(dirname))

    
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
        return self.dbdirnames["artists-db"]


    ###############################################################################
    # Discog Albums Directories
    ###############################################################################
    def getAlbumsDir(self):
        return self.dirnames["albums"]

    def getAlbumsDBDir(self):
        return self.dbdirnames["albums-db"]


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