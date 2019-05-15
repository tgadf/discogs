# -*- coding: utf-8 -*-
"""
Created on Fri Feb 17 15:45:48 2017

@author: tgadfort
"""

import bs4
from math import ceil
from strops import fixName
#import unicodedata as ud



def getNamesAndURLs(content):
    data = []
    for ref in content.findAll("a"):
        url    = ref.attrs['href']
        name   = ref.text
          
        discID = getArtistDiscID(url)
        data.append([name,url,discID])                    
    return data
    


def getArtistDiscID(suburl, debug = False):
    ival = "/artist"
    if not isinstance(suburl, str) and not isinstance(suburl, unicode):
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
    
    
    
def getArtistMediaCounts(bsdata, debug = False):
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
    
    

def getArtistName(bsdata, debug = False):
    ## 1st Try
    result = bsdata.find("h1", {'class':'hide_desktop'})
    if result:
        artist = result.text
        if len(artist) > 0:
            if debug: print "Found artist using hide_desktop:",artist
            artist = fixName(artist)
            return artist
        
    ## 2nd Try
    result = bsdata.find("h1", {'class':'hide_mobile'})
    if result:
        artist = result.text
        if len(artist) > 0:
            if debug: print "Found artist using hide_mobile:",artist
            artist = fixName(artist)
            return artist
        
    return None
    
    
    
def getArtistURL(bsdata, debug = False):
    # 1st Try
    result = bsdata.find("link", {"rel": "canonical"})
    if result:
        url = result.attrs["href"]
        url = url.replace("https://www.discogs.com", "")
        if url.find("/artist/") > -1:
            if debug: print "Found URL using rel: canoical -->",url
            return url
            
    # 2nd Try
    result = bsdata.find("link", {"hreflang": "en"})
    if result:
        url = result.attrs["href"]
        url = url.replace("https://www.discogs.com", "")
        if url.find("/artist/") > -1:
            if debug: print "Found URL using hreflang: en -->",url
            return url            

    if debug: print "Could not find URL!"
    return None    
    

def getArtistMediaAlbum(td, debug = False):
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
    
    
def getArtistMedia(bsdata, debug = False):
    table = bsdata.find("table", {"id": "artist"})
    if table == None:
        if debug: print "Could not find any media!"
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
            retval      = getArtistMediaAlbum(result)
            album       = fixName(retval.get("Album"))
            url         = retval.get("URL")
            albumformat = retval.get("Format")

        if album == None:
            if debug: print "Could not find album name."
            continue
        
        # Code
        code = tr.attrs.get("data-object-id")
        
        # AlbumClass
        albumclass = tr.attrs.get("data-object-type")
        
        # AlbumURL
        result  = tr.find("td", {"class": "artist"})
        artists = None
        if result:
            artists = getNamesAndURLs(result)
                
        # Year
        result = tr.find("td", {"class": "year"})
        year   = None
        if result:
            year = result.text

        if False:
            print album
            print artists
            print albumformat
            print albumclass
            print code
            print year
        
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
    for name,v in media.iteritems():
        newMedia[name] = {}
        for item in v:
            code = item['Code']
            del item['Code']
            newMedia[name][code] = item
        
    media = newMedia
    
    if debug:
        print "Found the following media and counts:"
        for k,v in media.iteritems():
            print "  ",len(v),'\t',k
    return media
    
    
def getArtistVariations(bsdata, debug = False):
    result = bsdata.find("div", {"class": "profile"})
    variations = {}
    if result:
        heads = result.findAll("div", {"class": "head"})
        heads = [x.text for x in heads]
        heads = [x.replace(":","") for x in heads]
        
        content = result.findAll("div", {"class": "content"})
        if len(heads) != len(content):
            print "Mismatch in head/content"
            raise()

        for i in range(len(heads)):
            if heads[i] == "Sites":
                content[i] = getNamesAndURLs(content[i])
            elif heads[i] == "In Groups":
                content[i] = getNamesAndURLs(content[i])
            elif heads[i] == "Variations":
                content[i] = getNamesAndURLs(content[i])
            elif heads[i] == "Aliases":
                content[i] = getNamesAndURLs(content[i])
            else:
                content[i] = content[i].text
                content[i] = content[i].strip()
            variations[heads[i]] = content[i]
    
    return variations
    
    
    
def getArtistPages(bsdata, debug = False):
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
            if debug: print "Found pages from total",num,total
        except:
            if debug: print "Can not parse pages",pages
            raise()
        
            
    return num,total
        
    
def parse(bsdata, debug = False):
    if not isinstance(bsdata, bs4.BeautifulSoup):
        print "Can not parse artist because data is not BS4."
        raise()
    
    retval = {}
    retval["Artist"]      = getArtistName(bsdata, debug)
    retval["URL"]         = getArtistURL(bsdata, debug)
    retval["ID"]          = getArtistDiscID(retval["URL"], debug)
    retval["Pages"]       = getArtistPages(bsdata, debug)
    retval["Variations"]  = getArtistVariations(bsdata, debug)
    retval["MediaCounts"] = getArtistMediaCounts(bsdata, debug)
    retval["Media"]       = getArtistMedia(bsdata, debug)

    #print retval
    return retval    