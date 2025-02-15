import asyncio
import logging

from dataclasses import dataclass, field
from .SSCClient import SSCClient
from .const import (
    SSC_SENSOR_UID_SUID_LOW,
    SSC_SENSOR_UID_SUID_HIGH,
    SSC_MSG_REQUEST_SUID,
    SSC_ATTRIBUTE_NAME,
    SSC_ATTRIBUTE_VENDOR,
    SSC_ATTRIBUTE_AVAILABLE,
    SSC_ATTRIBUTE_SAMPLE_RATE,
    SSC_ATTRIBUTE_STREAM_TYPE,
    SSC_MSG_RESPONSE_SUID,
    SSC_MSG_RESPONSE_ENABLE_REPORT,
    SSC_MSG_RESPONSE_GET_ATTRIBUTES,
    SSC_MSG_REQUEST_GET_ATTRIBUTES,
    SSC_STREAM_TYPE_ON_CHANGE,
    SSC_STREAM_TYPE_CONTINUOUS,
    SSC_MSG_REQUEST_ENABLE_REPORT_ON_CHANGE,
    SSC_MSG_REQUEST_ENABLE_REPORT_CONTINUOUS,
)
from .protobufs import ssc_sensor_suid_pb2 as ssc_sensor_suid
from .protobufs import ssc_common_pb2 as ssc_common


LOG = logging.getLogger("SSCSensor")

MAX_RETRIES = 5


@dataclass
class SensorAttributes:
    name: str | None = None
    vendor: str | None = None
    sample_rates: list[float] = field(default_factory=list)
    stream_type: int | None = None
    available: bool = False


class SSCSensor:
    sensor_id: str
    service_available: bool
    service_retries: int

    uid_high: int | None
    uid_low: int | None

    client: SSCClient | None

    attributes: SensorAttributes | None

    def __init__(self, sensor_id: str):
        super().__init__()
        self.sensor_id = sensor_id
        self.service_available = False
        self.service_retries = 0
        self.attributes = None
        self.uid_high = None
        self.uid_low = None
        self.client = None

    async def set_client(self, client: SSCClient):
        self.client = client

    async def discover(self, data_type: str):
        LOG.debug(f"Discovering sensor: {data_type}")
        request = ssc_sensor_suid.SscSuidRequest()

        request.data_type = data_type
        request.enable_updates = False
        request.only_default_values = True
        data = request.SerializeToString()

        await self.client.send(
            SSC_SENSOR_UID_SUID_HIGH,
            SSC_SENSOR_UID_SUID_LOW,
            SSC_MSG_REQUEST_SUID,
            data,
        )

    async def parse_discovery(self, data: bytes):
        LOG.debug("Got discovery response")
        suid_msg = ssc_sensor_suid.SscSuidResponse()
        suid_msg.ParseFromString(data)

        if len(suid_msg.uid) > 0 and suid_msg.data_type == "registry":
            LOG.debug("Registry available")
            self.service_available = True
            await self.discover(self.sensor_id)
            return

        if not self.service_available:
            self.service_retries += 1

            if self.service_retries >= MAX_RETRIES:
                raise RuntimeError("Sensor service unavailable")

            await asyncio.sleep(1)

            LOG.debug(
                f"registry unavailable, retrying ({self.service_retries}/{MAX_RETRIES})"
            )
            await self.wait_for_sensor_service()
            return

        if suid_msg.data_type != self.sensor_id:
            return

        if len(suid_msg.uid) > 0:
            self.uid_high = suid_msg.uid[0].high
            self.uid_low = suid_msg.uid[0].low

            LOG.debug(
                f"Discovered {self.sensor_id}: ({hex(self.uid_high)} {hex(self.uid_low)})"
            )
            await self.load_attributes()
        else:
            LOG.error(f"Sensor is unavailable")
            raise RuntimeError(f"Sensor {self.sensor_id} unavailable")

    async def parse_attribute(self, attr: ssc_common.SscAttr):
        if attr.id == SSC_ATTRIBUTE_NAME:
            if len(attr.value_array.v) == 1:
                self.attributes.name = attr.value_array.v[0].s

        elif attr.id == SSC_ATTRIBUTE_VENDOR:
            if len(attr.value_array.v) == 1:
                self.attributes.vendor = attr.value_array.v[0].s

        elif attr.id == SSC_ATTRIBUTE_AVAILABLE:
            if len(attr.value_array.v) == 1:
                self.attributes.available = attr.value_array.v[0].b

        elif attr.id == SSC_ATTRIBUTE_SAMPLE_RATE:
            for rate in attr.value_array.v:
                self.attributes.sample_rates.append(rate.f)

        elif attr.id == SSC_ATTRIBUTE_STREAM_TYPE:
            if len(attr.value_array.v) == 1:
                self.attributes.stream_type = attr.value_array.v[0].i

    async def on_msg(self, msg_id: int, uid_high: int, uid_low: int, data: bytes):
        pass

    async def on_report(self, msg_id: int, uid_high: int, uid_low: int, data: bytes):
        LOG.debug(f"Got report {msg_id} for ({hex(uid_high)} {hex(uid_low)})")
        if (
            uid_high == SSC_SENSOR_UID_SUID_HIGH
            and uid_low == SSC_SENSOR_UID_SUID_LOW
            and msg_id == SSC_MSG_RESPONSE_SUID
        ):
            await self.parse_discovery(data)

        elif (
            uid_high == self.uid_high
            and uid_low == self.uid_low
            and msg_id == SSC_MSG_RESPONSE_GET_ATTRIBUTES
        ):
            attr_msg = ssc_common.SscAttrResponse()

            attr_msg.ParseFromString(data)
            self.attributes = SensorAttributes()
            for attr in attr_msg.attr:
                await self.parse_attribute(attr)
            LOG.info(f"Sensor Attributes ({hex(self.uid_high)} {hex(self.uid_low)}):")
            LOG.info(f"  name: {self.attributes.name}")
            LOG.info(f"  vendor: {self.attributes.vendor}")
            LOG.info(f"  data_type: {self.sensor_id}")
            LOG.info(f"  available: {self.attributes.available}")
            LOG.info(
                f"  stream_type: {'continuous' if self.attributes.stream_type == SSC_STREAM_TYPE_CONTINUOUS else 'on-change'}"
            )
            LOG.info(f"  sample_rates: {self.attributes.sample_rates}")
        elif (
            uid_high == self.uid_high
            and uid_low == self.uid_low
            and msg_id == SSC_MSG_RESPONSE_ENABLE_REPORT
        ):
            config_msg = ssc_common.SscConfigResponse()

            config_msg.ParseFromString(data)

            LOG.info(
                f"Configuration updated for {self.sensor_id} ({hex(self.uid_high)} {hex(self.uid_low)}):"
            )

            LOG.info(f"  mode: {config_msg.mode if config_msg.mode else 'UNKNOWN'}")
            LOG.info(
                f"  sample-rate: {config_msg.sample_rate if config_msg.sample_rate else 0.0} Hz"
            )

        else:
            await self.on_msg(msg_id, uid_high, uid_low, data)

    async def load_attributes(self):
        if not self.client:
            raise RuntimeError("Tried to setup sensor without a client")
        req = ssc_common.SscAttrRequest()
        req.enable_updates = False
        data = req.SerializeToString()
        await self.client.send(
            self.uid_high, self.uid_low, SSC_MSG_REQUEST_GET_ATTRIBUTES, data
        )

    async def wait_for_sensor_service(self):
        if not self.client:
            raise RuntimeError("Tried to setup sensor without a client")
        LOG.debug("Checking sensor availability")
        request = ssc_sensor_suid.SscSuidRequest()
        request.data_type = "registry"
        request.enable_updates = False
        request.only_default_values = True

        data = request.SerializeToString()

        await self.client.send(
            SSC_SENSOR_UID_SUID_HIGH,
            SSC_SENSOR_UID_SUID_LOW,
            SSC_MSG_REQUEST_SUID,
            data,
        )

    async def enable(self, sample_rate: float | None = None):
        if not self.client:
            raise RuntimeError("Tried to setup sensor without a client")
        if not self.attributes or not self.attributes.available:
            raise RuntimeError("Tried to enable a sensor, which is unavailable")

        msg_id = None
        buf = None
        if self.attributes.stream_type == SSC_STREAM_TYPE_CONTINUOUS:
            enable_req = ssc_common.SscEnableConfigRequest()
            if len(self.attributes.sample_rates) == 0:
                raise RuntimeError("No sample rate")

            if sample_rate or sample_rate not in self.attributes.sample_rates:
                enable_req.sample_rate = self.attributes.sample_rates[0]
                LOG.info(
                    f"Wrong or no sample_rate specified using slowest: {enable_req.sample_rate} Hz"
                )
            else:
                enable_req.sample_rate = sample_rate

            buf = enable_req.SerializeToString()
            msg_id = SSC_MSG_REQUEST_ENABLE_REPORT_CONTINUOUS

        elif self.attributes.stream_type == SSC_STREAM_TYPE_ON_CHANGE:
            msg_id = SSC_MSG_REQUEST_ENABLE_REPORT_ON_CHANGE
        else:
            raise RuntimeError("Sensor has no stream type")

        await self.client.send(self.uid_high, self.uid_low, msg_id, buf)

    async def open(self):
        if not self.client or not self.client.is_open:
            raise RuntimeError("Client hasn't been opened yet")

        self.service_available = False
        self.service_retries = 0
        await self.wait_for_sensor_service()
        while not self.attributes or not self.attributes.available:
            await asyncio.sleep(0.2)
