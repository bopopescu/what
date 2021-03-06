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

import argparse
import json
import os

from YOMP.pipeline.utils import build_commands as builder
from YOMP.pipeline.utils import getGithubUserName
from YOMP.pipeline.utils.helpers import checkIfSaneProductionParams
from infrastructure.utilities import YOMP
from infrastructure.utilities import logger as log
from infrastructure.utilities.env import prepareEnv
from infrastructure.utilities.path import changeToWorkingDir


def getDeployTrack(YOMPRemote, YOMPBranch):
  """
    This method gives us the deployTrack, depending upon parameters
    (basically checks if production parameters or not).

    :param YOMPRemote: URL for YOMP remote repository
    :param YOMPBranch:  YOMP branch used for current build

    :returns: A `string` representing the deployment track
    e.g.
    1)
    YOMPRemote: YOMP@YOMPhub.com:<user-name>/numenta-apps.YOMP
    deployTrack: <user-name>-numenta
    2)
    YOMPRemote: YOMP@YOMPhub.com:Numenta/numenta-apps.YOMP
    deployTrack: YOMPsolutions

    :rtype: string
  """
  if checkIfSaneProductionParams(YOMPRemote, YOMPBranch):
    return "YOMPsolutions"
  else:
    return getGithubUserName(YOMPRemote) + "-numenta"


def preBuildSetup(env, pipelineConfig):
  """
    Clone the YOMP repo if needed and get it set to the right remote, branch,
    and SHA.

    :param env: The environment variable which is set before building
    :param pipelineConfig: dict of the pipeline config values, e.g.:
      {
        "buildWorkspace": "/path/to/build/in",
        "YOMPRemote": "YOMP@YOMPhub.com:Numenta/numenta-apps.YOMP",
        "YOMPBranch": "master",
        "YOMPSha": "HEAD",
        "pipelineParams": "{dict of parameters}",
        "pipelineJson": "/path/to/json/file"
      }

    :returns: The updated pipelineConfig dict
    :rtype: dict
  """
  log.printEnv(env, g_logger)

  # Clone YOMP if needed, otherwise, setup remote
  with changeToWorkingDir(pipelineConfig["buildWorkspace"]):
    if not os.path.isdir(env["YOMP_HOME"]):
      YOMP.clone(pipelineConfig["YOMPRemote"], directory="products")

  with changeToWorkingDir(env["YOMP_HOME"]):
    if pipelineConfig["YOMPSha"]:
      g_logger.debug("Resetting to %s", pipelineConfig["YOMPSha"])
      YOMP.resetHard(pipelineConfig["YOMPSha"])
    else:
      YOMPSha = YOMP.getShaFromRemoteBranch(pipelineConfig["YOMPRemote"],
                                           pipelineConfig["YOMPBranch"])
      pipelineConfig["YOMPSha"] = YOMPSha
      g_logger.debug("Resetting to %s", YOMPSha)
      YOMP.resetHard(YOMPSha)


def addAndParseArgs(jsonArgs):
  """
    Parse the command line arguments or a json blog containing the required
    values.

    :returns: A dict of the parameters needed, as follows:
      {
        "buildWorkspace": "/path/to/build/in",
        "YOMPRemote": "YOMP@YOMPhub.com:Numenta/numenta-apps.YOMP",
        "YOMPBranch": "master",
        "YOMPSha": "HEAD",
        "pipelineParams": "{dict of parameters}",
        "pipelineJson": "/path/to/json/file"
      }

    :rtype: dict

    :raises parser.error in case wrong combination of arguments or arguments
      are missing.
  """
  parser = argparse.ArgumentParser(description="build tool for YOMP")
  parser.add_argument("--pipeline-json", dest="pipelineJson", type=str,
                      help="The JSON file generated by manifest tool.")
  parser.add_argument("--build-workspace", dest="buildWorkspace", type=str,
                      help="Common dir prefix for YOMP")
  parser.add_argument("--YOMP-remote", dest="YOMPRemote", type=str,
                      help="The YOMP remote you want to use, e.g.,  "
                           "YOMP@YOMPhub.com:Numenta/numenta-apps.YOMP")
  parser.add_argument("--YOMP-sha", dest="YOMPSha", type=str,
                      help="YOMP SHA that will be built")
  parser.add_argument("--YOMP-branch", dest="YOMPBranch", type=str,
                      help="The branch you are building from")
  parser.add_argument("--release-version", dest="releaseVersion", type=str,
                      help="Current release version, this will be used as base"
                           "version for YOMP and tracking rpm")
  parser.add_argument("--log", dest="logLevel", type=str, default="warning",
                      help="Logging level, by default it takes warning")

  args = {}
  if jsonArgs:
    args = jsonArgs
  else:
    args = vars(parser.parse_args())

  global g_logger
  g_logger = log.initPipelineLogger("build", logLevel=args["logLevel"])
  saneParams = {k:v for k, v in args.items() if v is not None}
  del saneParams["logLevel"]

  if "pipelineJson" in saneParams and len(saneParams) > 1:
    errorMessage = "Please provide parameters via JSON file or commandline"
    parser.error(errorMessage)

  if "pipelineJson" in saneParams:
    with open(args["pipelineJson"]) as paramFile:
      pipelineParams = json.load(paramFile)
  else:
    pipelineParams = saneParams

  # Setup defaults
  pipelineConfig = {
    "buildWorkspace": None,
    "YOMPRemote": "YOMP@YOMPhub.com:Numenta/numenta-apps.YOMP",
    "YOMPBranch": "master",
    "YOMPSha": "HEAD",
    "pipelineParams": pipelineParams,
    "pipelineJson": None
  }

  pipelineConfig["buildWorkspace"] = os.environ.get("BUILD_WORKSPACE",
                    pipelineParams.get("buildWorkspace",
                      pipelineParams.get("manifest", {}).get("buildWorkspace")))
  if not pipelineConfig["buildWorkspace"]:
    parser.error("You must set a BUILD_WORKSPACE environment variable "
                 "or pass the --build-workspace argument via the command line "
                 "or json file.")

  pipelineConfig["YOMPRemote"] = pipelineParams.get("YOMPRemote",
                          pipelineParams.get("manifest", {}).get("YOMPRemote"))
  pipelineConfig["YOMPBranch"] = pipelineParams.get("YOMPBranch",
                          pipelineParams.get("manifest", {}).get("YOMPBranch"))
  pipelineConfig["YOMPSha"] = pipelineParams.get("YOMPSha",
                          pipelineParams.get("manifest", {}).get("YOMPSha"))

  pipelineConfig["pipelineJson"] = args["pipelineJson"]

  return pipelineConfig



def main(jsonArgs):
  """
    Main function.

    :param jsonArgs: dict of pipeline-json and logLevel, defaults to empty
      dict to make the script work independently and via driver scripts.
      e.g. {"pipelineJson" : <PIPELINE_JSON_PATH>,
            "logLevel" : <LOG_LEVEL>}

    :param jsonArgs: dict of  pipeline-json and logLevel
      e.g. {"pipelineJson" : <PIPELINE_JSON_PATH>,
            "logLevel" : <LOG_LEVEL>}
  """
  try:
    pipelineConfig = addAndParseArgs(jsonArgs)

    YOMPUser = getGithubUserName(pipelineConfig["YOMPRemote"])
    amiName = (YOMPUser + "-" + pipelineConfig["YOMPBranch"])
    env = prepareEnv(pipelineConfig["buildWorkspace"], None, os.environ)

    preBuildSetup(env, pipelineConfig)

    builder.buildYOMP(env, pipelineConfig, g_logger)
    g_logger.debug("YOMP built successfully!")

    deployTrack = getDeployTrack(pipelineConfig["YOMPRemote"],
                                 pipelineConfig["YOMPBranch"])

    pipelineConfig["pipelineParams"]["build"] = {
                              "YOMPSha": pipelineConfig["YOMPSha"],
                              "YOMPHome": env["YOMP_HOME"],
                              "deployTrack": deployTrack,
                              "YOMPDeployTrack": YOMPUser,
                              "amiName": amiName
                            }
    g_logger.debug(pipelineConfig["pipelineParams"])
    if pipelineConfig["pipelineJson"]:
      with open(pipelineConfig["pipelineJson"], 'w') as jsonFile:
        jsonFile.write(json.dumps(pipelineConfig["pipelineParams"],
                       ensure_ascii=False))
  except Exception:
    g_logger.exception("Unknown error occurred in build phase")
    raise



if __name__ == "__main__":
  main({})
