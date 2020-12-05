from ioUtils import getFile
from fsUtils import isFile
from webUtils import getHTML, isBS4
from strUtils import fixName
from math import ceil, floor

from dbBase import dbBase

class artistAMIDClass:
    def __init__(self, ID=None, err=None):
        self.ID=ID
        self.err=err
        
    def get(self):
        return self.__dict__
    
            
class artistAMURLClass:
    def __init__(self, url=None, err=None):
        self.url = url
        self.err = err
        
    def get(self):
        return self.__dict__
        
        
class artistAMNameClass:
    def __init__(self, name=None, err=None):
        self.name = name
        self.err  = err
        
    def get(self):
        return self.__dict__
    

class artistAMMediaClass:
    def __init__(self, err=None):
        self.media = {}
        self.err   = err
        
    def get(self):
        return self.__dict__
    

class artistAMMediaDataClass:
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
    

class artistAMMediaAlbumClass:
    def __init__(self, url=None, album=None, aformat=None, err=None):
        self.url     = url
        self.album   = album
        self.aformat = aformat
        self.err     = err        
        
    def get(self):
        return self.__dict__

    
class artistAMMediaCountsClass:
    def __init__(self, err=None):
        self.counts = {}
        self.err    = err
        
    def get(self):
        return self.__dict__
    

class artistAMPageClass:
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
    

class artistAMProfileClass:
    def __init__(self, profile=None, aliases=None, members=None, sites=None, groups=None, search=None, variations=None, err=None):
        self.profile    = profile
        self.aliases    = aliases
        self.members    = members
        self.sites      = sites
        self.groups     = groups
        self.variations = variations
        self.search     = search
        self.err        = err
        
    def get(self):
        return self.__dict__
    

class artistAMURLInfo:
    def __init__(self, name=None, url=None, ID=None, err=None):
        self.name = name
        self.url  = url
        self.ID   = ID
        self.err  = err
        
    def get(self):
        return self.__dict__
        

class artistAMDataClass:
    def __init__(self, artist=None, url=None, ID=None, pages=None, profile=None, media=None, mediaCounts=None, err=None):
        self.artist      = artist
        self.url         = url
        self.ID          = ID
        self.pages       = pages
        self.profile     = profile
        self.media       = media
        self.mediaCounts = mediaCounts
        self.err         = err
        
        
    def show(self):
        print("AllMusic Artist Data Class")
        print("-------------------------")
        print("Artist:  {0}".format(self.artist.name))
        print("URL:     {0}".format(self.url.url))
        print("ID:      {0}".format(self.ID.ID))
        print("Profile: {0}".format(self.profile.get()))
        print("Pages:   {0}".format(self.pages.get()))
        print("Media:   {0}".format(self.mediaCounts.get()))
        for mediaType,mediaTypeAlbums in self.media.media.items():
            print("   {0}".format(mediaType))
            for album in mediaTypeAlbums:
                print("      {0}".format(album.album))     
        
    def get(self):
        return self.__dict__


        
class artistAM(dbBase):
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

                ID = self.getartistAMDiscID(url)
                data.append(artistAMURLInfo(name=name, url=url, ID=ID))
        return data





    #######################################################################################################################################
    ## Artist URL
    #######################################################################################################################################
    def getartistAMURL(self):
        result1 = self.bsdata.find("link", {"rel": "canonical"})
        result2 = self.bsdata.find("link", {"hreflang": "en"})
        if result1 and not result2:
            result = result1
        elif result2 and not result1:
            result = result2
        elif result1 and result2:
            result = result1
        else:        
            auc = artistAMURLClass(err=True)
            return auc

        if result:
            url = result.attrs["href"]
            url = url.replace("https://www.allmusic.com", "")
            if url.find("/artist/") == -1:
                url = None
                auc = artistAMURLClass(url=url, err="NoArtist")
            else:
                auc = artistAMURLClass(url=url)
        else:
            auc = artistAMURLClass(err="NoLink")

        return auc

    

    #######################################################################################################################################
    ## Artist ID
    #######################################################################################################################################                
    def getartistAMDiscID(self, suburl):
        ival = "/artist"
        if isinstance(suburl, artistAMURLClass):
            suburl = suburl.url
        if not isinstance(suburl, str):
            aic = artistAMIDClass(err="NotStr")            
            return aic

        pos = suburl.find(ival)
        if pos == -1:
            aic = artistAMIDClass(err="NotArtist")            
            return aic

        data = suburl[pos+len(ival)+1:]
        pos  = data.rfind("-")
        discIDurl = data[(pos+3):]       
        discID = discIDurl.split("/")[0]
        
        try:
            int(discID)
        except:
            aic = artistAMIDClass(err="NotInt")            
            return aic

        aic = artistAMIDClass(ID=discID)
        return aic
    
    

    #######################################################################################################################################
    ## Artist Name
    #######################################################################################################################################
    def getartistAMName(self):
        artistBios = self.bsdata.findAll("div", {"class": "artist-bio-container"})
        if len(artistBios) > 0:
            for div in artistBios:
                h1 = div.find("h1", {"class": "artist-name"})
                if h1 is not None:
                    artistName = h1.text.strip()
                    if len(artistName) > 0:
                        artist = fixName(artistName)
                        anc = artistAMNameClass(name=artist, err=None)
                    else:
                        anc = artistAMNameClass(name=artist, err="Fix")
                else:
                    anc = artistAMNameClass(err="NoH1")
        else:       
            anc = artistAMNameClass(err=True)
            return anc
        
        return anc
    
    

    #######################################################################################################################################
    ## Artist Media
    #######################################################################################################################################
    def getartistAMMediaAlbum(self, td):
        amac = artistAMMediaAlbumClass()
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
    
    
    def getartistAMMedia(self):
        amc  = artistAMMediaClass()
        name = "Albums"
        amc.media[name] = []

        tables = self.bsdata.findAll("table")
        for table in tables:
            trs = table.findAll("tr")

            header  = trs[0]
            ths     = header.findAll("th")
            headers = [x.text.strip() for x in ths]
            

            for tr in trs[1:]:
                tds = tr.findAll("td")
                
                ## Name
                key = "Name"
                if len(headers[1]) == 0:
                    idx = 1
                    mediaType = tds[idx].text.strip()
                    if len(mediaType) == 0:
                        mediaType = name
                else:
                    mediaType = name

                ## Year
                key  = "Year"
                idx  = headers.index(key)
                year = tds[idx].text.strip()

                ## Title
                key   = "Album"
                idx   = headers.index(key)
                ref   = tds[idx].findAll("a")
                try:
                    refdata = ref[0]
                    url     = refdata.attrs['href']
                    album   = refdata.text.strip()
                    
                    data = url.split("/")[-1]
                    pos  = data.rfind("-")
                    discIDurl = data[(pos+3):]       
                    discID = discIDurl.split("/")[0]

                    try:
                        int(discID)
                        code = discID
                    except:
                        code = None
                        
                except:
                    print("Could not parse {0}".format(ref))

                amdc = artistAMMediaDataClass(album=album, url=url, aclass=None, aformat=None, artist=None, code=code, year=year)
                if amc.media.get(mediaType) is None:
                    amc.media[mediaType] = []
                amc.media[mediaType].append(amdc)

        return amc
    
    

    #######################################################################################################################################
    ## Artist Media Counts
    #######################################################################################################################################        
    def getartistAMMediaCounts(self, media):
        
        amcc = artistAMMediaCountsClass()
        
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
    def getartistAMProfile(self):       
        from json import loads
        result = self.bsdata.find("section", {"class": "basic-info"})
        if result is None:
            try:
                content = self.bsdata.find("meta", {"name": "title"})
                searchTerm = content.attrs["content"]
                searchTerm = searchTerm.replace("Artist Search for ", "")
                searchTerm = searchTerm.replace(" | AllMusic", "")
                searchTerm = searchTerm[1:-1]
            except:
                apc = artistAMProfileClass(err="No Profile")
                return apc
            
            apc = artistAMProfileClass(search=searchTerm)
            return apc
            
            
            
           
        data   = {}
       
        members = result.find("div", {"class": "group-members"})
        if members is not None:
            data["Members"] = [item.text.strip() for item in members.findAll("span")]
        else:
            data["Members"] = []
       
        genres = result.find("div", {"class": "genre"})
        genre  = self.getNamesAndURLs(genres)
        styles = result.find("div", {"class": "styles"})
        style = self.getNamesAndURLs(styles)
        #data["Profile"] = str({'genre': genre, 'style': style})
        data["Profile"] = {'genre': genre, 'style': style}
               
        apc = artistAMProfileClass(profile=data.get("Profile"), aliases=data.get("Aliases"),
                                 members=data.get("Members"), groups=data.get("In Groups"),
                                 sites=data.get("Sites"), variations=data.get("Variations"))
        return apc


    
    #######################################################################################################################################
    ## Artist Pages
    #######################################################################################################################################
    def getartistAMPages(self):
        apc   = artistAMPageClass()
        from numpy import ceil
        bsdata = self.bsdata

    
        apc   = artistAMPageClass(ppp=1, tot=1, redo=False, more=False)
        return apc
            
        pageData = bsdata.find("div", {"class": "pagination bottom"})
        if pageData is None:
            err = "pagination bottom"
            apc = artistAMPageClass(err=err)
            return apc
        else:
            x = pageData.find("strong", {"class": "pagination_total"})
            if x is None:
                err = "pagination_total"
                apc = artistAMPageClass(err=err)
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
                    apc   = artistAMPageClass(err=err)
                    return apc

                if ppp < 500:
                    if tot < 25 or ppp == tot:
                        apc   = artistAMPageClass(ppp=ppp, tot=tot, redo=False, more=False)
                    else:
                        apc   = artistAMPageClass(ppp=ppp, tot=tot, redo=True, more=False)
                else:
                    if tot < 500:
                        apc   = artistAMPageClass(ppp=ppp, tot=tot, redo=False, more=False)
                    else:
                        apc   = artistAMPageClass(ppp=ppp, tot=tot, redo=False, more=True)
                        
                return apc
            
        return artistAMPageClass()



    def parse(self):
        bsdata = self.bsdata
        
        artist      = self.getartistAMName()
        url         = self.getartistAMURL()
        ID          = self.getartistAMDiscID(url)
        pages       = self.getartistAMPages()
        profile     = self.getartistAMProfile()
        media       = self.getartistAMMedia()
        mediaCounts = self.getartistAMMediaCounts(media)
        
        err = [artist.err, url.err, ID.err, pages.err, profile.err, mediaCounts.err, media.err]
        
        adc = artistAMDataClass(artist=artist, url=url, ID=ID, pages=pages, profile=profile, mediaCounts=mediaCounts, media=media, err=err)
        
        return adc