from ioUtils import getFile
from fsUtils import isFile
from webUtils import getHTML, isBS4
from strUtils import fixName
from math import ceil, floor
import json

from dbBase import dbBase
from discogsUtils import lastfmUtils



class artistLMIDClass:
    def __init__(self, ID=None, err=None):
        self.ID=ID
        self.err=err
        
    def get(self):
        return self.__dict__
    
            
class artistLMURLClass:
    def __init__(self, url=None, err=None):
        self.url = url
        self.err = err
        
    def get(self):
        return self.__dict__
        
        
class artistLMNameClass:
    def __init__(self, name=None, err=None):
        self.name = name
        self.err  = err
        
    def get(self):
        return self.__dict__
    

class artistLMMediaClass:
    def __init__(self, err=None):
        self.media = {}
        self.err   = err
        
    def get(self):
        return self.__dict__
    

class artistLMMediaDataClass:
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
    

class artistLMMediaAlbumClass:
    def __init__(self, url=None, album=None, aformat=None, err=None):
        self.url     = url
        self.album   = album
        self.aformat = aformat
        self.err     = err        
        
    def get(self):
        return self.__dict__

    
class artistLMMediaCountsClass:
    def __init__(self, err=None):
        self.counts = {}
        self.err    = err
        
    def get(self):
        return self.__dict__
    

class artistLMPageClass:
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
    

class artistLMProfileClass:
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
    

class artistLMURLInfo:
    def __init__(self, name=None, url=None, ID=None, err=None):
        self.name = name
        self.url  = url
        self.ID   = ID
        self.err  = err
        
    def get(self):
        return self.__dict__
        

class artistLMDataClass:
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


        
class artistLM(dbBase):
    def __init__(self, debug=False):
        self.debug = debug
        self.dutils = lastfmUtils()
        
    def getData(self, inputdata, debug=False):
        self.debug = debug
        if self.debug:
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
                data.append(artistLMURLInfo(name=name, url=url, ID=ID))
        return data





    #######################################################################################################################################
    ## Artist URL
    #######################################################################################################################################
    def getartistLMURL(self):
        metalink = self.bsdata.find("meta", {"property": "og:url"})
        if metalink is None:
            auc = artistLMURLClass(err="NoLink")
            return auc
        
        try:
            url = metalink.attrs["content"]
        except:
            auc = artistLMURLClass(err="NoContent")
            return auc

        auc = artistLMURLClass(url=url)
        return auc

    

    #######################################################################################################################################
    ## Artist ID
    #######################################################################################################################################                
    def getartistLMDiscID(self, artist):
        name     = artist.name
        artistID = self.dutils.getArtistID(name)
        if artistID is None:
            aic = artistLMIDClass(err="NoArtistID")
            return aic            
        aic = artistLMIDClass(ID=artistID)
        return aic
    
    

    #######################################################################################################################################
    ## Artist Name
    #######################################################################################################################################
    def getartistLMName(self):
        try:
            artistdiv  = self.bsdata.find("div", {"id": "tlmdata"})
            artistdata = artistdiv.attrs['data-tealium-data']
        except:
            anc = artistLMNameClass(name=None, err = "NoTealiumData")

        try:
            artistvals = json.loads(artistdata)
            artist     = artistvals["musicArtistName"]
        except:
            anc = artistLMNameClass(name=None, err="NoArtistName")
            return anc


        anc = artistLMNameClass(name=artist, err=None)
        return anc
    
    

    #######################################################################################################################################
    ## Artist Media
    #######################################################################################################################################
    def getartistLMMediaAlbum(self, td):
        amac = artistLMMediaAlbumClass()
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
    
    
    def getartistLMMedia(self, artist):
        if self.debug:
            print("\tFinding ArtistLM Media")
        amc  = artistLMMediaClass()
        name = "Albums"
        amc.media[name] = []
        
        mediaType = "Albums"

        albumsection = self.bsdata.find("section", {"id": "artist-albums-section"})
        if albumsection is None:
            if self.debug:
                print("\t\tNo Album Section!")
            amc.media[mediaType] = []
            return amc

            
            
            raise ValueError("Cannot find album section!")
            
        
            
        ols = albumsection.findAll("ol", {"class": "buffer-standard"}) # resource-list--release-list resource-list--release-list--with-20"})
        if self.debug:
            print("\t\tFound {0} Resource Lists".format(len(ols)))
        for ol in ols:
            lis = ol.findAll("li", {"class": "resource-list--release-list-item-wrap"})
            for il, li in enumerate(lis):
                h3 = li.find("h3", {"class": "resource-list--release-list-item-name"})
                if h3 is None:
                    if self.debug:
                        print("\t\tNo <h3> in artist list section ({0}/{1}): {2}".format(il,len(lis), li))
                    continue
                    raise ValueError("No <h3> in artist list section ({0}/{1}): {2}".format(il,len(lis), li))
                linkdata = self.getNamesAndURLs(h3)
                if len(linkdata) == 0:
                    continue
                #print(linkdata[0].get())
                
                ## Name
                album = linkdata[0].name

                #amdc = artistLMMediaDataClass(album=album, url=url, aclass=None, aformat=None, artist=None, code=code, year=year)

                ## URL
                url = linkdata[0].url
                
                ## Code
                code = self.dutils.getArtistID(album)
                
                ## Year
                year = None
                codedatas = li.findAll("p", {"class", "resource-list--release-list-item-aux-text"})
                if len(codedatas) == 2:
                    codedata = codedatas[1].text
                    vals     = [x.strip() for x in codedata.split("\n")]
                    if len(vals) == 5:
                        try:
                            year = vals[2][:-2]
                            year = year.split()[-1]
                            year = int(year)
                        except:
                            year = None
                

                amdc = artistLMMediaDataClass(album=album, url=url, aclass=None, aformat=None, artist=[artist.name], code=code, year=year)
                if amc.media.get(mediaType) is None:
                    amc.media[mediaType] = []
                amc.media[mediaType].append(amdc)
                if self.debug:
                    print("\t\tAdding Media ({0} -- {1})".format(album, url))

        return amc
    
    

    #######################################################################################################################################
    ## Artist Media Counts
    #######################################################################################################################################        
    def getartistLMMediaCounts(self, media):
        
        amcc = artistLMMediaCountsClass()
        
        credittype = "Releases"
        if amcc.counts.get(credittype) == None:
            amcc.counts[credittype] = {}
        for creditsubtype in media.media.keys():
            amcc.counts[credittype][creditsubtype] = int(len(media.media[creditsubtype]))
            
        return amcc
        
        
        amcc.err = "No Counts"
        return amcc
        
        results = self.bsdata.findAll("ul", {"class": "facets_nav"})
        if results is None or len(results) == 0:
            amcc.err = "No Counts"
            return amcc
            
        for result in results:
            for li in result.findAll("li"):
                ref = li.find("a")
                if ref:
                    attrs = ref.attrs
                    span = ref.find("span", {"class": "facet_count"})
                    count = None
                    if span:
                        count = span.text
                        credittype    = attrs.get("data-credit-type")
                        creditsubtype = attrs.get("data-credit-subtype")
                        if credittype and creditsubtype:
                            if amcc.counts.get(credittype) == None:
                                amcc.counts[credittype] = {}
                            if amcc.counts[credittype].get(creditsubtype) == None:
                                try:
                                    amcc.counts[credittype][creditsubtype] = int(count)
                                except:
                                    amcc.counts[credittype][creditsubtype] = count
                                    amcc.err = "Non Int"

        return amcc
    
    

    #######################################################################################################################################
    ## Artist Variations
    #######################################################################################################################################
    def getartistLMProfile(self):       
        data = {}
        
        artistdiv  = self.bsdata.find("div", {"id": "tlmdata"})
        if artistdiv is not None:
            artistdata = artistdiv.attrs['data-tealium-data']
        else:
            artistdata = None
    
        if artistdata is not None:
            try:
                artistvals = json.loads(artistdata)
                genres     = artistvals["tag"]
            except:
                genres     = None

            if genres is not None:
                genres = genres.split(",")
            else:
                genres = None
        else:
            genres = None
        
       
        data["Profile"] = {'genre': genres, 'style': None}
               
        apc = artistLMProfileClass(profile=data.get("Profile"), aliases=data.get("Aliases"),
                                 members=data.get("Members"), groups=data.get("In Groups"),
                                 sites=data.get("Sites"), variations=data.get("Variations"))
        return apc


    
    #######################################################################################################################################
    ## Artist Pages
    #######################################################################################################################################
    def getartistLMPages(self):
        pageData = self.bsdata.find("ul", {"class": "pagination-list"})
        if pageData is None:
            err = "pagination-list"
            apc = artistLMPageClass(err=err)
            return apc
        
        lis = pageData.findAll("li", {"class": "pagination-page"})
        ppp = 20

        if len(lis) > 1:
            lastPage = self.getNamesAndURLs(lis[-1])
            try:
                tot = lastPage[0].name
            except:
                tot = None
                #raise ValueError("Error getting last page from {0}".format(lastPage))
                
            try:
                tot = int(tot)
                apc   = artistLMPageClass(ppp=ppp, tot=tot, redo=False, more=True)
            except:
                tot = 1
                apc   = artistLMPageClass(ppp=ppp, tot=tot, redo=False, more=False)

        else:
            tot = 1
        
        return apc
            



    def parse(self):
        bsdata = self.bsdata
        
        artist      = self.getartistLMName()
        url         = self.getartistLMURL()
        ID          = self.getartistLMDiscID(artist)
        pages       = self.getartistLMPages()
        profile     = self.getartistLMProfile()
        media       = self.getartistLMMedia(artist)
        mediaCounts = self.getartistLMMediaCounts(media)
        
        err = [artist.err, url.err, ID.err, pages.err, profile.err, mediaCounts.err, media.err]
        
        adc = artistLMDataClass(artist=artist, url=url, ID=ID, pages=pages, profile=profile, mediaCounts=mediaCounts, media=media, err=err)
        
        return adc