from dbArtistsBase import dbArtistsBase
from dbBase import dbBase
from artistMB import artistMB
from discogsUtils import musicbrainzUtils
import urllib
from urllib.parse import quote
from webUtils import getHTML
from fsUtils import isFile, setFile
from multiArtist import multiartist
from ioUtils import getFile
from time import sleep
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
        if isinstance(page, int) and page > 1:
            pageURL = "?page={0}".format(page)
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
        iDown   = 0
        for href, hrefData in artistDB.items():
            if iDown > 20:
                break
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
                if force is False:
                    continue

            iDown += 1
            self.downloadArtistURL(url, savename, force=force)
            
    
    def getSearchArtistURL(self, artist):
        baseURL = self.baseURL
        extra = "search?query={0}&type=artist&limit=100&method=indexed".format(quote(artist))
        url = urllib.parse.urljoin(baseURL, extra)         
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
    def artistIgnoreList(self):
        ignores  = ["Downloads", "Various Artists"]
        ignores += ["Glee", "Disney", "Sesame Street", "Nashville Cast"]
        ignores += ["Various Artists", "Vários intérpretes", "Various Interprets"]
        ignores += ["original score", "Downloads", "Glee Cast", "Sound Ideas", "Rain Sounds"]
        ignores += ["101 Strings", "TBS RADIO 954kHz", "Armin van Buuren ASOT Radio", "Piano Tribute Players"]
        ignores += ["Yoga Music", "GTA San Andreas"]

        return ignores
        
    def assertDBModValExtraData(self, modVal, maxPages=None, test=True):
        mulArts             = multiartist()        
        
        print("assertDBModValExtraData(",modVal,")")
        artistDBDir = self.disc.getArtistsDBDir()
        dbname  = setFile(artistDBDir, "{0}-DB.p".format(modVal))     
        dbdata  = getFile(dbname)
        nerrs   = 0
        ignores = self.artistIgnoreList()

        
        for artistID,artistData in dbdata.items():
            pages = artistData.pages
            if pages.more is True:
                npages = pages.pages
                if maxPages is not None:
                    npages = min([npages, maxPages])
                artistRef = artistData.url.url
                print(artistID,'\t',artistData.artist.name)
                if artistData.artist.name in ignores:
                    print("\tNot downloading artist in ignore list: {0}".format(artistData.artist.name))
                    continue
                
                for p in range(2, npages+1):
                    url      = self.getArtistURL(artistRef, p)
                    savename = self.getArtistSavename(artistID, p)
                    print(artistID,'\t',url,'\t',savename)
                    print("\t---> {0} / {1}".format(p, npages))
                    if test is True:
                        print("\t\tWill download: {0}".format(url))
                        print("\t\tJust testing... Will not download anything.")
                        continue
                    if not isFile(savename):
                        self.downloadArtistURL(url=url, savename=savename, force=True)
                        sleep(3)