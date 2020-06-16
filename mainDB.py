from masterdb import masterdb
from pandas import concat

class mainDB:
    def __init__(self, mdb=None, create=False):
        self.mdb    = mdb
        self.create = create

        self.slimArtistDB      = {}
        self.knownSlimArtistDB = {}

        self.slimArtistAlbumsDB      = {}
        self.knownSlimArtistAlbumsDB = {}
        
        self.dbdata = {}

        self.setDBBasic()
        #self.setDBs()
        
        
    def setDBBasic(self):
        
        dbdata = {}
        keys   = ["Artists", "Artist", "Utils"]

        ### Discogs
        from artistsDC import artistsDC
        from artistDC import artistDC
        from discogsUtils import discogsUtils
        dbinfo = [artistsDC, artistDC, discogsUtils]
        dbinfo = dict(zip(keys, dbinfo))
        dbdata["Discogs"] = dbinfo

        ### AllMusic
        from artistsAM import artistsAM
        from artistAM import artistAM
        from discogsUtils import allmusicUtils
        dbinfo = [artistsAM, artistAM, allmusicUtils]
        dbinfo = dict(zip(keys, dbinfo))
        dbdata["AllMusic"] = dbinfo

        ### MusicBrainz
        from artistsMB import artistsMB
        from artistMB import artistMB
        from discogsUtils import musicbrainzUtils
        dbinfo = [artistsMB, artistMB, musicbrainzUtils]
        dbinfo = dict(zip(keys, dbinfo))
        dbdata["MusicBrainz"] = dbinfo

        ## AceBootlegs
        from artistAB import artistAB
        from artistsAB import artistsAB
        from discogsUtils import acebootlegsUtils
        dbinfo = [artistsAB, artistAB, acebootlegsUtils]
        dbinfo = dict(zip(keys, dbinfo))
        dbdata["AceBootlegs"] = dbinfo

        ## RateYourMusic
        from artistRM import artistRM
        from artistsRM import artistsRM
        from discogsUtils import rateyourmusicUtils
        dbinfo = [artistsRM, artistRM, rateyourmusicUtils]
        dbinfo = dict(zip(keys, dbinfo))
        dbdata["RateYourMusic"] = dbinfo

        ## LastFM
        from artistLM import artistLM
        from artistsLM import artistsLM
        from discogsUtils import lastfmUtils
        dbinfo = [artistsLM, artistLM, lastfmUtils]
        dbinfo = dict(zip(keys, dbinfo))
        dbdata["LastFM"] = dbinfo

        ## DatPiff
        from artistDP import artistDP
        from artistsDP import artistsDP
        from discogsUtils import datpiffUtils
        dbinfo = [artistsDP, artistDP, datpiffUtils]
        dbinfo = dict(zip(keys, dbinfo))
        dbdata["DatPiff"] = dbinfo

        ## RockCorner
        from artistRC import artistRC
        from artistsRC import artistsRC
        from discogsUtils import rockcornerUtils
        dbinfo = [artistsRC, artistRC, rockcornerUtils]
        dbinfo = dict(zip(keys, dbinfo))
        dbdata["RockCorner"] = dbinfo

        ## CDandLP
        from artistCL import artistCL
        from artistsCL import artistsCL
        from discogsUtils import cdandlpUtils
        dbinfo = [artistsCL, artistCL, cdandlpUtils]
        dbinfo = dict(zip(keys, dbinfo))
        dbdata["CDandLP"] = dbinfo

        ## MusicStack
        from artistMS import artistMS
        from artistsMS import artistsMS
        from discogsUtils import musicstackUtils
        dbinfo = [artistsMS, artistMS, musicstackUtils]
        dbinfo = dict(zip(keys, dbinfo))
        dbdata["MusicStack"] = dbinfo

        ## MetalStorm
        from artistMT import artistMT
        from artistsMT import artistsMT
        from discogsUtils import metalstormUtils
        dbinfo = [artistsMT, artistMT, metalstormUtils]
        dbinfo = dict(zip(keys, dbinfo))
        dbdata["MetalStorm"] = dbinfo

        ## General
        from discogsBase import discogs
        for db in dbdata.keys():
            print("Creating DB Info For {0}".format(db))
            dbdata[db]["Disc"]    = discogs(db.lower())
            dbdata[db]["Artist"]  = dbdata[db]["Artist"](dbdata[db]["Disc"])
            dbdata[db]["Artists"] = dbdata[db]["Artists"](dbdata[db]["Disc"])
            dbdata[db]["Utils"]   = dbdata[db]["Utils"]()
            
        self.dbdata = dbdata
        
        
        
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