from ioUtils import getFile
from fsUtils import isFile
from webUtils import getHTML, isBS4
from strUtils import fixName
from math import ceil, floor
from hashlib import md5

from discogsBase import discogs

class artistMBIDClass:
    def __init__(self, ID=None, err=None):
        self.ID=ID
        self.err=err
        
    def get(self):
        return self.__dict__
    
            
class artistMBURLClass:
    def __init__(self, url=None, err=None):
        self.url = url
        self.err = err
        
    def get(self):
        return self.__dict__
        
        
class artistMBNameClass:
    def __init__(self, name=None, err=None):
        self.name = name
        self.err  = err
        
    def get(self):
        return self.__dict__
    

class artistMBMediaClass:
    def __init__(self, err=None):
        self.media = {}
        self.err   = err
        
    def get(self):
        return self.__dict__
    

class artistMBMediaDataClass:
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
    

class artistMBMediaAlbumClass:
    def __init__(self, url=None, album=None, aformat=None, err=None):
        self.url     = url
        self.album   = album
        self.aformat = aformat
        self.err     = err        
        
    def get(self):
        return self.__dict__

    
class artistMBMediaCountsClass:
    def __init__(self, err=None):
        self.counts = {}
        self.err    = err
        
    def get(self):
        return self.__dict__
    

class artistMBPageClass:
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
    

class artistMBProfileClass:
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
    

class artistMBURLInfo:
    def __init__(self, name=None, url=None, ID=None, err=None):
        self.name = name
        self.url  = url
        self.ID   = ID
        self.err  = err
        
    def get(self):
        return self.__dict__
        

class artistMBDataClass:
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


        
class artistMB(discogs):
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

                ID = self.getartistMBDiscID(url)
                data.append(artistMBURLInfo(name=name, url=url, ID=ID))
        return data





    #######################################################################################################################################
    ## Artist URL
    #######################################################################################################################################
    def getartistMBURL(self):
        artistData = self.bsdata.find("div", {"class": "artistheader group-icon"})
        if artistData is None:
            auc = artistMBURLClass(err=True)
            return auc
        
        ref = artistData.find("a")
        if ref is None:
            auc = artistMBURLClass(err="NoLink")
            return auc

        url = ref.attrs["href"]
        if url.find("/artist/") == -1:
            url = None
            auc = artistMBURLClass(url=url, err="NoArtist")
        else:
            auc = artistMBURLClass(url=url)

        return auc

    

    #######################################################################################################################################
    ## Artist ID
    #######################################################################################################################################                
    def getartistMBDiscID(self, suburl):
        ival = "/artist"
        if isinstance(suburl, artistMBURLClass):
            suburl = suburl.url
        if not isinstance(suburl, str):
            aic = artistMBIDClass(err="NotStr")            
            return aic

        pos = suburl.find(ival)
        if pos == -1:
            aic = artistMBIDClass(err="NotArtist")            
            return aic

        uuid = suburl[pos+len(ival)+1:]

        
        m = md5()
        for val in uuid.split("-"):
            m.update(val.encode('utf-8'))
        hashval = m.hexdigest()
        discID  = str(int(hashval, 16))
        
        try:
            int(discID)
        except:
            aic = artistMBIDClass(err="NotInt")            
            return aic

        aic = artistMBIDClass(ID=discID)
        return aic
    
    

    #######################################################################################################################################
    ## Artist Name
    #######################################################################################################################################
    def getartistMBName(self):
        artistData = self.bsdata.find("div", {"class": "artistheader group-icon"})
        if artistData is None:
            anc = artistMBNameClass(err=True)
            return anc
        
        h1 = artistData.find("h1")
        if h1 is not None:
            artistName = h1.text.strip()
            if len(artistName) > 0:
                artist = fixName(artistName)
                anc = artistMBNameClass(name=artist, err=None)
            else:
                anc = artistMBNameClass(name=artist, err="Fix")
        else:
            anc = artistMBNameClass(err="NoH1")
        
        return anc
    
    

    #######################################################################################################################################
    ## Artist Media
    #######################################################################################################################################
    def getartistMBMediaAlbum(self, td):
        amac = artistMBMediaAlbumClass()
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
    
    
    def getartistMBMedia(self):
        amc  = artistMBMediaClass()
        
        
        mediaTypes = [x.text for x in self.bsdata.findAll("h3")]
        tables     = dict(zip(mediaTypes, self.bsdata.findAll("table")))

        for mediaType, table in tables.items():
            headers = [x.text for x in table.findAll("th")]
            trs = table.findAll('tr')
            for tr in trs[1:]:
                tds = tr.findAll("td")

                ## Year
                idx  = headers.index("Year")
                year = tds[idx].text

                ## Title
                idx    = headers.index("Title")
                refs   = [x.attrs['href'] for x in tds[idx].findAll('a')]
                if len(refs) == 0:
                    raise ValueError("No link for album")
                url    = refs[0]
                album  = tds[idx].text

                    
                m = md5()
                uuid = url.split("/")[-1]
                for val in uuid.split("-"):
                    m.update(val.encode('utf-8'))
                hashval = m.hexdigest()
                code = int(hashval, 16)
                

                ## Artist
                idx     = headers.index("Artist")
                artists = []
                for artistVal in tds[idx].findAll('a'):
                    url = artistVal.attrs['href']
                    name = artistVal.text
                    m = md5()
                    uuid = url.split("/")[-1]
                    for val in uuid.split("-"):
                        m.update(val.encode('utf-8'))
                    hashval = m.hexdigest()
                    ID = int(hashval, 16)
                    artists.append(artistMBURLInfo(name=name, url=url, ID=ID))
                       

                amdc = artistMBMediaDataClass(album=album, url=url, aclass=None, aformat=None, artist=artists, code=code, year=year)
                if amc.media.get(mediaType) is None:
                    amc.media[mediaType] = []
                amc.media[mediaType].append(amdc)

        
        

        return amc
    
    

    #######################################################################################################################################
    ## Artist Media Counts
    #######################################################################################################################################        
    def getartistMBMediaCounts(self, media):
        
        amcc = artistMBMediaCountsClass()
        
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
    def getartistMBProfile(self):
        data   = {}        
        genres = self.bsdata.find("div", {"class": "genre-list"})
        genre  = self.getNamesAndURLs(genres)
        style  = []
        data["Profile"] = {'genre': genre, 'style': style}
               
        apc = artistMBProfileClass(profile=data.get("Profile"), aliases=data.get("Aliases"),
                                 members=data.get("Members"), groups=data.get("In Groups"),
                                 sites=data.get("Sites"), variations=data.get("Variations"))
        return apc


    
    #######################################################################################################################################
    ## Artist Pages
    #######################################################################################################################################
    def getartistMBPages(self):
        apc   = artistMBPageClass()
        from numpy import ceil
        bsdata = self.bsdata

    
        apc   = artistMBPageClass(ppp=1, tot=1, redo=False, more=False)
        return apc
            
        pageData = bsdata.find("div", {"class": "pagination bottom"})
        if pageData is None:
            err = "pagination bottom"
            apc = artistMBPageClass(err=err)
            return apc
        else:
            x = pageData.find("strong", {"class": "pagination_total"})
            if x is None:
                err = "pagination_total"
                apc = artistMBPageClass(err=err)
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
                    apc   = artistMBPageClass(err=err)
                    return apc

                if ppp < 500:
                    if tot < 25 or ppp == tot:
                        apc   = artistMBPageClass(ppp=ppp, tot=tot, redo=False, more=False)
                    else:
                        apc   = artistMBPageClass(ppp=ppp, tot=tot, redo=True, more=False)
                else:
                    if tot < 500:
                        apc   = artistMBPageClass(ppp=ppp, tot=tot, redo=False, more=False)
                    else:
                        apc   = artistMBPageClass(ppp=ppp, tot=tot, redo=False, more=True)
                        
                return apc
            
        return artistMBPageClass()



    def parse(self):
        bsdata = self.bsdata
        
        artist      = self.getartistMBName()
        url         = self.getartistMBURL()
        ID          = self.getartistMBDiscID(url)
        pages       = self.getartistMBPages()
        profile     = self.getartistMBProfile()
        media       = self.getartistMBMedia()
        mediaCounts = self.getartistMBMediaCounts(media)
        
        err = [artist.err, url.err, ID.err, pages.err, profile.err, mediaCounts.err, media.err]
        
        adc = artistMBDataClass(artist=artist, url=url, ID=ID, pages=pages, profile=profile, mediaCounts=mediaCounts, media=media, err=err)
        
        return adc