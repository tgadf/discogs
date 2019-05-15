class discogsUtils:
    def __init__(self):
        self.baseURL  = "https://www.discogs.com/search/"        

    def getBaseURL(self):
        return baseURL
    

    ###############################################################################
    #
    # Artist Functions
    #
    ###############################################################################
    def getArtistID(self, href, debug=False):
        if href is None:
            if debug:
                print("Could not get artist disc ID from None!")
            return None
        
        ival = "/artist"
        pos = href.find(ival)
        if pos == -1:
            if debug:
                print("Could not find discID in {0}".format(suburl))
            return None

        try:
            data = href[pos+len(ival)+1:]
            pos  = data.find("-")
            discID = data[:pos]
        except:
            print("Could not extract discID from {0}".format(href))
            return None
        
        try:
            int(discID)
        except:
            if debug:
                print("DiscID {0} is not an integer".format(discID))
            return None

        if debug:
            print("Found ID {0} from {1}".format(discID, href))
            
        return discID
    
    

    ###############################################################################
    #
    # Discog Hash Functions
    #
    ###############################################################################
    def getHashVal(self, artist, href):
        m = md5()
        if artist: m.update(artist)
        if href:   m.update(href)
        retval = m.hexdigest()
        return retval

    def getHashMod(self, hashval, modval):
        ival = int(hashval, 16)
        return ival % modval

    def getDiscIDHashMod(self, discID, modval):
        if discID == None:
            return -1
        ival = int(discID)
        return ival % modval

    def getArtistHashVal(self, artist, href):
        artist = makeStrFromUnicode(artist)
        hashval = getHashVal(artist, href)
        return hashval

    def getFileHashVal(self, ifile):
        fname = getBaseFilename(ifile)
        hname = makeStrFromUnicode(fname)
        hashval = getHashVal(hname, None)
        return hashval

    def getArtistHashMod(self, artist, href, modval):
        hashval = getArtistHashVal(artist,href)
        return getHashMod(hashval, modval)

    def getFileHashMod(self, ifile, modval):
        hashval = getFileHashVal(ifile)
        return getHashMod(hashval, modval)

