from typing import Callable
from enum import Enum

from .SSCSensor import SSCSensor
from .const import SSC_MSG_REPORT_MEASUREMENT
from .protobufs import ssc_sensor_pressure_pb2 as ssc_sensor_pressure


class PressureAccuracy(Enum):
    Unreliable = 0
    Low = 1
    Medium = 2
    High = 3


class SSCPressureSensor(SSCSensor):
    def __init__(self, on_measurement: Callable):
        super().__init__("pressure")
        self.on_measurement_callback = on_measurement

    async def on_msg(self, msg_id: int, uid_high: int, uid_low: int, data: bytes):
        if not self.uid_high == uid_high and not self.uid_low == uid_low:
            return
        if msg_id == SSC_MSG_REPORT_MEASUREMENT:
            msg = ssc_sensor_pressure.SscPressureResponse()
            msg.ParseFromString(data)

            if len(msg.pressure) != 1:
                return

            pressure = msg.pressure[0]

            if self.on_measurement_callback:
                await self.on_measurement_callback(
                    pressure, PressureAccuracy(msg.accuracy)
                )
