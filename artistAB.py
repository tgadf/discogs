from ioUtils import getFile
from fsUtils import isFile
from webUtils import getHTML, isBS4
from strUtils import fixName
from math import ceil, floor
from hashlib import md5
import re
from collection import Counter
from unicodedata import normalize

from discogsBase import discogs

class artistABIDClass:
    def __init__(self, ID=None, err=None):
        self.ID=ID
        self.err=err
        
    def get(self):
        return self.__dict__
    
            
class artistABURLClass:
    def __init__(self, url=None, err=None):
        self.url = url
        self.err = err
        
    def get(self):
        return self.__dict__
        
        
class artistABNameClass:
    def __init__(self, name=None, err=None):
        self.name = name
        self.err  = err
        
    def get(self):
        return self.__dict__
    

class artistABMediaClass:
    def __init__(self, err=None):
        self.media = {}
        self.err   = err
        
    def get(self):
        return self.__dict__
    

class artistABMediaDataClass:
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
    

class artistABMediaAlbumClass:
    def __init__(self, url=None, album=None, aformat=None, err=None):
        self.url     = url
        self.album   = album
        self.aformat = aformat
        self.err     = err        
        
    def get(self):
        return self.__dict__

    
class artistABMediaCountsClass:
    def __init__(self, err=None):
        self.counts = {}
        self.err    = err
        
    def get(self):
        return self.__dict__
    

class artistABPageClass:
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
    

class artistABProfileClass:
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
    

class artistABURLInfo:
    def __init__(self, name=None, url=None, ID=None, err=None):
        self.name = name
        self.url  = url
        self.ID   = ID
        self.err  = err
        
    def get(self):
        return self.__dict__
        

class artistABDataClass:
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


        
class artistAB(discogs):
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

                ID = self.getartistABDiscID(url)
                data.append(artistABURLInfo(name=name, url=url, ID=ID))
        return data





    #######################################################################################################################################
    ## Artist URL
    #######################################################################################################################################
    def getartistABURL(self, data):
        auc = artistABURLClass(url=data["URL"])
        return auc

    

    #######################################################################################################################################
    ## Artist ID
    #######################################################################################################################################                
    def getartistABDiscID(self, suburl):
        ival = "/artist"
        if isinstance(suburl, artistABURLClass):
            suburl = suburl.url
        if not isinstance(suburl, str):
            aic = artistABIDClass(err="NotStr")            
            return aic

        pos = suburl.find(ival)
        if pos == -1:
            aic = artistABIDClass(err="NotArtist")            
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
            aic = artistABIDClass(err="NotInt")            
            return aic

        aic = artistABIDClass(ID=discID)
        return aic
    
    

    #######################################################################################################################################
    ## Artist Name
    #######################################################################################################################################
    def getartistABName(self, data):
        anc = artistABNameClass(name=data["Name"], err=None)
        return anc
    
    

    #######################################################################################################################################
    ## Artist Media
    #######################################################################################################################################
    def getartistABMediaAlbum(self, td):
        amac = artistABMediaAlbumClass()
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
    
    
    def getartistABMedia(self, data):
        amc  = artistABMediaClass()
        mediaType = "Bootleg"
        for media in data["Media"]:
            amdc = artistABMediaDataClass(album=media["AlbumName"], url=media["AlbumURL"], aclass=None, aformat=media["Format"], artist=media["AlbumArtist"], code=media["Code"], year=media["Year"])
            if amc.media.get(mediaType) is None:
                amc.media[mediaType] = []
            amc.media[mediaType].append(amdc)

        return amc
    
    

    #######################################################################################################################################
    ## Artist Media Counts
    #######################################################################################################################################        
    def getartistABMediaCounts(self, media):
        
        amcc = artistABMediaCountsClass()
        
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
    def getartistABProfile(self):
        data   = {}        
        genres = self.bsdata.find("div", {"class": "genre-list"})
        genre  = self.getNamesAndURLs(genres)
        style  = []
        data["Profile"] = {'genre': genre, 'style': style}
               
        apc = artistABProfileClass(profile=data.get("Profile"), aliases=data.get("Aliases"),
                                 members=data.get("Members"), groups=data.get("In Groups"),
                                 sites=data.get("Sites"), variations=data.get("Variations"))
        return apc


    
    #######################################################################################################################################
    ## Artist Pages
    #######################################################################################################################################
    def getartistABPages(self):
        apc   = artistABPageClass()
        from numpy import ceil
        bsdata = self.bsdata

    
        apc   = artistABPageClass(ppp=1, tot=1, redo=False, more=False)
        return apc



    def parse(self):
        bsdata = self.bsdata

        data = {}
        data["Name"]   = Counter()
        data["URL"]    = []
        data["Media"]  = []


        links = bsdata.findAll("link", {"rel": "alternate"})
        for link in links:
            ref  = link.attrs['href']
            val  = ref.split("/")[-3]
            if val in ["ace-bootlegs.com", "comments"]:
                continue
            url = "/".join(ref.split("/")[:-2])


        articles = bsdata.findAll("article")
        for ia,article in enumerate(articles):
            metas = article.attrs['class']
            posts = [x for x in metas if x.startswith("post-")]
            code  = None
            for post in posts:
                if post in ["post-entry"]:
                    continue
                try:
                    code = str(int(post.split("-")[-1]))
                except:
                    continue
                break

            h2 = article.find("h2")
            if h2 is None:
                raise ValueError("Cannot find h2 in article")
            ref = h2.find("a")
            if ref is None:
                raise ValueError("Cannot find ref in h2: {0}".format(h2))
            albumURL = ref.attrs['href']

            txt = ref.text
            #print(txt)
            txt = normalize('NFC', txt)
            #print(txt)
            vals = txt.split(" – ")
            if len(vals) == 1:
                vals = [x.decode('utf-8').replace("\t", "").strip() for x in txt.encode('utf-8').split(b"\xe2\x80\x93")]
            if len(vals) == 1:
                vals = [x.strip() for x in txt.split(" -")]
            if len(vals) < 2:
                print("Cannot find artist, album in {0}".format(txt))
                continue

            artistName = vals[0]
            albumName  = " - ".join(vals[1:])
            albumName  = " ".join([x.title() for x in albumName.split(" ")])



            metadiv  = article.find("div", {"class": "post-info"})
            if metadiv is None:
                raise ValueError("Cannot find div post-info entry")
            year = None
            for ref in metadiv.findAll("a"):
                if ref.text.startswith("19") or ref.text.startswith("20"):
                    year = ref.text
                    break


            metacontdiv  = article.find("div", {"class": "post-entry-content"})
            if metacontdiv is None:
                raise ValueError("Cannot find div post-entry-content entry")
            try:
                metatext = metacontdiv.find("p").text
            except:
                metatext = None

            keys = ["Name"]
            vals = []
            metatextsplits = metatext.split(" : ")
            for j,text in enumerate(metatextsplits):
                if j == 0:
                    words = text.split(" ")
                    nextKey = words[-1]
                    vals.append(" ".join(words[:-1]))
                else:
                    words = text.split(" ")
                    keys.append(nextKey)
                    if j < len(metatextsplits) -1:
                        nextKey = words[-1]
                        vals.append(" ".join(words[:-1]))
                    else:
                        vals.append(text)
                        break

            fmat = dict(zip(keys, vals))    

            data["Name"][artistName] += 1    
            data["URL"].append(url)    
            data["Media"].append({"AlbumName": albumName, "AlbumURL": albumURL, "AlbumArtist": artistName, "Code": code, "Year": year, "Format": fmat})

        try:
            name = " ".join([x.title() for x in data["Name"].most_common(1)[0][0].split()])
        except:
            return artistABDataClass(artist=None, url=None, ID=None, pages=None, profile=None, mediaCounts=None, media=None, err="No Name")
        data["Name"] = name

        
        artist      = self.getartistABName(data)
        url         = self.getartistABURL(data)
        ID          = self.getartistABDiscID(url)
        pages       = self.getartistABPages()
        profile     = self.getartistABProfile()
        media       = self.getartistABMedia(data)
        mediaCounts = self.getartistABMediaCounts(media)
        
        err = [artist.err, url.err, ID.err, pages.err, profile.err, mediaCounts.err, media.err]
        
        adc = artistABDataClass(artist=artist, url=url, ID=ID, pages=pages, profile=profile, mediaCounts=mediaCounts, media=media, err=err)
        
        return adc