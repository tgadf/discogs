from ioUtils import getFile
from fsUtils import isFile
from webUtils import getHTML, isBS4
from strUtils import fixName
from math import ceil, floor
from hashlib import md5

from discogsBase import discogs

class artistRCIDClass:
    def __init__(self, ID=None, err=None):
        self.ID=ID
        self.err=err
        
    def get(self):
        return self.__dict__
    
            
class artistRCURLClass:
    def __init__(self, url=None, err=None):
        self.url = url
        self.err = err
        
    def get(self):
        return self.__dict__
        
        
class artistRCNameClass:
    def __init__(self, name=None, err=None):
        self.name = name
        self.err  = err
        
    def get(self):
        return self.__dict__
    

class artistRCMediaClass:
    def __init__(self, err=None):
        self.media = {}
        self.err   = err
        
    def get(self):
        return self.__dict__
    

class artistRCMediaDataClass:
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
    

class artistRCMediaAlbumClass:
    def __init__(self, url=None, album=None, aformat=None, err=None):
        self.url     = url
        self.album   = album
        self.aformat = aformat
        self.err     = err        
        
    def get(self):
        return self.__dict__

    
class artistRCMediaCountsClass:
    def __init__(self, err=None):
        self.counts = {}
        self.err    = err
        
    def get(self):
        return self.__dict__
    

class artistRCPageClass:
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
    

class artistRCProfileClass:
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
    

class artistRCURLInfo:
    def __init__(self, name=None, url=None, ID=None, err=None):
        self.name = name
        self.url  = url
        self.ID   = ID
        self.err  = err
        
    def get(self):
        return self.__dict__
        

class artistRCDataClass:
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


        
class artistRC(discogs):
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
                data.append(artistRCURLInfo(name=name, url=url, ID=ID))
        return data





    #######################################################################################################################################
    ## Artist URL
    #######################################################################################################################################
    def getartistRCURL(self):
        artistData = self.bsdata.find("link", {"rel": "canonical"})
        if artistData is None:
            auc = artistRCURLClass(err=True)
            return auc
        
        try:
            artistURL = artistData.attrs['href']
            auc = artistRCURLClass(url=artistURL, err=None)
        except:
            auc = artistRCURLClass(err="TxtErr")

        return auc

    

    #######################################################################################################################################
    ## Artist ID
    #######################################################################################################################################                
    def getartistRCDiscID(self, artist):
        name = artist.name
        
        m = md5()
        for val in name.split(" "):
            m.update(val.encode('utf-8'))
        hashval = m.hexdigest()
        discID  = str(int(hashval, 16) % int(1e9))
        aic = artistRCIDClass(ID=discID)
        return aic
    
    

    #######################################################################################################################################
    ## Artist Name
    #######################################################################################################################################
    def getartistRCName(self):
        artistData = self.bsdata.find("section", {"id": "artist-info"})
        if artistData is None:            
            anc = artistRCNameClass(err=True)
            return anc
        
        h1 = artistData.find("h1")
        if h1 is None:
            anc = artistRCNameClass(err="NoH1")
            return anc
            
        artistName = h1.text
        anc = artistRCNameClass(name=artistName, err=None)
        return anc
    
    

    #######################################################################################################################################
    ## Artist Media
    #######################################################################################################################################
    def getartistRCMediaAlbum(self, td):
        amac = artistRCMediaAlbumClass()
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
    
    
    def getartistRCMedia(self, artist):
        amc  = artistRCMediaClass()
        
        mediaType = "Albums"
        
        artistSection = self.bsdata.find("section", {"id": "album-artist"})
        if artistSection is None:
            raise ValueError("Cannot find Artist Section")

        articles = artistSection.findAll("article")
        for ia,article in enumerate(articles):
            ref = article.find('a')
            if ref is None:
                raise ValueError("No ref in article")
            albumURL = ref.attrs['href']

            caption = ref.find("figcaption")
            if caption is None:
                raise ValueError("No figcaption in article")

            b = caption.find("b")
            if b is None:
                raise ValueError("No bold in caption")

            i = caption.find("i")
            if i is None:
                raise ValueError("No italics in caption")

            albumName = b.text
            albumYear = i.text

            
            m = md5()
            for val in albumURL.split("/"):
                m.update(val.encode('utf-8'))
            hashval = m.hexdigest()
            code  = str(int(hashval, 16) % int(1e9))

            artists = [artist.name]

            amdc = artistRCMediaDataClass(album=albumName, url=albumURL, aclass=None, aformat=None, artist=artists, code=code, year=albumYear)
            if amc.media.get(mediaType) is None:
                amc.media[mediaType] = []
            amc.media[mediaType].append(amdc)
        
   
        mediaType = "Songs"
        
        singlesSection = self.bsdata.find("ol", {"id": "songs-list"})
        if singlesSection is None:
            raise ValueError("Cannot find Singles Section")
        lis = singlesSection.findAll("li")
        for li in lis:
            ref = li.find('a')
            if ref is None:
                raise ValueError("No ref in article")
            albumURL = ref.attrs['href']
            
            b = ref.find("b")
            if b is None:
                raise ValueError("No bold in ref")
                
            albumName = b.text
            albumYear = None

            
            m = md5()
            for val in albumURL.split("/"):
                m.update(val.encode('utf-8'))
            hashval = m.hexdigest()
            code  = str(int(hashval, 16) % int(1e10))

            artists = [artist.name]

            amdc = artistRCMediaDataClass(album=albumName, url=albumURL, aclass=None, aformat=None, artist=artists, code=code, year=albumYear)
            if amc.media.get(mediaType) is None:
                amc.media[mediaType] = []
            amc.media[mediaType].append(amdc)
        

        return amc
    
    

    #######################################################################################################################################
    ## Artist Media Counts
    #######################################################################################################################################        
    def getartistRCMediaCounts(self, media):
        
        amcc = artistRCMediaCountsClass()
        
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
    def getartistRCProfile(self):
        data   = {}
        apc = artistRCProfileClass(profile=data.get("Profile"), aliases=data.get("Aliases"),
                                 members=data.get("Members"), groups=data.get("In Groups"),
                                 sites=data.get("Sites"), variations=data.get("Variations"))
        return apc


    
    #######################################################################################################################################
    ## Artist Pages
    #######################################################################################################################################
    def getartistRCPages(self):
        apc   = artistRCPageClass()
        from numpy import ceil
        bsdata = self.bsdata

    
        apc   = artistRCPageClass(ppp=1, tot=1, redo=False, more=False)
        return apc
            
        pageData = bsdata.find("div", {"class": "pagination bottom"})
        if pageData is None:
            err = "pagination bottom"
            apc = artistRCPageClass(err=err)
            return apc
        else:
            x = pageData.find("strong", {"class": "pagination_total"})
            if x is None:
                err = "pagination_total"
                apc = artistRCPageClass(err=err)
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
                    apc   = artistRCPageClass(err=err)
                    return apc

                if ppp < 500:
                    if tot < 25 or ppp == tot:
                        apc   = artistRCPageClass(ppp=ppp, tot=tot, redo=False, more=False)
                    else:
                        apc   = artistRCPageClass(ppp=ppp, tot=tot, redo=True, more=False)
                else:
                    if tot < 500:
                        apc   = artistRCPageClass(ppp=ppp, tot=tot, redo=False, more=False)
                    else:
                        apc   = artistRCPageClass(ppp=ppp, tot=tot, redo=False, more=True)
                        
                return apc
            
        return artistRCPageClass()



    def parse(self):
        bsdata = self.bsdata
        
        artist      = self.getartistRCName()
        url         = self.getartistRCURL()
        ID          = self.getartistRCDiscID(artist)
        pages       = self.getartistRCPages()
        profile     = self.getartistRCProfile()
        media       = self.getartistRCMedia(artist)
        mediaCounts = self.getartistRCMediaCounts(media)
        
        err = [artist.err, url.err, ID.err, pages.err, profile.err, mediaCounts.err, media.err]
        
        adc = artistRCDataClass(artist=artist, url=url, ID=ID, pages=pages, profile=profile, mediaCounts=mediaCounts, media=media, err=err)
        
        return adc