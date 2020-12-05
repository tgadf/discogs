from matchAlbums import matchAlbums
from listUtils import getFlatList


class matchClass:
    def __init__(self, artistID, artistName, db, match):
        self.artistID = artistID
        self.artistName = artistName
        self.db = db
        if isinstance(match, dict):
            self.matchScore = match["Score"]
            self.matchID    = match["ID"]
            self.matchN     = match["Matches"]
        else:
            self.matchScore = None
            self.matchID    = None
            self.matchN     = None
            
    def show(self):
        if self.matchID is not None:
            print("{0} is matched to {1}. Found {2} matches with a max score of {3}".format(self.artistName, self.matchID, self.matchN, self.matchScore))
        else:
            print("{0} is unmatched".format(self.artistName)) 
            
        

class matchDBArtist:
    def __init__(self, maindb, debug=False):
        self.debug     = debug
        self.dbaccess  = maindb.dbdata
        self.dbdatamap = maindb.dbdatamap
        self.dbs       = list(self.dbdatamap.keys())
        
        self.matchNumArtistName     = None
        self.matchArtistNameCutoff  = None
        self.matchArtistAlbumCutoff = None
        self.matchNumArtistAlbums   = None
        self.matchScore             = None
        
        self.clean()
        self.setThresholds()

    def clean(self):
        self.setArtistInfo(None, None, None)
        
    def setArtistInfo(self, artistName, artistID, artistAlbums):
        self.artistName = artistName
        self.artistID   = artistID
        self.artistAlbums = artistAlbums
        
        
    #############################################################################
    # Matching Thresholds
    #############################################################################
    def setThresholds(self, matchNumArtistName=10, matchArtistNameCutoff=0.7, 
                      matchNumArtistAlbums=2, matchArtistAlbumCutoff=0.9, matchScore=1.5):
        self.matchNumArtistName     = matchNumArtistName
        self.matchArtistNameCutoff  = matchArtistNameCutoff
        self.matchNumArtistAlbums   = matchNumArtistAlbums
        self.matchArtistAlbumCutoff = matchArtistAlbumCutoff
        self.matchScore             = matchScore
        

    #############################################################################
    # Get List of Possible IDs for DBs
    #############################################################################
    def findPotentialArtistNameMatchesByDB(self, db):
        artistIDs = self.dbdatamap[db].getArtistIDs(self.artistName, self.matchNumArtistName,
                                                    self.matchArtistNameCutoff, debug=self.debug)
        return artistIDs
    
    def findPotentialArtistNameMatches(self):
        if self.debug:
            print("  Getting DB Artist IDs for ArtistName: {0}".format(self.artistName))
        artistIDs = {db: self.findPotentialArtistNameMatchesByDB(db) for db in self.dbs}
        return artistIDs
    
    def findPotentialArtistNameMatchesWithoutAlbums(self):
        ### Step 1: Get Artist IDs
        artistIDs = self.findPotentialArtistNameMatches()
        
        ### Step 2: Get Match For Each Pair
        dbMatches = {}
        for db, artistDBIDPairs in artistIDs.items():
            bestMatch = None
            if len(artistDBIDPairs) == 1:
                for artistDBName,artistDBIDs in artistDBIDPairs.items():
                    if len(artistDBIDs) == 1:
                        bestMatch = {"ID": artistDBIDs[0], "Matches": 0, "Score": 0}

            if bestMatch is None:
                mc = matchClass(self.artistID, self.artistName, db, None)
            else:
                mc = matchClass(self.artistID, self.artistName, db, bestMatch)
            dbMatches[db] = mc
        
        return dbMatches
    
    
    
        

    #############################################################################
    # Get List of Possible Matches for DBs (if Albums Are Available)
    #############################################################################
    def findPotentialArtistAlbumMatchesByDB(self, db):
        if self.artistName is None:
            raise ValueError("Artist Name is not set")
        if self.artistAlbums is None:
            raise ValueError("Artist Albums is not set")
        
        ### Step 1: Get Artist IDs
        artistDBIDPairs = self.findPotentialArtistNameMatchesByDB(db)

        
        ### Step 2: Get Match For Each Pair
        dbMatches = {}
        for artistDBName,artistDBIDs in artistDBIDPairs.items():
            for artistDBID in artistDBIDs:
                ### Step 2a: Get Albums
                dbArtistAlbums = self.dbdatamap[db].getArtistAlbums(artistDBID, flatten=True)
                
                ### Step 2b: Match
                ma = matchAlbums(cutoff=self.matchArtistAlbumCutoff)
                ma.match(self.artistAlbums, dbArtistAlbums)
                dbMatches[artistDBID] = ma
                
                

        ### Step 3: Find Best Match
        bestMatch = {"ID": None, "Matches": 0, "Score": 0.0}
        for artistDBID,ma in dbMatches.items():
            if ma.near < self.matchNumArtistAlbums:
                continue
            if ma.score < self.matchScore:
                continue
                
            if ma.near > bestMatch["Matches"]:
                bestMatch = {"ID": artistDBID, "Matches": ma.near, "Score": ma.score}
            elif ma.near == bestMatch["Matches"]:
                if ma.score > bestMatch["Score"]:
                    bestMatch = {"ID": artistDBID, "Matches": ma.near, "Score": ma.score}

        if bestMatch["ID"] is not None:
            mc = matchClass(self.artistID, self.artistName, db, bestMatch)
        else:
            mc = matchClass(self.artistID, self.artistName, db, None)
            
        return mc
    
    
    def findPotentialArtistAlbumMatches(self):
        if self.debug:
            print("  Getting DB Artist IDs for ArtistName: {0}".format(self.artistName))
        artistIDs = {db: self.findPotentialArtistAlbumMatchesByDB(db) for db in self.dbs}
        return artistIDs
    
    
    def findPotentialArtistAlbumMatchesByDBList(self, dbs):
        if self.debug:
            print("  Getting DB Artist IDs for ArtistName: {0}".format(self.artistName))
        artistIDs = {db: self.findPotentialArtistAlbumMatchesByDB(db) for db in dbs}
        return artistIDs