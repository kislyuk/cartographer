# carta: libraries and utilities used by cartographer.

import logging, time

logger = logging.getLogger(__name__)

from mongoengine import *

class POI(Document):
    name = StringField(required=True)
    at = PointField(required=True)
