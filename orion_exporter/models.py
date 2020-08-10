import json
import logging as log

import requests
from django.conf import settings
from django.contrib.gis.geos import Point, Polygon, LineString
from django.db import models
from django.utils import timezone
from rest_framework import status

from orion_exporter.fields_mapping import ORION_FIELDS_TYPES


class OrionEntity(models.Model):
    sent_to_orion = models.BooleanField(
        'Sent to Orion', default=False
    )
    last_orion_update = models.DateTimeField(
        'Orion update timestamp', null=True, blank=True
    )

    class Meta:
        abstract = True

    @staticmethod
    def orion_translation(orion_type, fields, object_id):
        """
        Translates the object to be sent to Orion

        @param orion_type: Indicates the orion message type (ex.:
        AirQualityObserved)
        @param fields: All the fields that are to send to orion
        @param object_id: Object ID that will be sent to Orion
        @return: Dictionary that will be sent to orion
        """
        message = {
            "type": orion_type,
            "id": str(object_id)
        }

        for field in fields:
            for orion_type in ORION_FIELDS_TYPES:
                if isinstance(field, orion_type):
                    translation_type = ORION_FIELDS_TYPES[orion_type]
                    break
            if translation_type == "DateTime":
                value = fields[field].strftime("%Y-%m-%dT%H:%M:%SZ")

            elif isinstance(fields[field], (Point, Polygon, LineString)):
                value = json.loads(fields[field].geojson)
                value = value.coordiantes

            elif isinstance(fields[field], dict):
                value = json.dumps(fields[field])

            else:
                value = fields[field]

            message[field] = {
                "value": value,
                "type": translation_type
            }
        return message

    def send_to_orion(self, obj):
        """
        Send the object to Orion via HTTP POST Request

        @param obj: Object to be parsed and sent to Orion
        """

        orion_base_url = getattr(
            settings, 'ORION_URL', 'http://orion:1026'
        )
        headers = {
            'Content-Type': 'application/json'
        }
        orion_type, fields = obj.orion_properties
        message = self.orion_translation(
            orion_type, fields, obj.id
        )

        data = {
            "actionType": "APPEND",
            "entities": [message]
        }
        response = requests.post(
            '{}/v2/op/update'.format(orion_base_url),
            data=json.dumps(data),
            headers=headers
        )
        if response.status_code == status.HTTP_204_NO_CONTENT:
            self.sent_to_orion = True
            self.last_orion_update = timezone.now()
            self.save()
        else:
            log.error(
                "Impossible to send data to Orion Context Broker. Status "
                "Code: {}".format(response.status_code)
            )
