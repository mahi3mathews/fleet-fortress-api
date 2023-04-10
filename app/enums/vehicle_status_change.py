from enum import Enum


class VehicleStatusChange:
    status_flow = {
        "NOT_STARTED": ["STARTED"],
        "STARTED": ["ON_THE_WAY"],
        "ON_THE_WAY": ["NOT_STARTED", "ON_DESTINATION"],
        "ON_DESTINATION": ["NOT_STARTED"]
    }
