from masterdb import masterdb
from dbArtistMap import dbArtistMap
from pandas import concat
from dbArtistsDiscogs import dbArtistsDiscogs
from dbArtistsAllMusic import dbArtistsAllMusic
from dbArtistsMusicBrainz import dbArtistsMusicBrainz
from dbArtistsLastFM import dbArtistsLastFM
from dbArtistsRockCorner import dbArtistsRockCorner
from dbArtistsDatPiff import dbArtistsDatPiff
from dbArtistsAceBootlegs import dbArtistsAceBootlegs
from dbArtistsCDandLP import dbArtistsCDandLP
from dbArtistsRateYourMusic import dbArtistsRateYourMusic
from dbArtistsMusicStack import dbArtistsMusicStack


class mainDB:
    def __init__(self, mdb=None, create=False, debug=False, artistColumnName="CleanDiscArtist"):
        self.mdb    = None
        self.create = create
        self.debug  = debug

        self.slimArtistDB      = {}
        self.knownSlimArtistDB = {}

        self.slimArtistAlbumsDB      = {}
        self.knownSlimArtistAlbumsDB = {}
        
        self.dbdata    = {}
        self.dbdatamap = {}

        self.setDBBasic()
        #self.setDBs()
        
        self.artistColumnName = artistColumnName
        
        
    def getDBs(self):
        return self.dbdata.keys()
    
    
    def loadDBDataMap(self):    
        self.dbdatamap = {db: dbArtistMap(db) for db in self.getDBs()}


    def setDBBasic(self):
        if self.debug:
            print("Setting Basic Database Objects")

        dbdata = {}

        dbArtists = dbArtistsDiscogs()
        dbdata[dbArtists.db] = [dbArtists.disc, dbArtists, dbArtists.artist, dbArtists.dutils]

        dbArtists = dbArtistsAllMusic()
        dbdata[dbArtists.db] = [dbArtists.disc, dbArtists, dbArtists.artist, dbArtists.dutils]

        dbArtists = dbArtistsMusicBrainz()
        dbdata[dbArtists.db] = [dbArtists.disc, dbArtists, dbArtists.artist, dbArtists.dutils]

        dbArtists = dbArtistsLastFM()
        dbdata[dbArtists.db] = [dbArtists.disc, dbArtists, dbArtists.artist, dbArtists.dutils]

        dbArtists = dbArtistsRockCorner()
        dbdata[dbArtists.db] = [dbArtists.disc, dbArtists, dbArtists.artist, dbArtists.dutils]

        #dbArtists = dbArtistsDatPiff()
        #dbdata[dbArtists.db] = [dbArtists.disc, dbArtists, dbArtists.artist, dbArtists.dutils]

        dbArtists = dbArtistsAceBootlegs()
        dbdata[dbArtists.db] = [dbArtists.disc, dbArtists, dbArtists.artist, dbArtists.dutils]

        dbArtists = dbArtistsCDandLP()
        dbdata[dbArtists.db] = [dbArtists.disc, dbArtists, dbArtists.artist, dbArtists.dutils]

        dbArtists = dbArtistsRateYourMusic()
        dbdata[dbArtists.db] = [dbArtists.disc, dbArtists, dbArtists.artist, dbArtists.dutils]

        dbArtists = dbArtistsMusicStack()
        dbdata[dbArtists.db] = [dbArtists.disc, dbArtists, dbArtists.artist, dbArtists.dutils]


        keys   = ["Disc", "Artists", "Artist", "Utils"]
        if self.debug:
            print("Database Records:")
        for db in dbdata.keys():
            if self.debug:
                print("  Creating Database Records for {0}".format(db))
            dbdata[db] = dict(zip(keys, dbdata[db]))
            
        self.dbdata = dbdata
        if self.debug:
            print("Available DBs: {0}".format(", ".join(self.dbdata.keys())))
        
            

        
    ###################################################################################################
    # Known DB Data
    ###################################################################################################
    def setDBArtists(self, db=None, recreate=True):
        if db is not None:
            dbs = [db]
        else:
            dbs = self.dbdata.keys()
            
        for db in dbs:
            disc  = self.dbdata[db]["Disc"]
            mymdb = masterdb(db, disc, force=self.create, artistColumnName=self.artistColumnName)
            if self.create is True and recreate is True:
                mymdb.createArtistIDMap()
            self.slimArtistDB[db]       = mymdb.getSlimArtistDB()
            
            
    def setDBAlbums(self, db=None):
        if db is not None:
            dbs = [db]
        else:
            dbs = self.dbdata.keys()
            
        for db in dbs:
            disc  = self.dbdata[db]["Disc"]
            mymdb = masterdb(db, disc, force=self.create, artistColumnName=self.artistColumnName)
            if self.create is True:
                mymdb.createArtistAlbumIDMap()
            self.slimArtistAlbumsDB[db]      = mymdb.getSlimArtistAlbumsDB()
            
        
    def setDBFull(self, db=None, doAlbums=True):
        if db is not None:
            dbs = [db]
        else:
            dbs = self.dbdata.keys()
            
        for db in dbs:
            disc  = self.dbdata[db]["Disc"]
            mymdb = masterdb(db, disc, force=self.create, artistColumnName=self.artistColumnName)
            if self.mdb is not None:
                mymdb.setMyMusicDB(self.mdb)
            if self.create is True:
                mymdb.createArtistIDMap()

            self.slimArtistDB[db]       = mymdb.getSlimArtistDB()
            
            if doAlbums is False:
                continue
            
            if self.create is True:
                mymdb.createArtistAlbumIDMap()

            self.slimArtistAlbumsDB[db]      = mymdb.getSlimArtistAlbumsDB()


        
    ###################################################################################################
    # Known DB Data
    ###################################################################################################
    def setDBKnown(self, db=None):
        if db is not None:
            dbs = [db]
        else:
            dbs = self.dbdata.keys()
            
        for db in dbs:
            disc  = self.dbdata[db]["Disc"]
            mymdb = masterdb(db, disc, force=self.create, artistColumnName=self.artistColumnName)
            if self.mdb is not None:
                mymdb.setMyMusicDB(self.mdb)
            if self.create is True:
                mymdb.createArtistIDMap()

            self.knownSlimArtistDB[db]       = mymdb.getKnownSlimArtistDB()
            
            if self.create is True:
                mymdb.createArtistAlbumIDMap()

            self.knownSlimArtistAlbumsDB[db] = mymdb.getKnownSlimArtistAlbumsDB()


            
            

    def get(self):
        return self.dbdata
    
    def getDBData(self, db):
        return self.dbdata[db]
    
    def getKnownArtistDBs(self):
        return self.knownSlimArtistDB
    
    def getKnownArtistAlbumDBs(self):
        return self.knownSlimArtistAlbumsDB
    
    def getFullArtistDBs(self):
        return self.slimArtistDB
    
    def getFullArtistAlbumDBs(self):
        return self.slimArtistAlbumsDB
    
    
    
    
    
    ############################################################################################################
    # Helper Functions
    ############################################################################################################
    def getArtistDBKeys(self, dbName):
        masterDBDF = self.dbdata[dbName]["Disc"].getMasterSlimArtistDiscogsDB()
        #masterDBDF = self.slimArtistDB[db]
        artistDBKeys = list(zip(masterDBDF[self.artistColumnName], masterDBDF.index))
        return artistDBKeys
    
    
    def getArtistDBIDFromUtil(self, dbName, value):
        artistID = self.dbdata[dbName]["Utils"].getArtistID(value)
        return artistID
        
    
    def getArtistDBNameFromID(self, dbName, artistID):
        dbmap = self.dbdatamap.get(dbName)
        if dbmap is None:
            print("Could not find DB {0} in dbdatamap".format(dbName))
            return None
        artistName = dbmap.getArtistNameFromID(artistID)
        return artistName
    
    def getArtistDBIDFromName(self, dbName, artistName):
        dbmap = self.dbdatamap.get(dbName)
        if dbmap is None:
            print("Could not find DB {0} in dbdatamap".format(dbName))
            return None
        artistID = dbmap.getArtistIDFromName(artistName)
        return artistID
    
    def getArtistDBAlbumsFromID(self, dbName, artistID):
        dbmap = self.dbdatamap.get(dbName)
        if dbmap is None:
            print("Could not find DB {0} in dbdatamap".format(dbName))
            return None
        artistAlbums = dbmap.getArtistAlbums(artistID, flatten=True)
        return artistAlbums
        
    
    def getBasicArtistInfo(self, name):
        retval = []
        for db,artistDB in self.knownSlimArtistDB.items():
            result = artistDB[artistDB[self.finalArtistName] == name].copy(deep=True)
            if result.shape[0] == 0:
                continue
            if result.shape[0] > 1:
                raise ValueError("More than one artist match in db [{0}] for artist [{1}]".format(db, name))
            result.reset_index(inplace=True)
            result.index = [db]
            cols = list(result.columns)
            cols[0] = "ID"
            result.columns = cols
            retval.append(result)
        
        retval = concat(retval)
        return retval
    
    def getFullArtistInfo(self, name):
        retval = []
        for db,artistDB in self.slimArtistDB.items():
            result = artistDB[artistDB[self.finalArtistName] == name].copy(deep=True)
            if result.shape[0] == 0:
                continue
            if result.shape[0] > 1:
                raise ValueError("More than one artist match in db [{0}] for artist [{1}]".format(db, name))
            result.reset_index(inplace=True)
            result.index = [db]
            cols = list(result.columns)
            cols[0] = "ID"
            result.columns = cols
            retval.append(result)
        
        retval = concat(retval)
        return retval