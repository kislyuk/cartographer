#!/usr/bin/env python3

import os, sys, logging, urllib, time, string, json, argparse, collections, datetime, re, bz2, math
from concurrent.futures import ThreadPoolExecutor, wait
import lz4

saver = ThreadPoolExecutor(max_workers=16)

logging.basicConfig(level=logging.DEBUG)

sys.path.append(os.path.join(os.path.dirname(__file__), "lib", "python"))
from carta import (logger, POI)

from mongoengine import *

connect('carta')

zoomspacing = [round(0.0001*(1.6**n), 4) for n in range(21, 1, -1)]

for lat in range(-90, 90, 2):
    for lng in range(-180, 180, 2):
        futures = []
        n_updated = 0
        points = list(POI.objects(at__geo_within_box=((lng, lat), (lng+2, lat+2))))
        for i, p1 in enumerate(points):
            for j, p2 in enumerate(points[i+1:]):
                coords1, coords2 = p1.at['coordinates'], p2.at['coordinates']
                dist = math.sqrt(abs(coords1[0]-coords2[0])**2 + abs(coords1[1]-coords2[1])**2)

                for zoom, spacing in enumerate(zoomspacing):
                    if dist < spacing:
                        continue
                    occluded_point = p1 if p1.rank < p2.rank else p2
                    break
                occluded_point.min_zoom = max(occluded_point.min_zoom, zoom)
                #futures.append(saver.submit(occluded_point.save))
                occluded_point.save()
                n_updated += 1
        #wait(futures)
        print(lat, lng, len(points), n_updated)

#        docs_by_rank = sorted(POI.objects(at__geo_within_center=(doc.at['coordinates'], spacing)),
#                              key=lambda point: point.rank or 0,
#                              reverse=True)
#		for doc in POI.objects(at__geo_within_center=(doc.at['coordinates'], 1)):
#			print("\t", doc.name, doc.min_zoom)
#        for doc in docs_by_rank:
#    for doc in POI.objects(at__geo_within_center=(doc.at['coordinates'], 1), min_zoom__gt=0).order_by('-rank'):
#    for doc in POI.objects(at__geo_within_center=(doc.at['coordinates'], 1), min_zoom=99).order_by('-rank'):
#    for doc2 in POI.objects(at__geo_within_center=(doc.at['coordinates'], zoomspacing[doc.min_zoom]), min_zoom__lte=doc.min_zoom).order_by('-rank'):
