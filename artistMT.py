from ioUtils import getFile
from fsUtils import isFile
from webUtils import getHTML, isBS4
from strUtils import fixName
from math import ceil, floor
import json

from discogsBase import discogs
from discogsUtils import metalstormUtils



class artistMTIDClass:
    def __init__(self, ID=None, err=None):
        self.ID=ID
        self.err=err
        
    def get(self):
        return self.__dict__
    
            
class artistMTURLClass:
    def __init__(self, url=None, err=None):
        self.url = url
        self.err = err
        
    def get(self):
        return self.__dict__
        
        
class artistMTNameClass:
    def __init__(self, name=None, err=None):
        self.name = name
        self.err  = err
        
    def get(self):
        return self.__dict__
    

class artistMTMediaClass:
    def __init__(self, err=None):
        self.media = {}
        self.err   = err
        
    def get(self):
        return self.__dict__
    

class artistMTMediaDataClass:
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
    

class artistMTMediaAlbumClass:
    def __init__(self, url=None, album=None, aformat=None, err=None):
        self.url     = url
        self.album   = album
        self.aformat = aformat
        self.err     = err        
        
    def get(self):
        return self.__dict__

    
class artistMTMediaCountsClass:
    def __init__(self, err=None):
        self.counts = {}
        self.err    = err
        
    def get(self):
        return self.__dict__
    

class artistMTPageClass:
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
    

class artistMTProfileClass:
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
    

class artistMTURLInfo:
    def __init__(self, name=None, url=None, ID=None, err=None):
        self.name = name
        self.url  = url
        self.ID   = ID
        self.err  = err
        
    def get(self):
        return self.__dict__
        

class artistMTDataClass:
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


        
class artistMT(discogs):
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
                data.append(artistMTURLInfo(name=name, url=url, ID=ID))
        return data





    #######################################################################################################################################
    ## Artist URL
    #######################################################################################################################################
    def getartistMTURL(self):       
        metalink = self.bsdata.find("meta", {"property": "og:url"})
        if metalink is None:
            auc = artistMTURLClass(err="NoLink")
            return auc

        try:
            url = metalink.attrs["content"]
        except:
            auc = artistMTURLClass(err="NoContent")
            return auc

        auc = artistMTURLClass(url=url)
        return auc

    

    #######################################################################################################################################
    ## Artist ID
    #######################################################################################################################################                
    def getartistMTDiscID(self, url):
        codeData = url.url.split("band_id=")[1]
        artistID = codeData.split("&")[0]
        aic = artistMTIDClass(ID=artistID)
        return aic
    
    

    #######################################################################################################################################
    ## Artist Name
    #######################################################################################################################################
    def getartistMTName(self):        
        artistdiv  = self.bsdata.find("div", {"class": "page_title"})
        if artistdiv is None:
            anc = artistMTNameClass(name=None, err = "NoData")
            return anc

        txt = artistdiv.text.strip()
        if txt.endswith(" - Discography"):
            artistName = txt[:-len(" - Discography")]
        else:
            anc = artistMTNameClass(name=None, err="NoSyntax")
            return anc
        
        anc = artistMTNameClass(name=artistName, err=None)
        return anc
    
    

    #######################################################################################################################################
    ## Artist Media
    #######################################################################################################################################
    def getartistMTMediaAlbum(self, td):
        amac = artistMTMediaAlbumClass()
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
    
    
    def getartistMTMedia(self, artist):
        amc  = artistMTMediaClass()
        divs = self.bsdata.findAll("div", {"class": "discography-album"})
        for div in divs:
            divalbum = div.find("div", {"class": "album-title"})
            if divalbum is None:
                print("No album-title div")
            spans = divalbum.findAll("span")
            if len(spans) == 3:
                titleSpan  = spans[0]
                titleData  = self.getNamesAndURLs(titleSpan)[0]
                albumName  = titleData.name
                albumURL   = titleData.url

                mediaTypeSpan = spans[1]
                mediaType     = mediaTypeSpan.text

                yearSpan      = spans[2]
                year          = yearSpan.text
            elif len(spans) == 2:
                titleSpan  = spans[0]
                titleData  = self.getNamesAndURLs(titleSpan)[0]
                albumName  = titleData.name
                albumURL   = titleData.url

                mediaType  = "Album"

                yearSpan   = spans[1]
                year       = yearSpan.text
            elif len(spans) == 1:
                titleSpan  = spans[0]
                titleData  = self.getNamesAndURLs(titleSpan)[0]
                albumName  = titleData.name
                albumURL   = titleData.url

                mediaType  = "Album"
                year       = None
            else:
                print("Could not parse line with {0} spans".format(len(spans)))
                continue

            if mediaType.startswith("["):
                mediaType = mediaType[1:]
            if mediaType.endswith("]"):
                mediaType = mediaType[:-1]


            try:
                codeData = albumURL.split("album_id=")[1]
                code     = codeData.split("&")[0]
            except:
                code = self.dutils.getAlbumID(albumName)

            amdc = artistMTMediaDataClass(album=albumName, url=albumURL, aclass=None, aformat=None, artist=[artist.name], code=code, year=year)
            if amc.media.get(mediaType) is None:
                amc.media[mediaType] = []
            amc.media[mediaType].append(amdc)

        return amc
    
    

    #######################################################################################################################################
    ## Artist Media Counts
    #######################################################################################################################################        
    def getartistMTMediaCounts(self, media):
        
        amcc = artistMTMediaCountsClass()
        
        credittype = "Releases"
        if amcc.counts.get(credittype) == None:
            amcc.counts[credittype] = {}
        for creditsubtype in media.media.keys():
            amcc.counts[credittype][creditsubtype] = int(len(media.media[creditsubtype]))
            
        return amcc
    
    

    #######################################################################################################################################
    ## Artist Variations
    #######################################################################################################################################
    def getartistMTProfile(self):       
        data = {}
        apc = artistMTProfileClass(profile=data.get("Profile"), aliases=data.get("Aliases"),
                                 members=data.get("Members"), groups=data.get("In Groups"),
                                 sites=data.get("Sites"), variations=data.get("Variations"))
        return apc


    
    #######################################################################################################################################
    ## Artist Pages
    #######################################################################################################################################
    def getartistMTPages(self):
        pages = {"page 1": True}
        refs  = self.bsdata.findAll("a", {"class": "pagination_new"})
        for ref in refs:
            try:
                attrs = ref.attrs
                pages[attrs["title"]] = True
            except:
                break
        tot   = len(pages)
        if tot > 1:
            more = True
        else:
            more = False
        apc   = artistMTPageClass(ppp=1, tot=tot, redo=False, more=more)
        return apc
    
    

    def parse(self):
        bsdata = self.bsdata
        
        artist      = self.getartistMTName()
        url         = self.getartistMTURL()
        ID          = self.getartistMTDiscID(url)
        pages       = self.getartistMTPages()
        profile     = self.getartistMTProfile()
        media       = self.getartistMTMedia(artist)
        mediaCounts = self.getartistMTMediaCounts(media)
        
        err = [artist.err, url.err, ID.err, pages.err, profile.err, mediaCounts.err, media.err]
        
        adc = artistMTDataClass(artist=artist, url=url, ID=ID, pages=pages, profile=profile, mediaCounts=mediaCounts, media=media, err=err)
        
        return adc