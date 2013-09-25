#!/usr/bin/env python3

import os, sys, logging, urllib, time, string, json, argparse, collections, datetime, re, bz2
import lz4

logging.basicConfig(level=logging.DEBUG)

sys.path.append(os.path.join(os.path.dirname(__file__), "lib", "python"))
from carta import (logger, POI)

from mongoengine import *

connect('carta')
POI.drop_collection()

#POI(name='si02', at=[151.0, -34.0]).save()

from xml.etree import cElementTree as ElementTree
#from xml.etree import ElementTree

# See http://en.wikipedia.org/wiki/Template:Coord
#ElementTree.register_namespace('http://www.mediawiki.org/xml/export-0.8/', '')

input_filename = "data/enwiki-latest-pages-articles.xml.bz2"

coord_re = re.compile("{{coord.+?}}")
#{{coord|28|N|2|E|scale:10000000_type:country_region:DZ|format=dms|display=title}}

title, text, coord = None, None, None

def normalize_coords(lat_d, long_d, lat_m=None, lat_s=None, lat_NS=None, long_m=None, long_s=None, long_EW=None):
    try:
        lat_d, long_d = float(lat_d), float(long_d)
        if lat_m:
            lat_d += float(lat_m)/60
        if lat_s:
            lat_d += float(lat_s)/3600
        if lat_NS == 'S':
            lat_d *= -1
        if long_m:
            long_d += float(long_m)/60
        if long_s:
            long_d += float(long_s)/3600
        if long_EW == 'W':
            long_d *= -1
    except:
        lat_d, long_d = None, None
    return lat_d, long_d

def coord2latlng(line):
    match = re.match("{{coord\s*\|\s*(?:([\d\.\-]+)\s*\|\s*)(?:([\d\.\-]+)\s*\|\s*)?(?:([\d\.\-]+)\s*\|\s*)?(N|S)\s*\|\s*(?:([\d\.\-]+)\s*\|\s*)(?:([\d\.\-]+)\s*\|\s*)?(?:([\d\.\-]+)\s*\|\s*)?(E|W)", line)
    if match:
        lat_d, lat_m, lat_s, lat_h, lng_d, lng_m, lng_s, lng_h = match.groups()
        return normalize_coords(lat_d, lng_d, lat_m, lat_s, lat_h, lng_m, lng_s, lng_h)
    else:
        match = re.match("{{coord\s*\|\s*([\d\.\-]+)\s*\|\s*([\d\.\-]+)", line)
        if match:
            lat_d, lng_d = match.groups()
            return float(lat_d), float(lng_d)
        else:
            raise Exception("No match")

def extract_abstract(text):
    img = None
    img_match = re.match(r"\[\[Image:([^\|\]]+)", text)
    if img_match:
        img = img_match.group(1)
    for para in text.split('\n\n'):
        if all(re.match(r'^\s*$', line) or re.match(r'^(\[\[File|\[\[Image|\{\{)', line) for line in para.split('\n')):
            continue
        abstract, template_depth = '', 0
        for chunk in re.split("(\{\{|\}\})", para):
            if chunk == '{{':
                template_depth += 1
            elif chunk == '}}':
                template_depth -= 1
            elif template_depth == 0:
                abstract += chunk
        abstract = re.sub(r"'''(.+?)'''", r"\1", abstract)
        abstract = re.sub(r"\[\[([^\|]+?)\]\]", r'<a href="//en.wikipedia.org/wiki/\1" target=_blank>\1</a>', abstract)
        abstract = re.sub(r"\[\[(.+?)\|(.+?)\]\]", r'<a href="//en.wikipedia.org/wiki/\1" target=_blank>\2</a>', abstract)
        abstract = abstract.strip()
        if re.match('^\s*$', abstract):
            continue
        elif abstract.startswith('{|') and abstract.endswith('|}'):
            continue
        elif abstract.startswith('&lt;'):
            continue
        return abstract, img

i, j = 0, 0
with bz2.BZ2File(input_filename) as bz2_fh:
    title, coords, old_coords, lat, lng, text, in_text = None, None, {}, None, None, '', False
    title_re = re.compile("^\s*<title>(.+)</title>\s*$")
    coord_re = re.compile("{{coord")
    # TODO: match one-liners (|lat_d=1|long_d=1)
    old_coord_re = re.compile("\|\s*(lat_d|lat_m|lat_s|lat_NS|long_d|long_m|long_s|long_EW)\s*=\s*([\d\.\-]+)")
    text_start_re = re.compile('^\s*<text xml:space="preserve">')
    text_end_re = re.compile("</text>\s*$")

    for line in bz2_fh:
        line = line.decode('utf-8')
        title_match = title_re.match(line)
        if title_match:
            if 'lat_d' in old_coords and 'long_d' in old_coords:
                lat, lng = normalize_coords(**old_coords)
                j += 1
            if lat and lng:
                abstract, img = extract_abstract(text) or ''
                #print("\t".join(map(str, (title, lat, lng))))
                print(title)
                try:
                    POI(name=title, at=[lng, lat], abstract=lz4.compress(abstract), alen=len(text), img=img).save()
                    #POI(name=title, at=[lng, lat], abstract=abstract).save()
                except:
                    print("Insert error:", title, lat, lng, file=sys.stderr)
#                print("Begin abstract")
#                print(abstract)
#                print("End abstract")
            title = title_match.group(1)
            coords, old_coords, lat, lng, text, in_text = None, {}, None, None, '', False
            continue
        coord_match = coord_re.match(line)
        if coord_match:
            try:
                lat, lng = coord2latlng(line)
#                print("\t".join(map(str, (title, lat, lng))))
                i += 1
            except:
                sys.stderr.write("No match: "+line)
        old_coord_match = old_coord_re.match(line)
        if old_coord_match:
            datum, value = old_coord_match.groups()
            old_coords[datum] = value
        text_start_match = text_start_re.match(line)
        if text_start_match:
            in_text = True
            text += re.match('^\s*<text xml:space="preserve">(.*)', line).group(1)
            continue
        if in_text:
            text += line
            text_end_match = text_end_re.match(line)
            if text_end_match:
                in_text = False

        if i+j>100:
            exit()

sys.stderr.write(str(i+j)+" total coords processed\n")
sys.stderr.write(str(j)+" in old format\n")

'''
    root = None
    i=0
    for event, element in ElementTree.iterparse(bz2_fh, events=("start", "end")):
        if root is None:
            root = element
        if event == 'end' and element.tag == ns+'page':
            page = element.find(ns+'revision').find(ns+'text')
            if not (page and page.text):
                continue
            coords = coord_re.match(page.text)
            if coords:
                try:
                    lat, lng = coord2latlng(coords.group(0))
                    print("\t".join([str(lat), str(lng), str(element.find(ns+'title').text)]))
#                    summary = re.match("fff", page.text, flags=re.DOTALL)
#                    summary = summary.group(1) if summary else page.text
#                    print(summary)
#                    break
                except:
                    print("No match:", coords.group(0), file=sys.stderr)
            i += 1

# [u'coord', u'21', u'28', u'57', u'S', u'39', u'40', u'19', u'E',
#[u'coord', u'37.971421', u'23.726166', u'type:landmark_region:GR', u'display=title'] Acropolis of Athens
#            
#            print(element))
#            print(element.tag)
#            print(
# and element.tag == 'page':
#            if element.find('text')
#            title = element
#            if element.tag == 'title':
#                title = element.text
            
#            if i % 10000 == 0:
#            print(element.tag, element.attrib)
            #print(bz2_fh.tell()/os.stat(input_filename).st_size)
            root.clear()
        
#        if i > 10000:
#            break
'''
