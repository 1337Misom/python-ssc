LOG_FORMAT = "[%(name)s][%(levelname)s]: %(message)s"

SSC_MSG_REQUEST_ENABLE_REPORT_CONTINUOUS = 513
SSC_MSG_REQUEST_ENABLE_REPORT_ON_CHANGE = 514

SSC_MSG_RESPONSE_ENABLE_REPORT = 768

SSC_MSG_REPORT_PEDO_STEP_EVENT = 1028
SSC_MSG_REPORT_MEASUREMENT = 1025
SSC_MSG_REPORT_HEART_RATE = 779
SSC_MSG_REPORT_PEDO_STEP_EVENT_CONFIG = 775


SSC_PROCESSOR_APSS = 1
SSC_SUSPEND_MODE_WAKEUP = 0
SSC_SENSOR_TYPE_SUID = "suid"

SSC_SENSOR_UID_SUID_LOW = 0xABABABABABABABAB
SSC_SENSOR_UID_SUID_HIGH = 0xABABABABABABABAB

SSC_MSG_REQUEST_SUID = 512
SSC_MSG_RESPONSE_SUID = 768

SSC_MSG_REQUEST_GET_ATTRIBUTES = 1
SSC_MSG_RESPONSE_GET_ATTRIBUTES = 128


SSC_ATTRIBUTE_NAME = 0
SSC_ATTRIBUTE_VENDOR = 1
SSC_ATTRIBUTE_TYPE = 2
SSC_ATTRIBUTE_AVAILABLE = 3
SSC_ATTRIBUTE_VERSION = 4
SSC_ATTRIBUTE_API = 5
SSC_ATTRIBUTE_SAMPLE_RATE = 6
SSC_ATTRIBUTE_SAMPLE_RESOLUTIONS = 7
SSC_ATTRIBUTE_FIFO_SIZE = 8
SSC_ATTRIBUTE_ACTIVE_CURRENT_CONSUMPTION = 9
SSC_ATTRIBUTE_SLEEP_CURRENT_CONSUMPTION = 10
SSC_ATTRIBUTE_AVAILABLE_RANGES = 11
SSC_ATTRIBUTE_OPERATING_MODES = 12
SSC_ATTRIBUTE_DRI = 13
SSC_ATTRIBUTE_STREAM_SYNC = 14
SSC_ATTRIBUTE_EVENT_SIZE = 15
SSC_ATTRIBUTE_STREAM_TYPE = 16
SSC_ATTRIBUTE_DYNAMIC = 17
SSC_ATTRIBUTE_HARDWARE_ID = 18
SSC_ATTRIBUTE_RIGID_BODY = 19
SSC_ATTRIBUTE_PLACEMENT = 20
SSC_ATTRIBUTE_PHYSICAL_SENSOR = 21
SSC_ATTRIBUTE_PHYSICAL_SENSOR_TESTS = 22
SSC_ATTRIBUTE_SELECTED_RESULTION = 23
SSC_ATTRIBUTE_SELECTED_RANGE = 24
SSC_ATTRIBUTE_LOW_LATENCY_RATES = 25
SSC_ATTRIBUTE_PASSIVE_REQUEST = 26

SSC_STREAM_TYPE_CONTINUOUS = 0
SSC_STREAM_TYPE_ON_CHANGE = 1
