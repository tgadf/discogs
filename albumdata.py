# -*- coding: utf-8 -*-
"""
Created on Sun Feb 19 11:26:57 2017

@author: tgadfort
"""

from htmlParser import isBS4
from collections import OrderedDict
from strops import fixName, stripName



def getNamesAndURLs(content):
    data = []
    for ref in content.findAll("a"):
        url    = ref.attrs['href']
        name   = fixName(ref.text)
        discID = getArtistDiscID(url)
        data.append([name,url,discID])
    return data
    

def cleanContent(key, content, debug = False):
    for i,item in enumerate(content):
        name   = stripName(item[0])
        if debug: 
            if name != item[0]:
                print "\t",key,'\t\t',item[0],' -> ',name
        url    = item[1]
        discID = item[2]
        content[i] = [name,url,discID]
        
    return content


def getArtistDiscID(suburl, debug = False):
    ival = "/artist"
    if not isinstance(suburl, str):
        if debug: print "SUBURL is not a string:",suburl
        return None
        
    pos = suburl.find(ival)
    if pos == -1:
        if debug: print "Could not find discID in", suburl
        return None
            
    data = suburl[pos+len(ival)+1:]
    pos  = data.find("-")
    discID = data[:pos]
    try:
        int(discID)
    except:
        if debug: print "DiscID is not an integer:",discID
        return None
    
    if debug: print "Found ID:",discID
    return str(discID)


def getAlbumInfo(bsdata, filename = None, debug = False):
    result = bsdata.find("div", {"class": "profile"})
    info = {}
    if result:
        for span in result.findAll("span", {"itemprop": "name"}):
            attrs = span.attrs
            if "title" in attrs.keys():
                artist = getNamesAndURLs(span)
                if info.get("Artist") == None:
                    info["Artist"] = []
                info["Artist"].append(artist)
                if debug:
                    print "Found Artist:",artist
            else:
                album = fixName(span.text)
                album = album.strip()
                album = album.replace("\n", "")
                info["Album"] = album
                if debug:
                    print "Found Album:",info["Album"]

    if info.get("Artist") == None:
        print result
        print filename
        raise ValueError("No Artist!!")

    ## Fix artist list (if needed)
    artists = []
    for artist in info["Artist"]:
        if isinstance(artist, list):
            if isinstance(artist[0], list):
                artists.append(artist[0])
            else:
                artists.append(artist)
        else:
            artists.append(artist)

    info["Artist"] = artists
            
    return info
        
    
def getAlbumProfile(bsdata, filename = None, debug = False):
    result = bsdata.find("div", {"class": "profile"})
    variations = {}
    if result:
        heads = result.findAll("div", {"class": "head"})
        heads = [x.text for x in heads]
        heads = [x.replace(":","") for x in heads]
        
        content = result.findAll("div", {"class": "content"})
        if len(heads) != len(content):
            print "Mismatch in head/content"

        for i in range(min(len(heads),len(content))):
            reftest = content[i].find("a")
            if reftest:
                content[i] = getNamesAndURLs(content[i])
                if heads[i] == "Country" or heads[i] == "Released":
                    content[i] = cleanContent(heads[i], content[i])
            else:
                content[i] = content[i].text
                content[i] = content[i].strip()
            variations[heads[i]] = content[i]
    
    return variations



def getAlbumTracks(bsdata, filename = None, debug = False):
    result = bsdata.find("table", {"class": "playlist"})
    tracks = OrderedDict()
    if result:
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

            if position == None:
                position = len(tracks)+1

            tracks[position] = {"Name": name, "Length": duration}
            
            if debug: print position,name,url,duration          
            
    return tracks
    
    
    
def getAlbumURL(bsdata, filename = None, debug = False):
    # 1st Try
    result = bsdata.find("link", {"rel": "canonical"})
    if result:
        url = result.attrs["href"]
        url = url.replace("https://www.discogs.com", "")        
        if debug: print "Found URL using rel: canoical -->",url
        return url
            
    # 2nd Try
    result = bsdata.find("link", {"hreflang": "en"})
    if result:
        url = result.attrs["href"]
        url = url.replace("https://www.discogs.com", "")
        if debug: print "Found URL using hreflang: en -->",url
        return url

    if debug: print "Could not find URL!"
    return None



def getAlbumCode(albumURL, filename = None, debug = False):
    try:
        code = albumURL.split('/')[-1]
        code = str(int(code))
    except:
        code = None
        
    if code == None:
        if albumURL.find("Various?anv=") != -1:
            code = -1
            
    return code
        


def getAlbumVersions(bsdata, filename = None, debug = False):
    for h3 in bsdata.findAll("h3"):
        attrs = h3.attrs
        if attrs.get("data-for"):
            if attrs["data-for"] == ".m_versions":
                for val in h3.strings:
                    if val.find("Versions") != -1:
                        versions = val.replace("Versions", "")
                        versions = versions.replace("(", "")
                        versions = versions.replace(")", "")
                        versions = versions.strip()
                        if debug: print "Found versions:",versions
                        return versions
        
    if debug: print "Found NO versions!"
    return None



def getAlbumCredits(bsdata, filename = None, debug = False):    
    result = bsdata.find("div", {"class": "credits"})
    credit = {}
    if result:
        for li in result.findAll("li"):
            role = li.find("span", {"class": "role"})
            if role:
                role = role.text
            href = getNamesAndURLs(li)
            credit[role] = href
    
    return credit

        
    
def parse(bsdata, filename = None, debug = False):
    if not isBS4(bsdata):
        raise ValueError("Can not parse album because data is not BS4.")
    
    keys = ["Artist", "Album", "Profile", "URL", "Tracks", "Versions", "Credits"]    
    retval = {}
    for key in keys: retval[key] = None
    info                  = getAlbumInfo(bsdata, filename, debug)
    if info.get("Album") == None:
        print "Could not find Album for file:"
        print filename
        return retval
    if info.get("Artist") == None:
        print "Could not find Artist for file:"
        print filename
        return retval
    
    retval["Album"]       = info["Album"]
    retval["Artist"]      = info["Artist"]
    retval["Profile"]     = getAlbumProfile(bsdata, filename, debug)
    retval["URL"]         = getAlbumURL(bsdata, filename, debug)
    retval["Tracks"]      = getAlbumTracks(bsdata, filename, debug)
    retval["Versions"]    = getAlbumVersions(bsdata, filename, debug)
    retval["Credits"]     = getAlbumCredits(bsdata, filename, debug)

    #print retval
    return retval    