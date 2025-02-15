from typing import Callable

from .SSCSensor import SSCSensor
from .const import SSC_MSG_REPORT_PEDO_STEP_EVENT, SSC_MSG_REPORT_PEDO_STEP_EVENT_CONFIG
from .protobufs import ssc_sensor_pedo_pb2 as ssc_sensor_pedo


class SSCPedoSensor(SSCSensor):
    def __init__(self, on_measurement: Callable):
        super().__init__("pedometer")
        self.on_measurement_callback = on_measurement

    async def on_msg(self, msg_id: int, uid_high: int, uid_low: int, data: bytes):
        if not self.uid_high == uid_high and not self.uid_low == uid_low:
            return
        if (
            msg_id == SSC_MSG_REPORT_PEDO_STEP_EVENT
            or msg_id == SSC_MSG_REPORT_PEDO_STEP_EVENT_CONFIG
        ):
            msg = ssc_sensor_pedo.SscPedoResponse()
            msg.ParseFromString(data)

            steps = msg.step_count

            if self.on_measurement_callback:
                await self.on_measurement_callback(steps)
