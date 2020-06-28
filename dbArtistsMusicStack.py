from dbArtistsBase import dbArtistsBase
from dbBase import dbBase
from artistMS import artistMS
from discogsUtils import musicstackUtils
import urllib
from urllib.parse import quote
from webUtils import getHTML
from fsUtils import isFile
from hashlib import md5
from ioUtils import saveFile



##################################################################################################################
# Base Class
##################################################################################################################
class dbArtistsMusicStack(dbArtistsBase):
    def __init__(self, debug=False):
        self.db     = "MusicStack"
        self.disc   = dbBase(self.db.lower())
        self.artist = artistMS(self.disc)
        self.dutils = musicstackUtils()
        self.debug  = debug
        
        self.baseURL   = "https://www.musicstack.com/"
        self.searchURL = "https://www.musicstack.com/"
        
        super().__init__(self.db, self.disc, self.artist, self.dutils, debug=debug)


        
    ##################################################################################################################
    # Artist URL
    ##################################################################################################################
    def getArtistURL(self, artistRef, page=1):
        baseURL = self.disc.discogURL
        url     = urllib.parse.urljoin(baseURL, artistRef)
        return url

        
    
    ##################################################################################################################
    # Search Functions
    ##################################################################################################################    def searchForArtist(self, artist=None):
        files = findPatternExt("/Users/tgadfort/Downloads/", pattern="MusicStack", ext=".html")
        for ifile in files:
            fname  = getBaseFilename(ifile)
            artist = fname[:fname.find(" Vinyl Records")]
            self.parseSearchForArtist(artist=artist, ifile=ifile)
    
    def parseSearchForArtist(self, artist, ifile):

        ## Parse data
        bsdata = getHTML(ifile)
        
        artistDB  = []

        tables = bsdata.findAll("table")
        if self.debug:
            print("Found {0} tables".format(len(tables)))
        for i,table in enumerate(tables):
            trs = table.findAll("tr")
            jj = 0
            headers = None
            values  = []
            for j,tr in enumerate(trs):
                tds  = tr.findAll("td")
                #print('\t',len(tds))
                #tds  = [list(td.strings) for td in tds]
                if len(tds) == 8:
                    if jj == 0:
                        headers = tds
                        if self.debug:
                            print("  Found Header: {0}".format(headers))
                    else:
                        values.append(tds)
                        if self.debug:
                            print("  Found Value: {0}".format(tds))

                    jj += 1

            if headers is not None:
                keys = []
                for header in headers:
                    b = header.find("b")
                    if b is None:
                        keys.append(str(len(keys)))
                    else:
                        txt = b.text.strip()
                        keys.append(txt)
                        
                if self.debug:
                    print("  Keys: {0}".format(keys))
                    print("  Values: {0}".format(len(values)))


                for value in values:
                    value = [x for ix,x in enumerate(value) if keys[ix] in ["Artist", "Title"]]
                    album = dict(zip(["Artist", "Title"], value))
                    album["Artist"] = album["Artist"].text
                    album["Album"]  = {"Name": album["Title"].text}
                    try:
                        album["Album"]["URL"] = album["Title"].find("a").attrs['href']
                    except:
                        album["Album"]["URL"] = None
                    del album["Title"]
                    artistDB.append({"ArtistName": album["Artist"], "AlbumName": album["Album"]["Name"], "AlbumURL": album["Album"]["URL"]})
                break

        artistID = self.dutils.getArtistID(artist)
        page     = 1
        savename = self.getArtistSavename(artistID, page)
        while isFile(savename) and False:
            page += 1
            savename = self.getArtistSavename(artistID, page)
        print("Saving {0} new artist media to {1}".format(len(artistDB), savename))
        saveFile(idata=artistDB, ifile=savename)