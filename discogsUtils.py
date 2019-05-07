class discogsUtils:
    def __init__(self):
        self.baseURL  = "https://www.discogs.com/search/"        

    def getBaseURL(self):
        return baseURL
    
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
    
    
    