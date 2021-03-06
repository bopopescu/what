#------------------------------------------------------------------------------
# Copyright 2013-2014 Numenta Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#------------------------------------------------------------------------------
""" `YOMP cloudwatch` CLI integration tests.
"""
import yaml
import os
import unittest2 as unittest
import re
from subprocess import (
  call,
  PIPE,
  Popen
)



CMD_ADD_METRIC = """
  YOMP cloudwatch add $YOMP_API_HOST $YOMP_API_KEY \
    --region=%s \
    --namespace=%s \
    --metric=%s \
    --dimensions %s %s
  """
CMD_CREDENTIALS = "YOMP credentials $YOMP_API_HOST"
CMD_DELETE_MODEL = "YOMP DELETE $YOMP_API_HOST/_models/%s $YOMP_API_KEY"
CMD_GET_AVAILABLE_METRICS = \
  "YOMP GET $YOMP_API_HOST/_metrics/cloudwatch/regions/%s $YOMP_API_KEY"
CMD_GET_MODEL = "YOMP GET $YOMP_API_HOST/_models/%s $YOMP_API_KEY"
CMD_GET_REGIONS = "YOMP GET $YOMP_API_HOST/_metrics/cloudwatch $YOMP_API_KEY"



class TestCloudWatch(unittest.TestCase):
  """ Test `YOMP cloudwatch` command """

  def _executeYOMPCLI(self, cmd):
    """ Helper method for executing YOMP CLI command using Popen() """
    result = Popen(
      [cmd],
      shell=True,
      env=dict(os.environ.items() + self.env.items()),
      stdout=PIPE,
      stderr=PIPE)
    result.wait()
    (stdout, stderr) = result.communicate()
    self.assertFalse(result.returncode, """`%s` returned non-zero exit code.

      STDOUT: %s
      STDERR: %s""" % (cmd, stdout, stderr))
    return stdout.strip()


  def setUp(self):
    self.env = {"YOMP_API_HOST": "https://localhost"}

    # Save AWS credentials, get API key
    self.env["YOMP_API_KEY"] = self._executeYOMPCLI(CMD_CREDENTIALS)


  def testCreate(self):
    """ YOMP CLI can create cloudwatch models """

    # Get list of regions
    cloudwatch = yaml.load(self._executeYOMPCLI(CMD_GET_REGIONS))

    # We'll attempt to create three models for three different metric
    # namespaces in the available regions

    count = 0
    namespaces = set()
    for region in cloudwatch["regions"]:
      # Get available metrics for region
      metrics = \
        yaml.load(self._executeYOMPCLI(CMD_GET_AVAILABLE_METRICS % region))

      for metric in metrics:
        if metric["namespace"] in namespaces:
          # Skip.  Already created a model in this namespace
          continue

        # Construct `YOMP cloudwatch add` command

        (dimension, value) = next(iter(metric["dimensions"].items()))
        dimensionValue = next(iter(value))
        cmd = re.sub(" +", " ", CMD_ADD_METRIC.strip()) % (
          region,
          metric["namespace"],
          metric["metric"],
          dimension,
          dimensionValue)

        # Run `YOMP cloudwatch add` command
        uid = self._executeYOMPCLI(cmd)

        # Compare result to original metric returned by the cloudwatch api
        model = yaml.load(self._executeYOMPCLI(CMD_GET_MODEL % uid))
        params = yaml.load(model["parameters"])

        self.assertEqual(uid, model["uid"])
        self.assertEqual(metric["region"], region)
        self.assertEqual(metric["region"], model["location"])
        self.assertEqual(metric["identifier"], model["server"])

        self.addCleanup(self._executeYOMPCLI,CMD_DELETE_MODEL % uid)

        namespaces.add(metric["namespace"])
        count += 1
        if count > 2:
          break

      else:
        self.fail("Unable to create enough models")

      if count > 2:
        break
    else:
      self.fail("Unable to create enough models")



