# SPDX-License-Identifier: AGPL-3.0-or-later

from enum import Enum
from typing import Callable
import math

from .protobufs import ssc_sensor_rotationvector_pb2 as ssc_senso_rotv
from .SSCSensor import SSCSensor
from .const import SSC_MSG_REPORT_MEASUREMENT


class CompassAccuracy(Enum):
    Unreliable = 0
    Low = 1
    Medium = 2
    High = 3


class SSCCompassSensor(SSCSensor):
    def __init__(self, on_measurement: Callable):
        super().__init__("rotv")
        self.on_measurement_callback = on_measurement

    async def calculate_azimuth(self, x: float, y: float, z: float, w: float) -> float:
        q0 = w
        q1 = x
        q2 = y
        q3 = z

        q1_q2 = 2 * q1 * q2
        q3_q0 = 2 * q3 * q0
        sq_q1 = 2 * q1 * q1
        sq_q3 = 2 * q3 * q3

        r1 = q1_q2 - q3_q0
        r4 = 1 - sq_q1 - sq_q3
        azimuth = math.atan2(r1, r4)

        azimuth = azimuth * 180 / math.pi
        if azimuth < 0.0:
            azimuth += 360.0

        return azimuth

    async def on_msg(self, msg_id: int, uid_high: int, uid_low: int, data: bytes):
        if not self.uid_high == uid_high and not self.uid_low == uid_low:
            return
        if msg_id == SSC_MSG_REPORT_MEASUREMENT:
            msg = ssc_senso_rotv.SscRotationvectorResponse()
            msg.ParseFromString(data)

            if len(msg.rotation) != 4:
                return

            x = msg.rotation[0]
            y = msg.rotation[1]
            z = msg.rotation[2]
            w = msg.rotation[3]
            azimuth = await self.calculate_azimuth(x, y, z, w)

            accuracy = CompassAccuracy(msg.accuracy)

            if self.on_measurement_callback:
                await self.on_measurement_callback(azimuth, accuracy)
