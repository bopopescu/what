#!/usr/bin/env python
# ----------------------------------------------------------------------
# Numenta Platform for Intelligent Computing (NuPIC)
# Copyright (C) 2015, Numenta, Inc.  Unless you have purchased from
# Numenta, Inc. a separate commercial license for this software code, the
# following terms and conditions apply:
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see http://www.gnu.org/licenses.
#
# http://numenta.org/licenses/
# ----------------------------------------------------------------------

""" Enable monitoring of models on an HTM server """

import json
import logging
from optparse import OptionParser
import os
import sys

from taurus.metric_collectors import logging_support, metric_utils



DEFAULT_HTM_SERVER = os.environ.get("TAURUS_HTM_SERVER")



g_log = logging.getLogger("metric_collectors.monitor_metrics")



def _parseArgs():
  """
  :returns: dict of arg names and values:
    htmServer
    apiKey
    modelsFilePath
  """
  helpString = (
    "%prog [options] model-objects-file-from-unmonitor_metrics\n\n"
    "Enable monitoring of metrics on an HTM server from a models file "
    "generated by unmonitor_metrics. This file contains model properties "
    "that are necessary for re-monitoring of the metrics.\n"
    "NOTE: USER MUST WAIT for all background processing on the HTM server "
    "triggered by unmonitor_metrics to complete before executing this command, "
    "or risk defineModel requests getting lost when deleteModel deletes the "
    "model's message queue. This is due to the lack of separation between "
    "metric and model IDs in HTM Engine. There is presently no HTM Server API "
    "to assist with the wait.")

  parser = OptionParser(helpString)

  parser.add_option(
    "--server",
    action="store",
    type="string",
    dest="htmServer",
    default=DEFAULT_HTM_SERVER,
    help="Hostname or IP address of server running HTM Engine API to create "
    "models [default: %default]")

  parser.add_option(
    "--apikey",
    action="store",
    type="string",
    dest="apiKey",
    help="API Key of HTM Engine")

  options, positionalArgs = parser.parse_args()

  if len(positionalArgs) != 1:
    msg = ("Command must have exactly one positional arg - the models input "
           "file path")
    g_log.error(msg)
    parser.error(msg)
  else:
    modelsFilePath = positionalArgs[0]

  if not options.htmServer:
    msg = ("Missing or empty Hostname or IP address of server running HTM "
           "Engine API")
    g_log.error(msg)
    parser.error(msg)

  if not options.apiKey:
    msg = "Missing or empty API Key of HTM Engine"
    g_log.error(msg)
    parser.error(msg)


  return dict(
    htmServer=options.htmServer,
    apiKey=options.apiKey,
    modelsFilePath=modelsFilePath
  )



def main():
  logging_support.LoggingSupport.initTool()

  try:
    options = _parseArgs()
    g_log.info("Running %s with options=%r", sys.argv[0], options)

    modelsFilePath = options["modelsFilePath"]

    # Get prior model properties from a file generated by unmonitor_metrics
    with open(modelsFilePath) as inModelsFile:
      models = json.load(inModelsFile)

    if not models:
      g_log.warning("No model objects in models input file %s",
                    modelsFilePath)
      return

    g_log.info("Remonitoring %d models", len(models))

    for i, model in enumerate(models, 1):
      # Monitor
      metric_utils.createHtmModel(
        host=options["htmServer"],
        apiKey=options["apiKey"],
        modelParams=model["parameters"])

      g_log.info("Enabled monitoring of metric=%s (%d of %d)",
                 model["uid"], i, len(models))

    g_log.info("Remonitored %d metrics", len(models))
  except SystemExit as e:
    if e.code != 0:
      g_log.exception("monitor_metrics failed")
    raise
  except Exception:
    g_log.exception("unmonitor_metrics failed")
    raise



if __name__ == "__main__":
  main()
