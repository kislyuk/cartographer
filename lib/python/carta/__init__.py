# carta: libraries and utilities used by cartographer.

import logging, time

logger = logging.getLogger(__name__)

from mongoengine import *

class POI(Document):
    name = StringField(required=True)
    at = PointField(required=True, auto_index=False)
    abstract = BinaryField(required=True)
    rank = IntField(required=True)
    min_zoom = IntField(default=21)
    img = StringField()
    meta = {
        'indexes': [
            [("at", "2dsphere"), ("min_zoom", 1), ("rank": -1)],
            # [("at", "2dsphere"), ("rank", 1)],
        ]
    }
