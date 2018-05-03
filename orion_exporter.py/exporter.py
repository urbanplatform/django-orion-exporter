import json
import requests

from django.conf import settings

ORION_URL = getattr(settings, ORION_URL, 'http://localhost:1026/')


def get_related_field(instance, field):
    field_path = field.split('.')
    attr = instance
    for elem in field_path:
        try:
            attr = getattr(attr, elem)
        except AttributeError:
            return None
    return attr

def send_to_orion(instance):
    fields = instance.fiware_datamodel

    entity = {
        "id": str(get_related_field(instance, fields['id'])),
        "type": fields['type'],
    }

    for key, value in fields['dynamic_attributes'].iteritems():
        attribute_value = getattr(instance, key)
        attribute_name = value['name']
        attribute_type = value['type']
        
        if attribute_type == 'DateTime':
            attribute_value = attribute_value.isoformat().replace('+00:00', 'Z')
        elif attribute_type == 'geo:json':
            attribute_value = json.loads(attribute_value.json)

        attribute = {
            attribute_name: {
                "type": attribute_type,
                "value": attribute_value
            }
        }
        entity.update(attribute)
    
    for key, value in fields['static_attributes'].iteritems():
        entity.update({key: value})

    body = {
        "actionType": "APPEND",
        "entities": [entity]
    }
    
    orion_request = requests.post("{}v2/op/update".format(ORION_URL), data=json.dumps(body), headers={"Content-Type": "application/json"})
    print("Sending to Orion")
    print(json.dumps(body))
    print(orion_request)
