# Citibrain Points of Interest Django App - POIs App

This Django App provides RESTfull and AMQP interfaces for Traffic events.

## Requirements

#### Citibrain Assets App v5.0.0
* Available at `git+ssh://git@gitlab.ubiwhere.com:2223/citibrain-iot-platform/citibrain-assets.git@5.0.0`
    
#### Citibrain Skeleton App v4.0.0
* Available at `git+ssh://git@gitlab.ubiwhere.com:2223/citibrain-iot-platform/citibrain-app-skeleton.git@4.0.0`

#### RabbitMQ
TODO

## Installation

* Add `git+ssh://git@gitlab.ubiwhere.com:2223/mbaas/apps/traffic_events` to your project requirements

## Configuration

#### Project

* Add the `traffic_events` to your Django Project Installed Apps:

```
INSTALLED_APPS = [
    ...,
    'traffic_events',
]
```

* Run `python manage.py migrate`

* Include the URL conf in your project urls.py like this:

 `from traffic_events.api.urls import traffic_router`

 `url(r'^api/traffic/', include(traffic_router.urls, namespace='traffic')),`


#### Environment Variables

There are some environment variables that must be include, otherwise they will be assumed with default values:

`CONSUMER_QUEUE`: RabbitMQ queue that will be used for the AMQP connection. The default value is `pois_queue`
`CONSUMER_EXCHANGE`: RabbitMQ queue that will be used for the AMQP connection. The default value is `pois_exchange`

`AMQP_USER`: RabbitMQ User that will be used for the AMQP connection. The default value is `guest`
`AMQP_PASS`: RabbitMQ Password that will be used for the AMQP connection. The default value is `guest`
`AMQP_HOST`: RabbitMQ Host for the AMQP connection. The default value is `gurabbitmq`
`AMQP_PORT`: RabbitMQ Port AMQP connection. The default value is `5672`


## Examples

#### HTTP

* Go to `http://localhost:8000/api/traffic/traffic_events` to list all the available traffic events

#### AMQP

TODO