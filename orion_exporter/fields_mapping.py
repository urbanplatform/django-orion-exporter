import datetime

from django.contrib.gis.geos import Point, Polygon, LineString

ORION_FIELDS_TYPES = {
    int: 'Integer',
    float: 'Float',
    str: 'String',
    datetime.datetime: 'DateTime',
    bool: 'Boolean',
    dict: 'Property',
    list: 'Property',
    Point: 'Point',
    Polygon: 'Polygon',
    LineString: 'LineString'
}
