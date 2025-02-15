from typing import Callable
from enum import Enum

from .const import SSC_MSG_REPORT_MEASUREMENT
from .SSCSensor import SSCSensor
from .protobufs import ssc_sensor_accelerometer_pb2 as ssc_sensor_accel


class AccelAccuracy(Enum):
    Unreliable = 0
    Low = 1
    Medium = 2
    High = 3


class SSCAccelSensor(SSCSensor):
    def __init__(self, on_measurement: Callable):
        super().__init__("accel")
        self.on_measurement_callback = on_measurement

    async def on_msg(self, msg_id: int, uid_high: int, uid_low: int, data: bytes):
        if not self.uid_high == uid_high and not self.uid_low == uid_low:
            return
        if msg_id == SSC_MSG_REPORT_MEASUREMENT:
            msg = ssc_sensor_accel.SscAccelerometerResponse()
            msg.ParseFromString(data)
            if len(msg.acceleration) != 3:
                return
            x = msg.acceleration[0]
            y = msg.acceleration[1]
            z = msg.acceleration[2]

            if self.on_measurement_callback:
                await self.on_measurement_callback(x, y, z, AccelAccuracy(msg.accuracy))
