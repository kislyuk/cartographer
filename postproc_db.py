#!/usr/bin/env python3

import os, sys, logging, urllib, time, string, json, argparse, collections, datetime, re, bz2
import lz4

logging.basicConfig(level=logging.DEBUG)

sys.path.append(os.path.join(os.path.dirname(__file__), "lib", "python"))
from carta import (logger, POI)

from mongoengine import *

connect('carta')

zoomspacing = (round(0.001*(1.6**n), 4) for n in range(21, 1, -1))

i=0
for doc in POI.objects:
	print(doc.name)
	for zoom, spacing in enumerate(zoomspacing):
		docs_by_rank = sorted(POI.objects(at__geo_within_center=(doc.at['coordinates'], spacing)),
			                  key=lambda point: point.alen or 0,
			                  reverse=True)
#		for doc in POI.objects(at__geo_within_center=(doc.at['coordinates'], 1)):
#			print("\t", doc.name, doc.min_zoom)
		for doc in docs_by_rank:
			print(zoom, spacing, doc.alen, "\t", doc.name)

	i += 1
	if i > 10:
		break
