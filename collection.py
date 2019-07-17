from fsUtils import setFile, isFile, setDir, isDir, moveFile
from fileUtils import getBasename
from ioUtils import getFile, saveFile
from webUtils import getWebData, getHTML
from searchUtils import findExt, findPattern
from timeUtils import clock, elapsed, update
from collections import Counter
from discogsUtils import discogsUtils
from math import ceil
import urllib
from artists import artists

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
    
        self.arts = artists(discog)
        
    
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
    def getCollectionTypes(self, coltype, top=None, frac=None, N=None):
        colFile = setFile(col.starterDir, "{0}.txt".format(coltype))
        data = open(colFile, "r").readlines()
        data = [x.replace("\n", "") for x in data]
        names = [" ".join(x.split()[1:]) for x in data]
        counts = [int(x.split()[0].replace(",", "")) for x in data]
        
        if frac is not None:
            fracs  = [100*x/sum(counts) for x in counts]
            names = [k for k,v in zip(names, fracs) if v > frac]
            return names
        if top is not None:
            names = [k for k,v in zip(names, counts) if v > top]
            return genres
        if N is not None:
            names = names[:N]
            return names
        
        return names
    
    
    def getGenres(self, top=None, frac=None, N=None):
        return self.getCollectionTypes("genres", top, frac, N)

    def getCountries(self, top=None, frac=None, N=None):
        return self.getCollectionTypes("countries", top, frac, N)

    def getStyles(self, top=None, frac=None, N=None):
        return self.getCollectionTypes("styles", top, frac, N)
    
    
    
    def downloadCollection(self, maxPages, style=None, genre=None, country=None, year=None, fmat=None, decade=None):
        from time import sleep 
        
        collectionDict = {}
        collectionDict["Style"]    = "style_exact"
        collectionDict["Genre"]    = "genre_exact"
        collectionDict["Country"]  = "country_exact"
        collectionDict["Decade"]   = "decade"
        collectionDict["Year"]     = "year"
        collectionDict["Format"]   = "format_exact"
        collectionDict["Base"]     = "limit=250&sort=have%2Cdesc&layout=sm"
        
        self.discog.searchURL      = "https://www.discogs.com/search/"
        
        baseURL = "?{0}".format(collectionDict["Base"])

        val = "-".join([x.replace("/", "") for x in [country, year, decade, genre, style, fmat] if x is not None])
        print("SaveVal -> {0}".format(val))
        
        
        subURLs = []
        if style is not None:
            subURLs.append("&{0}={1}".format(collectionDict["Style"], urllib.parse.quote(style)))
        if genre is not None:
            subURLs.append("&{0}={1}".format(collectionDict["Genre"], urllib.parse.quote(genre)))
        if country is not None:
            subURLs.append("&{0}={1}".format(collectionDict["Country"], urllib.parse.quote(country)))
        if year is not None:
            subURLs.append("&{0}={1}".format(collectionDict["Year"], urllib.parse.quote(year)))
        if fmat is not None:
            subURLs.append("&{0}={1}".format(collectionDict["Format"], urllib.parse.quote(fmat)))
        if decade is not None:
            subURLs.append("&{0}={1}".format(collectionDict["Decade"], urllib.parse.quote(decade)))
        subURL = "".join(subURLs)

        for page in range(1,maxPages+1):
            savename = setFile(self.getCollectionsDir(),"{0}-{1}.p".format(val, page))
            if isFile(savename):
                continue
                
            print("  Trying to download and save {0}".format(savename))
            
            url = "{0}{1}{2}&page={3}".format(self.discog.searchURL, baseURL, subURL, page)            
            print(url)


            user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
            headers={'User-Agent':user_agent,} 

            sleep(1)
            
            request=urllib.request.Request(url,None,headers) #The assembled request
            response = urllib.request.urlopen(request)
            data = response.read() # The data u need
            
            print("Saving {0}".format(savename))
            saveFile(idata=data, ifile=savename)
            sleep(3)
            
            
    def downloadCollectionsByYear(self, year, maxPages, Ncountries=10, Ngenres=10, Nstyles=10):        
        countries = self.getCountries(N=Ncountries)
        genres    = self.getGenres(N=Ngenres)
        styles    = self.getStyles(N=Nstyles)

        for country in countries:
            for genre in genres:
                self.downloadCollection(maxPages=maxPages, country=country, style=None, genre=genre, year=year)
            
        
        
        
        
    
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

        #https://www.discogs.com/search/?sort=have%2Cdesc&limit=250&country_exact=US&year=2018&type=master&decade=2010
        
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

            
        iArtist = 0
        for href, hrefData in artistDB.items():
            iArtist += 1
            if href.startswith("/artist") is False:
                continue
        
            discID   = self.arts.discogsUtils.getArtistID(href)
            url      = self.arts.getArtistRef(href)
            savename = self.arts.getArtistSavename(discID)

            print(iArtist,'/',len(artistDB),'\t:',len(discID),'\t',url)
            if isFile(savename):
                continue

            self.arts.downloadArtistURL(url, savename)
            
            
                
        return artistDB


    def parseCollections(self, debug=False):
        collectionsDir  = self.getCollectionsDir()
        collectionFiles = findExt(collectionsDir, ext=".p")
        print("Found {0} downloaded collection files".format(len(collectionFiles)))
        for i,ifile in enumerate(collectionFiles):
            print("Parsing {0}/{1}: {2}".format(i,len(collectionFiles), ifile))
            try:
                fdata  = getFile(ifile)
            except:
                dst = ifile.replace("collections/", "collections/py2/")
                moveFile(ifile, dst)
            bsdata = getHTML(fdata)
            self.parseCollectionFile(bsdata, debug=False, verydebug=False)
            print("")
            
            

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

            
            

        nameids = {}
        namerefs = {}
        for artist,discID in artistNameToID.items():
            name  = self.discogsUtils.getArtistName(artist)
            ref   = artistNameToRef[artist]

            if nameids.get(name) is None:
                nameids[name] = {}
            nameids[name][discID] = 1

            if namerefs.get(name) is None:
                namerefs[name] = {}
            namerefs[name][ref] = 1


        nameids  = {k: list(v.keys()) for k,v in nameids.items()}
        namerefs = {k: list(v.keys()) for k,v in namerefs.items()}      
        
        savenames = {"NameToIDs": nameids, "NameToRefs": namerefs}
        for basename,savedata in savenames.items():
            savename = setFile(self.getDiscogDBDir(), "{0}.p".format(basename))
            print("Saving {0} entries to {1}".format(len(savedata), savename))
            saveFile(ifile=savename, idata=savedata, debug=True)      


        savenames = {"RefCounts": artistRefCounts,
                     "RefToID": artistRefToID, "NameToID": artistNameToID, "NameToRef": artistNameToRef,
                     "IDToRef": artistIDToRef, "IDToName": artistIDToName, "RefToName": artistRefToName}
        for basename,savedata in savenames.items():
            savename = setFile(self.getDiscogDBDir(), "{0}.p".format(basename))
            print("Saving {0} entries to {1}".format(len(savedata), savename))
            saveFile(ifile=savename, idata=savedata, debug=True)

            
            
        elapsed(startTime, startCmt)