from multiprocessing import Pool
import time

class parseDBArtistsData:
    def __init__(self, maindb, debug=False, force=False):
        self.debug=debug
        self.dbdata = maindb.dbdata
        self.force = force

    def parseArtistsAM(self, modVal):
        self.dbdata["AllMusic"]["Artists"].parseArtistModValFiles(modVal, force=self.force)
        #artsAM.parseArtistModValFiles(modVal, force=self.force)

    def parseArtistsDC(self, modVal):
        self.dbdata["Discogs"]["Artists"].parseArtistModValFiles(modVal, force=self.force)
        #artsDC.parseArtistModValFiles(modVal, force=self.force)

    def parseArtistsMB(self, modVal):
        self.dbdata["MusicBrainz"]["Artists"].parseArtistModValFiles(modVal, force=self.force)
        #artsMB.parseArtistModValFiles(modVal, force=self.force)

    def parseArtistsAB(self, modVal):
        return
        #artsAB.parseArtistFiles(force=self.force)

    def parseArtistsDP(self, modVal):
        self.dbdata['DatPiff']['Artists'].parseArtistFiles()
        #artsDP.parseArtistFiles(force=self.force)

    def parseArtistsRM(self, modVal):
        self.dbdata["RateYourMusic"]["Artists"].parseArtistModValFiles(modVal, force=self.force)
        #artsRM.parseArtistModValFiles(modVal, force=self.force)

    def parseArtistsLM(self, modVal):
        self.dbdata["LastFM"]["Artists"].parseArtistModValFiles(modVal, force=self.force)
        #artsLM.parseArtistModValFiles(modVal, force=self.force)

    def parseArtistsRC(self, modVal):
        self.dbdata["RockCorner"]["Artists"].parseArtistModValFiles(modVal, force=self.force)
        #artsRC.parseArtistModValFiles(modVal, force=self.force)

    def parseArtistsCL(self, modVal):
        self.dbdata["CDandLP"]["Artists"].parseArtistModValFiles(modVal, force=self.force)
        #artsCL.parseArtistModValFiles(modVal, force=self.force)

    def parseArtistsMS(self, modVal):
        return
        #artsMS.parseArtistFiles(force=self.force)

    def parseArtistsMT(self, modVal):
        return
        #artsMT.parseArtistModValFiles(modVal, force=self.force)

        
    def parseMetadata(self, db, nProcs=5, modVals=range(100), force=None):
        print("Parsing {0} with {1} processes using [{2}] mod values.".format(db, nProcs, modVals))
        self.dbdata[db]["Artists"].parseArtistMetadataFiles()

    def parse(self, db, nProcs=8, modVals=range(100), force=None):
        if force is not None:
            self.force = force
        print("Parsing {0} with {1} processes using [{2}] mod values.".format(db, nProcs, modVals))
        pool = Pool(processes=nProcs)
        if db == "Discogs":
            result = pool.map_async(self.parseArtistsDC, modVals)
        elif db == "AllMusic":
            result = pool.map_async(self.parseArtistsAM, modVals)
        elif db == "MusicBrainz":
            result = pool.map_async(self.parseArtistsMB, modVals)
        elif db == "AceBootlegs":
            result = pool.map_async(self.parseArtistsAB, [None])
        elif db == "DatPiff":
            result = pool.map_async(self.parseArtistsDP, [None])
        elif db == "RateYourMusic":
            dbdata["RateYourMusic"]["Artists"].parseDownloadedFiles()
            result = pool.map_async(self.parseArtistsRM, modVals)
        elif db == "LastFM":
            result = pool.map_async(self.parseArtistsLM, modVals)
        elif db == "RockCorner":
            result = pool.map_async(self.parseArtistsRC, modVals)
        elif db == "CDandLP":
            result = pool.map_async(self.parseArtistsCL, modVals)
            #result = pool.map_async(parseArtistsCL, range(56,72))
            #result = pool.map_async(parseArtistsCL, [55,25,26])
        elif db == "MusicStack":
            result = pool.map_async(self.parseArtistsMS, [None])
        elif db == "MetalStorm":
            result = pool.map_async(self.parseArtistsMT, modVals)
        else:
            raise ValueError("[{0}] is not recognized as a DB".format(db))

        while not result.ready():
            if force is True:
                time.sleep(10)
            else:
                time.sleep(1)
        print("")
        return result.get()