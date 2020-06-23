from dbArtistsBase import dbArtistsBase
from dbBase import dbBase
from artistMB import artistMB
from discogsUtils import musicbrainzUtils
import urllib
from urllib.parse import quote
from webUtils import getHTML
from fsUtils import isFile
from hashlib import md5


##################################################################################################################
# Base Class
##################################################################################################################
class dbArtistsMusicBrainz(dbArtistsBase):
    def __init__(self, debug=False):
        self.db     = "MusicBrainz"
        self.disc   = dbBase(self.db.lower())
        self.artist = artistMB(self.disc)
        self.dutils = musicbrainzUtils()
        self.debug  = debug
        
        self.baseURL   = "https://musicbrainz.org/"
        self.searchURL = "https://musicbrainz.org/search?"
        
        super().__init__(self.db, self.disc, self.artist, self.dutils, debug=debug)


        
    ##################################################################################################################
    # Artist URL
    ##################################################################################################################
    def getArtistURL(self, artistRef, page=1):
        baseURL = self.baseURL
        url     = urllib.parse.urljoin(baseURL, artistRef)
        return url

        
    
    ##################################################################################################################
    # Search Functions
    ##################################################################################################################
    def parseSearchArtist(self, artist, data):
        if data is None:
            return None
        
        ## Parse data
        bsdata = getHTML(data)
        
        artistDB  = {}

        tables = bsdata.findAll("table")
        for table in tables:
            ths = table.findAll("th")
            headers = [x.text for x in ths]
            trs = table.findAll("tr")
            for tr in trs[1:]:
                tds    = tr.findAll("td")
                name   = tds[0].find('a').text
                href   = tds[0].find('a').attrs['href']
            
                if artistDB.get(href) is None:
                    artistDB[href] = {"N": 0, "Name": name}
                artistDB[href]["N"] += 1
        
    
        if self.debug:
            print("Found {0} artists".format(len(artistDB)))
                
        iArtist = 0
        for href, hrefData in artistDB.items():
            iArtist += 1

            discID   = self.dutils.getArtistID(href)
            
            uuid = href.split('/')[-1]

            m = md5()
            for val in uuid.split("-"):
                m.update(val.encode('utf-8'))
            hashval = m.hexdigest()
            discID  = str(int(hashval, 16))

            url      = self.getArtistURL(href)
            savename = self.getArtistSavename(discID)

            print(iArtist,'/',len(artistDB),'\t:',discID,'\t',url)
            
            if isFile(savename):
                continue

            self.downloadArtistURL(url, savename)
            
    
    def getSearchArtistURL(self, artist):
        baseURL = self.baseURL
        extra = "search?query={0}&type=artist&limit=100&method=indexed".format(quote(artist))
        url = urllib.parse.urljoin(baseURL, extra)         
        return url
    
        
    def searchForArtist(self, artist):
        print("\n\n===================== Searching For {0} =====================".format(artist))
        url = self.getSearchArtistURL(artist)
        if url is None:
            raise ValueError("URL is None!")
                    
        ## Download data
        data, response = self.downloadURL(url)
        if response != 200:
            print("Error downloading {0}".format(url))
            return False

        self.parseSearchArtist(artist, data)