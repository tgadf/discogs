from dbArtistsBase import dbArtistsBase
from dbBase import dbBase
from artistLM import artistLM
from discogsUtils import lastfmUtils
import urllib
from urllib.parse import quote
from webUtils import getHTML
from fsUtils import isFile, setFile
from multiArtist import multiartist
from ioUtils import getFile
from time import sleep



##################################################################################################################
# Base Class
##################################################################################################################
class dbArtistsLastFM(dbArtistsBase):
    def __init__(self, debug=False):
        self.db     = "LastFM"
        self.disc   = dbBase(self.db.lower())
        self.artist = artistLM(self.disc)
        self.dutils = lastfmUtils()
        self.debug  = debug
        
        self.baseURL       = "https://www.last.fm/"
        self.searchURL = "https://www.last.fm/search/" #artists?q=Ariana+Grande
        
        super().__init__(self.db, self.disc, self.artist, self.dutils, debug=debug)


        
    ##################################################################################################################
    # Artist URL
    ##################################################################################################################
    def getArtistURL(self, artistRef, page=1):
        #print("getArtistURL(",artistRef,")")
        if artistRef.startswith("http"):
            url = artistRef
        else:
            baseURL = self.baseURL
            if artistRef.startswith("/") is True:
                #print("Join", end="\t")
                url     = urllib.parse.urljoin(baseURL, quote(artistRef[1:]))
                #print(url)
            else:
                url     = urllib.parse.urljoin(baseURL, quote(artistRef))
            #print(url)
                
            if url.endswith("/") is False:
                url     = "{0}{1}".format(url, "/+albums?order=release_date")
            else:
                url     = "{0}{1}".format(url, "+albums?order=release_date")
                
            #print(url)
        
        if isinstance(page, int) and page > 1:
            pageURL = "&page={0}".format(page)
            url = "{0}{1}".format(url, pageURL)
        return url 
    
        
    
    ##################################################################################################################
    # Search Functions
    ##################################################################################################################
    def parseSearchArtist(self, artist, data, force=False):
        if data is None:
            return None
        
        ## Parse data
        bsdata = getHTML(data)
        
        artistDB  = {}
        
        uls = bsdata.findAll("ul", {"class": "artist-results"})
        for ul in uls:
            lis = ul.findAll("li", {"class": "artist-result"})
            for li in lis:
                h4 = li.find("h4")
                if h4 is None:
                    raise ValueError("No h4 in list")
                ref = h4.find('a')
                if ref is None:
                    raise ValueError("No ref in h4")

                name = ref.attrs['title']
                url  = ref.attrs['href']
                artistID = self.dutils.getArtistID(name)
        
                #print(name,'\t',url,'\t',artistID)
                if artistDB.get(url) is None:
                    artistDB[url] = {"N": 0, "Name": name}
                artistDB[url]["N"] += 1
        
    
        if self.debug:
            print("Found {0} artists".format(len(artistDB)))
                
        iArtist = 0
        for href, hrefData in artistDB.items():
            iArtist += 1
        
            name     = hrefData["Name"]
            discID   = self.dutils.getArtistID(name)
            url      = self.getArtistURL(href)
            savename = self.getArtistSavename(discID)

            print(iArtist,'/',len(artistDB),'\t:',discID,'\t',url)
            
            if isFile(savename):
                if force is False:
                    continue

            self.downloadArtistURL(url, savename, force=force)
            
    
    def getSearchArtistURL(self, artist):
        baseURL = self.searchURL    
        url = urllib.parse.urljoin(baseURL, "{0}{1}".format("artists?q=", quote(artist))) 
        return url
    
        
    def searchForArtist(self, artist, force=False):
        print("\n\n===================== Searching For {0} =====================".format(artist))
        url = self.getSearchArtistURL(artist)
        if url is None:
            raise ValueError("URL is None!")
                    
        ## Download data
        data, response = self.downloadURL(url)
        if response != 200:
            print("Error downloading {0}".format(url))
            return False

        self.parseSearchArtist(artist, data, force)
                
        
    
    ##################################################################################################################
    # Extra Data
    ##################################################################################################################
    def assertDBModValExtraData(self, modVal, maxPages=None, test=True):
        mulArts             = multiartist()        
        
        print("assertDBModValExtraData(",modVal,")")
        artistDBDir = self.disc.getArtistsDBDir()
        dbname  = setFile(artistDBDir, "{0}-DB.p".format(modVal))     
        dbdata  = getFile(dbname)
        nerrs = 0
        
        for artistID,artistData in dbdata.items():
            pages = artistData.pages
            if pages.more is True:
                npages = pages.tot
                if maxPages is not None:
                    npages = min([npages, maxPages])
                artistRef = artistData.url.url
                print(artistID,'\t',artistData.artist.name)
                multiValues = mulArts.getArtistNames(artistData.artist.name)
                if len(multiValues) > 1:
                    print("\tNot downloading multis: {0}".format(multiValues.keys()))
                    continue
                for p in range(2, npages+1):
                    url      = self.getArtistURL(artistRef, p)
                    savename = self.getArtistSavename(artistID, p)
                    print(artistID,'\t',url,'\t',savename)
                    if test is True:
                        print("\t\tWill download: {0}".format(url))
                        print("\t\tJust testing... Will not download anything.")
                        continue
                    if not isFile(savename):
                        self.downloadArtistURL(url=url, savename=savename, force=True)
                        sleep(3)