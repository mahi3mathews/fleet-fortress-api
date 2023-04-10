from enum import Enum


class VehicleRouteStatus(Enum):
    STARTED = "out of depot"
    ON_THE_WAY = 'on the route'
    ON_DESTINATION = 'on destination'
    NOT_STARTED = "at depot"
