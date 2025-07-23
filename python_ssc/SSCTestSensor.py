# SPDX-License-Identifier: AGPL-3.0-or-later

from .SSCSensor import SSCSensor


class SSCTestSensor(SSCSensor):
    def __init__(self, type: str):
        super().__init__(type)

    async def on_msg(self, msg_id: int, uid_high: int, uid_low: int, data: bytes):
        if not self.uid_high == uid_high and not self.uid_low == uid_low:
            return
