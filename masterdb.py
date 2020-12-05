from pandas import Series, DataFrame
from timeUtils import clock, elapsed
from ioUtils import saveFile, getFile
from difflib import SequenceMatcher
from searchUtils import findPatternExt
from fsUtils import setFile

from masterArtistNameDB import masterArtistNameDB
from multiArtist import multiartist

class masterdb:
    def __init__(self, db, disc, force=False, debug=False, artistColumnName="CleanDiscArtist"):
        self.db    = db
        self.disc  = disc
        self.debug = debug
        self.force = force
        
        self.manDB      = masterArtistNameDB("main")
        self.mularts = multiartist(cutoff=0.9, discdata=None, exact=False)
        self.mularts.setKnownMultiDelimArtists(["../multiartist/multiDelimArtists.p"])
        
        self.finalArtistName = artistColumnName
        
        self.mydb  = None
        
        self.artistIDToName = None
        self.artistNameToID = None
        
        
    def setMyMusicDB(self, mydb):
        self.mydb = mydb
        
      
    ########################################################################################################################
    #
    # Associated Functions
    #
    ########################################################################################################################
    def directoryName(self, x):
        if x is None:
            return x
        if "..." in x:
            x = x.replace("...", "")
        if "/" in x:
            x = x.replace("/", "-")
        return x

    def realName(self, x):
        if x is None:
            return [None,-1]

        lenx = len(x)
        if len(x) < 1:
            return [x,-1]

        if x[-1] != ")":
            return [x, None]


        if lenx >=5:
            if x[-3] == "(":
                try:
                    num = int(x[-2:-1])
                    val = x[:-3].strip()
                    return [val, num]
                except:
                    return [x, None]

        if lenx >= 6:
            if x[-4] == "(":
                try:
                    num = int(x[-3:-1])
                    val = x[:-4].strip()
                    return [val, num]
                except:
                    return [x, None]

        if lenx >= 7:
            if x[-4] == "(":
                try:
                    num = int(x[-3:-1])
                    val = x[:-4].strip()
                    return [val, num]
                except:
                    return [x, None]

        return [x, None]

    def discConv(self, x):
        if x is None:
            return ""
        x = x.replace("/", "-")
        x = x.replace("¡", "")
        while x.startswith(".") and len(x) > 1:
            x = x[1:]
        x = x.strip()
        return x

    def cleanMB(self, x):
        pos = [x.rfind("(")+1, x.rfind(")")]
        if sum([p > 0 for p in pos]) != len(pos):
            return x
        parval = x[pos[0]:pos[1]]
        return x[:pos[0]-2].strip()  
        
        
        
        
    ########################################################################################################################
    #
    #
    # Artist Information
    #
    #
    ########################################################################################################################
    

    ########################################################################################################################
    # Artist ID Map
    ########################################################################################################################
    def createArtistIDMap(self):
        start, cmt = clock("Creating Artist DBs")

        artistIDToName       = {}
        artistIDToRef        = {}
        artistIDToVariations = {}

        artistMetadataDBDir = self.disc.getArtistsMetadataDBDir()
        files = findPatternExt(artistMetadataDBDir, pattern="-Metadata", ext='.p')

        for i,ifile in enumerate(files):
            print(ifile,' \t',end="")
            db = getFile(ifile)
            artistIDToName.update({k: v[0] for k,v in db.items()})
            artistIDToRef.update({k: v[1] for k,v in db.items()})    
            artistIDToVariations.update({k: v[2] for k,v in db.items()})

            print(i,len(artistIDToName))
        print("\n\n==============================================\n")

        savenames = {"IDToRef": artistIDToRef, "IDToName": artistIDToName, "IDToVariations": artistIDToVariations}
        for basename,savedata in savenames.items():
            savename = setFile(self.disc.getDiscogDBDir(), "Artist{0}.p".format(basename))
            print("Saving {0} entries to {1}\n".format(len(savedata), savename))
            saveFile(ifile=savename, idata=savedata, debug=True)

        elapsed(start, cmt)



    
    ########################################################################################################################
    # Artist Name to ID Map
    ########################################################################################################################
    def setArtistNameToIDMap(self):
        start, cmt = clock("\n","="*25,"Creating Artist Name To ID Map","="*25)
        
        if self.disc is None:
            raise ValueError("Must set disc before calling this")

        try:
            artistIDToName = self.disc[self.finalArtistName].to_dict()
        except:
            raise ValueError("Could not find {0} in columns {1}".format(self.finalArtistName, disc.columns))

        artistNameToID = {}
        print("Found {0} ID -> Name entries".format(len(artistIDToName)))
        for artistID,artistName in artistIDToName.items():
            if artistNameToID.get(artistName) is None:
                artistNameToID[artistName] = []
            artistNameToID[artistName].append(artistID)
        print("Found {0} Name -> ID entries".format(len(artistNameToID)))
        
        return artistNameToID
        self.artistNameToID = artistNameToID
        self.artistIDToName = artistIDToName
        


    ########################################################################################################################
    # Artist (Slim) DB
    ########################################################################################################################
    def getSlimArtistDB(self):
        if self.force is True:
            self.createSlimArtistDB()
        discdf = self.disc.getMasterSlimArtistDiscogsDB()
        return discdf

    
    def getKnownSlimArtistDB(self):
        if self.force is True:
            self.createKnownSlimArtistDB()
        discdf = self.disc.getMasterKnownSlimArtistDiscogsDB()
        return discdf
    
        
    def createSlimArtistDB(self):
        start, cmt = clock("\n=================================== Creating Artist DB ===================================")
        
        print("Loading ArtistID Data")
        artistIDtoName  = Series(self.disc.getArtistIDToNameData())
        artistIDtoRef   = Series(self.disc.getArtistIDToRefData())

        print("Creating Pandas DataFrame for {0} Artists".format(artistIDtoName.shape[0]))
        cols = ["Name"]
        discdf = DataFrame(artistIDtoName)
        discdf.columns = cols
        print("\tShape --> {0}".format(discdf.shape))

        discdf["Ref"] = artistIDtoRef
        print("\tShape --> {0}".format(discdf.shape))

        print("  Finding Real Artist Name")
        discdf[["Artist", "Num"]] = DataFrame(discdf['Name'].apply(self.realName).tolist(), index=discdf.index)
        print("\tShape --> {0}".format(discdf.shape))

        print("  Removing None Artist")
        #discdf = discdf[~discdf["Artist"].isna()]
        print("\tShape --> {0}".format(discdf.shape))

        print("  Finding Disc Artist Name")
        discdf["DiscArtist"] = discdf['Artist'].apply(self.discConv)
        print("\tShape --> {0}".format(discdf.shape))

        if self.disc.base == "musicbrainz":
            print("  Cleaning Disc Artist Name (MusicBrainz Only)")
            discdf["DiscArtist"] = discdf['DiscArtist'].apply(self.cleanMB)
            print("\tShape --> {0}".format(discdf.shape))

        discdf["CleanDiscArtist"] = discdf['DiscArtist'].apply(self.manDB.renamed)
            
        discdf["MultiStatus"] = discdf['CleanDiscArtist'].apply(lambda x: len(self.mularts.getArtistNames(x)))
            
        print("DataFrame Shape is {0}".format(discdf.shape))
        elapsed(start, cmt)

        saveFilename = self.disc.getMasterSlimArtistDiscogsDBFilename()
        print("Saving Master Artist DB File: {0}".format(saveFilename))
        saveFile(ifile=saveFilename, idata=discdf, debug=False)
        
    
    def createKnownSlimArtistDB(self):
        start, cmt = clock("\n=================================== Creating Known Artist DB ===================================")
        slimArtistDF = self.disc.getMasterSlimArtistDiscogsDB()
        print("DataFrame Shape is {0}".format(slimArtistDF.shape))
        
        if self.mydb is None:
            raise ValueError("My Music DB Must Be Set")
        
        musicmap = self.mydb.get()
        mydbdata = {artistName: mdb.get(self.db) for artistName, mdb in musicmap.items() if mdb.get(self.db) is not None}
        myIDdata = [dbdata.get("ID") for artistName, dbdata in mydbdata.items() if dbdata.get("ID") is not None]
        discdf   = slimArtistDF[slimArtistDF.index.isin(myIDdata)]
        print("DataFrame Shape is {0}".format(discdf.shape))
        
        saveFilename = self.disc.getMasterKnownSlimArtistDiscogsDBFilename()
        print("Saving Master Known Artist DB File: {0}".format(saveFilename))
        saveFile(ifile=saveFilename, idata=discdf, debug=False)
        
        
        
        
    ########################################################################################################################
    #
    #
    # Artist Information
    #
    #
    ########################################################################################################################
        

    ########################################################################################################################
    # Artist Albums Map
    ########################################################################################################################
    def createArtistAlbumIDMap(self):
        start, cmt = clock("Creating Artist DBs")

        artistIDAlbumNames     = {}
        artistIDAlbumRefs      = {}
        artistIDCoreAlbumNames = {}
        artistIDCoreAlbumRefs  = {}

        artistMetadataDBDir = self.disc.getArtistsMetadataDBDir()
        files = findPatternExt(artistMetadataDBDir, pattern="-MediaMetadata", ext='.p')

        core = ["Albums"]
        nAllAlbums  = 0
        nCoreAlbums = 0
        for i,ifile in enumerate(files):
            print(ifile,'\t',end="")
            db = getFile(ifile)

            for j,(artistID,artistData) in enumerate(db.items()):
                artistIDAlbumNames[artistID]     = {}
                artistIDAlbumRefs[artistID]      = {}
                artistIDCoreAlbumNames[artistID] = {}
                artistIDCoreAlbumRefs[artistID]  = {}

                for mediaName,mediaData in artistData.items():
                    artistIDAlbumNames[artistID].update({mediaName: mediaData[0]})
                    artistIDAlbumRefs[artistID].update({mediaName: mediaData[1]})
                    nAllAlbums += len(mediaData[0])
                    if mediaName in core:
                        artistIDCoreAlbumNames[artistID].update({mediaName: mediaData[0]})
                        artistIDCoreAlbumRefs[artistID].update({mediaName: mediaData[1]})
                        nCoreAlbums += len(mediaData[0])

            print("{0: <10}{1: <10}{2: <10}".format(len(artistIDAlbumNames),nCoreAlbums,nAllAlbums))
        print("\n\n==============================================\n")


        savenames = {"IDToAlbumNames": artistIDAlbumNames, "IDToAlbumRefs": artistIDAlbumRefs, 
                     "IDToCoreAlbumNames": artistIDCoreAlbumNames, "IDToCoreAlbumRefs": artistIDCoreAlbumRefs}
        for basename,savedata in savenames.items():
            savename = setFile(self.disc.getDiscogDBDir(), "Artist{0}.p".format(basename))
            print("Saving {0} entries to {1}\n".format(len(savedata), savename))
            saveFile(ifile=savename, idata=savedata, debug=True)


        elapsed(start, cmt)



    ########################################################################################################################
    # Artist Albums DB
    ########################################################################################################################
    def getSlimArtistAlbumsDB(self):        
        if self.force is True:
            self.createSlimArtistAlbumIDMap()            
        artistAlbumsDBDF = self.disc.getMasterSlimArtistAlbumsDiscogsDB()
        return artistAlbumsDBDF

    def getKnownSlimArtistAlbumsDB(self):        
        if self.force is True:
            self.createKnownArtistAlbumIDMap()
        knownArtistAlbumsDBDF = self.disc.getMasterKnownArtistAlbumsDiscogsDB()
        return knownArtistAlbumsDBDF

    
    def createKnownArtistAlbumIDMap(self):
        start, cmt = clock("\n=================================== Creating Known Artist Album DB ===================================")
        
        artistAlbumsDBDF = self.getSlimArtistAlbumsDB()
        print("DataFrame Shape is {0}".format(artistAlbumsDBDF.shape))
        
        if self.mydb is None:
            raise ValueError("My Music DB Must Be Set")
        
        musicmap = self.mydb.get()
        mydbdata = {artistName: mdb.get(self.db) for artistName, mdb in musicmap.items() if mdb.get(self.db) is not None}
        myIDdata = [dbdata.get("ID") for artistName, dbdata in mydbdata.items() if dbdata.get("ID") is not None]
        discdf   = artistAlbumsDBDF[artistAlbumsDBDF.index.isin(myIDdata)]        
        print("DataFrame Shape is {0}".format(discdf.shape))

        saveFilename = self.disc.getMasterKnownArtistAlbumsDiscogsDBFilename()
        print("Saving Known Artist Albums DB File: {0}".format(saveFilename))
        saveFile(ifile=saveFilename, idata=discdf, debug=False)
    
        
    def createSlimArtistAlbumIDMap(self):
        start, cmt = clock("\n=================================== Creating Artist Album DB ===================================")
        
        print("Loading ArtistID Data")
        artistIDtoAlbumNames  = Series(self.disc.getArtistIDToAlbumNamesData())

        print("Creating Pandas DataFrame for {0} Artists".format(artistIDtoAlbumNames.shape[0]))
        cols = ["Albums"]
        discdf = DataFrame(artistIDtoAlbumNames)
        discdf.columns = cols
        print("\tShape --> {0}".format(discdf.shape))

        print("DataFrame Shape is {0}".format(discdf.shape))

        saveFilename = self.disc.getMasterSlimArtistAlbumsDiscogsDBFilename()
        print("Saving Master Artist Albums DB File: {0}".format(saveFilename))
        saveFile(ifile=saveFilename, idata=discdf, debug=False)

        elapsed(start, cmt)        
        

    ########################################################################################################################
    # Artist Metadata Map
    ########################################################################################################################
    def createArtistMetadataMap(self):
        start, cmt = clock("Creating Artist DBs")

        artistIDGenre          = {}
        artistIDStyle          = {}
        artistIDCollaborations = {}

        albumsMetadataDBDir = self.disc.getAlbumsMetadataDBDir()
        files = findPatternExt(albumsMetadataDBDir, pattern="-ArtistMetadata", ext='.p')

        for ifile in files:
            print(ifile,'\t',end="")
            for artistID,artistData in getFile(ifile).items():
                genre   = artistData['Genre']
                artistIDGenre[artistID] = genre
                artists = artistData['Artists']
                artistIDCollaborations[artistID] = artists
                style   = artistData['Style']
                artistIDStyle[artistID] = style
            print(len(artistIDGenre))
        print("\n\n==============================================\n")


        savenames = {"IDToGenre": artistIDGenre, "IDToStyle": artistIDStyle, "IDToCollaborations": artistIDCollaborations}
        for basename,savedata in savenames.items():
            savename = setFile(self.disc.getDiscogDBDir(), "Artist{0}.p".format(basename))
            print("Saving {0} entries to {1}\n".format(len(savedata), savename))
            saveFile(ifile=savename, idata=savedata, debug=True)   

        elapsed(start, cmt)


    ########################################################################################################################
    # Album ID Map
    ########################################################################################################################
    def createAlbumIDMap(self):
        start, cmt = clock("Creating Artist DBs")

        albumIDToName    = {}
        albumIDToRef     = {}
        albumIDToArtists = {}

        albumsMetadataDBDir = self.disc.getAlbumsMetadataDBDir()
        files = findPatternExt(albumsMetadataDBDir, pattern="-ArtistAlbums", ext='.p')
        for ifile in files:
            print(ifile,'\t',end="")
            for artistID,artistData in getFile(ifile).items():
                for albumID,albumData in artistData.items():
                    albumName    = albumData[0]
                    albumRef     = albumData[1]
                    albumCountry = albumData[2].most_common(1)[0]
                    albumYear    = albumData[3].most_common(1)[0]


                    albumIDToName[albumID] = albumName
                    albumIDToRef[albumID]  = albumRef

                    if albumIDToArtists.get(albumID) is None:                
                        albumIDToArtists[albumID] = []
                    albumIDToArtists[albumID].append(artistID)
            print(len(albumIDToArtists))
        print("\n\n==============================================\n")

        for albumID in albumIDToArtists.keys():
            albumIDToArtists[albumID] = list(set(albumIDToArtists[albumID]))
        print("\n\n==============================================\n")


        savenames = {"IDToName": albumIDToName, "IDToRef": albumIDToRef, "IDToArtists": albumIDToArtists}
        for basename,savedata in savenames.items():
            savename = setFile(self.disc.getDiscogDBDir(), "Album{0}.p".format(basename))
            print("Saving {0} entries to {1}\n".format(len(savedata), savename))
            saveFile(ifile=savename, idata=savedata, debug=True) 

        elapsed(start, cmt)