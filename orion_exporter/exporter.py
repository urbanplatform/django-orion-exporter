from __future__ import absolute_import

import json
import logging

import requests
from celery import Celery
from django.conf import settings
from django.db.models.query import QuerySet
from orion_exporter.models import OrionEntity
from orion_exporter.models import OrionServicePath

ORION_URL = getattr(settings, "ORION_URL", 'http://localhost:1026/')
BROKER_URL = getattr(settings, "BROKER_URL")

app = Celery(broker=BROKER_URL)


def save_entity_and_path(entity, path):
    orion_entity, created = OrionEntity.objects.get_or_create(
        name=entity
    )

    print ('Entity {} {}.\n'.format(entity, 'created' if created else 'not created'))

    if orion_entity:
        orion_service_path, created = OrionServicePath.objects.get_or_create(
            entity=orion_entity,
            name=path
        )

        print ('Service Path {} for Entity {} {}.\n'.format(
            path, orion_entity, 'created' if created else 'not created')
        )


def get_related_field(instance, field):
    if not field:
        return None
    field_path = field.split('.')
    attr = instance
    for elem in field_path:
        try:
            attr = getattr(attr, elem)
        except AttributeError:
            return None
    return attr


@app.task
def send_request(body, headers):
    print("Sending to Orion")
    print(json.dumps(body))

    clean_headers = {
        "Content-Type": "application/json"
    }

    try:
        orion_request = requests.post("{}v2/op/update".format(ORION_URL), data=json.dumps(body), headers=headers)
        print(orion_request, orion_request.text)
    except:
        logging.exception("Failed to send update to orion for entity {} with Fiware Headers".format(body))

    save_entity_and_path(body.get('entities')[0].get('type'), headers.get('Fiware-ServicePath'))

    try:
        orion_request = requests.post("{}v2/op/update".format(ORION_URL), data=json.dumps(body), headers=clean_headers)
        print(orion_request, orion_request.text)
    except:
        logging.exception("Failed to send update to orion for entity {} without Fiware Headers".format(body))


def remove_bad_chars(value):
    bad_chars = ['<','>','"', '\'', '=', ';', '(', ')']

    if isinstance(value, basestring):
        for bad_char in bad_chars:
            value = value.replace(bad_char, '')
    return value


def get_path(instance_aux, service_path_division):
    if not service_path_division:

        return instance_aux

    for division in service_path_division:

        if instance_aux.__class__.__name__ == 'ManyRelatedManager':
            instance_aux = instance_aux.all().values()
            service_path_division.pop(0)

            for aux in instance_aux:
                return get_path(aux.get(division), service_path_division)

        else:
            if isinstance(instance_aux, QuerySet):
                for aux in instance_aux:
                    service_path_division.pop(0)
                    return get_path(aux.get(division), service_path_division)

            else:
                instance_aux = getattr(instance_aux, division)
                service_path_division.pop(0)
                return get_path(instance_aux, service_path_division)


def send_to_orion(instance):
    fields = instance.fiware_datamodel
    headers = {"Content-Type": "application/json"}

    '''
    input:
    { ...
        "service": "Ubiwhere",
        "service_path": {
            "path": "/Parking/OffStreetParking",
            "base_path": "parking_area.sources.location_name"
        }
    }

    output:
        {
            "Fiware-Service": "Ubiwhere",
            "Content-Type": "application/json",
            "Fiware-ServicePath": "Koln/Parking/OffStreetParking" # base_path + path
        }
    '''
    fiware_service = fields.get('service', {})
    service_path_division = fields.get('service_path', {}).get('base_path', {})
    service_path_division = service_path_division.split('.') if service_path_division is not None else None
    fiware_service_path = fields.get('service_path', {}).get('path', {})

    instance_aux = instance

    base_path = get_path(instance_aux, service_path_division) if service_path_division else None

    headers['Fiware-Service'] = fiware_service if fiware_service else None
    headers['Fiware-ServicePath'] = "{}{}".format(
        "/{}".format(base_path.replace(' ', '')) if base_path is not None else "", fiware_service_path
    )

    entity = {
        "id": str(get_related_field(instance, fields['id'])),
        "type": fields['type'],
    }

    for key, value in fields['dynamic_attributes'].iteritems():
        # Ignore null or empty values (don't append to entity)

        attribute_value = get_related_field(instance, key)
        force_null = value.get('force_null', False)

        if not attribute_value and not force_null:
            continue

        attribute_name = value['name']
        attribute_type = value['type']

        if not attribute_value and force_null:
            attribute_value = None
            attribute_type = 'Text'
        else:
            if attribute_type == 'DateTime':
                attribute_value = attribute_value.isoformat().replace('+00:00', 'Z')
            elif attribute_type == 'geo:json':
                attribute_value = json.loads(attribute_value.json)

        attribute = {
            attribute_name: {
                "type": attribute_type,
                "value": remove_bad_chars(attribute_value)
            }
        }
        entity.update(attribute)

    static_attributes = fields.get('static_attributes', {})
    for key, value in static_attributes.iteritems():
        entity.update({key: value})

    '''
    {
        "related_querysets": {
            "source_times": {
                "name": "sourceTimes",
                "fields": {
                    "start_date": {
                        "type": "DateTime",
                        "name": "startDate"
                    },
                    "end_date": {
                        "type": "DateTime",
                        "name": "startDate"
                    }
                }
            }
        }
    }

    {
        "sourceTimes": [
            {
                "startDate": "2018-05-01T00:00:00Z",
                "endDate": "2018-05-02T00:00:00Z"
            },
            {
                "startDate": "2018-05-01T00:00:00Z",
                "endDate": "2018-05-02T00:00:00Z"
            }
        ]
    }

    '''

    related_querysets = fields.get('related_querysets', {})

    for field, attributes in related_querysets.iteritems():
        attribute_name = attributes['name']
        fields = attributes['fields']

        '''
        Get a list of dictionaries with
        '''
        original_values = getattr(instance, field).all().values(*fields.keys())
        clean_values = []

        for entry in original_values:
            new_entry = {}

            for key, value in entry.iteritems():
                force_null = fields[key].get('force_null', False)

                if not value and not force_null:
                    continue

                entry_name = fields[key]['name']
                entry_type = fields[key]['type']

                if not value and force_null:
                    value = None
                else:
                    if entry_type == 'DateTime':
                        value = value.isoformat().replace('+00:00', 'Z')
                    elif entry_type == 'geo:json':
                        value = json.loads(value.json)

                new_entry[entry_name] = remove_bad_chars(value)

            clean_values.append(new_entry)

        entity.update(
            {
                attribute_name: {
                    "type": 'StructuredValue',
                    "value": clean_values
                }
            }
        )

    body = {
        "actionType": "APPEND",
        "entities": [entity]
    }

    send_request.delay(body, headers)
