import asyncio
import gi
import threading
import argparse
import logging

gi.require_version("Qrtr", "1.0")
gi.require_version("Qmi", "1.0")


from gi.repository import GLib
from datetime import datetime


from ..SSCHeartRateSensor import HeartRateAccuracy, SSCHeartRateSensor
from ..SSCLightSensor import SSCLightSensor, LightAccuracy
from ..SSCAccelSensor import SSCAccelSensor, AccelAccuracy
from ..SSCPedoSensor import SSCPedoSensor
from ..SSCFossilSleepSensor import SSCFossilSleepSensor
from ..SSCFossilTrackerSensor import SSCFossilTrackerSensor
from ..SSCLifeqSPo2Sensor import SPO2Accuracy, SSCLifeqSPo2Sensor, SPO2Gender
from ..SSCPressureSensor import PressureAccuracy, SSCPressureSensor
from ..SSCCompassSensor import SSCCompassSensor, CompassAccuracy
from ..SSCClient import SSCClient
from ..SSCTestSensor import SSCTestSensor


LOG_MAP = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}


async def on_light(intensity: float, accuracy: LightAccuracy):
    print(f"Light ({accuracy.name}): {intensity:.2f} Lux")


async def on_accel(x: float, y: float, z: float, accuracy: AccelAccuracy):
    print(f"Accel ({accuracy.name}):")
    print(f"    x: {x:.4f}m/s²")
    print(f"    y: {y:.4f}m/s²")
    print(f"    z: {z:.4f}m/s²")


async def on_hr(bpm: float, accuracy: HeartRateAccuracy):
    print(f"Heart Rate ({accuracy.name}): {bpm:.2f} BPM")


async def on_pedo(steps: int):
    print(f"Steps: {steps}")


async def on_pressure(pressure: float, accuracy: PressureAccuracy):
    print(f"Pressure ({accuracy.name}): {pressure:.2f} hPa")


async def on_spo2(
    spo2: float,
    confidence: float,
    algo_state: float,
    signal_state: float,
    accuracy: SPO2Accuracy,
):
    print(f"SPO2 ({accuracy.name}):")
    print(f"    spo2: {spo2:.2f} %")
    print(f"    confidence: {confidence:.2f} %")
    print(f"    algo state: {algo_state}")
    print(f"    signal state: {signal_state}")


async def on_compass(orientation: float, accuracy: CompassAccuracy):
    print(f"Orientation ({accuracy.name}): {orientation}°")


async def main():
    parser = argparse.ArgumentParser(
        prog="Program to test Qualcomm sensors exposed through QMI",
        epilog="This program should not be used for any medical purposes and should be considered as a toy.",
    )
    parser.add_argument(
        "-t",
        "--type",
        required=True,
        help="Which sensor(s) to read. (fsl_sleep, fsl_tracker) are not implemented yet",
        action="extend",
        nargs="+",
        choices=[
            "light",
            "accel",
            "heart_rate",
            "pedometer",
            "spo2",
            "pressure",
            "compass",
            "fsl_sleep",
            "fsl_tracker",
            "test",
        ],
    )
    parser.add_argument(
        "-d",
        "--duration",
        default=10,
        help="Seconds to sample sensor(s)",
        required=False,
        type=int,
    )

    parser.add_argument(
        "--log_level",
        default="INFO",
        help="Log level to use",
        required=False,
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    )

    args = parser.parse_args()

    log_level = LOG_MAP[args.log_level]
    logging.basicConfig(level=log_level)

    main_loop = GLib.MainLoop()
    loop_thread = threading.Thread(target=main_loop.run)
    loop_thread.start()

    sensor = None
    client = SSCClient()

    sensor_list = []
    for sns_name in args.type:
        if sns_name == "light":
            sensor = SSCLightSensor(on_light)
        elif sns_name == "accel":
            sensor = SSCAccelSensor(on_accel)
        elif sns_name == "heart_rate":
            sensor = SSCHeartRateSensor(on_hr)
        elif sns_name == "pedometer":
            sensor = SSCPedoSensor(on_pedo)
        elif sns_name == "fsl_sleep":
            sensor = SSCFossilSleepSensor(lambda: print("Not implemented"))
        elif sns_name == "fsl_tracker":
            sensor = SSCFossilTrackerSensor(lambda: print("Not implemented"))
        elif sns_name == "spo2":
            sensor = SSCLifeqSPo2Sensor(on_spo2)
        elif sns_name == "pressure":
            sensor = SSCPressureSensor(on_pressure)
        elif sns_name == "compass":
            sensor = SSCCompassSensor(on_compass)
        elif sns_name == "test":
            sensor = SSCTestSensor(input("Data Type: "))
        sensor_list.append(sensor)

        await client.open()

    for sensor in sensor_list:
        await client.register_sensor(sensor)

    for sensor in sensor_list:
        await sensor.open()

        if isinstance(sensor, SSCLifeqSPo2Sensor):
            await sensor.configure(
                SPO2Gender.Male,
                20,
                1.80,
                70.0,
                120.0,
                70.0,
                26.1,
                40.0,
                25.0,
                0.0,
                datetime.now().timestamp(),
            )  # These are pretty random and should definitely be change by someone with medical experience

        await sensor.enable()

    print(f"Sleeping for {args.duration}")
    await asyncio.sleep(args.duration)
    GLib.idle_add(main_loop.quit)


def main_sync():
    asyncio.run(main())


if __name__ == "__main__":
    main_sync()
