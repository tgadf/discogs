from fsUtils import setFile, isFile
from fileUtils import getBasename
from ioUtils import getFile, saveFile
from webUtils import getWebData, getHTML
from searchUtils import findExt, findPattern
from timeUtils import clock, elapsed, update
from collections import Counter
from math import ceil

class collections():
    def __init__(self, discog, basedir=None):
        self.discog = discog
        self.name = "collections"
        
        self.maxCollections = 500

        ## General Imports
        self.getCodeDir          = self.discog.getCodeDir
        self.getCollectionsDir   = self.discog.getCollectionsDir
        self.getCollectionsDBDir = self.discog.getCollectionsDBDir
        self.getDiscogDBDir      = self.discog.getDiscogDBDir
        self.discogsUtils        = discogsUtils()
        
        self.starterDir = setDir(self.getCodeDir(), self.name)
        if not isDir(self.starterDir):
            print("Creating {0}".format(self.starterDir))
            mkDir(self.starterDir, debug=True)
        
        self.collectionsTxtFile = setFile(self.starterDir, "collections.txt")
        self.collectionsFile    = setFile(self.starterDir, "collections.json")
    
    
    
    ###############################################################################
    # Getter/Setter
    ###############################################################################
    def getCollectionsTxtFile(self):
        return self.collectionsTxtFile
    
    def getCollectionsFile(self):
        return self.collectionsFile

    
    
    ###############################################################################
    # Parse Global Collections and Download Collections Files  (1)
    ###############################################################################
    def getCollectionsData(self, debug=False):         
        filename = self.getCollectionsFile
        try:
            collectionsData = getFile(filename)
        except:
            raise ValueError("Could not open {0}".format(filename))
        return collectionsData
        

    def createCollectionsData(self, debug=False):
        print("  Creating Collection Data")
        filename = self.getCollectionsTxtFile()         
        collectionsTxtData = getFile(filename)
        collectionsTxtData = collectionsTxtData.split("\n")
        print("    Found {0} entries in the txt file".format(len(collectionsTxtData)))
            
        results = {}
        i = 0
        collection = None
        while i < len(collectionsTxtData):
            line = collectionsTxtData[i]
            if len(line) == 0:
                collection = None
            elif line.startswith("#"):
                collection = line[2:]
                results[collection] = Counter()
            else:
                val = line
                cnt = val.split()[0]
                value = " ".join(val.split()[1:])
                try:
                    cnt = int(cnt.replace(",", ""))
                except:
                    raise ValueError("Could not parse",cnt)

                if debug:
                    print(collection,'\t',cnt,'\t',value)
                results[collection][value] = cnt

            i += 1
            #print i,len(data)
            if i > 1000:
                break

        savename = self.collectionsFile
        print("  Saving {0} collections to {1}".format(len(results), savename))
        saveFile(savename, results)
    
            
        
    ###############################################################################
    # Download Collections Files  (2)
    ###############################################################################
    def downloadCollections(self, debug=False):
        collectionsData = self.getCollectionsData()
        if collectionsData is None:
            raise ValueError("Could not get collections data!")
        
        collectionDict = {}
        collectionDict["Style"]    = "style_exact"
        collectionDict["Genre"]    = "genre_exact"
        collectionDict["Country"]  = "country_exact"
        collectionDict["Base"]     = "limit=250&sort=have%2Cdesc&layout=sm"
        #https://www.discogs.com/search/?sort=have%2Cdesc&layout=sm&page=1&country_exact=US

        baseURL  = u"https://www.discogs.com/search/"
        problems = {}

        for collection,collectionData in collectionsData.items():
            cData = Counter(collectionData)
            for item in cData.most_common():
                num = item[1]
                val = item[0]
                pages = int(ceil((num+1)/500.0))

                maxVal = min(self.maxCollections, pages)
                for i in range(maxVal):
                    pageNum  = i+1

                    subURL  = "?{0}&{1}={2}&page={3}".format(collectionDict["Base"], collectionDict[collection], val, pageNum)

                    if debug:
                        print("Getting  ",collection,'-',val,i,nicerate(i,maxVal))

                    URL = "{0}{1}".format(baseURL, subURL)
                    savename = setFile(self.getCollectionsDir(),"{0}-{1}.p".format(val, pageNum))
                    print(isFile(savename), savename)
                    continue
                    if not isFile(savename) or force:
                        if debug:
                            print("  Downloading",URL)
                        retval = getWebData(base=URL, suburl=None, extra=None, savename=savename, 
                                         useSafari=useSafari, dtime=dtime, debug=debug)
                        if not retval:
                            print("  There was an error. Logging it.")
                            if problems.get(collection) == None:
                                problems[collection] = []
                            problems[collection].append(subURL)
                        #https://www.discogs.com/search/%3Flimit%3D250%26sort%3Dhave%252Cdesc%26layout%3Dsm%26genre_exact%3DElectronic%26page%3D1
                    if debug:
                        print("Retreived",collection,'-',val,i,nicerate(i,maxVal),"\n")



    ###############################################################################
    # Parse Downloaded Collection Files To Create Master Artist List  (3)
    ###############################################################################
    def parseCollectionFile(self, bsdata, debug=False, verydebug=False):
        artistDB  = {}

        h4s = bsdata.findAll("h4")
        if verydebug:
            print("Found {0} h4 tags".format(len(h4s)))
        
        for ih4,h4 in enumerate(h4s):
            spans = h4.findAll("span")
            ref   = None
            if len(spans) == 0:
                ref = h4.find("a")
            else:
                ref = spans[0].find("a")
                
            if ref is None:
                continue
                
            try:
                href   = ref.attrs.get('href')
                artist = ref.text.strip()
            except:
                print("Could not get artist/href from {0}".format(ref))
                continue
                
            if not href.endswith("?anv="):
                if artistDB.get(href) is None:
                    artistDB[href] = {"N": 0, "Name": artist}
                    if verydebug:
                        print("  Adding {0}".format(artist))
                artistDB[href]["N"] += 1
                
        if debug:
            print("Found {0} artists".format(len(artistDB)))
                
        return artistDB


    def parseCollections(self, debug=False):
        collectionsDir  = self.getCollectionsDir()
        collectionFiles = findExt(collectionsDir, ext=".p")
        print("Found {0} downloaded collection files".format(len(collectionFiles)))
        
        collectionsDBDir  = self.getCollectionsDBDir()

        collectionDB = {}
        parsed       = {}


        pfiles = findPattern(collectionsDBDir, pattern="parsedCollections")
        print("Found {0} previously parsed collection files".format(len(pfiles)))
        for ifile in pfiles:
            for k in getFile(ifile).keys():
                parsed[k] = 1
        print("Found {0} previously parsed collections".format(len(parsed)))
        

        #print "Looping over",len(files),"files.\n"
        startVal,startCmt = clock("Parsing Collection Data")
        nCF = 1
        for i in range(1,1000):
            ifile = setFile(collectionsDBDir, "parsedCollections-{0}.p".format(i))
            if not isFile(ifile):
                break
            nCF += 1
                
        total = len(collectionFiles)
        for i,ifile in enumerate(collectionFiles):
            name   = getBasename(ifile)
            if parsed.get(name):
                continue

            try:
                fdata  = getFile(ifile, version=2)
                bsdata = getHTML(fdata)
            except:
                continue
            #print(bsdata)
            artistDB = self.parseCollectionFile(bsdata, debug=False, verydebug=False)
            collectionDB[name] = artistDB

            #if (i+1) % 10 == 0: print "  --> Found",len(artistDB),"after",i+1,"files."
            
            if (i+1) % 25 == 0:
                update(startVal, proc=i+1, total=total)


            #if (i+1) % 25 == 0: inter(startVal,i+1,len(files))

            if (i+1) % 250 == 0:
                savename = setFile(collectionsDBDir, "parsedCollections-{0}.p".format(nCF))
                saveFile(ifile=savename, idata=collectionDB, debug=True)
                nCF += 1
                collectionDB = {}

        elapsed(startVal, startCmt)

        savename = setFile(collectionsDBDir, "parsedCollections-{0}.p".format(nCF))
        saveFile(ifile=savename, idata=collectionDB, debug=True)

        

    ###############################################################################
    # Merged Parsed Collection Data  (4)
    ###############################################################################
    def mergeCollections(self, force=False, debug=False):
        start,cmt = clock("Merging Parsed CollectionsDB Files")
        
        collectionsDBDir = self.getCollectionsDBDir()
        savename = setFile(collectionsDBDir, "mergedParsedCollections.p")
        if isFile(savename):
            print("Merged file {0} already exists. Rerun with force=True".format(savename))
            return
        files = findPattern(collectionsDBDir, pattern="parsedCollections")
        print("Found {0} previously parsed collection files".format(len(files)))
        
        colData = {}
        for i,ifile in enumerate(files):
            if debug:
                print("{0}\t{1}".format(i, ifile), end=" \t")
            data = getFile(ifile)
            for pname,pdata in data.items():
                for href,hrefData in pdata.items():
                    if colData.get(href) is None:
                        colData[href] = {'N': 0, 'Names': Counter()}
                    colData[href]['N'] += hrefData['N']
                    colData[href]['Names'][hrefData['Name']] += hrefData['N']
                    
            if debug:
                print(len(colData))

                        
        elapsed(start,cmt)

        print("Saving {0} artists hrefs to {1}".format(len(colData), savename))
        saveFile(ifile=savename, idata=colData, debug=True)



    def createCollectionDBs(self, debug=False):
        collectionsDBDir = self.getCollectionsDBDir()
        
        filename = setFile(collectionsDBDir, "mergedParsedCollections.p")
        if not isFile(filename):
            print("Merged file {0} does not exist.".format(filename))
            return
        collectionData = getFile(filename, debug=True)
        print("Found {0} artists from {1}".format(len(collectionData), filename))

        ## The DBs
        artistRefCounts = {}
        artistRefToID   = {}
        artistRefToName = {}
        artistNameToID  = {}
        artistNameToRef = {}
        artistIDToRef   = {}
        artistIDToName  = {}


        startTime,startCmt = clock("Creating Initial Artist Database")

        for href,hrefData in collectionData.items():
            num   = hrefData['N']
            names = hrefData['Names']
            
            try:
                artistName = names.most_common(1)[0][0]
            except:
                print("Could not extract artist name from {0}".format(names))
                artistName = None
            
            artistRef = href
            artistID  = self.discogsUtils.getArtistID(href)
            
            if not all([artistRef, artistID, artistName]):
                if debug:
                    print("Not all values are real for {0}".format(href))
                continue
            
            artistRefCounts[artistRef]  = num
            artistRefToID[artistRef]    = artistID
            artistNameToID[artistName]  = artistID
            artistIDToRef[artistID]     = artistRef
            artistNameToRef[artistName] = artistRef
            artistIDToName[artistID]    = artistName
            artistRefToName[artistRef]  = artistName


        savenames = {"RefCounts": artistRefCounts,
                     "RefToID": artistRefToID, "NameToID": artistNameToID, "NameToRef": artistNameToRef,
                     "IDToRef": artistIDToRef, "IDToName": artistIDToName, "RefToName": artistRefToName}
        for basename,savedata in savenames.items():
            savename = setFile(self.getDiscogDBDir(), "{0}.p".format(basename))
            print("Saving {0} entries to {1}".format(len(savedata), savename))
            saveFile(ifile=savename, idata=savedata, debug=True)
            
            
        elapsed(startTime, startCmt)