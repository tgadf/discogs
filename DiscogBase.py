#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 16 18:11:35 2017

@author: tgadfort
"""

import sys
from hashlib import md5
from collections import Counter

if '/Users/tgadfort/Python' not in sys.path:
    sys.path.insert(0, '/Users/tgadfort/Python')

from fileio import get, save 
from fileinfo import getBaseFilename, getBasename, getDirname
from fsio import setDir, mkSubDir, setFile, moveFile, moveDir, setSubFile, removeFile, isFile
from search import findSubExt, findSubDirs, findExt, findDirs
from strops import makeStrFromUnicode, makeUnicode
from timing import start,inter,end

from DiscogPath import getBaseDBDir, getArtistsDir, getArtistsDBDir, getDiscogDir, getAlbumsDir, getAlbumsDBDir, getArtistsExtraDir, getSearchDir
from albumdata import getAlbumCode
from artistdata import parse
from htmlParser import getHTML

###############################################################################
#
# Slim Counts File
#
###############################################################################
def slimArtistCounts(minCounts, debug = False):
    print "Producing Slimmed DBs."

    startVal = start()
    artistCounts     = getArtistCounts(slim = False, debug = True)
    inter(startVal,1,6)
    
    #artistRefs       = getArtistRefs(False, debug = True)
    discIDs          = []
    for item in artistCounts.most_common():
        cnt    = item[1]
        discID = item[0]
        if cnt >= minCounts:
            discIDs.append(discID)

    print "Keeping",len(discIDs),"of",len(artistCounts)

    artistDB         = getArtistDB(slim = False, debug = True)
    inter(startVal,2,6)
    slimArtistDB     = { discID: artistDB[discID] for discID in discIDs }
    inter(startVal,3,6)
    artistRefs       = getArtistRefs(slim = False, debug = True)
    inter(startVal,4,6)
    slimArtistRefs   = { discID: artistRefs[discID] for discID in discIDs }
    inter(startVal,5,6)
    slimArtistNames  = {v: makeStrFromUnicode(k) for k, v in slimArtistDB.iteritems()}

    saveArtistDB(slimArtistDB, slim = True)
    saveArtistRefs(slimArtistRefs, slim = True)
    saveArtistNameDB(slimArtistNames, slim = True)

    end(startVal)


###############################################################################
#
# Discog Basic Counts Files
#
###############################################################################
def getBaseDB(dbname, ext = "yaml", slim = False, debug = True):
    basedir  = getBaseDBDir()
    name     = dbname+"."+ext
    if slim:
        name = dbname+"Slim."+ext
    ifile    = setFile(basedir, name)
    if debug: print "Loading",ifile,"..."    
    data  = get(ifile)
    if debug: print "Loading",ifile,"... Found",len(data),"artists."
    return data

    
def saveBaseDB(dbname, db, slim, ext = "yaml", debug = True):
    basedir  = getBaseDBDir()
    savename = setFile(basedir, dbname+"."+ext)
    if slim:
        savename = setFile(basedir, dbname+"Slim."+ext)
    if debug: print "Saving",len(db),"artist counts to",savename
    save(savename, db)
    


def saveArtistCounts(artistCounts, slim = False, debug = False):
    ext = "json"
    saveBaseDB("artistCounts", artistCounts, slim, ext, debug)

def getArtistCounts(slim = False, debug = False):
    ext = "json"
    return Counter(getBaseDB("artistCounts", ext, slim, debug))



def saveArtistDB(artistDB, slim = False, debug = False):
    ext = "json"
    saveBaseDB("artistDB", artistDB, slim, ext, debug)

def getArtistDB(slim = False, debug = False):
    ext = "json"
    return getBaseDB("artistDB", ext, slim, debug)



def saveArtistRefs(artistRefs, slim = False, debug = False):
    ext = "yaml"
    saveBaseDB("artistRefs", artistRefs, slim, ext, debug)

def getArtistRefs(slim = False, debug = False):
    ext = "yaml"
    return getBaseDB("artistRefs", ext, slim, debug)



def saveArtistNames(artistNames, slim = False, debug = False):
    ext = "yaml"
    saveBaseDB("artistNames", artistNames, slim, ext, debug)

def getArtistNames(slim = False, debug = False):
    ext = "yaml"
    return getBaseDB("artistNames", ext, slim, debug)



def saveArtistNameIDs(artistNameIDs, slim = False, debug = False):
    ext = "yaml"
    saveBaseDB("artistNameIDs", artistNameIDs, slim, ext, debug)
    
def getArtistNameIDs(slim = False, debug = False):
    ext = "yaml"
    return getBaseDB("artistNameIDs", ext, slim, debug)

def makeArtistNameIDs(slim = False, debug = False):
    data = getArtistNames(debug = True)
    artistNameIDs = {makeStrFromUnicode(v): k for k, v in data.iteritems()}
    if artistNameIDs.get(None):
        del artistNameIDs[None]
    saveArtistNameIDs(artistNameIDs, debug = True)



def saveKnownArtistIDs(artistKnownIDs, debug = False):
    ext = "json"
    slim = False
    saveBaseDB("knownArtistIDs", artistKnownIDs, slim, ext, debug)

def getKnownArtistIDs(debug = False):
    ext = "json"
    slim = False
    return getBaseDB("knownArtistIDs", ext, slim, debug)

    

###############################################################################
#
# Discog Hash Functions
#
###############################################################################
def getHashVal(artist, href):
    m = md5()
    if artist: m.update(artist)
    if href:   m.update(href)
    retval = m.hexdigest()
    return retval

def getHashMod(hashval, modval = 500):
    ival = int(hashval, 16)
    return ival % modval

def getDiscIDHashMod(discID, modval = 500):
    if discID == None:
        return -1
    ival = int(discID)
    return ival % modval

def getArtistHashVal(artist, href):
    artist = makeStrFromUnicode(artist)
    hashval = getHashVal(artist, href)
    return hashval

def getFileHashVal(ifile):
    fname = getBaseFilename(ifile)
    hname = makeStrFromUnicode(fname)
    hashval = getHashVal(hname, None)
    return hashval

def getArtistHashMod(artist, href, modval = 500):
    hashval = getArtistHashVal(artist,href)
    return getHashMod(hashval, modval)

def getFileHashMod(ifile, modval = 50):
    hashval = getFileHashVal(ifile)
    return getHashMod(hashval, modval)


    


###############################################################################
#
# Merge DBs
#
###############################################################################
def mergeArtistDBs(onlyDB = True):

    newCnts     = getBaseDB("artistCountsNew", slim = False, ext = "json", debug = True)
    data = getArtistDB(slim = False, debug = True)
    ids  = dict(data.items() + newCnts.items())
    saveArtistCounts(ids, slim=False, debug=True)

    newDBs     = getBaseDB("artistDBNew", slim = False, ext = "json", debug = True)
    data = getArtistDB(slim = False, debug = True)
    ids  = dict(data.items() + newDBs.items())
    saveArtistDB(ids, slim=False, debug=True)

    if onlyDB == False:
        newRefs    = getBaseDB("artistRefsNew", slim = False, ext = "yaml", debug = True)
        data = getArtistRefs(slim = False, debug = True)
        refs = dict(data.items() + newRefs.items())
        saveArtistRefs(refs, slim=False, debug=True)

    
        newNames   = getBaseDB("artistNamesNew", slim = False, ext = "yaml", debug = True)
        data  = getArtistNames(slim = False, debug = True)
        names = dict(data.items() + newNames.items())
        saveArtistNames(names, slim=False, debug=True)
    
        newNameIDs = getBaseDB("artistNameIDsNew", slim = False, ext = "yaml", debug = True)
        data    = getArtistNameIDs(slim = False, debug = True)
        nameIDs = dict(data.items() + newNameIDs.items())
        saveArtistNameIDs(nameIDs, slim=False, debug=True)
   
    
###############################################################################
#
# Downloaded Artists DB
#
###############################################################################


###############################################################################
#
# Add New Artists To DBs
#
###############################################################################
def getNewDBs():
    
    try:
        newIDs     = getBaseDB("artistDBNew", slim = False, ext = "json", debug = True)
    except:
        newIDs     = {}

    try:
        newCnts    = getBaseDB("artistCountsNew", slim = False, ext = "json", debug = True)
    except:
        newCnts     = {}

    try:
        newRefs    = getBaseDB("artistRefsNew", slim = False, ext = "yaml", debug = True)
    except:
        newRefs    = {}

    try:
        newNames   = getBaseDB("artistNamesNew", slim = False, ext = "yaml", debug = True)
    except:
        newNames   = {}

    try:
        newNameIDs = getBaseDB("artistNameIDsNew", slim = False, ext = "yaml", debug = True)
    except:
        newNameIDs = {}
    
    return newIDs, newCnts, newRefs, newNames, newNameIDs


def saveNewDBs(newToDB):
    
    newIDs, newCnts, newRefs, newNames, newNameIDs = getNewDBs()
    
    tmpnewIDs       = {k: 1 for k in newToDB.keys()}
    artistDBNew     = dict(tmpnewIDs.items() + newIDs.items())
    
    tmpnewCnts      = {k: 1 for k in newToDB.keys()}
    artistCountsNew = dict(tmpnewCnts.items() + newCnts.items())
    
    tmpnewRefs      = {k: v["URL"] for k,v in newToDB.iteritems()}
    artistRefsNew   = dict(tmpnewRefs.items() + newRefs.items())
    
    tmpnewNames     = {k: v["Name"] for k,v in newToDB.iteritems()}    
    artistNames     = dict(tmpnewNames.items() + newNames.items())
    
    tmpnewNameIDs   = {v["Name"]: k for k,v in newToDB.iteritems()}
    artistNameIDs   = dict(tmpnewNameIDs.items() + newNameIDs.items())
    
    
    saveBaseDB("artistDBNew", artistDBNew, slim = False, ext = "json", debug = True)
    saveBaseDB("artistCountsNew", artistCountsNew, slim = False, ext = "json", debug = True)
    saveBaseDB("artistRefsNew", artistRefsNew, slim = False, ext = "yaml", debug = True)
    saveBaseDB("artistNamesNew", artistNames, slim = False, ext = "yaml", debug = True)
    saveBaseDB("artistNameIDsNew", artistNameIDs, slim = False, ext = "yaml", debug = True)
    
    
    
def fixArtistDBs(debug = True):
    artistsDBDir = getArtistsDBDir()
    files = findExt(artistsDBDir, ext=".p")
    print "Finding files... Found",len(files),"files."
    noData = {}
    for i, ifile in enumerate(files):
        data = get(ifile)
        saveIt = False
        for discID in data.keys():
            discogArtistData = data[discID]["Media"]
            if discogArtistData == None:
                print "No Media:",discID
                noData[discID] = 1
                continue
            
            for mediaType in discogArtistData.keys():
                mediaData = discogArtistData[mediaType]
                if isinstance(mediaData,list):
                    saveIt = True
                    newMediaData = {}
                    for albumData in mediaData:
                        albumID = albumData['Code']
                        newMediaData[albumID] = albumData
                        del newMediaData[albumID]['Code']
                    data[discID]["Media"][mediaType] = newMediaData

        if saveIt:
            save(ifile, data)
    
    savename = "/Users/tgadfort/Documents/music/MusicDB/artistsWithNoDiscogMatch.yaml"
    save(savename, noData, debug)
    
    
    
def findArtistVariations(modVal=500):
    artistsDBDir = getArtistsDBDir()
    artistDB     = getArtistDB()
    files = findExt(artistsDBDir, ext=".p")
    print "Finding files... Found",len(files),"files."
    
    toGet = {}
    for i,ifile in enumerate(files):
        print "Checking db:",ifile,'\t',len(toGet)
        data = get(ifile, debug = True)
        for discID,artistData in data.iteritems():
            url = artistData.get("URL")
            if url:
                if artistDB.get(discID) == None:
                    toGet[discID] = url
            variations = artistData.get("Variations")
            if variations:
                groups = variations.get("In Groups")
                if groups:
                    for group in groups:
                        groupID  = group[2]
                        groupURL = group[1]
                        if artistDB.get(discID) == None:
                            toGet[groupID] = groupURL
                aliases = variations.get("Aliases")
                if aliases:
                    for alias in aliases:
                        aliasID  = alias[2]
                        aliasURL = alias[1]
                        if artistDB.get(discID) == None:
                            toGet[aliasID] = aliasURL

    savename = setFile(getSearchDir(), "toGet.yaml")
    save(savename, toGet)    


    
def certifyArtistDBs(modVal=500, option = "Back"):
    artistsDBDir = getArtistsDBDir()
    files = findExt(artistsDBDir, ext=".p")
    print "Finding files... Found",len(files),"files."
    
    toGet = {}
    noIDs = {}
    if option == "Back":
        for i,ifile in enumerate(files):
            print "Checking db:",ifile,'\t',len(toGet),len(noIDs)
            data = get(ifile, debug = True)
            for discID,artistData in data.iteritems():
                if artistData == None:                
                    noIDs[discID] = 1
                    continue
                    raise ValueError("ArtistData for discID:",discID,"is None")
                modValue   = getDiscIDHashMod(discID, modval=modVal)
                artistFile1 = setSubFile(getArtistsDir(), str(modValue), discID+".p")
                artistFile2 = setFile(getArtistsExtraDir(), discID+"-1.p")
                if not isFile(artistFile1) and not isFile(artistFile2):
                    url = artistData.get("URL")
                    if url:
                        toGet[discID] = url
                    variations = artistData.get("Variations")
                    if variations:
                        groups = variations.get("In Groups")
                        if groups:
                            for group in groups:
                                groupID  = group[2]
                                groupURL = group[1]
                                toGet[groupID] = groupURL
                        aliases = variations.get("Aliases")
                        if aliases:
                            for alias in aliases:
                                aliasID  = alias[2]
                                aliasURL = alias[1]
                                toGet[aliasID] = aliasURL
                    continue
                    raise ValueError("Original files for discID",discID,"does not exist!")
                continue
                artistName = artistData.get("Artist")
                if artistName == None:
                    print artistData
                    if isFile(artistFile1):
                        print artistFile1
                    if isFile(artistFile2):
                        print artistFile2
                    raise ValueError("Artist name is missing for discID:",discID)
                artistMedia = artistData.get("Media")
                if artistMedia == None:
                    print artistData
                    raise ValueError("Artist media is missing for discID:",discID)
    
        savename = setFile(getSearchDir(), "toGet.yaml")    
        save(savename, toGet)
    
        savename = setFile(getSearchDir(), "IDsToGet.yaml")    
        save(savename, noIDs)
        

    if option == "Forward":                
        for modValue in range(modVal):
            print "Checking mod:",modValue
            files  = findSubExt(getArtistsDir(), str(modValue), ext=".p")
            dbfile = setFile(getArtistsDBDir(), str(modValue)+"-DB.p")
            data = get(dbfile, debug = True)
            nNew = 0
            for i,ifile in enumerate(files):
                discID = getBaseFilename(ifile)
                if data.get(discID) == None:
                    bsdata       = getHTML(ifile)
                    artistData   = parse(bsdata, debug = False)
                    data[discID] = artistData
                    nNew += 1
                    continue

            if nNew > 0:
                print "Added",nNew,"to",dbfile
                save(dbfile, data, debug = True)

        return            
        savename = setFile(getSearchDir(), "toGet.yaml")    
        save(savename, toGet)
    
        savename = setFile(getSearchDir(), "IDsToGet.yaml")    
        save(savename, noIDs)
        
    
    
    


###############################################################################
#
# Create DBs from Parsed DBs
#
###############################################################################    
def createMasterDBs(modVal=500):
    startVal = start()

    files = findExt(getArtistsDBDir(), ext=".p")
    print "Finding files... Found",len(files),"files."
    artistDB      = {}
    artistNames   = {}
    artistNameIDs = {}
    artistRefs    = {}
    for i, ifile in enumerate(files):
        inter(startVal,i+1,len(files))
        data = get(ifile)
        for discID,artistData in data.iteritems():
            artistName = makeStrFromUnicode(artistData["Artist"])
            artistURL  = makeStrFromUnicode(artistData["URL"])
            
            artistDB[discID]        = 1
            artistRefs[discID]      = artistURL
            artistNames[discID]     = artistName
            artistNameIDs[artistName] = discID

    end(startVal)
    startVal = start()
        
    saveArtistDB(artistDB, debug = True)
    saveArtistRefs(artistRefs, debug = True)
    saveArtistNames(artistNames, debug = True)
    saveArtistNameIDs(artistNameIDs, debug = True)

    end(startVal)
 
    

def createArtistDBs(modVal=500):
    startVal = start()

    artistsDBDir = getArtistsDBDir()
    print "Finding files..."
            

    data = {}    
    files = findSubExt(artistsDBDir, '*', ext=".p")
    print "Finding files... Found",len(files),"files."
    for i, ifile in enumerate(files):
        if (i+1) % 1000 == 0: inter(startVal, i+1, len(files))
        
        artistData = get(ifile)
        discID     = artistData["ID"]
        modValue   = getDiscIDHashMod(discID, modval=modVal)
        if data.get(str(modValue)) == None:
            savename = setFile(artistsDBDir, str(modValue)+"-DB.p")
            data[str(modValue)] = get(savename)

        data[str(modValue)][discID] = artistData
        outfile = setSubFile(getDiscogDir(), 'artist-db', getBasename(ifile))
        moveFile(ifile, outfile, debug = True)


    for k,v in data.iteritems():
        savename = setFile(artistsDBDir, str(k)+"-DB.p")
        save(savename, v, debug = True)
        
    end(startVal)
    

def createAlbumDBs(modVal=500):
    startVal = start()

    albumsDBDir = getAlbumsDBDir()
    print "Finding files..."
            
    data = {}
    modVals = findDirs(albumsDBDir, debug = True)
    for modDir in modVals:
        print modDir
        discIDs = findDirs(modDir, debug = True)
        for discID in discIDs:
            files = findSubExt(discID, '*', ext=".p")
            for ifile in files:
                albumData = get(ifile)
                if albumData == None:
                    removeFile(ifile, debug = True)
                    continue
                albumArtist = albumData.get("Artist")
                if albumArtist == None:
                    removeFile(ifile, debug = True)
                    continue
                try:
                    artistID  = albumData["Artist"][0][2]
                except:
                    removeFile(ifile, debug = True)
                    continue
                    
                modValue  = str(getDiscIDHashMod(artistID, modval=modVal))
                code      = str(getAlbumCode(albumData['URL']))
                
                if data.get(modValue) == None:
                    data[modValue] = {}
                if data[modValue].get(artistID) == None:
                    data[modValue][artistID] = {}
                data[modValue][artistID][code] = albumData
            

    for k,v in data.iteritems():
        savename = setFile(setDir(getDiscogDir(), 'album-db'), str(k)+"-DB.p")
        save(savename, v, debug = True)
        
    end(startVal)

    
def renameFileByDiscID():
    startVal = start()
    
    artistsDBDir = getArtistsDBDir()
    artistNameIDs = getArtistNameIDs(debug = True)
    files = findSubExt(getDiscogDir(), "artist-db", ext=".p")
    
    for i, ifile in enumerate(files):
        if (i+1) % 100 == 0: inter(startVal, i+1, len(files))
        fname = getBaseFilename(ifile)
        iname = makeStrFromUnicode(makeUnicode(fname))
        if artistNameIDs.get(iname):
            discID   = artistNameIDs[iname]
            modValue = getDiscIDHashMod(discID, modval=500)
            subDir   = mkSubDir(artistsDBDir, str(modValue))
            outdir   = subDir
            outname  = setFile(outdir, discID+".p")
            moveFile(ifile, outname, debug = True)            
            continue


    end(startVal)
    return




def renameArtistAlbums():
    artistDBDir = getArtistsDBDir()
    albumsDir   = getAlbumsDir()
    files = findExt(artistDBDir, ext=".p")
    for ifile in files:
        data = get(ifile)
        for discID in data.keys():
            modValue = getDiscIDHashMod(discID, modval=500)

            artistData = data[discID]
            #artistAlbums = artistData['Albums']
            #modDir     = setDir(albumsDir, str(modValue))
            #artistDir  = setDir(modDir, discID)
            albums = findSubExt(albumsDir, [str(modValue), discID, '*'], ext='.p')
            print discID,'\t',len(albums)            
            for album in albums:
                name = makeStrFromUnicode(makeUnicode(getBaseFilename(album)))
                mediatype = getBasename(getDirname(album))
                mediaalbums = artistData['Media'].get(mediatype)
                if mediaalbums:
                    for albumdata in mediaalbums:
                        if makeStrFromUnicode(makeUnicode(albumdata['Album'])) == name:
                            albumID = albumdata['Code']
                            outfile = setFile(getDirname(album), albumID+".p")
                            moveFile(album, outfile, debug = True)
                            print name,'--->',albumID


    
def renameDirByDiscID():
    startVal = start()
    
    albumsDir = getAlbumsDBDir()
    dirs  = findSubDirs(getDiscogDir(), "album-db", debug = True)
    #artistNameIDs = getArtistNameIDs(debug = True)
    
    newToDB = {}
    
    for i, idir in enumerate(dirs):
        discID = None
        
        name = makeStrFromUnicode(makeUnicode(getBasename(idir)))
        #if artistNameIDs.get(name): discID = artistNameIDs[name]

        if discID == None and True:
            files = findSubExt(idir, "*", ext='.p')
            if len(files) == 0: continue
            print i,'\t',idir,'\t',len(files)
                
            for j, ifile in enumerate(files):
                if discID != None: break
                albumData = get(files[j])
                if albumData == None:
                    removeFile(ifile, debug = True)
                    continue
                if discID != None: break
                try:
                    artistData = albumData['Artist']
                    artist = makeStrFromUnicode(makeUnicode(artistData[0]))
                    ref    = makeStrFromUnicode(makeUnicode(artistData[1]))
                    discID = artistData[2]
                except:
                    discID = None

                if discID == None:
                    try:
                        artistData = albumData['Artist'][0]
                        artist = makeStrFromUnicode(makeUnicode(artistData[0]))
                        ref    = makeStrFromUnicode(makeUnicode(artistData[1]))
                        discID = artistData[2]
                    except:
                        discID = None


        if discID:
            modValue = getDiscIDHashMod(discID, modval=500)
            subDir   = mkSubDir(albumsDir, str(modValue))
            outdir   = subDir
            outname  = setDir(outdir, discID)
            moveDir(idir, outname, debug = True)
        else:
            #print "\tNo discID"
            continue
        #newToDB[discID] = {"URL": ref, "Name": artist}
        continue

    #saveNewDBs(newToDB)
    return
        
    print albumData
    ref    = artistData.get("URL")
    name   = makeStrFromUnicode(makeUnicode(artistData.get("Artist")))
    newToDB[discID] = {"URL": ref, "Name": name}


        
    f()
        
    
    if (i+1) % 5000 == 0: inter(startVal, i+1, len(dirs))
    fname = getBasename(idir)
    iname = makeStrFromUnicode(makeUnicode(fname))
    if artistNameIDs.get(iname):
        discID   = artistNameIDs[iname]
        modValue = getDiscIDHashMod(discID, modval=500)
        subDir   = mkSubDir(albumsDir, str(modValue))
        outdir   = subDir
        outname  = setDir(outdir, discID)
        moveDir(idir, outname, debug = True)
    else:
        print "Could not find",iname

    end(startVal)
    return
            
    
    
###############################################################################
#
# Downloaded Artists DB
#
###############################################################################
def createDownloadedArtistsFile(fromRaw = True, debug = False):
    if fromRaw:
        startVal = start()
        print "  Getting artistDB ..."
        artistDB = getArtistDB()
        print "  Getting artistDB ... Found",len(artistDB),"artists IDs."
        
                                        
        artistsDir = getArtistsDir()
        print "  Finding files in",artistsDir,"..."
        files = findSubExt(artistsDir, "*", ext=".p")
        print "  Finding files in",artistsDir,"... Found:",len(files)
        
        newFilesDir    = mkSubDir(getDiscogDir(), "artists-new")
        artistKnownIDs = {}
        
        for i,ifile in enumerate(files):
            discID = getBaseFilename(ifile)
            if artistDB.get(discID):
                artistKnownIDs[discID] = 1
            else:
                outfile = setFile(newFilesDir, getBasename(ifile))
                moveFile(ifile, outfile, debug = True)

            if (i+1) % 1000 == 0:
                inter(startVal,i+1,len(files))

        end(startVal)            
        
        saveKnownArtistIDs(artistKnownIDs, debug=True)