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
    def sanitize_value(value):
        """
        Sanitizes values
        @param value:
        @return:
        """
        return "" if not value else value

    def orion_translation(self, info):
        """
        Translates the object to be sent to Orion
        """
        fields = info.get('fields')
        message = {
            "type": info.get('orion_type'),
            "id": str(fields.get('id'))
        }
        del fields['id']

        for key, val in fields.items():
            for orion_type in ORION_FIELDS_TYPES:
                if isinstance(val, orion_type):
                    translation_type = ORION_FIELDS_TYPES[orion_type]
                    break

            if translation_type == "DateTime":
                value = val.strftime("%Y-%m-%dT%H:%M:%SZ")

            elif isinstance(val, (Point, Polygon, LineString)):
                value = json.loads(val.geojson)
                value = {
                    "type": translation_type,
                    "coordinates": value.get('coordinates')
                }
                translation_type = "geo:json"

            elif isinstance(val, dict):
                value = val

            else:
                value = val

            message[key] = {
                "value": self.sanitize_value(value),
                "type": translation_type
            }

        return message

    def send_to_orion(self, obj):
        """
        Send the object to Orion via HTTP POST Request

        @param obj: Object to be parsed and sent to Orion
        """
        info = obj.orion_properties

        if info:
            orion_base_url = getattr(
                settings, 'ORION_URL', 'http://orion:1026'
            )
            headers = {
                'Content-Type': 'application/json'
            }

            for info in info:
                message = self.orion_translation(
                    info
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
                        "Code: {}. Message: {}".format(
                            response.status_code,
                            response.text
                        )
                    )
