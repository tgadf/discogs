from ioUtils import getFile
from fsUtils import isFile
from webUtils import getHTML, isBS4
from strUtils import fixName
from math import ceil, floor
import json

from discogsBase import discogs
from discogsUtils import cdandlpUtils



class artistCLIDClass:
    def __init__(self, ID=None, err=None):
        self.ID=ID
        self.err=err
        
    def get(self):
        return self.__dict__
    
            
class artistCLURLClass:
    def __init__(self, url=None, err=None):
        self.url = url
        self.err = err
        
    def get(self):
        return self.__dict__
        
        
class artistCLNameClass:
    def __init__(self, name=None, err=None):
        self.name = name
        self.err  = err
        
    def get(self):
        return self.__dict__
    

class artistCLMediaClass:
    def __init__(self, err=None):
        self.media = {}
        self.err   = err
        
    def get(self):
        return self.__dict__
    

class artistCLMediaDataClass:
    def __init__(self, album=None, url=None, aclass=None, aformat=None, artist=None, code=None, year=None, err=None):
        self.album   = album
        self.url     = url
        self.aclass  = aclass
        self.aformat = aformat
        self.artist  = artist
        self.code    = code
        self.year    = year
        self.err     = err
        
    def get(self):
        return self.__dict__
    

class artistCLMediaAlbumClass:
    def __init__(self, url=None, album=None, aformat=None, err=None):
        self.url     = url
        self.album   = album
        self.aformat = aformat
        self.err     = err        
        
    def get(self):
        return self.__dict__

    
class artistCLMediaCountsClass:
    def __init__(self, err=None):
        self.counts = {}
        self.err    = err
        
    def get(self):
        return self.__dict__
    

class artistCLPageClass:
    def __init__(self, ppp = None, tot = None, more=None, redo=None, err=None):
        self.ppp   = ppp
        self.tot   = tot
        if isinstance(ppp, int) and isinstance(tot, int):
            self.pages = int(ceil(tot/ppp))
        else:
            self.pages = None

        self.err   = err

        self.more  = more
        self.redo  = redo
        
    def get(self):
        return self.__dict__
    

class artistCLProfileClass:
    def __init__(self, profile=None, aliases=None, members=None, sites=None, groups=None, variations=None, err=None):
        self.profile    = profile
        self.aliases    = aliases
        self.members    = members
        self.sites      = sites
        self.groups     = groups
        self.variations = variations
        self.err        = err
        
    def get(self):
        return self.__dict__
    

class artistCLURLInfo:
    def __init__(self, name=None, url=None, ID=None, err=None):
        self.name = name
        self.url  = url
        self.ID   = ID
        self.err  = err
        
    def get(self):
        return self.__dict__
        

class artistCLDataClass:
    def __init__(self, artist=None, url=None, ID=None, pages=None, profile=None, media=None, mediaCounts=None, err=None):
        self.artist      = artist
        self.url         = url
        self.ID          = ID
        self.pages       = pages
        self.profile     = profile
        self.media       = media
        self.mediaCounts = mediaCounts
        self.err         = err
        
    def get(self):
        return self.__dict__


        
class artistCL(discogs):
    def __init__(self, debug=False):
        self.debug = debug
        self.dutils = cdandlpUtils()
        
    def getData(self, inputdata, debug=False):
        if debug:
            print(inputdata)
            
        if isinstance(inputdata, str):
            if isFile(inputdata):
                try:
                    bsdata = getHTML(getFile(inputdata))
                except:
                    try:
                        bsdata = getHTML(getFile(inputdata, version=2))
                    except:
                        raise ValueError("Cannot read artist file: {0}".format(inputdata))
            else:
                try:
                    bsdata = getHTML(inputdata)
                except:
                    raise ValueError("Not sure about string input: {0} . It is not a file".format(inputdata))
        elif isBS4(inputdata):
            bsdata = inputdata
            pass
        else:
            raise ValueError("Not sure about input type: {0}".format(type(inputdata)))

        self.bsdata = bsdata
        
        return self.parse()
        
        
            
        
    def getNamesAndURLs(self, content):
        data = []
        if content is not None:
            for ref in content.findAll("a"):
                url    = ref.attrs['href']
                name   = ref.text

                ID = None
                data.append(artistCLURLInfo(name=name, url=url, ID=ID))
        return data





    #######################################################################################################################################
    ## Artist URL
    #######################################################################################################################################
    def getartistCLURL(self):       
        formlinks = self.bsdata.findAll("form", {"method": "get"})
        for formlink in formlinks:
            attrs = formlink.attrs
            if attrs.get('name') is not None:
                continue
        
            try:
                url = formlink.attrs["action"]
            except:
                auc = artistCLURLClass(err="NoContent")
                return auc

            auc = artistCLURLClass(url=url)
            return auc

    

    #######################################################################################################################################
    ## Artist ID
    #######################################################################################################################################                
    def getartistCLDiscID(self, url):
        url = url.url
        artistID = self.dutils.getArtistID(url)
        aic = artistCLIDClass(ID=artistID)
        return aic
    
    

    #######################################################################################################################################
    ## Artist Name
    #######################################################################################################################################
    def getartistCLName(self):        
        artistdiv  = self.bsdata.find("div", {"class": "twelve large-20 columns"})
        if artistdiv is None:
            anc = artistCLNameClass(name=None, err = "No Data")
            return anc

        h1 = artistdiv.find("h1")
        if h1 is None:            
            anc = artistCLNameClass(name=None, err = "No H1")
            return anc
        
        try:
            artistName = h1.text
            artistName = artistName.title()
        except:
            anc = artistCLNameClass(name=None, err="NoArtistName")
            return anc


        anc = artistCLNameClass(name=artistName, err=None)
        return anc
    
    

    #######################################################################################################################################
    ## Artist Media
    #######################################################################################################################################
    def getartistCLMediaAlbum(self, td):
        amac = artistCLMediaAlbumClass()
        for span in td.findAll("span"):
            attrs = span.attrs
            if attrs.get("class"):
                if 'format' in attrs["class"]:
                    albumformat = span.text
                    albumformat = albumformat.replace("(", "")
                    albumformat = albumformat.replace(")", "")
                    amac.format = albumformat
                    continue
            span.replaceWith("")

        ref = td.find("a")
        if ref:
            amac.url   = ref.attrs['href']
            amac.album = ref.text
        else:
            amac.err = "NoText"

        return amac
    
    
    def getartistCLMedia(self, artist):
        amc  = artistCLMediaClass()
        name = "Albums"
        amc.media[name] = []
        
        mediaType = "Albums"

        known = {}
        divs = self.bsdata.findAll("div", {"class": "div_item_listing"})
        for i,div in enumerate(divs):
            descrs    = div.findAll("div", {"class": "listingDescription"})
            if len(descrs) != 1:
                continue
                
            ref = descrs[0].find('a', {"class": "listingTitle"})
            if ref is None:
                url = None
            else:
                url = ref.attrs['href']
                
            albumdata = list(descrs[0].strings)
            albumdata = [x.replace("\n", "") for x in albumdata]
            albumdata = [x.replace("\t", "") for x in albumdata]
            albumdata = [x.replace("\r", "") for x in albumdata]
            albumdata = [x for x in albumdata if len(x) > 0]

            artistName = albumdata[0].title()
            albumName  = albumdata[1].title()
            
            code = self.dutils.getAlbumID(albumName)
            if known.get(code) is None:
                known[code] = True
            else:
                continue
            year = None

            amdc = artistCLMediaDataClass(album=albumName, url=url, aclass=None, aformat=None, artist=[artist.name], code=code, year=year)
            if amc.media.get(mediaType) is None:
                amc.media[mediaType] = []
            amc.media[mediaType].append(amdc)

        return amc
    
    

    #######################################################################################################################################
    ## Artist Media Counts
    #######################################################################################################################################        
    def getartistCLMediaCounts(self, media):
        
        amcc = artistCLMediaCountsClass()
        
        credittype = "Releases"
        if amcc.counts.get(credittype) == None:
            amcc.counts[credittype] = {}
        for creditsubtype in media.media.keys():
            amcc.counts[credittype][creditsubtype] = int(len(media.media[creditsubtype]))
            
        return amcc
    
    

    #######################################################################################################################################
    ## Artist Variations
    #######################################################################################################################################
    def getartistCLProfile(self):       
        data = {}
        apc = artistCLProfileClass(profile=data.get("Profile"), aliases=data.get("Aliases"),
                                 members=data.get("Members"), groups=data.get("In Groups"),
                                 sites=data.get("Sites"), variations=data.get("Variations"))
        return apc


    
    #######################################################################################################################################
    ## Artist Pages
    #######################################################################################################################################
    def getartistCLPages(self):
        pages = {"page 1": True}
        refs  = self.bsdata.findAll("a", {"class": "pagination_new"})
        for ref in refs:
            attrs = ref.attrs
            pages[attrs["title"]] = True
        tot   = len(pages)
        if tot > 1:
            more = True
        else:
            more = False
        apc   = artistCLPageClass(ppp=1, tot=tot, redo=False, more=more)
        return apc
    
    

    def parse(self):
        bsdata = self.bsdata
        
        artist      = self.getartistCLName()
        url         = self.getartistCLURL()
        ID          = self.getartistCLDiscID(url)
        pages       = self.getartistCLPages()
        profile     = self.getartistCLProfile()
        media       = self.getartistCLMedia(artist)
        mediaCounts = self.getartistCLMediaCounts(media)
        
        err = [artist.err, url.err, ID.err, pages.err, profile.err, mediaCounts.err, media.err]
        
        adc = artistCLDataClass(artist=artist, url=url, ID=ID, pages=pages, profile=profile, mediaCounts=mediaCounts, media=media, err=err)
        
        return adc