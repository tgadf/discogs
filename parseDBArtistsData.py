from multiprocessing import Pool
from ioUtils import getFile, saveFile
import time

class parseDBArtistsData:
    def __init__(self, maindb, debug=False, force=False):
        self.debug=debug
        self.dbdata = maindb.dbdata
        self.force = force

        self.primary = True
        self.extra   = False
        self.credit  = False

        
    ####################################################################################################
    ## Discogs
    ####################################################################################################
    def parseArtistsDC(self, modVal):
        if self.primary is True:
            self.dbdata["Discogs"]["Artists"].parseArtistModValFiles(modVal, force=self.force)
        if self.extra is True:
            self.dbdata["Discogs"]["Artists"].parseArtistModValExtraFiles(modVal, force=False)

        
    ####################################################################################################
    ## AllMusic
    ####################################################################################################
    def parseArtistsAM(self, modVal):
        if self.credit is True:
            self.dbdata["AllMusic"]["Artists"].parseArtistModValCreditFiles(modVal, force=self.force)            
        else:
            self.dbdata["AllMusic"]["Artists"].parseArtistModValFiles(modVal, force=self.force)
            if False:
                ctds = getFile("creditToDownload.p")
                ctds.update(self.dbdata["AllMusic"]["Artists"].creditToDownload)
                saveFile(idata=ctds, ifile="creditToDownload.p")
        
    ####################################################################################################
    ## MusicBrainz
    ####################################################################################################
    def parseArtistsMB(self, modVal):
        if self.primary is True:
            self.dbdata["MusicBrainz"]["Artists"].parseArtistModValFiles(modVal, force=self.force)
        if self.extra is True:
            self.dbdata["MusicBrainz"]["Artists"].parseArtistModValExtraFiles(modVal, force=False)

        
    ####################################################################################################
    ## Last FM
    ####################################################################################################
    def parseArtistsLM(self, modVal):
        if self.primary is True:
            self.dbdata["LastFM"]["Artists"].parseArtistModValFiles(modVal, force=self.force)
        if self.extra is True:
            self.dbdata["LastFM"]["Artists"].parseArtistModValExtraFiles(modVal, force=False)
            

    ####################################################################################################
    ## Others
    ####################################################################################################
    def parseArtistsAB(self, modVal):
        return
        #artsAB.parseArtistFiles(force=self.force)

    def parseArtistsDP(self, modVal):
        self.dbdata['DatPiff']['Artists'].parseArtistFiles()
        #artsDP.parseArtistFiles(force=self.force)

    def parseArtistsRM(self, modVal):
        self.dbdata["RateYourMusic"]["Artists"].parseArtistModValFiles(modVal, force=self.force)
        #artsRM.parseArtistModValFiles(modVal, force=self.force)
            

    def parseArtistsRC(self, modVal):
        self.dbdata["RockCorner"]["Artists"].parseArtistModValFiles(modVal, force=self.force)
        #artsRC.parseArtistModValFiles(modVal, force=self.force)

    def parseArtistsCL(self, modVal):
        self.dbdata["CDandLP"]["Artists"].parseArtistModValFiles(modVal, force=self.force)
        #artsCL.parseArtistModValFiles(modVal, force=self.force)

    def parseArtistsMS(self, modVal):
        self.dbdata["MusicStack"]["Artists"].parseArtistModValFiles(modVal, force=self.force)        
        return
        #artsMS.parseArtistFiles(force=self.force)

    def parseArtistsMT(self, modVal):
        return
        #artsMT.parseArtistModValFiles(modVal, force=self.force)

        
    def parseMetadata(self, db, nProcs=5, modVals=range(100), force=None):
        print("Parsing {0} with {1} processes using [{2}] mod values.".format(db, nProcs, modVals))
        self.dbdata[db]["Artists"].parseArtistMetadataFiles()

        
    def parseDownloads(self, db):
        if db == "RateYourMusic":
            self.dbdata["RateYourMusic"]["Artists"].parseDownloadedFiles()
        if db == "MusicStack":
            self.dbdata["MusicStack"]["Artists"].parseDownloadedFiles()
        
        
    def parse(self, db, nProcs=8, modVals=range(100), force=None, primary=True, extra=False, credit=False):
        self.primary = primary
        self.extra   = extra
        self.credit  = credit
        if self.extra is True:
            self.primary = False
            self.credit  = False
        elif self.credit is True:
            self.primary = False
            self.extra   = False
        elif self.primary is True:
            self.credit  = False
            self.extra   = False

        
        print("DB: {0} --> Primary={1}   Extra={2}   Credit={3}".format(db, self.primary, self.extra, self.credit))
        
        
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
            result = pool.map_async(self.parseArtistsMS, modVals)
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