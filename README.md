# Program/Library to read sensor values using Qualcomm's SSC bus
Developed to test sensor on Qualcomm based smartwatches for AsteroidOS. Some things were taken from [`libssc`](https://codeberg.org/DylanVanAssche/libssc)

## Requirements
- Install `libqrtr`, `python3-protobuf` and `PyGObject`
- Build `libqmi` with `qrtr` support

## Reverse Engineering
- `libsensoraccess.so` used as a bridge between Java and QMI bus
- `SensorAccessService.apk` exposes the values to android

## Device compatibility
### Fossil Gen 6
- [x] accel (Accelerometer)
- [x] heart_rate (Heart rate)
- [x] ambient_light (Light sensor)
- [x] pedometer (Pedometer)
- [x] pressure (Pressure sensor)
- [x] spo2 (Blood oxygen)
- [x] rotv (Device rotation relative to the earth (compass))
- [ ] fsl_tracker (Fossil Tracker of some sort)
- [ ] fsl_sleep (Fossil sleep tracker)
- [ ] ott (lifeq ott sensor)
- [ ] calories (lifeq calories)
- [ ] rr (lifeq rr)
- [ ] daily_rhr (Daily Resting heart rate)
- [ ] fsl_wk (Fossil Workout tracker)
