from dbBase import dbBase
from searchUtils import findNearest
from pandas import DataFrame, Series


########################################################################################################
#
# Set Artist Database
#
########################################################################################################
class dbArtistMap():
    def __init__(self, db, known=False, debug=False):
        self.db    = db
        self.debug = debug
        if debug:
            print("Getting DB Data For {0}".format(db))
        
        try:
            self.disc           = dbBase(db.lower())
        except:
            raise ValueError("Cannot create a dbBase() object with [{0}]".format(db.lower()))
            
        self.discdf         = None
        self.artists        = None
        self.albumsDB       = None
        self.artistIDToName = None
        self.artistNameToID = None
        self.artistAlbumsDB = None
        self.Nalbums        = None
        self.known          = known
        if debug:
            if self.known is True:
                print("Only Getting Known Artist DB Data")
            else:
                print("Getting All Artist DB Data")
        
        self.artistIDToName = None
        self.artistNameToID = None
        
        self.finalArtistName = "CleanDiscArtist"
        
        self.setArtistIDMap()
        self.setAlbumIDMap()
        self.summary()
            
            
    ########################################################################################################
    #
    # Get Artist ID Mapping
    #
    ########################################################################################################
    def getArtistIDFromName(self, artistName):
        if self.artistNameToID is None:
            self.setArtistIDMap()
        if self.artistNameToID.get(artistName) is None:
            print("Artist [{0}] is not a member of artistNameToID.".format(artistName))
            return None
        artistID = self.artistNameToID[artistName]
        return artistID

    def getArtistNameFromID(self, artistID):
        if self.artistIDToName is None:
            self.setArtistIDMap()
        if self.artistIDToName.get(artistID) is None:
            print("Artist ID [{0}] is not a member of artistIDToName.".format(artistID))
            return None
        artistName = self.artistIDToName[artistID]
        return artistName
    
            
            
    ########################################################################################################
    #
    # Set Artist ID Mapping
    #
    ########################################################################################################
    def setArtistIDMap(self):
        if self.debug:
            print("  Getting Master Artist DB File ({0})".format(self.db))

        if self.known is True:
            self.discdf  = self.disc.getMasterKnownSlimArtistDiscogsDB()
        else:
            self.discdf  = self.disc.getMasterSlimArtistDiscogsDB()
            
        self.artists = [x for x in list(self.discdf[self.finalArtistName]) if x is not None]
        if self.debug:
            print("    Found {0} Artists in DB".format(len(self.artists)))

        self.artistIDToName = self.discdf[self.finalArtistName].to_dict()
        self.artistNameToID = {}
        if self.debug:
            print("    Found {0} ID -> Name entries".format(len(self.artistIDToName)))

        if self.known is True:
            if self.debug is True:
                print("    Only loading a subset of known artists into memory.")
        for artistID,artistName in self.artistIDToName.items():
            if artistName is None:
                continue
            if self.artistNameToID.get(artistName) is None:
                self.artistNameToID[artistName] = []
            self.artistNameToID[artistName].append(artistID)
        if self.debug:
            print("    Found {0} Name -> ID entries".format(len(self.artistNameToID)))
            
            
    ########################################################################################################
    #
    # Set Artist Album ID Mapping
    #
    ########################################################################################################
    def setAlbumIDMap(self):        
        if self.debug:
            print("  Getting Master Artist Album DB File ({0})".format(self.db))
            
        if self.known is True:
            self.albumsDB = self.disc.getMasterKnownArtistAlbumsDiscogsDB()
        else:
            self.albumsDB = self.disc.getMasterSlimArtistAlbumsDiscogsDB()
            
        if self.debug:
            if self.known is True:
                print("    Only loading a subset of known artists into memory.")
            print("    Found {0} Artist Albums".format(len(self.albumsDB)))
            
        if isinstance(self.albumsDB, DataFrame):
            if self.albumsDB.shape[0] == 0:
                self.albumsDB = Series()
                self.albumsDB.name = "Albums"
                return
           
        try:
            self.albumsDB = self.albumsDB["Albums"]
        except:
            raise ValueError("Error getting Albums from Artist Albums Database")
        
            
            
    ########################################################################################################
    #
    # Get Artist Data
    #
    ########################################################################################################
    def getNearestArtist(self, artistName, num=1, cutoff=0.9, debug=False):
        nearArtists = findNearest(artistName, self.getArtists(), num=num, cutoff=cutoff)
        if len(nearArtists) > 0:
            return nearArtists[0]
        return None

        
    def getArtistIDs(self, artistName, num=10, cutoff=0.7, debug=False):
        artistIDs = {}
        if self.artistNameToID.get(artistName) is not None:
            if debug is True:
                print("\tReturning ArtistIDs for Found ArtistName: {0}".format(artistName))
            artistIDs[artistName] = self.artistNameToID[artistName]
            return artistIDs
        elif num is None or cutoff is None:
            if debug is True:
                print("\tReturning Nothing Because Artist: {0} Was Not Found".format(artistName))
            return {}
        else:
            nearArtists = findNearest(artistName, self.getArtists(), num=num, cutoff=cutoff)
            if debug:
                print("Nearest Matches for: {0}".format(artistName))
            for nearArtist in nearArtists:
                artistIDs[nearArtist] = self.artistNameToID[nearArtist]
            return artistIDs
        
        return artistIDs
    
    
    def getArtistAlbums(self, artistID, flatten=False):
        if self.albumsDB is None:
            raise ValueError("Artist Albums not set!")
            
        if artistID is None:
            return {}
            
        if self.albumsDB.get(artistID) is None:
            print("# Artist ID [{0}] is not found in Albums DB [{1}]".format(artistID, self.db))
            return {}
        
        if flatten is True:
            return self.flattenedArtistAlbums(self.albumsDB[artistID])
        return self.albumsDB[artistID]
    

    def flattenedArtistAlbums(self, vals):
        if vals is None:
            return []
        if isinstance(vals, dict):
            albums = []
            for k,v in vals.items():
                if isinstance(v, dict):
                    for k2, v2 in v.items():
                        albums.append(v2)
                elif isinstance(v, list):
                    for v2 in v:
                        albums.append(v2)
                else:
                    raise ValueError("Need either a dict or list in flattenedArtistAlbums()")
            return list(set(albums))
        if isinstance(vals, list):
            albums = []
            for v in vals():
                if isinstance(v, list):
                    for v2 in v:
                        albums.append(v2)
                else:
                    raise ValueError("Need a list in flattenedArtistAlbums()")
            return list(set(albums))
        return []

            
            
    ########################################################################################################
    #
    # Summarize Artist Data
    #
    ########################################################################################################
    def getArtists(self):
        return self.artists
    
    def getNartistIDs(self):
        return len(self.artistIDToName)

    def getNartistNames(self):
        return len(self.artistNameToID)
    
    def getNalbums(self):
        try:
            nAlbums = sum([[len(v2) for v2 in v.values()][0] for k,v in self.albumsDB.items()])
        except:
            nAlbums = 0
        return nAlbums
    
    
    
    def summary(self):
        print("Summary Statistics For DB: {0}".format(self.db))
        print("    Using Known Artists: {0}".format(self.known))
        print("    Found {0} ID -> Name entries".format(self.getNartistIDs()))
        print("    Found {0} Name -> ID entries".format(self.getNartistNames()))
        print("    Found {0} Albums".format(self.getNalbums()))