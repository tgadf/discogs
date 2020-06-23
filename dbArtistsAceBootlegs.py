from dbArtistsBase import dbArtistsBase
from dbBase import dbBase
from artistAB import artistAB
from discogsUtils import acebootlegsUtils
import urllib
from urllib.parse import quote
from webUtils import getHTML
from fsUtils import isFile
from hashlib import md5


##################################################################################################################
# Base Class
##################################################################################################################
class dbArtistsAceBootlegs(dbArtistsBase):
    def __init__(self, debug=False):
        self.db     = "AceBootlegs"
        self.disc   = dbBase(self.db.lower())
        self.artist = artistAB(self.disc)
        self.dutils = acebootlegsUtils()
        self.debug  = debug
        
        self.baseURL   = "https://ace-bootlegs.com/"
        self.searchURL = "https://ace-bootlegs.com/"
        
        super().__init__(self.db, self.disc, self.artist, self.dutils, debug=debug)


        
    ##################################################################################################################
    # Artist URL
    ##################################################################################################################
    def getArtistURL(self, artistRef, page=1):
        baseURL = self.disc.discogURL
        url     = urllib.parse.urljoin(baseURL, artistRef)
        return url
    
    
    ##################################################################################################################
    # Main
    ##################################################################################################################
    def getMainSavename(self):
        artistDir = self.disc.getArtistsDir()
        savename  = setFile(artistDir, "main.p")
        return savename
    
    
    def downloadMainArtists(self, force=False, debug=False, sleeptime=2):        
        savename = self.getMainSavename()
        
        ## Parse data
        bsdata = getHTML(savename)        
        artistDB  = {}
        
        
        ## Find and Download Artists
        categories = bsdata.find("div", {"class": "sidebar-widget widget_categories"})
        if categories is None:
            raise ValueError("Cannot find categories!")
        uls = categories.findAll("ul")
        for ul in uls:
            lis = ul.findAll("li")
            for i, li in enumerate(lis):
                try:
                    catitem = li.attrs["class"][1]
                except:
                    raise ValueError("Cannot find list class item: {0}".format(li))
                ref  = li.find("a")
                if ref is None:
                    raise ValueError("Cannot find list link!")
                try:
                    href = ref.attrs['href']
                except:
                    raise ValueError("Cannot find list href!")

                # check for artist
                artistName = href.split('/')[-2]
                try:
                    int(artistName)
                    continue
                except:
                    if artistName.find("parent-category-ii") == -1:
                        pass
                    else:
                        continue

                # get artist ID
                artistID = catitem.split('-')[-1]
                try:
                    int(artistID)
                except:
                    continue


                if force is False and isFile(savename):
                    print("{0} exists.".format(savename))
                    continue
            
                url = href
                savename = self.getArtistSavename(artistID)
                print(i,'\t',artistID,'\t',artistName,'\t',savename)
                self.downloadArtistURL(url=url, savename=savename, parse=False)

                
        
    ##################################################################################################################
    # Search Functions
    ##################################################################################################################
    def searchForArtist(self, artist):
        return