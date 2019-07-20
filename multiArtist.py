from searchUtils import findNearest

class multiartist:
    def __init__(self, cutoff=0.9, discdata=None, exact=False):
        self.cutoff   = cutoff    
        self.discdata = discdata
        self.exact    = exact
        
        self.basicdelims = ["Duet With", "Presents", "Featuring"]
        self.delims = [",", "&", " And ", "+", "/", "With The", " with ", " With ", " y ", " Y ", " feat.", " Feat. ", " x ", " X "]
        self.discArtists = []
        if self.discdata is not None:
            self.discArtists = [x for x in discdata.keys() if x is not None]
        self.knownDelimArtists = {artist: True for artist in self.discArtists if self.nDelims(artist) > 0}

    
    def getDiscArtists(self):
        return self.discArtists
    
    def getKnownDelimArtists(self):
        return self.knownDelimArtists  
    
    def isKnownArtist(self, artist):
        if isinstance(self.discdata, dict):
            return self.discdata.get(artist) != None
        return False
    
    def nDelims(self, artist):
        return sum([x in artist for x in self.delims])
    
    
    def getDelimData(self, val):
        valdata = {d: [x.strip() for x in val.split(d)] for d in self.delims if d in val}
        return valdata
    
    
    def getBasicDelimData(self, val):
        valdata = {d: [x.strip() for x in val.split(d)] for d in self.basicdelims if d in val}
        return valdata

    def getNdelims(self, val):
        return len(val)

    def addArtist(self, allArtists, val, debug=False):
        #print("L={0}".format(len(allArtists)))
        if allArtists.get(val) is None:
            if debug:
                print("Adding {0}. Sum is {1}".format(val, len(allArtists)))
            allArtists[val] = True
    
    
    def cleanArtist(self, artist):
        artist = artist.replace("(", "")
        artist = artist.replace(")", "")
        return artist


    def newMethod(self, artist, debug=False):
        artist = self.cleanArtist(artist)
        allArtists = {}
        d1delims = self.getBasicDelimData(artist)
        if len(d1delims) == 0:
            d1delims = self.getDelimData(artist)
        if debug:
            print('1','\t',artist,'===>',d1delims)

        knownArtists = set()
        if len(d1delims) == 0:
            self.addArtist(allArtists, artist, debug)
            knownArtists = set(allArtists.keys())
        elif self.isKnownArtist(artist):
            self.addArtist(allArtists, artist, debug)
            knownArtists = set(allArtists.keys())
            d1delims = {}


        ##############################################################################
        ## 1st Delimiter Split
        ##############################################################################
        for delim1, delimdata1 in d1delims.items():
            delimdata1 = list(set(delimdata1).difference(knownArtists))
            for artist1 in delimdata1:
                d2delims = self.getDelimData(artist1)
                if debug:
                    print('2','\t',artist1,'===>',d2delims)
                if self.getNdelims(d2delims) == 0:
                    self.addArtist(allArtists, artist1, debug)
                    knownArtists = set(allArtists.keys())
                    continue
                elif self.isKnownArtist(artist1):
                    self.addArtist(allArtists, artist1, debug)
                    knownArtists = set(allArtists.keys())
                    d2delims = {}

                    
                ##############################################################################
                ## 2nd Delimiter Split
                ##############################################################################
                for delim2, delimdata2 in d2delims.items():
                    delimdata2 = list(set(delimdata2).difference(knownArtists))
                    for artist2 in delimdata2:
                        d3delims = self.getDelimData(artist2)
                        if debug:
                            print('3','\t',artist2,'===>',d3delims)
                        if self.getNdelims(d3delims) == 0:
                            self.addArtist(allArtists, artist2)
                            knownArtists = set(allArtists.keys())
                            continue
                        elif self.isKnownArtist(artist2):
                            self.addArtist(allArtists, artist2)
                            knownArtists = set(allArtists.keys())
                            d3delims = {}

                            
                        ##############################################################################
                        ## 3rd Delimiter Split
                        ##############################################################################
                        for delim3, delimdata3 in d3delims.items():
                            delimdata3 = list(set(delimdata3).difference(knownArtists))
                            for artist3 in delimdata3:
                                d4delims = self.getDelimData(artist3)
                                if self.getNdelims(d4delims) == 0:
                                    self.addArtist(allArtists, artist3)
                                    knownArtists = set(allArtists.keys())
                                    continue
                                elif self.isKnownArtist(artist3):
                                    self.addArtist(allArtists, artist3)
                                    knownArtists = set(allArtists.keys())
                                    d4delims = {}
                                    

                                ##############################################################################
                                ## 4th Delimiter Split
                                ##############################################################################
                                for delim4, delimdata4 in d4delims.items():
                                    delimdata4 = list(set(delimdata4).difference(knownArtists))
                                    for artist4 in delimdata4:
                                        d5delims = self.getDelimData(artist4)
                                        if self.getNdelims(d5delims) == 0:
                                            self.addArtist(allArtists, artist4)
                                            knownArtists = set(allArtists.keys())
                                            continue
                                        elif self.isKnownArtist(artist4):
                                            self.addArtist(allArtists, artist4)
                                            knownArtists = set(allArtists.keys())
                                            d5delims = {}


                                        ##############################################################################
                                        ## 5th Delimiter Split
                                        ##############################################################################
                                        for delim5, delimdata5 in d5delims.items():
                                            delimdata5 = list(set(delimdata5).difference(knownArtists))
                                            for artist5 in delimdata5:
                                                d6delims = self.getDelimData(artist5)
                                                if self.getNdelims(d6delims) == 0:
                                                    self.addArtist(allArtists, artist5)
                                                    knownArtists = set(allArtists.keys())
                                                    continue
                                                elif self.isKnownArtist(artist5):
                                                    self.addArtist(allArtists, artist5)
                                                    knownArtists = set(allArtists.keys())
                                                    d6delims = {}

                                                    

        ##############################################################################
        ## Combine Results
        ##############################################################################                                                    
        results = {}
        if self.discdata is not None and len(self.discArtists) > 0:
            for name in knownArtists:
                retval = self.discdata.get(name)
                if self.exact is False:
                    if retval is None:
                        retval = findNearest(name, self.discArtists, 1, self.cutoff)
                        if len(retval) == 1:
                            retval = self.discdata.get(retval[0])
                        else:
                            retval = None
                        
                results[name] = retval
        else:
            results = {k: ['?'] for k,v in allArtists.items()}
                
        return results

    def getArtistNames(self, artist, debug=False):        
        return self.newMethod(artist, debug)
    
        if self.nDelims(artist) == 0:
            names = {artist: []}
            return names
        
        if self.discdata is not None and len(self.discArtists) > 0:
            retval = self.discdata.get(artist)
            if retval is not None:
                return {artist: retval}
            else:
                retval = findNearest(artist, self.discArtists, 1, self.cutoff)
                if len(retval) == 1:
                    return {artist: self.discdata.get(retval[0])}        
        
        names = {artist: None}
        names = self.splitArtist(names)
        names = self.unravelDict(names)
        names = self.unravelDict(names)
        return names


    def unravelDict(self, dvals):
        fvals = {}
        for k,v in dvals.items():
            if isinstance(v, dict):
                for k2,v2 in v.items():
                    if isinstance(v2, dict):
                        for k3,v3 in v.items():
                            if isinstance(v3, dict):
                                for k4,v4 in v.items():
                                    fvals[k4] = v4
                            else:
                                fvals[k3] = v3
                    else:
                        fvals[k2] = v2
            else:
                fvals[k] = v

        return fvals


    def splitArtistDelim(self, artist, delval):
        names = {}    
        if delval not in artist:
            return None

        for val in artist.split(delval):
            val = val.strip()
            
            if self.discdata is not None and len(self.discArtists) > 0:
                retval = self.discdata.get(val)
                if retval is not None:
                    names[val] = retval
                else:
                    retval = findNearest(val, self.discArtists, 1, self.cutoff)
                    if len(retval) == 0:
                        names[val] = None
                    else:
                        names[val] = retval
            else:
                names[val] = [-1]

        if len(names) == 0:
            return None

        if any(names.values()) is False:
            return None

        return names


    def splitArtist(self, result):
        delims = self.delims
            
        #print("Input: {0}".format(result))
        for name in result.keys():
            #print("  Name -->",name,"\tCurrent Value -->",result[name])
            if result[name] is None:
                for delim in delims:
                    #print("\tDelim: {0}  for {1}".format(delim, name))
                    result2 = self.splitArtistDelim(name,delval=delim)
                    #print("\tDelim Result: {0}".format(result2))


                    if result2 is not None:
                        result[name] = result2
                        #print("\tName:",name,'\tResult:',result2)
                        for name2 in result2.keys():
                            if result2[name2] is None:
                                for delim2 in delims:
                                    #print("\t\tDelim2: {0}  for {1}".format(delim2, name2))
                                    result3 = self.splitArtistDelim(name2,delval=delim2)
                                    #print("\t\tDelim Result: {0}".format(result3))


                                    if result3 is not None:
                                        #print("\t\tName:",name2,'\tResult:',result3)
                                        result2[name2] = result3

                                        ## Breaking from delim2 
                                        break

                        ## Breaking from delim
                        break

        return result