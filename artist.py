from ioUtils import getFile
from fsUtils import isFile
from webUtils import getHTML, isBS4
from strUtils import fixName
from math import ceil, floor

from discogs import discogs

class artist(discogs):
    def __init__(self):
        self.name = "artist"
        
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
                raise ValueError("Not sure about string input: {0}".format(inputdata))
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

            discID = self.getArtistDiscID(url)
            data.append([name,url,discID])                    
        return data



    def getArtistDiscID(self, suburl, debug = False):
        ival = "/artist"
        if not isinstance(suburl, str):
            return None

        pos = suburl.find(ival)
        if pos == -1:
            return None

        data = suburl[pos+len(ival)+1:]
        pos  = data.find("-")
        discID = data[:pos]
        try:
            int(discID)
        except:
            return None

        return str(discID)



    def getArtistMediaCounts(self, bsdata, debug = False):
        mediaCounts = {}
        results = bsdata.findAll("ul", {"class": "facets_nav"})
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
                            if mediaCounts.get(credittype) == None:
                                mediaCounts[credittype] = {}
                            if mediaCounts[credittype].get(creditsubtype) == None:
                                mediaCounts[credittype][creditsubtype] = count

        return mediaCounts



    def getArtistName(self, bsdata, debug = False):
        ## 1st Try
        result = bsdata.find("h1", {'class':'hide_desktop'})
        if result:
            artist = result.text
            if len(artist) > 0:
                artist = fixName(artist)
                return artist

        ## 2nd Try
        result = bsdata.find("h1", {'class':'hide_mobile'})
        if result:
            artist = result.text
            if len(artist) > 0:
                artist = fixName(artist)
                return artist

        return None



    def getArtistURL(self, bsdata, debug = False):
        # 1st Try
        result = bsdata.find("link", {"rel": "canonical"})
        if result:
            url = result.attrs["href"]
            url = url.replace("https://www.discogs.com", "")
            if url.find("/artist/") > -1:
                return url

        # 2nd Try
        result = bsdata.find("link", {"hreflang": "en"})
        if result:
            url = result.attrs["href"]
            url = url.replace("https://www.discogs.com", "")
            if url.find("/artist/") > -1:
                return url            

        return None    


    def getArtistMediaAlbum(self, td, debug = False):
        retval = {"URL": None, "Album": None, "Format": None}
        for span in td.findAll("span"):
            attrs = span.attrs
            if attrs.get("class"):
                if 'format' in attrs["class"]:
                    albumformat = span.text
                    albumformat = albumformat.replace("(", "")
                    albumformat = albumformat.replace(")", "")
                    retval["Format"] = albumformat
                    continue
            span.replaceWith("")

        ref = td.find("a")
        if ref:
            retval["URL"]   = ref.attrs['href']
            retval["Album"] = ref.text

        return retval


    def getArtistMedia(self, bsdata, debug = False):
        table = bsdata.find("table", {"id": "artist"})
        if table == None:
            return None

        media = {}
        name  = None
        for tr in table.findAll("tr"):
            h3 = tr.find("h3")
            if h3:
                name = h3.text
                media[name] = []
                continue


            # Album, Class, Format
            result = tr.find("td", {"class": "title"})
            album  = None
            url    = None
            albumformat = name
            if result:
                retval      = self.getArtistMediaAlbum(result)
                album       = fixName(retval.get("Album"))
                url         = retval.get("URL")
                albumformat = retval.get("Format")

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

            data = {}
            data["Album"]  = album
            data["URL"]    = url
            data["Class"]  = albumclass
            data["Format"] = albumformat
            data["Artist"] = artists
            data["Code"]   = code
            data["Year"]   = year
            media[name].append(data)
            #if debug: print "  Found album:",album,"of type:",name


        newMedia = {}
        for name,v in media.items():
            newMedia[name] = {}
            for item in v:
                code = item['Code']
                del item['Code']
                newMedia[name][code] = item

        media = newMedia

        return media


    def getArtistVariations(self, bsdata, debug = False):
        result = bsdata.find("div", {"class": "profile"})
        variations = {}
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
                variations[heads[i]] = content[i]

        return variations



    def getArtistPages(self, bsdata, debug = False):
        result = bsdata.find("div", {"class": "pagination bottom "})
        total = 0
        num   = 0
        if result:
            pages = result.find("strong").text
            pages = pages.strip()
            pages = pages.split()[-1]
            pages = pages.replace(",", "")
            try:
                total = int(pages)
                num = int(ceil(float(total)/500))
            except:
                raise("Can not parse pages",pages)


        return num,total


    def parse(self, debug = False):
        bsdata = self.bsdata
        
        retval = {}
        retval["Artist"]      = self.getArtistName(bsdata, debug)
        retval["URL"]         = self.getArtistURL(bsdata, debug)
        retval["ID"]          = self.getArtistDiscID(retval["URL"], debug)
        retval["Pages"]       = self.getArtistPages(bsdata, debug)
        retval["Variations"]  = self.getArtistVariations(bsdata, debug)
        retval["MediaCounts"] = self.getArtistMediaCounts(bsdata, debug)
        retval["Media"]       = self.getArtistMedia(bsdata, debug)

        #print retval
        return retval    