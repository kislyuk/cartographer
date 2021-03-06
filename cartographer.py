#!/usr/bin/env python3

'''
identify important articles by article length - need compound index
search box
aggregate multiple icons into one that pops up a list
    ag clustering
    with a (+) button to zoom in to that cluster?
links to geo sightseeing blogs/aggregator/backref layer scrape
disqus or lighter on all abstracts; preserve links on all abstracts
panoramio layer
check wp for color conventions/add colors
scrape international wikipedias and add in-place translate

assign to each article the min zoomlevel at which it will be returned

after load:
    for every article, query db and rebalance zoomlevels within radius


find how to get better rank than alen (featured article status?)
client side: aggregation box
try to process region
'''

import os, sys, logging, urllib, time, string, json, argparse, collections, datetime, re
from functools import wraps

import lz4

from flask import Flask, request, redirect, render_template, url_for, flash, session, jsonify, send_from_directory

logging.basicConfig(level=logging.DEBUG)

sys.path.append(os.path.join(os.path.dirname(__file__), "lib", "python"))
from carta import (logger, POI)
from carta.packages.ensure import ensure

from mongoengine import *

connect('carta')

def parse_args():
    parser = argparse.ArgumentParser(description="Cartographer")
    parser.add_argument("--port", help="TCP port to listen on", type=int, default=9090)
    parser.add_argument("--mongo-host", help="Hostname to contact MongoDB on", default='localhost')
    parser.add_argument("--mongo-port", help="TCP port to contact MongoDB on", type=int, default=27027)
    parser.add_argument("--debug", action='store_true', default=False)
    args = parser.parse_args()
    return args

def create_cartographer(args):
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'map the soul'

    @app.route("/")
    def hi():
        return render_template('index.html')

    @app.route("/getPoints", methods=['POST'])
    def getPoints():
        print(request.json)
        zoom = int(request.json.get('zoom', 1))
        seen = request.json.get('seen', [])
        ensure(seen).is_a_list_of(str)
        points = POI.objects(at__geo_within_box=(request.json['SW'], request.json['NE']),
                             min_zoom=zoom,
                             name__nin=request.json['seen'])

        return jsonify({"points": [{"name": p.name,
                                    "lat": p.at['coordinates'][1],
                                    "lng": p.at['coordinates'][0],
                                    "abstract": lz4.decompress(p.abstract).decode() if p.abstract else '',
                                    "img": p.img,
                                    } for p in points]})

    return app

args = parse_args()

server = create_cartographer(args)

if __name__ == '__main__':
    server.run(host='0.0.0.0', port=args.port, debug=True, use_reloader=True)
