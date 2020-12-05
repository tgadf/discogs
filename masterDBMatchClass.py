from timeUtils import clock, elapsed
from listUtils import getFlatList
from ioUtils import getFile
from pandas import Series, DataFrame

class masterDBMatchClass:
    def __init__(self, maindb, mdbmaps):
        self.maindb  = maindb
        self.mdbmaps = mdbmaps
        
        self.finalArtistName = maindb.artistColumnName

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
        print("  Setting matchData for {0}".format(dbName))
        self.matchData[dbName] = matchData
        
        
    def getDF(self, dbName):                
        matchData = self.getDBMatchData(dbName, returnData=True)
        df = DataFrame({primaryKey: {"Artist": artistData["ArtistName"], "Albums": len(artistData["ArtistAlbums"])} for primaryKey,artistData in matchData.items()}).T        
        return df
    
    
    def getMasterDF(self, dbName):
        df = self.getDF(dbName)
        amDF = self.mdbmaps[dbName].getDF()
        mergeDF = df.join(amDF).copy(deep=True)
        mergeDF["DBMatches"][mergeDF["DBMatches"].isna()] = 0
        mergeDF = mergeDF.sort_values("Albums", ascending=False)
        return mergeDF
    
        
    def getDBMatchData(self, dbName, returnData=True):
        if self.matchData.get(dbName) is not None:
            return self.matchData[dbName]
        print("Loading Artist Albums")
        try:
            artistsDF = self.artistData[dbName]
            albumsDF  = self.getArtistAlbumsDB(dbName)
        except:
            raise ValueError("Could not get artist/albums for DB {0} from [{1}]".format(dbName, list(self.artistData.keys())))
        
        dbArtistAlbums = artistsDF[[self.finalArtistName]].join(albumsDF)
        dbArtistAlbums["Albums"] = dbArtistAlbums["Albums"].apply(lambda x: getFlatList([albums.values() for media,albums in x.items()]))
        
        matchData = {self.mdbmaps[dbName].getPrimaryKey(artistName=dbArtistData[self.finalArtistName], artistID=dbArtistID): {"ArtistName": dbArtistData[self.finalArtistName], "ArtistAlbums": dbArtistData["Albums"]} for dbArtistID,dbArtistData in dbArtistAlbums.T.to_dict().items() if dbArtistID is not None and len(dbArtistData[self.finalArtistName]) > 0}
        self.setDBMatchData(dbName, matchData)
        if returnData:
            return matchData
        
        
    def getArtistNameFromID(self, db, dbID):
        print("Do I call this also???")
        1/0
        df  = self.artistData[db]
        adf = df[df.index == dbID]
        if adf.shape[0] == 1:
            retval = list(adf[self.finalArtistName])[0]
            return retval
        else:
            return None
        
        
    def getDBPrimaryKeys(self, db):
        print("Do I call this???")
        1/0
        if self.matchData.get(db) is not None:
            matchData  = self.matchData[db]
        else:
            matchData  = self.getDBMatchData(db)
        dbPrimaryKeys = {primKey[1]: (primKey[0],primKey[1]) for primKey in matchData}
        return dbPrimaryKeys
        
    
    def getDataToMatch(self, db, maxValues=100, maxAlbums=100, minAlbums=0, sort=True, useKnown=True, dbMatches=0, ignores=[]):
        if self.matchData.get(db) is not None:
            matchData  = self.matchData[db]
        else:
            matchData  = self.getDBMatchData(db)
            
        salbums    = Series({primaryKey: len(artistData["ArtistAlbums"]) for primaryKey,artistData in matchData.items()}).sort_values(ascending=False)
        known = self.mdbmaps[db].getArtists()
        mdDF = DataFrame(matchData).T
        artistIgnores = getFlatList([getFile(x) for x in ignores])
        print("Found {0} ignores".format(len(artistIgnores)))
        
        
        nAlbums    = salbums.to_dict()
        
        if sort is True:
            sortedKeys = nAlbums.keys()
        else:
            sortedKeys = matchData.keys()
        
        cuts = {"Total": salbums.shape[0]}
        
        togetSAlbums = salbums[salbums.index.isin(mdDF[~mdDF["ArtistName"].isin(artistIgnores)].index)]
        cuts["After Ignores"] = togetSAlbums.shape[0]
        
        if useKnown is True:
            togetSAlbums = togetSAlbums[~togetSAlbums.index.isin(known.keys())]
            cuts["After Known"] = togetSAlbums.shape[0]
        else:
            mbDF = self.mdbmaps[db].getDF()
            knownKeys = mbDF[mbDF.DBMatches == dbMatches].index
            togetSAlbums = togetSAlbums[togetSAlbums.index.isin(knownKeys)]
            cuts["After DB Matches"] = togetSAlbums.shape[0]
                    
        togetSAlbums = togetSAlbums[togetSAlbums < maxAlbums]
        cuts["After MaxAlbums"] = togetSAlbums.shape[0]
        
        togetSAlbums = togetSAlbums[togetSAlbums >= minAlbums]
        cuts["After MinAlbums"] = togetSAlbums.shape[0]
        
        togetSAlbums = togetSAlbums.head(maxValues)
        cuts["After MaxValues"] = togetSAlbums.shape[0]
        
        if 1 == 0:
            dbsToMatch = {}
            for primaryKey in togetSAlbums.index:
                dbs = [dbName for dbName,dbID in self.mdbmaps[db].getArtistDataByKey(primaryKey).getDict().items() if dbID is None]
                dbs = list(set(dbs).difference(set(["DatPiff", "MetalStorm"])))
                dbsToMatch[primaryKey] = dbs

            def getMissing(x):
                return list(x[x.isna()].index)
                missing = self.mdbmaps[db].getDF().apply(getMissing, axis=1)
        else:
            dbsToMatch = {}

        sMatchData = Series(matchData)
        toMatch = sMatchData[sMatchData.index.isin(togetSAlbums.index)].to_dict()
        toMatch = [[primaryKey, artistData, dbsToMatch.get(primaryKey)] for primaryKey, artistData in toMatch.items()]


        for k,v in cuts.items():
            print("{0: <20} -> {1}".format(k,v))
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