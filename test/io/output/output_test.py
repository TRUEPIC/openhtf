# Copyright 2016 Google Inc. All Rights Reserved.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Unit tests for the openhtf.io.output module.

This test uses a pickled test record and expected output for each output
module.  The input record was generated by running examples/all_the_things.py
with the following output callback:

  import cPickle as pickle

  def _pickle(test_record):
    with open('./record.pickle', 'wb') as picklefile:
      pickle.dump(test_record, picklefile)

This pickled input record should be re-generated if the test record structure
is changed.  Expected outputs here should be updated also.  That can be done
by changing the value of UPDATE_OUTPUT to True and running this test.  Be sure
to change it back to False afterwards (there's a test to make sure you do).
"""

import cPickle as pickle
import difflib
import logging
import os.path
import unittest

from cStringIO import StringIO

import google.protobuf.text_format as text_format

from openhtf.io.output import json_factory
from openhtf.io.output import mfg_inspector
from openhtf.io.proto import test_runs_pb2
from openhtf.util import data


def _LocalFilename(filename):
  """Get an absolute path to filename in the same directory as this module."""
  return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)


class TestOutput(unittest.TestCase):

  UPDATE_OUTPUT = False

  @classmethod
  def setUpClass(cls):
    # Load input testrun from pickled file.
    with open(_LocalFilename('record.pickle'), 'rb') as picklefile:
      cls.record = pickle.load(picklefile)

    # Load our canonical 'correct' outputs from files.
    with open(_LocalFilename('record.json'), 'rb') as jsonfile:
      cls.json = jsonfile.read()
    with open(_LocalFilename('record.testrun'), 'rb') as testrunfile:
      cls.testrun = test_runs_pb2.TestRun.FromString(testrunfile.read())

  def testJson(self):
    json_output = StringIO()
    json_factory.OutputToJSON(json_output, sort_keys=True, indent=2)(self.record)
    if self.UPDATE_OUTPUT:
      with open(_LocalFilename('record.json'), 'wb') as jsonfile:
        jsonfile.write(json_output.getvalue())
    else:
      self.assertTrue(data.equals_log_diff(self.json, json_output.getvalue()))

  def testTestrun(self):
    testrun_output = StringIO()
    mfg_inspector.OutputToTestRunProto(testrun_output)(self.record)
    if self.UPDATE_OUTPUT:
      with open(_LocalFilename('record.testrun'), 'wb') as testrunfile:
        testrunfile.write(testrun_output.getvalue())
    else:
      actual = test_runs_pb2.TestRun.FromString(testrun_output.getvalue())
      self.assertTrue(data.equals_log_diff(
          text_format.MessageToString(self.testrun),
          text_format.MessageToString(actual)))

  def testUpdateOutput(self):
    """Make sure we don't accidentally leave UPDATE_OUTPUT True."""
    assert not self.UPDATE_OUTPUT, 'Change UPDATE_OUTPUT back to False!'
