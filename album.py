from ioUtils import getFile
from fsUtils import isFile
from fsUtils import removeFile
from fileUtils import getsize
from webUtils import getHTML, isBS4
from strUtils import fixName
from math import ceil, floor
from collections import OrderedDict

from discogsBase import discogs
from discogsUtils import discogsUtils

class albumArtistsClass:
    def __init__(self):
        self.artists = []
        self.err     = None
        
    def add(self, artist):
        self.artists.append(artist)
        if artist.err is not None:
            self.err = "Artist {0}".format(artist.name)
        
    def get(self):
        return self.__dict__
    
    
class albumArtistClass:
    def __init__(self, name=None, ID=None, err=None):
        self.name = name
        self.ID   = ID
        self.err  = err
        
    def get(self):
        return self.__dict__
        
        
class albumNameClass:
    def __init__(self, name=None, err=None):
        self.name = name
        self.err  = err
        
    def get(self):
        return self.__dict__
    

class albumCodeClass:
    def __init__(self, code=None, err=None):
        self.code = code
        self.err  = err
        
    def get(self):
        return self.__dict__
    
            
class albumURLClass:
    def __init__(self, url=None, err=None):
        self.url = url
        self.err = err
        
    def get(self):
        return self.__dict__
    

class albumBasicClass:
    def __init__(self, artist=None, album=None):
        self.artist  = artist
        self.album   = album
        
    def get(self):
        return self.__dict__

    
class albumProfileClass:
    def __init__(self, label=None, aformat=None, country=None, released=None, genre=None, style=None, err=None):
        self.label    = label
        self.aformat  = aformat
        self.country  = country
        self.released = released
        self.genre    = genre
        self.style    = style
        self.err      = err
        
    def get(self):
        return self.__dict__
    

class albumTrackClass:
    def __init__(self):
        self.tracks = []
        self.err    = None
        
    def add(self, track):
        if track.position is None:
            track.position = len(self.tracks)+1
        self.tracks.append(track)
        if track.err is not None:
            self.err = "Track {0}".format(len(self.tracks))
        
    def get(self):
        return self.__dict__
    

class albumTrackDataClass:
    def __init__(self, name=None, length=None, position=None, err=None):
        self.name      = length
        self.length    = length
        self.position  = position
        self.err       = err
        
    def get(self):
        return self.__dict__
    

class albumVersionClass:
    def __init__(self, text=None, nums=None, err=None):
        self.text = text
        self.nums = nums
        self.err  = err
        
    def get(self):
        return self.__dict__
    

class albumCreditClass:
    def __init__(self):
        self.credit = {}
        self.err    = None
        
    def add(self, role, ref, err=None):
        self.credit[role] = ref
        if err is not None:
            self.err = "Role: {0}".format(role)
        
    def get(self):
        return self.__dict__
    

class albumURLInfo:
    def __init__(self, name=None, url=None, ID=None, err=None):
        self.name = name
        self.url  = url
        self.ID   = ID
        self.err  = err
        
    def get(self):
        return self.__dict__
        
        
class albumDataClass:
    def __init__(self, artist=None, album=None, profile=None, url=None, code=None, tracks=None, versions=None, credits=None, err=None):
        self.artist   = artist
        self.album    = album
        self.profile  = profile
        self.url      = url
        self.code     = code
        self.tracks   = tracks
        self.versions = versions
        self.credits  = credits
        self.err      = err
                
    def get(self):
        return self.__dict__




class album(discogs):
    def __init__(self):
        self.bsdata    = None
        self.filename  = None
        self.debug     = False
        self.dutils    = discogsUtils()

    def stripName(self, name):
        if name == None:
            return None
        
        if isinstance(name,str):
            if len(name) > 2:
                if name[:2] == "\n ":
                    name = name[2:].strip()
                if name[-1] == "\n":
                    name = name[:-1].strip()
        return name

        
        
    def getData(self, inputdata):
        bsdata = None
        if isinstance(inputdata, bytes):
            try:
                bsdata = getHTML(str(inputdata))
            except:
                raise ValueError("Not sure about btypes input: {0}".format(inputdata))
        elif isinstance(inputdata, str):
            if isFile(inputdata):
                try:
                    self.filename = inputdata
                    bsdata = getHTML(getFile(inputdata))
                except:
                    try:
                        bsdata = getHTML(getFile(inputdata, version=2))
                    except:
                        raise ValueError("Cannot read artist file: {0}".format(inputdata))
                        
                if self.filename is not None:
                    if getsize(self.filename) < 1000:
                        raise ValueError("Not a real file: {0}".format(self.filename))
            else:
                try:
                    bsdata = getHTML(inputdata)
                except:
                    raise ValueError("Not sure about string input: {0}".format(inputdata))
        elif isBS4(inputdata):
            bsdata = inputdata
        else:
            raise ValueError("Not sure about input type: {0}".format(type(inputdata)))

        self.bsdata = bsdata
        
        return self.parse()
    

    def getNamesAndURLs(self, content):
        data = []
        for ref in content.findAll("a"):
            url    = ref.attrs['href']
            name   = fixName(ref.text)
            try:
                ID = self.dutils.getArtistID(url)
            except:
                ID = None
                            
            data.append(albumURLInfo(name=name, url=url, ID=ID))
        return data


    def cleanContent(self, key, content, debug = False):
        for i,item in enumerate(content):
            name   = self.stripName(item[0])
            if debug: 
                if name != item[0]:
                    print("\t",key,'\t\t',item[0],' -> ',name)
            url    = item[1]
            discID = item[2]
            content[i] = [name,url,discID]

        return content


    def getAlbumBasics(self):
        info = {"Err": None}

        aac = albumArtistsClass()
        anc = None
        
        
        result = self.bsdata.find("div", {"class": "profile"})
        if result:
            spans = result.findAll("span")
            for span in spans:
                attrs = span.attrs
                if "title" in attrs.keys():
                    artists = self.getNamesAndURLs(span)
                    for artist in artists:
                        aac.add(artist)
                        if self.debug:
                            print("Found Artist:",artist)
                else:
                    album = fixName(span.text)
                    album = album.strip()
                    album = album.replace("\n", "")
                    anc = albumNameClass(name=album, err=None)
                    if self.debug:
                        print("Found Album:",album)


        if len(aac.artists) == 0:
            aac.err = "No Data"
        if anc is None:
            anc = albumNameClass(err="No Data")
                    
        abc = albumBasicClass(artist=aac, album=anc)
        return abc


    def getAlbumProfile(self):
        result = self.bsdata.find("div", {"class": "profile"})
        data   = {"Err": None}
        if result:
            heads = result.findAll("div", {"class": "head"})
            heads = [x.text for x in heads]
            heads = [x.replace(":","") for x in heads]

            content = result.findAll("div", {"class": "content"})
            if len(heads) != len(content):
                data["Err"] = "Mismatch in head/content"

            for i in range(min(len(heads),len(content))):
                reftest = content[i].find("a")
                if reftest:
                    content[i] = self.getNamesAndURLs(content[i])
                    if heads[i] == "Country" or heads[i] == "Released":
                        content[i][0].name = self.stripName(content[i][0].name)
                else:
                    content[i] = albumURLInfo(name=content[i].text.strip())
                data[heads[i]] = content[i]

            apc = albumProfileClass(label=data.get("Label"), aformat=data.get("Format"),
                                    country=data.get("Country"), released=data.get("Released"),
                                    genre=data.get("Genre"), style=data.get("Style"),
                                    err=data.get("Err"))
        else:
            apc = albumProfileClass(err="No Profile")                
                
        return apc



    def getAlbumTracks(self):
        atc = albumTrackClass()
        
        result = self.bsdata.find("table", {"class": "playlist"})
        if result is None:
            atc.err = "No Tracks"
        else:
            trackLines = result.findAll("tr", {"class": "track"})
            if len(trackLines) == 0:
                trackLines = result.findAll("tr", {"class": "tracklist_track"})
                
            for tr in trackLines:
                # position
                attrs = tr.attrs
                position = None
                name = None
                url  = None
                duration = None
                if attrs:
                    position = attrs.get("data-track-position")

                # name
                td = tr.find("td", {"class": "track"})
                if td:
                    span = td.find("span", {"class": "tracklist_track_title"})
                    if span:
                        name = fixName(span.text)

                    meta = td.find("meta")
                    if meta:
                        url = meta.attrs.get("content")

                # duration
                td = tr.find("td", {"class": "tracklist_track_duration"})
                if td:
                    span = td.find("span")
                    if span:
                        duration = span.text

                if name is None:
                    err = "No Name"
                elif duration is None:
                    err = "No Duration"
                else:
                    err = None

                track = albumTrackDataClass(name=name, length=duration, position=position, err=err)
                atc.add(track)

                if self.debug:
                    print(position,name,duration)

        return atc



    def getAlbumURL(self):
        url = None
        
        # 1st Try
        result = self.bsdata.find("link", {"rel": "canonical"})
        if result is not None:
            url = result.attrs["href"]
            url = url.replace("https://www.discogs.com", "")        
            if self.debug:
                print("Found URL using rel: canoical -->",url)

        # 2nd Try
        if url is None:
            result = self.bsdata.find("link", {"hreflang": "en"})
            if result is not None:
                url = result.attrs["href"]
                url = url.replace("https://www.discogs.com", "")
                if self.debug:
                    print("Found URL using hreflang: en -->",url)

        if url is not None:
            auc = albumURLClass(url=url)
        else:
            auc = albumURLClass(err="No URL")            
                    
        return auc



    def getAlbumCode(self, url):
        err  = None
        code = None
        
        if url is not None:
            try:
                code = url.split('/')[-1]
                code = str(int(code))
            except:
                err  = "NaN"

            if code == None:
                if url.find("Various?anv=") != -1:
                    code = -1
                    err = "Various"
        else:
            err = "No URL"

        acc = albumCodeClass(code=code, err=err)
        return acc



    def getAlbumVersions(self):
        err  = None
        text = None
        nums = None
        h3s  = [x for x in self.bsdata.findAll("h3") if x.attrs.get('data-for') == ".m_versions"]
        if len(h3s) == 1:
            try:
                text = removeTag(h3s[0], tag='a').text.strip()
            except:
                text = None
                err  = "LinkErr"

            if text is not None:
                try:
                    nums = text[text.find("(")+1:text.find(")")].split(" of ")
                except:
                    nums = None
                    err  = "NumErr"

                if nums is not None:
                    try:
                        nums = [int(x) for x in nums]
                    except:
                        nums = None
                        err  = "NumNotInt"
        else:
            err = "NoVersions"

        avc = albumVersionClass(text=text, nums=nums, err=err)
        return avc



    def getAlbumCredits(self):
        acc = albumCreditClass()
        
        result = self.bsdata.find("div", {"class": "credits"})
        if result:
            for li in result.findAll("li"):
                role = li.find("span", {"class": "role"})
                if role:
                    role = role.text
                href = self.getNamesAndURLs(li)
                acc.add(role, href)
        else:
            acc.err = "NoCredits"

        return acc



    def parse(self, debug = False):
        basics = self.getAlbumBasics()
        artist = basics.artist
        album  = basics.album
        
        profile     = self.getAlbumProfile()
        url         = self.getAlbumURL()
        code        = self.getAlbumCode(url.url)
        tracks      = self.getAlbumTracks()
        versions    = self.getAlbumVersions()
        credits     = self.getAlbumCredits()

        
        err = [profile.err, url.err, code.err, tracks.err, versions.err, credits.err]
        
        adc = albumDataClass(artist=artist, album=album, profile=profile, url=url, code=code, tracks=tracks, versions=versions, credits=credits)
        
        return adc