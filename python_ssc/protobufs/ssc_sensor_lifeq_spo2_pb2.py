# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: ssc-sensor-lifeq-spo2.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1bssc-sensor-lifeq-spo2.proto\"6\n\x14SscLifeqSPo2Response\x12\x0c\n\x04spo2\x18\x01 \x03(\x02\x12\x10\n\x08\x61\x63\x63uracy\x18\x02 \x02(\x05\"\x83\x02\n\x17SscLifeqSPo2UserProfile\x12\x0e\n\x06gender\x18\x01 \x02(\x02\x12\x0b\n\x03\x61ge\x18\x02 \x02(\x02\x12\x0e\n\x06height\x18\x03 \x02(\x02\x12\x0e\n\x06weight\x18\x04 \x02(\x02\x12\x14\n\x0cmaxHeartRate\x18\x05 \x02(\x02\x12\x18\n\x10restingHeartRate\x18\x06 \x02(\x02\x12\x0f\n\x07\x62odyFat\x18\x07 \x02(\x02\x12\x0e\n\x06vo2max\x18\x08 \x02(\x02\x12\x0e\n\x06vo2min\x18\t \x02(\x02\x12\x10\n\x08timeZone\x18\n \x02(\x02\x12\x10\n\x08unixTime\x18\x0b \x02(\x02\x12\x13\n\x0btestLogging\x18\x0c \x02(\x02\x12\x11\n\tenableCLC\x18\r \x02(\x02\"s\n\x13SscLifeqSPo2Request\x12\x12\n\ncontinuous\x18\x01 \x02(\x08\x12\x0f\n\x07timeout\x18\x02 \x02(\x02\x12\x1a\n\x12measurementSpacing\x18\x03 \x02(\x02\x12\x1b\n\x13\x63onfidenceThreshold\x18\x04 \x02(\x02\",\n\x16SscLifeqRHRsyncRequest\x12\x12\n\nrestingBPM\x18\x01 \x02(\r')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'ssc_sensor_lifeq_spo2_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _SSCLIFEQSPO2RESPONSE._serialized_start=31
  _SSCLIFEQSPO2RESPONSE._serialized_end=85
  _SSCLIFEQSPO2USERPROFILE._serialized_start=88
  _SSCLIFEQSPO2USERPROFILE._serialized_end=347
  _SSCLIFEQSPO2REQUEST._serialized_start=349
  _SSCLIFEQSPO2REQUEST._serialized_end=464
  _SSCLIFEQRHRSYNCREQUEST._serialized_start=466
  _SSCLIFEQRHRSYNCREQUEST._serialized_end=510
# @@protoc_insertion_point(module_scope)
