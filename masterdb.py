from pandas import Series, DataFrame
from timeUtils import clock, elapsed
from ioUtils import saveFile, getFile
from difflib import SequenceMatcher
from searchUtils import findPatternExt
from fsUtils import setFile


class masterdb:
    def __init__(self, db, disc, force=False, debug=False):
        self.db    = db
        self.disc  = disc
        self.debug = debug
        self.force = force
        
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
            artistIDToName = self.disc["DiscArtist"].to_dict()
        except:
            raise ValueError("Could not find DiscArtist in columns {0}".format(disc.columns))

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

        print("  Finding Real Artist Name")
        discdf[["Artist", "Num"]] = DataFrame(discdf['Name'].apply(self.realName).tolist(), index=discdf.index)
        print("\tShape --> {0}".format(discdf.shape))

        print("  Removing None Artist")
        #discdf = discdf[~discdf["Artist"].isna()]
        print("\tShape --> {0}".format(discdf.shape))

        print("  Finding Disc Artist Name")
        discdf["DiscArtist"] = discdf['Artist'].apply(discConv)
        print("\tShape --> {0}".format(discdf.shape))

        if self.disc.base == "musicbrainz":
            print("  Cleaning Disc Artist Name (MusicBrainz Only)")
            discdf["DiscArtist"] = discdf['DiscArtist'].apply(cleanMB)
            print("\tShape --> {0}".format(discdf.shape))

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
    # Artist Albums DB
    ########################################################################################################################
    def getArtistAlbumsDB(self):        
        if self.force is True:
            self.createArtistAlbumIDMap()
        try:
            artistAlbumsDBDF = self.disc.getMasterArtistAlbumsDiscogsDB()
        except:
            artistAlbumsDBDF = DataFrame()
        return artistAlbumsDBDF

    def getKnownArtistAlbumsDB(self):        
        if self.force is True:
            self.createKnownArtistAlbumIDMap()
        try:
            knownArtistAlbumsDBDF = self.disc.getMasterKnownArtistAlbumsDiscogsDB()
        except:
            knownArtistAlbumsDBDF = DataFrame()
        return knownArtistAlbumsDBDF

    
    def createKnownArtistAlbumIDMap(self):
        start, cmt = clock("\n=================================== Creating Known Artist Album DB ===================================")
        artistAlbumsDBDF = self.getArtistAlbumsDB()
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
    
        
    def createArtistAlbumIDMap(self):
        start, cmt = clock("\n=================================== Creating Artist Album DB ===================================")
        
        print("Loading ArtistID Data")
        artistIDtoAlbumNames  = Series(self.disc.getArtistIDToAlbumNamesData())

        print("Creating Pandas DataFrame for {0} Artists".format(artistIDtoAlbumNames.shape[0]))
        cols = ["Albums"]
        discdf = DataFrame(artistIDtoAlbumNames)
        discdf.columns = cols
        print("\tShape --> {0}".format(discdf.shape))

        print("DataFrame Shape is {0}".format(discdf.shape))

        saveFilename = self.disc.getMasterArtistAlbumsDiscogsDBFilename()
        print("Saving Master Artist Albums DB File: {0}".format(saveFilename))
        saveFile(ifile=saveFilename, idata=discdf, debug=False)

        elapsed(start, cmt)




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



    
########################################################################################################################
#
# Music Pandas Functions 
#
########################################################################################################################
def getMusicData(discdf, key, value):
    retval = discdf[discdf[key] == value]
    if retval.shape[0] > 0:
        return retval
    else:
        return None
    
def getRowByIndex(pdf, idx):
    return pdf.loc[idx]    
    
    
    
########################################################################################################################
#
# Artist Name to ID Map
#
########################################################################################################################
def getArtistNameToIDMap(disc):
    start, cmt = clock("\n=================================== Creating Artist Name To ID Map ===================================")
    
    try:
        artistIDToName = disc["DiscArtist"].to_dict()
    except:
        raise ValueError("Could not find DiscArtist in columns {0}".format(disc.columns))
        
    artistNameToID = {}
    print("Found {0} ID -> Name entries".format(len(artistIDToName)))
    for artistID,artistName in artistIDToName.items():
        if artistNameToID.get(artistName) is None:
            artistNameToID[artistName] = []
        artistNameToID[artistName].append(artistID)
    print("Found {0} Name -> ID entries".format(len(artistNameToID)))
    return artistNameToID
    
    

########################################################################################################################
#
# Artist (Slim) DB
#
########################################################################################################################
def getSlimArtistDB(disc, mydb=None, force=False):
    start, cmt = clock("\n=================================== Creating Artist DB ===================================")
    if force is False:
        print("Using previously created Slim Artist DB")
        discdf = disc.getMasterSlimArtistDiscogsDB()
        elapsed(start, cmt)
        return discdf
    
    print("Loading ArtistID Data")
    artistIDtoName  = Series(disc.getArtistIDToNameData())
    artistIDtoRef   = Series(disc.getArtistIDToRefData())

    print("Creating Pandas DataFrame for {0} Artists".format(artistIDtoName.shape[0]))
    cols = ["Name"]
    discdf = DataFrame(artistIDtoName)
    discdf.columns = cols
    print("\tShape --> {0}".format(discdf.shape))
    
    print("  Finding Real Artist Name")
    discdf[["Artist", "Num"]] = DataFrame(discdf['Name'].apply(realName).tolist(), index=discdf.index)
    print("\tShape --> {0}".format(discdf.shape))
    
    print("  Removing None Artist")
    #discdf = discdf[~discdf["Artist"].isna()]
    print("\tShape --> {0}".format(discdf.shape))
        
    print("  Finding Disc Artist Name")
    discdf["DiscArtist"] = discdf['Artist'].apply(discConv)
    print("\tShape --> {0}".format(discdf.shape))
    
    if disc.base == "musicbrainz":
        print("  Cleaning Disc Artist Name (MusicBrainz Only)")
        discdf["DiscArtist"] = discdf['DiscArtist'].apply(cleanMB)
        print("\tShape --> {0}".format(discdf.shape))
    
    print("DataFrame Shape is {0}".format(discdf.shape))
    elapsed(start, cmt)

    print("Saving Master Artist DB File")
    saveFilename = disc.getMasterSlimArtistDiscogsDBFilename()
    saveFile(ifile=saveFilename, idata=discdf, debug=False)
    
    return discdf    

    

########################################################################################################################
#
# Artist DB
#
########################################################################################################################
def getArtistDB(disc, force=False):
    start, cmt = clock("\n=================================== Creating Artist DB ===================================")
    if force is False:
        print("Using previously created Artist DB")
        discdf = disc.getMasterArtistDiscogsDB()
        elapsed(start, cmt)
        return discdf
    
    print("Loading ArtistID Data")
    artistIDtoName  = Series(disc.getArtistIDToNameData())
    artistIDtoRef   = Series(disc.getArtistIDToRefData())
    artistIDToVariations  = Series(disc.getArtistIDToVariationsData())

    print("Creating Pandas DataFrame for {0} Artists".format(artistIDtoName.shape[0]))
    cols = ["Name"]
    discdf = DataFrame(artistIDtoName)
    discdf.columns = cols
    print("\tShape --> {0}".format(discdf.shape))

    print("  Joining Ref")
    discdf = discdf.join(DataFrame(artistIDtoRef))
    cols += ["Ref"]
    discdf.columns = cols
    print("\tShape --> {0}".format(discdf.shape))

    print("  Joining Variations")
    discdf = discdf.join(DataFrame(artistIDToVariations))
    cols += ["Variations"]
    discdf.columns = cols
    print("\tShape --> {0}".format(discdf.shape))

    discdf["Known"] = True
    
    print("  Finding Real Artist Name")
    discdf[["Artist", "Num"]] = DataFrame(discdf['Name'].apply(realName).tolist(), index=discdf.index)
    print("\tShape --> {0}".format(discdf.shape))

    

    print("DataFrame Shape is {0}".format(discdf.shape))
    elapsed(start, cmt)

    print("Saving Master Artist DB File")
    saveFilename = disc.getMasterArtistDiscogsDBFilename()
    saveFile(ifile=saveFilename, idata=discdf, debug=False)
    
    return discdf    
    
    
    

########################################################################################################################
#
# Artist Metadata DB
#
########################################################################################################################
def getArtistMetadataDB(disc, force=True):
    start, cmt = clock("\n=================================== Creating Artist Metadata DB ===================================")
    if force is False:
        print("Using previously created Artist Metadata DB")
        discdf = disc.getMasterArtistMetadataDiscogsDB()
        elapsed(start, cmt)
        return discdf
    
    print("Loading ArtistID Data")
    artistIDtoGenre          = Series(disc.getArtistIDToGenreData())
    artistIDtoStyle          = Series(disc.getArtistIDToStyleData())
    artistIDToCollaboration  = Series(disc.getArtistIDToCollaborationData())

    print("Creating Pandas DataFrame for {0} Artists".format(artistIDtoGenre.shape[0]))
    cols = ["Genre"]
    discdf = DataFrame(artistIDtoGenre)
    discdf.columns = cols
    print("\tShape --> {0}".format(discdf.shape))

    print("  Joining Style")
    discdf = discdf.join(DataFrame(artistIDtoStyle))
    cols += ["Style"]
    discdf.columns = cols
    print("\tShape --> {0}".format(discdf.shape))

    print("  Joining Collaboration")
    discdf = discdf.join(DataFrame(artistIDToCollaboration))
    cols += ["Collaboration"]
    discdf.columns = cols
    print("\tShape --> {0}".format(discdf.shape))

    print("DataFrame Shape is {0}".format(discdf.shape))
    elapsed(start, cmt)

    print("Saving Master Artist Metadata DB File")
    saveFilename = disc.getMasterArtistMetadataDiscogsDBFilename()
    saveFile(ifile=saveFilename, idata=discdf, debug=False)
    
    return discdf




########################################################################################################################
#
# Artist Albums DB
#
########################################################################################################################
def getArtistAlbumsDB(disc, loadRefs=False, force=False):
    start, cmt = clock("\n=================================== Creating Artist Albums DB ===================================")
    if force is False:
        print("Using previously created Artist Albums DB")
        discdf = disc.getMasterArtistAlbumsDiscogsDB()
        elapsed(start, cmt)
        return discdf
    
    print("Loading ArtistID Data")
    artistIDtoAlbumNames  = Series(disc.getArtistIDToAlbumNamesData())
    if loadRefs:
        artistIDtoAlbumRefs   = Series(disc.getArtistIDToAlbumRefsData())

    print("Creating Pandas DataFrame for {0} Artists".format(artistIDtoAlbumNames.shape[0]))
    cols = ["Albums"]
    discdf = DataFrame(artistIDtoAlbumNames)
    discdf.columns = cols
    print("\tShape --> {0}".format(discdf.shape))

    print("DataFrame Shape is {0}".format(discdf.shape))
    
    print("Saving Master Artist Albums DB File")
    saveFilename = disc.getMasterArtistAlbumsDiscogsDBFilename()
    saveFile(ifile=saveFilename, idata=discdf, debug=False)
    
    elapsed(start, cmt)
        
    return discdf






########################################################################################################################
#
# Artist Album Known DB
#
########################################################################################################################
def getArtistAlbumKnownDB(discAlbumDB, discArtistAlbumsDB):
    start, cmt = clock("\n=================================== Creating Artist Album DB ===================================")
    from pandas import Series, DataFrame
    
    idx=discAlbumDB.index
    
    tmpdb = discArtistAlbumsDB["Albums"].copy()
    print("Creating Pandas DataFrame for {0} Arist Albums".format(tmpdb.shape[0]))
    discdf = DataFrame(tmpdb.apply(isKnownAlbum, idx=idx).tolist(), index=tmpdb.index)
    discdf.columns = ["Known Albums", "All Albums", "Albums"]
    print("\tShape --> {0}".format(discdf.shape))
    
    print("DataFrame Shape is {0}".format(discdf.shape))
    elapsed(start, cmt)
    
    return discdf
    
def isKnownAlbum(x, **kwargs):
    retval = {}
    albumSummary = [0, 0]
    for mediaType in x.keys():
        for albumID in x[mediaType].keys():
            albumName = x[mediaType][albumID]
            #print(mediaType,albumID,albumName,'\t\t',end="")
            known     = albumID in kwargs['idx']
            #print(known)
            
            retval[albumID] = [albumName, mediaType, known]
            albumSummary[0] += known
            albumSummary[1] += 1
            
    return [albumSummary[0], albumSummary[1], retval]





########################################################################################################################
#
# Album DB
#
########################################################################################################################
def getAlbumDB(disc):
    start, cmt = clock("\n=================================== Creating Artist Album DB ===================================")
    from pandas import Series, DataFrame
    print("Loading AlbumID Data")
    albumIDtoName    = Series(disc.getAlbumIDToNameData())
    albumIDtoRef     = Series(disc.getAlbumIDToRefData())
    albumIDToArtists = Series(disc.getAlbumIDToArtistsData())

    print("Creating Pandas DataFrame for {0} Albums".format(albumIDtoName.shape[0]))
    cols = ["Name"]
    discdf = DataFrame(albumIDtoName)
    discdf.columns = cols
    print("\tShape --> {0}".format(discdf.shape))

    print("  Joining Ref")
    discdf = discdf.join(DataFrame(albumIDtoRef))
    cols += ["Ref"]
    discdf.columns = cols
    print("\tShape --> {0}".format(discdf.shape))

    print("  Joining Artists")
    discdf = discdf.join(DataFrame(albumIDToArtists))
    cols += ["Artists"]
    discdf.columns = cols
    print("\tShape --> {0}".format(discdf.shape))

    print("DataFrame Shape is {0}".format(discdf.shape))
    elapsed(start, cmt)
    
    return discdf





########################################################################################################################
#
# Master DB Join
#
########################################################################################################################
def createMasterDB(disc, discArtistDB, discArtistMetadataDB, discArtistAlbumKnownDB):
    start, cmt = clock("\n=================================== Creating Artist ID DB ===================================")
    print("Creating Pandas DataFrame for {0} Arist IDs".format(discArtistDB.shape[0]))
    print("  Joining Artist Metadata")
    discdf = discArtistDB.join(discArtistMetadataDB)
    print("\tShape --> {0}".format(discdf.shape))
    print("  Joining Artist Albums")
    discdf = discdf.join(discArtistAlbumKnownDB)
    print("\tShape --> {0}".format(discdf.shape))
    elapsed(start, cmt)

    savename = disc.getMasterDiscogsDBFilename()
    saveFile(idata=discdf, ifile=savename, debug=True)
    
    
    
    
    
    
########################################################################################################################
#
# Associated Functions
#
########################################################################################################################
def directoryName(x):
    if x is None:
        return x
    if "..." in x:
        x = x.replace("...", "")
    if "/" in x:
        x = x.replace("/", "-")
    return x

def realName(x):
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

def discConv(x):
    if x is None:
        return ""
    x = x.replace("/", "-")
    x = x.replace("¡", "")
    while x.startswith(".") and len(x) > 1:
        x = x[1:]
    x = x.strip()
    return x

def cleanMB(x):
    pos = [x.rfind("(")+1, x.rfind(")")]
    if sum([p > 0 for p in pos]) != len(pos):
        return x
    parval = x[pos[0]:pos[1]]
    return x[:pos[0]-2].strip()