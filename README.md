# Orion Exporter

This app is responsible to send every X minutes the configures data to Orion
Context Broker.

## Installation
To install you must add the package `` to your requirements. 

## Configuration

To set the data that you want to send to OCB you must configure the
correspondent data model. The model must inherit the `OrionEntity` model from
this package and the you must set the following property for the model:

### Inheritance

```python
from orion_exporter.models import OrionEntity

class Reading(OrionEntity):
    timestamp = models.DateTimeField()
```

### Property
```python
    @property
    def orion_properties(self):
        """Returns orion translation fields"""
        fields = {
            "<field_name>": self.<field_name>
        }
        _type = "<fiware_data_model_type>"

        return _type, fields
```

Example:

```python
    @property
    def orion_properties(self):
        """Returns orion translation fields and type"""
        fields = {
            "pm10": self.pm10
        }
        _type = "AirQualityObserved"

        return _type, fields
```

From this point you are ready to send data to OCB. Before you just need to
set in your project settings the task to do it:

```python
# Celery settings for tasks scheduling
CELERY_BEAT_SCHEDULE = {
    'export_to_orion': {
        'task': 'orion_exporter.tasks.send_to_orion',
        'schedule': timedelta(seconds=10),
        # 'schedule': crontab(minute='0', hour='0'),
        'options': {'queue': 'orion_exporter'}
    }
}
```