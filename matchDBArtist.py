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
            
        

class matchDBArtist:
    def __init__(self, maindb, debug=False):
        self.debug     = debug
        self.dbaccess  = maindb.dbdata
        self.dbdatamap = maindb.dbdatamap
        self.dbs       = list(self.dbdatamap.keys())
        self.clean()
        self.setThresholds()

    def clean(self):
        self.setArtistInfo(None, None, None)
        
    def setArtistInfo(self, artistName, artistID, artistAlbums):
        self.artistName = artistName
        self.artistID   = artistID
        self.artistAlbums = artistAlbums
        
    def setThresholds(self, num=10, cutoff=0.7, matchReq=0.85):
        self.num      = num
        self.cutoff   = cutoff
        self.matchReq = matchReq
        

    #############################################################################
    # Get List of Possible IDs for DBs
    #############################################################################
    def findPotentialArtistNameMatchesByDB(self, db):
        artistIDs = self.dbdatamap[db].getArtistIDs(self.artistName, self.num, self.cutoff, debug=self.debug)
        return artistIDs
    
    def findPotentialArtistNameMatches(self):
        if self.debug:
            print("  Getting DB Artist IDs for ArtistName: {0}".format(self.artistName))
        artistIDs = {db: self.findPotentialArtistNameMatchesByDB(db) for db in self.dbs}
        return artistIDs
    
    
    
        

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
                ma = matchAlbums(cutoff=self.cutoff)
                ma.match(self.artistAlbums, dbArtistAlbums)
                dbMatches[artistDBID] = ma
                
                

        ### Step 3: Find Best Match
        bestMatch = {"ID": None, "Matches": 0, "Score": 0.0}
        for artistDBID,ma in dbMatches.items():
            if ma.near == 0:
                continue
            if ma.score < self.matchReq:
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