from timeUtils import clock, elapsed
from listUtils import getFlatList
from pandas import Series

class masterDBMatchClass:
    def __init__(self, maindb, mdbmaps):
        self.maindb  = maindb
        self.mdbmaps = mdbmaps

        print("Loading Artist Names")
        self.artistData  = {db: self.getArtistNameDB(db) for db in maindb.dbdata.keys()}        
        #self.matchData   = {db: self.getDBMatchData(db) for db in maindb.dbdata.keys()}
        
        self.clean()


    def getArtistNameDB(self, db):
        return self.maindb.dbdata[db]["Disc"].getMasterSlimArtistDiscogsDB()
        
    def getArtistAlbumsDB(self, db):
        return self.maindb.dbdata[db]["Disc"].getMasterSlimArtistAlbumsDiscogsDB()
        
    def clean(self):
        self.matchData = {db: None for db in self.maindb.dbdata.keys()}
                

    def setDBMatchData(self, dbName, matchData):
        self.matchData[dbName] = matchData
        
    def getDBMatchData(self, dbName, returnData=True):
        if self.matchData.get(dbName) is not None:
            return self.matchData[dbName]
        print("Loading Artist Albums")
        artistsDF = self.artistData[dbName]
        albumsDF  = self.getArtistAlbumsDB(dbName)
        
        dbArtistAlbums = artistsDF[["DiscArtist"]].join(albumsDF)
        dbArtistAlbums["Albums"] = dbArtistAlbums["Albums"].apply(lambda x: getFlatList([albums.values() for media,albums in x.items()]))
        matchData = {(dbArtistData["DiscArtist"], dbArtistID): dbArtistData["Albums"] for dbArtistID,dbArtistData in dbArtistAlbums.T.to_dict().items()}
        self.setDBMatchData(dbName, matchData)
        if returnData:
            return matchData
        
        
    def getArtistNameFromID(self, db, dbID):
        df  = self.artistData[db]
        adf = df[df.index == dbID]
        if adf.shape[0] == 1:
            retval = list(adf["DiscArtist"])[0]
            return retval
        else:
            return None
        
        
    def getDBPrimaryKeys(self, db):
        if self.matchData.get(db) is not None:
            matchData  = self.matchData[db]
        else:
            matchData  = self.getDBMatchData(db)
        dbPrimaryKeys = {primKey[1]: (primKey[0],primKey[1]) for primKey in matchData}
        return dbPrimaryKeys
        
    
    def getDataToMatch(self, db, maxValues=100, maxAlbums=100, sort=True):
        if self.matchData.get(db) is not None:
            matchData  = self.matchData[db]
        else:
            matchData  = self.getDBMatchData(db)
        nAlbums    = Series({primaryKey: len(albums) for primaryKey,albums in matchData.items()}).sort_values(ascending=False).to_dict()
        if sort is True:
            sortedKeys = nAlbums.keys()
        else:
            sortedKeys = matchData.keys()
        
        toMatch = []
        known   = 0
        manyAlbums = 0
        for primaryKey in sortedKeys:
            albums = matchData[primaryKey]
            if not self.mdbmaps[db].isKnownKey(primaryKey):
                if maxValues is not None:
                    if len(toMatch) >= maxValues:
                        continue
                if nAlbums[primaryKey] >= maxAlbums:
                    manyAlbums += 1
                    continue
                toMatch.append([primaryKey[0],primaryKey[1],albums])
            else:
                known += 1
                
        print("ToMatch   -> {0}".format(len(toMatch)))
        print("MaxAlbums -> {0}".format(manyAlbums))
        print("Known     -> {0}".format(known))
        print("Total     -> {0}".format(len(matchData)))
        return {db: toMatch}
    
    
    def getMutualEntries(self):        
        dbOrder = list(self.mdbmaps.keys())
        entryMap = {db: {db2: None for db2 in dbOrder} for db in dbOrder}
        
        for db1 in dbOrder:
            db1df = self.mdbmaps[db1].getDF().T
            for j,db2 in enumerate(dbOrder):
                db2MatchesFromdb1 = db1df[[db1,db2]]
                num = db2MatchesFromdb1[~db2MatchesFromdb1[db2].isna()].shape[0]
                entryMap[db1][db2] = num
            
        print("{0: <25}".format(""), end="")
        for db in entryMap.keys():
            print("{0: <15}".format(db), end="")
        print("")
        for db1,dbEntries in entryMap.items():
            print("{0: <25}".format(db1), end="")
            for db2,db2Entry in dbEntries.items():                
                print("{0: <15}".format(db2Entry), end="")
            print("")
        print("")
    
    
    def matchMutualMaps(self):
        start,cmt = clock("Mutual mapping it")
        dbOrder = list(self.mdbmaps.keys())
        for i,db1 in enumerate(dbOrder):
            print(i,'\t',db1)
            db1df = self.mdbmaps[db1].getDF().T
            for j,db2 in enumerate(dbOrder):
                if i == j:
                    continue
                if not db2 in db1df.columns: 
                    continue
                db2MatchesFromdb1 = db1df[[db1,db2]]
                db2MatchesFromdb1 = db2MatchesFromdb1[~db2MatchesFromdb1[db2].isna()]
                for key,row in db2MatchesFromdb1.iterrows():
                    db1MatchID   = row[db1]
                    db2MatchID   = row[db2]
                    db2MatchName = self.getArtistNameFromID(db2,db2MatchID)
                    #print('\t{0: <30}{1: <20}{2: <20}{3}'.format(key[0],db1MatchID,db2MatchID,db2MatchName))
                    mdbmaps[db2].addArtist(db2MatchName,db2MatchID)
                    mdbmaps[db2].addArtistData(db2MatchName,db2MatchID,db1,db1MatchID)

        for i,db in enumerate(dbOrder):
            self.mdbmaps[db].save()
            
        elapsed(start, cmt)