from django.db import models
import pytz
import datetime
from django.contrib.gis.geos import Point, Polygon, LineString
from django.contrib.gis.db import models as gis_models
from requests import post
import json
from django.conf import settings


class OrionEntity(models.Model):
    sent = models.BooleanField('Sent to Orion', null=False, blank=False, default=False)
    last_orion_update = models.DateTimeField('Orion update timestamp', null=True, blank=True)

    class Meta:
        abstract = True

    def orion_translation(self, obj_type, obj_id, fields=None, names=None, transforms=None, metadata=None):
        type_dict = {int: 'Integer', float: 'Float', str: 'String', datetime.datetime: 'DateTime', bool: 'Boolean', dict: 'String', Point: 'Point', Polygon: 'Polygon', LineString: 'LineString'}
        bad_fields = ['id', 'sent', 'last_orion_update']

        msg = {
            'type': obj_type,
            'id': str(obj_id),
        }
        instance_vars = vars(self)

        if fields is None:
            fields = [key for key in vars(self)]
        if names is None:
            names = {}
        if transforms is None:
            transforms = {}
        for field in bad_fields:
            if field in fields:
                fields.remove(field)
        for field in fields:
            if field[0] == '_':
                fields.remove(field)

        for field in fields:
            if field in instance_vars and instance_vars[field] is not None:
                aux = None
                for var_type in type_dict:
                    if isinstance(instance_vars[field], var_type):
                        aux = type_dict[var_type]
                        break
                name = names.get(field)
                if name is None:
                    name = field
                if aux == 'DateTime':
                    val = instance_vars[field].strftime("%Y-%m-%dT%H:%M:%SZ")
                elif isinstance(instance_vars[field], dict):
                    val = json.dumps(instance_vars[field])
                else:
                    val = instance_vars[field]
                if isinstance(instance_vars[field], (Point, Polygon, LineString)):
                    msg[name] = json.loads(instance_vars[field].geojson)
                    msg[name]['value'] = msg[name].pop('coordinates')
                else:
                    msg[name] = {
                        'value': transforms[field](val) if field in transforms else val,
                        'type': aux
                    }
                if metadata is not None and metadata.get(field) is not None:
                    msg[name]['metadata'] = metadata.get(field)

        return msg

    def send_to_orion(self, obj_type, obj_id, fields=None, names=None, transforms=None, metadata=None):
        orion_base_url = getattr(settings, 'ORION_URL', 'http://orion:1026')
        headers = {'Content-Type': 'application/json'}
        message = self.orion_translation(obj_type, obj_id, fields, names, transforms, metadata)
        data = {
            "actionType": "APPEND",
            "entities": [message]
        }
        x = post('{}/v2/op/update'.format(orion_base_url), data=json.dumps(data), headers=headers)
        if x.status_code == 204:
            self.sent = True
            self.last_orion_update = datetime.datetime.now(tz=pytz.UTC)
            self.save()
