#!/usr/bin/python2.7
# --
# File: update_output.py
#
# Copyright (c) Phantom Cyber Corporation, 2016
#
# This unpublished material is proprietary to Phantom Cyber.
# All rights reserved. The methods and
# techniques described herein are considered trade secrets
# and/or confidential. Reproduction or distribution, in whole
# or in part, is forbidden except by express written permission
# of Phantom Cyber.
#
# --

import sys
import simplejson as json
import argparse
import subprocess
prog_name = None

_args = None


def main(argv):

    global _args
    global prog_name

    argparser = argparse.ArgumentParser()

    argparser.add_argument('-n', '--app_run_id',
                           help=('app_run id to use, will connect to the db'
                                 ' and extract the run'),
                           required=True)

    argparser.add_argument('-j', '--app_json',
                           help='app json to update', required=True)

    argparser.add_argument('-a', '--action',
                           help='action to update', required=True)

    _args = argparser.parse_args()

    # get the command that was used to execute this script

    command = prog_name.replace("update_output.py", "create_output.py")
    command += " -n {0}".format(_args.app_run_id)

    try:
        proc = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
        (input_json, err) = proc.communicate()
    except Exception as e:
        print("Error executing create_output.py script with app_run id: {0}"
              .format(_args.app_run_id))
        exit(1)

    output_json = "{0}-output.json".format(_args.app_run_id)

    app_run_dict = {}

    with open(output_json, 'r') as f:

        try:
            app_run_dict = json.loads(f.read())
        except Exception as e:
            print "Unable to load {0}".format(output_json)
            exit(1)

    app_run_output = app_run_dict.get('output')

    data_paths_in_app_run_output = [x.get('data_path') for x in app_run_output]

    app_json = {}
    # Open the app json
    with open(_args.app_json, 'r') as f:

        try:
            app_json = json.loads(f.read())
        except Exception as e:
            print "Unable to load {0}. {1}".format(output_json, str(e))
            exit(1)

    # The action
    actions = app_json.get('actions')

    if (not actions):
        print "actions not specified in app json"
        exit(1)

    action = [x for x in actions if x.get('action', '') == _args.action]

    if (not action):
        print "action '{0}' not found in app json".format(_args.action)
        exit(1)

    action = action[0]

    app_output = action.get('output')
    data_paths_in_app_output = [x.get('data_path') for x in app_output]

    extra_data_paths = (list(set(data_paths_in_app_run_output)
                        - set(data_paths_in_app_output)))

    items_to_add = [x for x in app_run_output
                    if x['data_path'] in extra_data_paths]

    print "Will be adding {0} data paths".format(len(items_to_add))

    if (items_to_add):
        app_output.extend(items_to_add)

        with open('./update-{0}.json'.format(_args.app_run_id),
                  "w") as res_json_file:
            json.dump({'output': app_output},
                      res_json_file,
                      sort_keys=False,
                      indent=2 * ' ')

        with open('./append-{0}.json'.format(_args.app_run_id),
                  "w") as res_json_file:
            json.dump({'output': items_to_add},
                      res_json_file,
                      sort_keys=False,
                      indent=2 * ' ')


if __name__ == "__main__":

    prog_name = sys.argv[0]
    main(sys.argv[1:])
