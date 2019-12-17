from pandas import Series, DataFrame
from timeUtils import clock, elapsed
from ioUtils import saveFile, getFile
from searchUtils import findPatternExt
from fsUtils import setFile





########################################################################################################################
#
# Artist ID Map
#
########################################################################################################################
def createArtistIDMap(disc):
    start, cmt = clock("Creating Artist DBs")

    artistIDToName       = {}
    artistIDToRef        = {}
    artistIDToVariations = {}

    artistMetadataDBDir = disc.getArtistsMetadataDBDir()
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
        savename = setFile(disc.getDiscogDBDir(), "Artist{0}.p".format(basename))
        print("Saving {0} entries to {1}\n".format(len(savedata), savename))
        saveFile(ifile=savename, idata=savedata, debug=True)

    elapsed(start, cmt)
    
    
    
    
########################################################################################################################
#
# Artist Albums Map
#
########################################################################################################################
def createArtistAlbumIDMap(disc):
    start, cmt = clock("Creating Artist DBs")

    artistIDAlbumNames     = {}
    artistIDAlbumRefs      = {}
    artistIDCoreAlbumNames = {}
    artistIDCoreAlbumRefs  = {}

    artistMetadataDBDir = disc.getArtistsMetadataDBDir()
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
                nAllAlbums += len(artistIDAlbumNames[artistID].values())
                if mediaName in core:
                    artistIDCoreAlbumNames[artistID].update({mediaName: mediaData[0]})
                    artistIDCoreAlbumRefs[artistID].update({mediaName: mediaData[1]})
                    nCoreAlbums += len(artistIDCoreAlbumNames[artistID].values())

        print("{0: <10}{1: <10}{2: <10}".format(len(artistIDAlbumNames),nCoreAlbums,nAllAlbums))
    print("\n\n==============================================\n")


    savenames = {"IDToAlbumNames": artistIDAlbumNames, "IDToAlbumRefs": artistIDAlbumRefs, 
                 "IDToCoreAlbumNames": artistIDCoreAlbumNames, "IDToCoreAlbumRefs": artistIDCoreAlbumRefs}
    for basename,savedata in savenames.items():
        savename = setFile(disc.getDiscogDBDir(), "Artist{0}.p".format(basename))
        print("Saving {0} entries to {1}\n".format(len(savedata), savename))
        saveFile(ifile=savename, idata=savedata, debug=True)


    elapsed(start, cmt)
    
    
    
    
    
    
########################################################################################################################
#
# Artist Metadata Map
#
########################################################################################################################
def createArtistMetadataMap(disc):
    start, cmt = clock("Creating Artist DBs")

    artistIDGenre          = {}
    artistIDStyle          = {}
    artistIDCollaborations = {}

    albumsMetadataDBDir = disc.getAlbumsMetadataDBDir()
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
        savename = setFile(disc.getDiscogDBDir(), "Artist{0}.p".format(basename))
        print("Saving {0} entries to {1}\n".format(len(savedata), savename))
        saveFile(ifile=savename, idata=savedata, debug=True)   

    elapsed(start, cmt)
    
    
    
    
    
########################################################################################################################
#
# Album ID Map
#
########################################################################################################################
def createAlbumIDMap(disc):
    start, cmt = clock("Creating Artist DBs")

    albumIDToName    = {}
    albumIDToRef     = {}
    albumIDToArtists = {}

    albumsMetadataDBDir = disc.getAlbumsMetadataDBDir()
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
        savename = setFile(disc.getDiscogDBDir(), "Album{0}.p".format(basename))
        print("Saving {0} entries to {1}\n".format(len(savedata), savename))
        saveFile(ifile=savename, idata=savedata, debug=True) 

    elapsed(start, cmt)
    
    
    
    
    
########################################################################################################################
#
# Test Lookup Maps
#
########################################################################################################################
def testLookupMaps(disc):
    print("Testing ArtistID --> Name")
    discdf = disc.getArtistIDToNameData()
    print("\tDim = {0}".format(len(discdf)))
    print("")

    print("Testing ArtistID --> Ref")
    discdf = disc.getArtistIDToRefData()
    print("\tDim = {0}".format(len(discdf)))
    print("")

    print("Testing ArtistID --> Variations")
    discdf = disc.getArtistIDToRefData()
    print("\tDim = {0}".format(len(discdf)))
    print("")

    print("Testing ArtistID --> Genre")
    discdf = disc.getArtistIDToGenreData()
    print("\tDim = {0}".format(len(discdf)))
    print("")

    print("Testing ArtistID --> Style")
    discdf = disc.getArtistIDToStyleData()
    print("\tDim = {0}".format(len(discdf)))
    print("")

    print("Testing ArtistID --> Collaborations")
    discdf = disc.getArtistIDToCollaborationData()
    print("\tDim = {0}".format(len(discdf)))
    print("")

    print("Testing ArtistID --> Album Names")
    discdf = disc.getArtistIDToAlbumNamesData()
    print("\tDim = {0}".format(len(discdf)))
    print("")

    print("Testing ArtistID --> Album Refs")
    discdf = disc.getArtistIDToAlbumRefsData()
    print("\tDim = {0}".format(len(discdf)))
    print("")

    print("Testing ArtistID --> Core Album Names")
    discdf = disc.getArtistIDToCoreAlbumNamesData()
    print("\tDim = {0}".format(len(discdf)))
    print("")

    print("Testing ArtistID --> Core Album Refs")
    discdf = disc.getArtistIDToCoreAlbumRefsData()
    print("\tDim = {0}".format(len(discdf)))
    print("")

    print("Testing AlbumID --> Album Names")
    discdf = disc.getAlbumIDToNameData()
    print("\tDim = {0}".format(len(discdf)))
    print("")

    print("Testing AlbumID --> Album Refs")
    discdf = disc.getAlbumIDToRefData()
    print("\tDim = {0}".format(len(discdf)))
    print("")

    print("Testing AlbumID --> Artists")
    discdf = disc.getAlbumIDToArtistsData()
    print("\tDim = {0}".format(len(discdf)))
    print("")