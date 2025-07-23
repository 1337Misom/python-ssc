# SPDX-License-Identifier: AGPL-3.0-or-later

from typing import Callable
import gi
import asyncio
import threading
import logging

gi.require_version("Qrtr", "1.0")
gi.require_version("Qmi", "1.0")

from gi.repository import GLib, Qrtr, Qmi, Gio
from .protobufs import ssc_common_pb2 as ssc_common
from .const import SSC_PROCESSOR_APSS, SSC_SUSPEND_MODE_WAKEUP

LOG = logging.getLogger("SSCClient")


class SSCClient:
    bus: Qrtr.Bus
    device: Qmi.Device
    client: Qmi.Client

    ssc_port: int
    on_small_id: int
    on_large_id: int

    sensors: list["SSCClient"]

    is_open: bool

    send_lock: asyncio.Lock

    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.is_open = False
        self.sensors = []
        self.send_lock = asyncio.Lock()

    async def _poll_event(self, event: threading.Event):
        while not event.is_set():
            await asyncio.sleep(0.2)

    def _run_once_glib(self, function: Callable, *args):
        function(*args)
        return False

    async def register_sensor(self, sensor: "SSCClient"):
        self.sensors.append(sensor)
        await sensor.set_client(self)

    async def open(self):
        LOG.debug("Opening SSC")
        event = threading.Event()
        GLib.idle_add(
            self._run_once_glib,
            Qrtr.Bus.new,
            1000,
            None,
            self.qrtr_new_bus_callback,
            event,
        )
        await self._poll_event(event)
        self.is_open = True
        LOG.debug("SSC opened")

    async def send(
        self,
        uid_high: int,
        uid_low: int,
        message_id: int,
        input_data: bytes | None = None,
    ):
        await self.send_lock.acquire()
        client_cfg = ssc_common.SscClientConfig()
        client_cfg.processor = SSC_PROCESSOR_APSS
        client_cfg.suspend_mode = SSC_SUSPEND_MODE_WAKEUP

        client_request_body = ssc_common.SscClientRequestBody()

        if input_data:
            client_request_body.msg = input_data
        uid_msg = ssc_common.SscUid()
        uid_msg.low = uid_low
        uid_msg.high = uid_high
        client_request = ssc_common.SscClientRequest()
        client_request.uid.CopyFrom(uid_msg)
        client_request.msg_id = message_id
        client_request.config.CopyFrom(client_cfg)
        client_request.request.CopyFrom(client_request_body)

        data = client_request.SerializeToString()

        inp = Qmi.MessageSscControlInput.new()

        inp.set_report_type(Qmi.SscReportType.LARGE)
        inp.set_data(data)

        LOG.debug(f"Sending Packet: {len(data) if data else 'None'} bytes")

        event = threading.Event()
        GLib.idle_add(
            self._run_once_glib,
            self.client.control,
            inp,
            10,
            None,
            self.request_ready,
            event,
        )
        await self._poll_event(event)

        LOG.debug(f"Packet sent")
        self.send_lock.release()

    def request_ready(
        self, client: Qmi.Client, result: Gio.Task, user_data: threading.Event
    ):
        output = self.client.control_finish(result)
        if not output:
            raise RuntimeError("Problem occured during request")
        output.get_result()
        LOG.debug("Request send successfully")
        user_data.set()

    def parse_report(self, data: bytes):
        msg = ssc_common.SscClientResponse()
        msg.ParseFromString(data)
        for body in msg.response:
            for sensor in self.sensors:
                asyncio.run_coroutine_threadsafe(
                    sensor.on_report(body.msg_id, msg.uid.high, msg.uid.low, body.msg),
                    self.loop,
                )

    def qmi_allocate_client_callback(
        self, device: Qmi.Device, result: Gio.Task, user_data: threading.Event
    ):
        self.client = self.device.allocate_client_finish(result)
        LOG.debug("Adding callbacks")
        self.on_small_id = self.client.connect("report-small", self.on_report_small)
        self.on_large_id = self.client.connect("report-large", self.on_report_large)
        user_data.set()

    def qmi_open_device_callback(
        self, device: Qmi.Device, result: Gio.Task, user_data: threading.Event
    ):
        self.device.open_finish(result)
        LOG.debug("Allocating Client")
        self.device.allocate_client(
            Qmi.Service.SSC,
            Qmi.CID_NONE,
            self.ssc_port,
            None,
            self.qmi_allocate_client_callback,
            user_data,
        )

    def qmi_new_device_callback(
        self, device: Qmi.Device, result: Gio.Task, user_data: threading.Event
    ):
        self.device = Qmi.Device.new_finish(result)
        LOG.debug("Opening Device")
        Qmi.Device.open(
            self.device,
            Qmi.DeviceOpenFlags.AUTO | Qmi.DeviceOpenFlags.EXPECT_INDICATIONS,
            self.ssc_port,
            None,
            self.qmi_open_device_callback,
            user_data,
        )

    def qrtr_new_bus_callback(
        self, bus: Qrtr.Bus, result: Gio.Task, user_data: threading.Event
    ):
        self.bus = Qrtr.Bus.new_finish(result)

        found = None
        ssc_port = 0
        for node in self.bus.peek_nodes():
            if (ssc_port := node.lookup_port(Qmi.Service.SSC)) >= 0:
                found = node
                self.ssc_port = ssc_port
                break

        if not found:
            raise RuntimeError("Unable to find SSC Service")
        LOG.debug("Creating Device")
        Qmi.Device.new_from_node(found, None, self.qmi_new_device_callback, user_data)

    async def on_report(self, msg_id: int, uid_high: int, uid_low: int, data: bytes):
        return

    def on_report_small(
        self, client: Qmi.Client, report: Qmi.IndicationSscReportSmallOutput
    ):
        data = report.get_data()
        self.parse_report(data)

    def on_report_large(
        self, client: Qmi.Client, report: Qmi.IndicationSscReportLargeOutput
    ):
        data = report.get_data()
        self.parse_report(data)
