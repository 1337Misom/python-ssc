# SPDX-License-Identifier: AGPL-3.0-or-later

from typing import Callable
from enum import Enum

from .SSCSensor import SSCSensor
from .const import SSC_MSG_REPORT_HEART_RATE
from .protobufs import ssc_sensor_heart_rate_pb2 as ssc_sensor_heart_rate


class HeartRateAccuracy(Enum):
    NoContact = -1
    Unreliable = 0
    Low = 1
    Medium = 2
    High = 3


class SSCHeartRateSensor(SSCSensor):
    def __init__(self, on_measurement: Callable):
        super().__init__("heart_rate")
        self.on_measurement_callback = on_measurement

    async def on_msg(self, msg_id: int, uid_high: int, uid_low: int, data: bytes):
        if not self.uid_high == uid_high and not self.uid_low == uid_low:
            return
        if msg_id == SSC_MSG_REPORT_HEART_RATE:
            msg = ssc_sensor_heart_rate.SscHeartRateResponse()
            msg.ParseFromString(data)

            if len(msg.bpm) != 1:
                return

            bpm = msg.bpm[0]

            if self.on_measurement_callback:
                await self.on_measurement_callback(bpm, HeartRateAccuracy(msg.accuracy))
