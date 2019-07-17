from searchUtils import findNearest

class multiartist:
    def __init__(self, cutoff=0.9, discdata=None):
        self.cutoff   = cutoff    
        self.discdata = discdata
        
        self.discArtists = []
        if self.discdata is not None:
            self.discArtists = [x for x in discdata.keys() if x is not None]
            

    def getArtistNames(self, artist):        
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


    def splitArtist(self, result, delims=[",", "&", " And ", "+", "Duet With", "Presents", "Featuring", "/", "With The", " with ", " With ", " y ", " feat.", " Feat. ", " x ", " X "]):
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