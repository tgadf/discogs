from multiprocessing import Pool
import time

class parseDBArtistsData:
    def __init__(self, maindb, debug=False):
        self.debug=debug
        self.dbdata = maindb.dbdata

    def parseArtistsAM(self, modVal, force=False, doExtra=False):
        self.dbdata["AllMusic"]["Artists"].parseArtistModValFiles(modVal, force=force)
        #artsAM.parseArtistModValFiles(modVal, force=force)

    def parseArtistsDC(self, modVal, force=False, doExtra=False):
        self.dbdata["Discogs"]["Artists"].parseArtistModValFiles(modVal, force=force)
        #artsDC.parseArtistModValFiles(modVal, force=force)

    def parseArtistsMB(self, modVal, force=False, doExtra=False):
        self.dbdata["MusicBrainz"]["Artists"].parseArtistModValFiles(modVal, force=force)
        #artsMB.parseArtistModValFiles(modVal, force=force)

    def parseArtistsAB(self, modVal, force=False, doExtra=False):
        artsAB.parseArtistFiles(force=force)

    def parseArtistsDP(self, modVal, force=False, doExtra=False):
        self.dbdata['DatPiff']['Artists'].parseArtistFiles()
        #artsDP.parseArtistFiles(force=force)

    def parseArtistsRM(self, modVal, force=False, doExtra=False):
        self.dbdata["RateYourMusic"]["Artists"].parseArtistModValFiles(modVal, force=force)
        #artsRM.parseArtistModValFiles(modVal, force=force)

    def parseArtistsLM(self, modVal, force=False, doExtra=False):
        self.dbdata["LastFM"]["Artists"].parseArtistModValFiles(modVal, force=force)
        #artsLM.parseArtistModValFiles(modVal, force=force)

    def parseArtistsRC(self, modVal, force=False, doExtra=False):
        self.dbdata["RockCorner"]["Artists"].parseArtistModValFiles(modVal, force=force)
        #artsRC.parseArtistModValFiles(modVal, force=force)

    def parseArtistsCL(self, modVal, force=False, doExtra=False):
        self.dbdata["CDandLP"]["Artists"].parseArtistModValFiles(modVal, force=force)
        #artsCL.parseArtistModValFiles(modVal, force=force)

    def parseArtistsMS(self, modVal, force=False, doExtra=False):
        artsMS.parseArtistFiles(force=force)

    def parseArtistsMT(self, modVal, force=False, doExtra=False):
        artsMT.parseArtistModValFiles(modVal, force=force)


    def parse(self, db, nProcs=8, modVals=range(100), force=False):
        pool = Pool(processes=nProcs)
        if db == "Discogs":
            result = pool.map_async(self.parseArtistsDC, modVals)
        elif db == "AllMusic":
            result = pool.map_async(self.parseArtistsAM, range(100))
        elif db == "MusicBrainz":
            result = pool.map_async(self.parseArtistsMB, range(100))
        elif db == "AceBootlegs":
            result = pool.map_async(self.parseArtistsAB, [None])
        elif db == "DatPiff":
            result = pool.map_async(self.parseArtistsDP, [None])
        elif db == "RateYourMusic":
            dbdata["RateYourMusic"]["Artists"].parseDownloadedFiles()
            result = pool.map_async(self.parseArtistsRM, range(100))
        elif db == "LastFM":
            result = pool.map_async(self.parseArtistsLM, range(100))
        elif db == "RockCorner":
            result = pool.map_async(self.parseArtistsRC, range(100))
        elif db == "CDandLP":
            result = pool.map_async(self.parseArtistsCL, range(100))
            #result = pool.map_async(parseArtistsCL, range(56,72))
            #result = pool.map_async(parseArtistsCL, [55,25,26])
        elif db == "MusicStack":
            result = pool.map_async(self.parseArtistsMS, [None])
        elif db == "MetalStorm":
            result = pool.map_async(self.parseArtistsMT, range(100))
        else:
            raise ValueError("[{0}] is not recognized as a DB".format(db))

        while not result.ready():
            if force is True:
                time.sleep(10)
            else:
                time.sleep(1)
        print("")
        return result.get()