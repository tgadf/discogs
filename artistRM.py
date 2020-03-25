from ioUtils import getFile
from fsUtils import isFile
from webUtils import getHTML, isBS4
from strUtils import fixName
from math import ceil, floor
from hashlib import md5

from discogsBase import discogs

class artistRMIDClass:
    def __init__(self, ID=None, err=None):
        self.ID=ID
        self.err=err
        
    def get(self):
        return self.__dict__
    
            
class artistRMURLClass:
    def __init__(self, url=None, err=None):
        self.url = url
        self.err = err
        
    def get(self):
        return self.__dict__
        
        
class artistRMNameClass:
    def __init__(self, name=None, err=None):
        self.name = name
        self.err  = err
        
    def get(self):
        return self.__dict__
    

class artistRMMediaClass:
    def __init__(self, err=None):
        self.media = {}
        self.err   = err
        
    def get(self):
        return self.__dict__
    

class artistRMMediaDataClass:
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
    

class artistRMMediaAlbumClass:
    def __init__(self, url=None, album=None, aformat=None, err=None):
        self.url     = url
        self.album   = album
        self.aformat = aformat
        self.err     = err        
        
    def get(self):
        return self.__dict__

    
class artistRMMediaCountsClass:
    def __init__(self, err=None):
        self.counts = {}
        self.err    = err
        
    def get(self):
        return self.__dict__
    

class artistRMPageClass:
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
    

class artistRMProfileClass:
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
    

class artistRMURLInfo:
    def __init__(self, name=None, url=None, ID=None, err=None):
        self.name = name
        self.url  = url
        self.ID   = ID
        self.err  = err
        
    def get(self):
        return self.__dict__
        

class artistRMDataClass:
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


        
class artistRM(discogs):
    def __init__(self, debug=False):
        self.debug = debug
        
    def getData(self, inputdata):
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
                data.append(artistRMURLInfo(name=name, url=url, ID=ID))
        return data





    #######################################################################################################################################
    ## Artist URL
    #######################################################################################################################################
    def getartistRMURL(self):
        artistData = self.bsdata.find("meta", {"property": "og:url"})
        if artistData is None:
            auc = artistRMURLClass(err=True)
            return auc
        
        url = artistData.attrs["content"]
        if url.find("/artist/") == -1:
            url = None
            auc = artistRMURLClass(url=url, err="NoArtist")
        else:
            auc = artistRMURLClass(url=url)

        return auc

    

    #######################################################################################################################################
    ## Artist ID
    #######################################################################################################################################
    def getartistRMDiscID(self, suburl):
        div = self.bsdata.find("div", {"class": "artist_name"})
        if div is None:
            aic = artistRMIDClass(err="NotArtist")            
            return aic

        inp = div.find("input")
        if inp is None:
            aic = artistRMIDClass(err="NoInput")            
            return aic

        try:
            value = inp.attrs['value']
        except:
            aic = artistRMIDClass(err="NoInputValue")            
            return aic

        if value.startswith("[Artist") and value.endswith("]"):
            try:
                discID = str(int(value[7:-1]))
            except:
                aic = artistRMIDClass(err="NotInt")            
                return aic
        else:
            aic = artistRMIDClass(err="NotInt")            
            return aic
        

        aic = artistRMIDClass(ID=discID)
        return aic
    
    

    #######################################################################################################################################
    ## Artist Name
    #######################################################################################################################################
    def getartistRMName(self):
        artistData = self.bsdata.find("h1", {"class": "artist_name_hdr"})
        if artistData is None:
            anc = artistRMNameClass(err="No H1")
            return anc
        
        artistName = artistData.text.strip()
        if len(artistName) > 0:
            artist = fixName(artistName)
            anc = artistRMNameClass(name=artist, err=None)
        else:
            anc = artistRMNameClass(name=artist, err="Fix")
        
        return anc
    
    

    #######################################################################################################################################
    ## Artist Media
    #######################################################################################################################################
    def getartistRMMediaAlbum(self, td):
        amac = artistRMMediaAlbumClass()
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
    
    
    def getartistRMMedia(self, artist, url):
        amc  = artistRMMediaClass()

        mediadatas = self.bsdata.findAll("div", {"id": "discography"})
        for mediadata in mediadatas:
            h3s        = mediadata.findAll("h3", {"class": "disco_header_label"})
            categories = [x.text for x in h3s]

            sufs    = mediadata.findAll("div", {"class": "disco_showing"})
            spans   = [x.find("span") for x in sufs]
            ids     = [x.attrs['id'] for x in spans]
            letters = [x[-1] for x in ids]


            for mediaType,suffix in dict(zip(categories, letters)).items():
                categorydata = mediadata.find("div", {"id": "disco_type_{0}".format(suffix)})
                albumdatas   = categorydata.findAll("div", {"class": "disco_release"})
                for albumdata in albumdatas:
                    
                    ## Code
                    codedata = albumdata.attrs['id']
                    code     = codedata.split("_")[-1]
                    try:
                        int(code)
                    except:
                        code = None
                        
                    ## Title
                    mainline = albumdata.find("div", {"class": "disco_mainline"})
                    maindata = self.getNamesAndURLs(mainline)
                    try:
                        album = maindata[0].name
                    except:
                        album = None
                        
                    try:
                        albumurl = maindata[0].url
                    except:
                        albumurl = None


                    ## Year
                    yeardata = albumdata.find("span", {"class": "disco_year_y"})
                    if yeardata is None:
                        yeardata = albumdata.find("span", {"class": "disco_year_ymd"})
                        
                    year     = None
                    if yeardata is not None:
                        year = yeardata.text

                    ## Artists        
                    artistdata   = albumdata.findAll("span")[-1]
                    albumartists = self.getNamesAndURLs(artistdata)
                    if len(albumartists) == 0:
                        albumartists = [artistRMURLInfo(name=artist.name, url=url.url.replace("https://rateyourmusic.com", ""), ID=None)]


                    amdc = artistRMMediaDataClass(album=album, url=albumurl, aclass=None, aformat=None, artist=albumartists, code=code, year=year)
                    if amc.media.get(mediaType) is None:
                        amc.media[mediaType] = []
                    amc.media[mediaType].append(amdc)

        
        

        return amc
    
    

    #######################################################################################################################################
    ## Artist Media Counts
    #######################################################################################################################################        
    def getartistRMMediaCounts(self, media):
        
        amcc = artistRMMediaCountsClass()
        
        credittype = "Releases"
        if amcc.counts.get(credittype) == None:
            amcc.counts[credittype] = {}
        for creditsubtype in media.media.keys():
            amcc.counts[credittype][creditsubtype] = int(len(media.media[creditsubtype]))
            
        return amcc
        
    

    #######################################################################################################################################
    ## Artist Variations
    #######################################################################################################################################
    def getartistRMProfile(self):
        data    = {}        
        profile = self.bsdata.find("div", {"class": "artist_info"})
        
        headers = profile.findAll("div", {"class": "info_hdr"})
        content = profile.findAll("div", {"class": "info_content"})
        
        headers = [x.text for x in headers]
        content = [x.text for x in content]
        
        data = dict(zip(headers, content))
               
        apc = artistRMProfileClass(profile=data.get("Formed"), aliases=data.get("Aliases"),
                                 members=data.get("Members"), groups=data.get("In Groups"),
                                 sites=data.get("Sites"), variations=data.get("Variations"))
        return apc


    
    #######################################################################################################################################
    ## Artist Pages
    #######################################################################################################################################
    def getartistRMPages(self):
        apc   = artistRMPageClass()
        from numpy import ceil
        bsdata = self.bsdata

    
        apc   = artistRMPageClass(ppp=1, tot=1, redo=False, more=False)
        return apc
            
        pageData = bsdata.find("div", {"class": "pagination bottom"})
        if pageData is None:
            err = "pagination bottom"
            apc = artistRMPageClass(err=err)
            return apc
        else:
            x = pageData.find("strong", {"class": "pagination_total"})
            if x is None:
                err = "pagination_total"
                apc = artistRMPageClass(err=err)
                return apc
            else:
                txt = x.text
                txt = txt.strip()
                txt = txt.replace("\n", "")
                retval = [tmp.strip() for tmp in txt.split('of')]

                try:
                    ppp   = int(retval[0].split('–')[-1])
                    tot   = int(retval[1].replace(",", ""))
                except:
                    err   = "int"
                    apc   = artistRMPageClass(err=err)
                    return apc

                if ppp < 500:
                    if tot < 25 or ppp == tot:
                        apc   = artistRMPageClass(ppp=ppp, tot=tot, redo=False, more=False)
                    else:
                        apc   = artistRMPageClass(ppp=ppp, tot=tot, redo=True, more=False)
                else:
                    if tot < 500:
                        apc   = artistRMPageClass(ppp=ppp, tot=tot, redo=False, more=False)
                    else:
                        apc   = artistRMPageClass(ppp=ppp, tot=tot, redo=False, more=True)
                        
                return apc
            
        return artistRMPageClass()



    def parse(self):
        bsdata = self.bsdata
        
        artist      = self.getartistRMName()
        url         = self.getartistRMURL()
        ID          = self.getartistRMDiscID(url)
        pages       = self.getartistRMPages()
        profile     = self.getartistRMProfile()
        media       = self.getartistRMMedia(artist, url)
        mediaCounts = self.getartistRMMediaCounts(media)
        
        err = [artist.err, url.err, ID.err, pages.err, profile.err, mediaCounts.err, media.err]
        
        adc = artistRMDataClass(artist=artist, url=url, ID=ID, pages=pages, profile=profile, mediaCounts=mediaCounts, media=media, err=err)
        
        return adc