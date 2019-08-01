from ioUtils import getFile
from fsUtils import isFile
from webUtils import getHTML, isBS4
from strUtils import fixName
from math import ceil, floor

from discogsBase import discogs

class artistIDClass:
    def __init__(self, ID=None, err=None):
        self.ID=ID
        self.err=err
        
    def get(self):
        return self.__dict__
    
            
class artistURLClass:
    def __init__(self, url=None, err=None):
        self.url = url
        self.err = err
        
    def get(self):
        return self.__dict__
        
        
class artistNameClass:
    def __init__(self, name=None, err=None):
        self.name = name
        self.err  = err
        
    def get(self):
        return self.__dict__
    

class artistMediaClass:
    def __init__(self, err=None):
        self.media = {}
        self.err   = err
        
    def get(self):
        return self.__dict__
    

class artistMediaDataClass:
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
    

class artistMediaAlbumClass:
    def __init__(self, url=None, album=None, aformat=None, err=None):
        self.url     = url
        self.album   = album
        self.aformat = aformat
        self.err     = err        
        
    def get(self):
        return self.__dict__

    
class artistMediaCountsClass:
    def __init__(self, err=None):
        self.counts = {}
        self.err    = err
        
    def get(self):
        return self.__dict__
    

class artistPageClass:
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
    

class artistProfileClass:
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
    

class artistURLInfo:
    def __init__(self, name=None, url=None, ID=None, err=None):
        self.name = name
        self.url  = url
        self.ID   = ID
        self.err  = err
        
    def get(self):
        return self.__dict__
        

class artistDataClass:
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


        
class artist(discogs):
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
        for ref in content.findAll("a"):
            url    = ref.attrs['href']
            name   = ref.text

            ID = self.getArtistDiscID(url)
            data.append(artistURLInfo(name=name, url=url, ID=ID))
        return data





    #######################################################################################################################################
    ## Artist URL
    #######################################################################################################################################
    def getArtistURL(self):
        result1 = self.bsdata.find("link", {"rel": "canonical"})
        result2 = self.bsdata.find("link", {"hreflang": "en"})
        if result1 and not result2:
            result = result1
        elif result2 and not result1:
            result = result2
        elif result1 and result2:
            result = result1
        else:        
            auc = artistURLClass(err=True)
            return auc

        if result:
            url = result.attrs["href"]
            url = url.replace("https://www.discogs.com", "")
            if url.find("/artist/") == -1:
                url = None
                auc = artistURLClass(url=url, err="NoArtist")
            else:
                auc = artistURLClass(url=url)
        else:
            auc = artistURLClass(err="NoLink")

        return auc

    

    #######################################################################################################################################
    ## Artist ID
    #######################################################################################################################################                
    def getArtistDiscID(self, suburl):
        ival = "/artist"
        if isinstance(suburl, artistURLClass):
            suburl = suburl.url
        if not isinstance(suburl, str):
            aic = artistIDClass(err="NotStr")            
            return aic

        pos = suburl.find(ival)
        if pos == -1:
            aic = artistIDClass(err="NotArtist")            
            return aic

        data = suburl[pos+len(ival)+1:]
        pos  = data.find("-")
        discID = data[:pos]
        try:
            int(discID)
        except:
            aic = artistIDClass(err="NotInt")            
            return aic

        aic = artistIDClass(ID=discID)
        return aic
    
    

    #######################################################################################################################################
    ## Artist Name
    #######################################################################################################################################
    def getArtistName(self):
        result1 = self.bsdata.find("h1", {'class':'hide_desktop'})
        result2 = self.bsdata.find("h1", {'class':'hide_mobile'})
        if result1 and not result2:
            result = result1
        elif result2 and not result1:
            result = result2
        elif result1 and result2:
            result = result1
        else:        
            anc = artistNameClass(err=True)
            return anc

        if result:
            artist = result.text
            if len(artist) > 0:
                artist = fixName(artist)
                anc = artistNameClass(name=artist, err=None)
            else:
                anc = artistNameClass(name=artist, err="Fix")
        else:
            anc = artistNameClass(err="NoH1")

        return anc
    
    

    #######################################################################################################################################
    ## Artist Media
    #######################################################################################################################################
    def getArtistMediaAlbum(self, td):
        amac = artistMediaAlbumClass()
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
    
    
    def getArtistMedia(self):
        amc = artistMediaClass()
        
        table = self.bsdata.find("table", {"id": "artist"})
        if table == None:
            amc.err="NoMedia"
            return amc

        name  = None
        for tr in table.findAll("tr"):
            h3 = tr.find("h3")
            if h3:
                name = h3.text
                amc.media[name] = []
                continue


            # Album, Class, Format
            result = tr.find("td", {"class": "title"})
            album  = None
            url    = None
            albumformat = name
            if result:
                retval      = self.getArtistMediaAlbum(result)
                album       = fixName(retval.album)
                url         = retval.url
                albumformat = retval.aformat

            if album == None:
                continue

            # Code
            code = tr.attrs.get("data-object-id")

            # AlbumClass
            albumclass = tr.attrs.get("data-object-type")

            # AlbumURL
            result  = tr.find("td", {"class": "artist"})
            artists = None
            if result:
                artists = self.getNamesAndURLs(result)

            # Year
            result = tr.find("td", {"class": "year"})
            year   = None
            if result:
                year = result.text

            amdc = artistMediaDataClass(album=album, url=url, aclass=albumclass, aformat=albumformat, artist=artists, code=code, year=year)
            amc.media[name].append(amdc)
            #if debug: print "  Found album:",album,"of type:",name


        if False:
            newMedia = {}
            for name,v in media.items():
                newMedia[name] = {}
                for item in v:
                    code = item['Code']
                    del item['Code']
                    newMedia[name][code] = item

            media = newMedia

        return amc
    
    

    #######################################################################################################################################
    ## Artist Media Counts
    #######################################################################################################################################        
    def getArtistMediaCounts(self):
        amcc = artistMediaCountsClass()
        
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
    def getArtistProfile(self):        
        result = self.bsdata.find("div", {"class": "profile"})
        data = {}
        if result:
            heads = result.findAll("div", {"class": "head"})
            heads = [x.text for x in heads]
            heads = [x.replace(":","") for x in heads]

            content = result.findAll("div", {"class": "content"})
            if len(heads) != len(content):
                raise("Mismatch in head/content")

            for i in range(len(heads)):
                if heads[i] == "Sites":
                    content[i] = self.getNamesAndURLs(content[i])
                elif heads[i] == "In Groups":
                    content[i] = self.getNamesAndURLs(content[i])
                elif heads[i] == "Variations":
                    content[i] = self.getNamesAndURLs(content[i])
                elif heads[i] == "Aliases":
                    content[i] = self.getNamesAndURLs(content[i])
                else:
                    content[i] = content[i].text
                    content[i] = content[i].strip()
                data[heads[i]] = content[i]
                
            apc = artistProfileClass(profile=data.get("Profile"), aliases=data.get("Aliases"),
                                     members=data.get("Members"), groups=data.get("In Groups"),
                                     sites=data.get("Sites"), variations=data.get("Variations"))
        else:
            apc = artistProfileClass(err="No Profile")
                
        return apc


    
    #######################################################################################################################################
    ## Artist Pages
    #######################################################################################################################################
    def getArtistPages(self):
        from numpy import ceil
        bsdata = self.bsdata


        pageData = bsdata.find("div", {"class": "pagination bottom"})
        if pageData is None:
            err = "pagination bottom"
            apc = artistPageClass(err=err)
            return apc
        else:
            x = pageData.find("strong", {"class": "pagination_total"})
            if x is None:
                err = "pagination_total"
                apc = artistPageClass(err=err)
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
                    apc   = artistPageClass(err=err)
                    return apc

                if ppp < 500:
                    if tot < 25 or ppp == tot:
                        apc   = artistPageClass(ppp=ppp, tot=tot, redo=False, more=False)
                    else:
                        apc   = artistPageClass(ppp=ppp, tot=tot, redo=True, more=False)
                else:
                    if tot < 500:
                        apc   = artistPageClass(ppp=ppp, tot=tot, redo=False, more=False)
                    else:
                        apc   = artistPageClass(ppp=ppp, tot=tot, redo=False, more=True)
                        
                return apc
            
        return artistPageClass()



    def parse(self):
        bsdata = self.bsdata
        
        artist      = self.getArtistName()
        url         = self.getArtistURL()
        ID          = self.getArtistDiscID(url)
        pages       = self.getArtistPages()
        profile     = self.getArtistProfile()
        mediaCounts = self.getArtistMediaCounts()
        media       = self.getArtistMedia()
        
        err = [artist.err, url.err, ID.err, pages.err, profile.err, mediaCounts.err, media.err]
        
        adc = artistDataClass(artist=artist, url=url, ID=ID, pages=pages, profile=profile, mediaCounts=mediaCounts, media=media, err=err)
        
        return adc