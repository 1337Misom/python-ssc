from typing import Callable
from .SSCSensor import SSCSensor


class SSCFossilSleepSensor(SSCSensor):
    def __init__(self, on_measurement: Callable):
        super().__init__("fsl_sleep")
        self.on_measurement_callback = on_measurement
        raise RuntimeError("Not implemented")

    async def on_msg(self, msg_id: int, uid_high: int, uid_low: int, data: bytes):
        if not self.uid_high == uid_high and not self.uid_low == uid_low:
            return
