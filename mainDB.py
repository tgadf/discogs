from masterdb import masterdb
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
    def __init__(self, mdb=None, create=False, debug=False):
        self.mdb    = mdb
        self.create = create
        self.debug  = debug

        self.slimArtistDB      = {}
        self.knownSlimArtistDB = {}

        self.slimArtistAlbumsDB      = {}
        self.knownSlimArtistAlbumsDB = {}
        
        self.dbdata = {}

        self.setDBBasic()
        #self.setDBs()
        
        
    def getDBs(self):
        return self.dbdata.keys()
        
        
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

        dbArtists = dbArtistsDatPiff()
        dbdata[dbArtists.db] = [dbArtists.disc, dbArtists, dbArtists.artist, dbArtists.dutils]

        dbArtists = dbArtistsAceBootlegs()
        dbdata[dbArtists.db] = [dbArtists.disc, dbArtists, dbArtists.artist, dbArtists.dutils]

        dbArtists = dbArtistsCDandLP()
        dbdata[dbArtists.db] = [dbArtists.disc, dbArtists, dbArtists.artist, dbArtists.dutils]

        dbArtists = dbArtistsRateYourMusic()
        dbdata[dbArtists.db] = [dbArtists.disc, dbArtists, dbArtists.artist, dbArtists.dutils]

        dbArtists = dbArtistsMusicStack()
        dbdata[dbArtists.db] = [dbArtists.disc, dbArtists, dbArtists.artist, dbArtists.dutils]


        keys   = ["Disc", "Artists", "Artist", "Utils"]
        for db in dbdata.keys():
            if self.debug:
                print("  Creating Database Records for {0}".format(db))
            dbdata[db] = dict(zip(keys, dbdata[db]))
            
        self.dbdata = dbdata
        if self.debug:
            print("Available DBs: {0}".format(", ".join(self.dbdata.keys())))
        
        
        
    #################################
    # Known DB Data
    #################################
    def setDBFull(self, db=None):
        if db is not None:
            dbs = [db]
        else:
            dbs = self.dbdata.keys()
            
        for db in dbs:
            disc  = self.dbdata[db]["Disc"]
            mymdb = masterdb(db, disc, force=self.create)
            if self.mdb is not None:
                mymdb.setMyMusicDB(self.mdb)
            if self.create is True:
                mymdb.createArtistIDMap()

            self.slimArtistDB[db]       = mymdb.getSlimArtistDB()
            
            if self.create is True:
                mymdb.createArtistAlbumIDMap()

            self.slimArtistAlbumsDB[db]      = mymdb.getSlimArtistAlbumsDB()


        
    #################################
    # Known DB Data
    #################################
    def setDBKnown(self, db=None):
        if db is not None:
            dbs = [db]
        else:
            dbs = self.dbdata.keys()
            
        for db in dbs:
            disc  = self.dbdata[db]["Disc"]
            mymdb = masterdb(db, disc, force=self.create)
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
    def getBasicArtistInfo(self, name):
        retval = []
        for db,artistDB in self.knownSlimArtistDB.items():
            result = artistDB[artistDB["DiscArtist"] == name].copy(deep=True)
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
            result = artistDB[artistDB["DiscArtist"] == name].copy(deep=True)
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