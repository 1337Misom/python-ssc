# SPDX-License-Identifier: AGPL-3.0-or-later

from typing import Callable
from enum import Enum

from .protobufs import ssc_sensor_lifeq_spo2_pb2 as ssc_sensor_lifeq_spo2
from .SSCSensor import SSCSensor
from .const import SSC_MSG_REPORT_MEASUREMENT

SSC_SPO2_LIFEQ_ENABLE_MSG_ID = 5336
SSC_SPO2_LIFEQ_CONFIG_MSG_ID = 5333


class SPO2Accuracy(Enum):
    Unreliable = 0
    Low = 1
    Medium = 2
    High = 3


class SPO2Gender(Enum):
    Male = 1.0
    Female = 2.0
    Unknown = 3.0


class SSCLifeqSPo2Sensor(SSCSensor):
    def __init__(self, on_measurement: Callable):
        super().__init__("spo2")
        self.on_measurement_callback = on_measurement

    async def configure(
        self,
        gender: SPO2Gender,
        age: float,
        height: float,  # in meters
        weight: float,  # in kg
        maxHeartRate: float,  # in BPM
        restingHeartRate: float,  # in BPM
        bodyFat: float,  # in percent
        vo2max: float,  # in ml/(kg*min)
        vo2min: float,  # in ml/(kg*min)
        timeZone: float,  # in min
        unixTime: float,  # in seconds
    ):
        if not self.client:
            raise RuntimeError("Tried to configure sensor without a client")
        if not self.attributes.available:
            raise RuntimeError("Tried to configure a sensor, which is unavailable")

        configure_req = ssc_sensor_lifeq_spo2.SscLifeqSPo2UserProfile()
        configure_req.gender = gender.value
        configure_req.age = age
        configure_req.height = height
        configure_req.weight = weight
        configure_req.maxHeartRate = maxHeartRate
        configure_req.restingHeartRate = restingHeartRate
        configure_req.bodyFat = bodyFat
        configure_req.vo2max = vo2max
        configure_req.vo2min = vo2min
        configure_req.timeZone = timeZone
        configure_req.unixTime = unixTime
        configure_req.testLogging = 0.0
        configure_req.enableCLC = 0.0

        msg_id = SSC_SPO2_LIFEQ_CONFIG_MSG_ID

        buf = configure_req.SerializeToString()
        await self.client.send(self.uid_high, self.uid_low, msg_id, buf)

    async def enable(
        self,
        continous: bool = False,
        timeout: int = 60,
        measurementSpacing: int = 5,
        confidenceThreshold: float = 0.90,
    ):
        if not self.attributes.available:
            raise RuntimeError("Tried to enable a sensor, which is unavailable")

        if not self.client:
            raise RuntimeError("Tried to enable sensor without a client")

        msg_id = SSC_SPO2_LIFEQ_ENABLE_MSG_ID

        enable_req = ssc_sensor_lifeq_spo2.SscLifeqSPo2Request()
        enable_req.continuous = continous
        enable_req.timeout = timeout
        enable_req.measurementSpacing = measurementSpacing
        enable_req.confidenceThreshold = confidenceThreshold
        buf = enable_req.SerializeToString()

        await self.client.send(self.uid_high, self.uid_low, msg_id, buf)

    async def on_msg(self, msg_id: int, uid_high: int, uid_low: int, data: bytes):
        if not self.uid_high == uid_high and not self.uid_low == uid_low:
            return
        if msg_id == SSC_MSG_REPORT_MEASUREMENT:
            msg = ssc_sensor_lifeq_spo2.SscLifeqSPo2Response()
            msg.ParseFromString(data)

            if len(msg.spo2) != 4:
                return

            spo2 = msg.spo2[0]
            confidence = msg.spo2[1]
            algo_state = msg.spo2[2]
            signal_state = msg.spo2[3]
            accuracy = SPO2Accuracy(msg.accuracy)

            if self.on_measurement_callback:
                await self.on_measurement_callback(
                    spo2, confidence, algo_state, signal_state, accuracy
                )
