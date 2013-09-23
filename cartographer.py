#!/usr/bin/env python3

import os, sys, logging, urllib, time, string, json, argparse, collections, datetime, re
from functools import wraps

import lz4

from flask import Flask, request, redirect, render_template, url_for, flash, session, jsonify, send_from_directory

logging.basicConfig(level=logging.DEBUG)

sys.path.append(os.path.join(os.path.dirname(__file__), "lib", "python"))
from carta import (logger, POI)

from mongoengine import *

connect('carta')

#POI(name='w00tz', at=[150.0, -34.0]).save()
#POI(name='si02', at=[151.0, -34.0]).save()
#POI(name="Her Majesty's Ass", at=[0.0, 0.0]).save()

#for p in POI.objects(at__geo_within_box=((149.0, -34.0), (152.0, -34.0))):
#    print(p.to_json())
# for p in POI.objects(at__geo_within_box=((147.32612890625, -35.31204838938832), (153.96187109375, -33.471836015830874))):
#     print("w00tw00t"+p.name)

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

        points = POI.objects(at__geo_within_box=(request.json['SW'], request.json['NE']))
        for p in points:
            print(p.name, p.at)
        print(p.at['coordinates'])
        return jsonify({"points": [{"name": p.name,
                                    "lat": p.at['coordinates'][1],
                                    "lng": p.at['coordinates'][0],
                                    "abstract": lz4.decompress(p.abstract).decode() if p.abstract else ''
                                    } for p in points]})

    return app

args = parse_args()

server = create_cartographer(args)

if __name__ == '__main__':
    server.run(host='0.0.0.0', port=args.port, debug=True, use_reloader=True)
