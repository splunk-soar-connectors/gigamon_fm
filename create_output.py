#!/usr/bin/python2.7
# --
# File: create_output.py
#
# Copyright (c) Phantom Cyber Corporation, 2014-2016
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
import os
import re
import simplejson as json
from collections import OrderedDict
# import pprint
import argparse
import subprocess
prog_name = None

_column_order = 0
_produces = OrderedDict()
indent = 0
_args = None

# PSQL_COMMAND = 'psql -d phantom -U django -tc "select row_to_json(x) from
# app_run x where id = {app_run_id}"'
PSQL_COMMAND = ('psql -d phantom -tc "select row_to_json(x) from app_run'
                'x where id = {app_run_id}"')


def main(argv):

    global _produces
    global _args
    global _column_order

    argparser = argparse.ArgumentParser()

    arggroup = argparser.add_mutually_exclusive_group(required=True)

    arggroup.add_argument('-i', '--ijson',
                          help=('input json file, this should be the json of'
                                'the app_run in the db, output of "{0}""'
                                .format(PSQL_COMMAND)))

    arggroup.add_argument('-n', '--app_run_id',
                          help=('app_run id to use, will connect to the db and'
                                'extract the run'))

    argparser.add_argument('-o',
                           '--ojson',
                           help=('output json file that will contain the'
                                 'output section, if not specified'
                                 'automatically generated'))

    argparser.add_argument('-c',
                           '--add_columns',
                           help=('add autogenerated column names and column'
                                 'number values'),
                           action='store_true')

    argparser.add_argument('-k',
                           '--add_contains',
                           help=('add an empty contains section even if the'
                                 'contains of a value cannot be determined'),
                           action='store_true')

    argparser.add_argument('-r',
                           '--remove_unknown_items',
                           help=('An item that does not have a contains or'
                                 'column details will be removed'),
                           action='store_true')

    _args = argparser.parse_args()

    # check for connector run
    if (_args.app_run_id):
        try:
            # The last item will contain the sql
            cmd = PSQL_COMMAND.format(app_run_id=_args.app_run_id)
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
            (input_json, err) = proc.communicate()
        except Exception as e:
            print("Error getting the app_run json for id: {0}"
                  .format(_args.app_run_id))
            exit(1)

        if (input_json):
            # write it to a file
            _args.ijson = './{0}.json'.format(_args.app_run_id)
            with open(_args.ijson, 'w') as out_file:
                out_file.write(input_json)
                out_file.close()
        else:
            print("Failed to get json for app_run_id: {0}"
                  .format(_args.app_run_id))
            exit(1)

    if (_args.ojson is None):
        file_name_split = os.path.splitext(_args.ijson)
        _args.ojson = file_name_split[0] + '-output' + file_name_split[1]
        print "Will be using output file as {0}".format(_args.ojson)

    input_json = None

    print "Working on {0}".format(_args.ijson)

    try:
        with open(_args.ijson) as json_file:
            # input_json = json.loads(json_file.read())
            json_str = json_file.read()
            # clean up the file so that we are able to load the json
            # Remove the ISODates
            json_mod_str = re.sub('ISODate(.*),', r'"removed",', json_str)
            json_str = re.sub('ISODate(.*)', r'"removed"', json_mod_str)
            # print json_str

            input_json = json.loads(json_str, object_pairs_hook=OrderedDict)
            # print input_json
    except Exception as e:
        print "failed to load json file"
        raise e
        sys.exit(1)

    _column_order = 0

    # Check if the output is that of spawn
    if ('result' in input_json):
        input_json = input_json['result']

    # atleast result_data should be present
    if ('result_data' not in input_json):
        print "did not find result_data in input json"
        sys.exit(1)

    # create a json that contains only the data that we are going to parse
    produces_input_json = OrderedDict()

    produces_input_json['action_result'] = OrderedDict()
    produces_input_json['action_result'] = input_json['result_data']
    produces_input_json['summary'] = input_json['result_summary']

    _create_produce_dict(produces_input_json, '')

    out_json = OrderedDict()
    render = {'type': 'table', 'width': 12, 'height': 5, 'title': ''}

    if (input_json['action']):
        render.update({'title':
                      input_json['action'].replace('_', ' ').title()})

    out_json['render'] = render
    out_json['output'] = _get_produce_output()

    try:
        with open(_args.ojson, "w") as res_json_file:
            json.dump(out_json, res_json_file, sort_keys=False, indent=2 * ' ')
    except:
        print "failed to save to json file"
        sys.exit(1)

    print "Wrote {0}".format(_args.ojson)


def _get_produce_output():

    global _args
    global _column_order
    ret_produces_list = []

    for k, v in _produces.iteritems():

        # ignore the action_result.parameter.context if present
        if ('action_result.*.parameter.context' in v['data_path']):
            continue

        # ignore the action_result.context if present
        if ('action_result.*.context' in v['data_path']):
            continue

        if (not _args.add_contains) and (len(v['contains']) == 0):
            # will need to delete them
            del v['contains']

        # sanitize the data path
        v['data_path'] = v['data_path'].replace('action_result.*.',
                                                'action_result.', 1)

        # last minute validations
        if (_args.remove_unknown_items):
            if (('contains' not in v)
                    and ('column_order' not in v)
                    and ('column_name' not in v)):

                continue

        # All the validations are finished we are going to add it to the list,
        # so the last
        # thing to do is add the column number
        if _args.add_columns:
            # Ignore the connector run summary
            if (v['data_path'].find('summary.total_objects', 0) == -1):
                # Column name is already added, set the column number here
                v['column_order'] = _column_order
                _column_order += 1

        ret_produces_list.append(v)

    return ret_produces_list


def _get_column_name(key):

    ret_name = ''

    name_list = [x.strip() for x in key.split('_')]

    for name in name_list:
        ret_name += name.capitalize() + ' '

    return ret_name.strip()


def _get_contains(value, key=None):

    value_regex_matches = [
            {"regex": ("^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.)"
                       "{3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$"),
             "contains_str": "ip"},
            {"regex": "^[a-zA-Z]\:.*\\\\", "contains_str": "file path"},
            {"regex": ".*\.exe$|.*\.dll$|.*\.sys$",
             "contains_str": "file name"},
            {"regex": "^[0-9a-fA-F]{32}$", "contains_str": "md5"},
            {"regex": "^[0-9a-fA-F]{40}$", "contains_str": "sha1"},
            {"regex": "^[0-9a-fA-F]{64}$", "contains_str": "sha256"},
            {"regex": "http", "contains_str": "url"},
            {"regex": "\[.*\] .*/.*\.vmx$", "contains_str": "vm"},
            {"regex": "^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,6}$",
             "contains_str": "email"},
            {"regex": "(?i)^PH_FW_RULE", "contains_str": "firewall rule"}]

    key_regex_matches = [
            {"regex": "(?i)p?pid|(parent)?processid", "contains_str": "pid"},
            {"regex": "(?i).*hostname", "contains_str": "host name"},
            {"regex": "(?i).*domain", "contains_str": "domain"},
            {"regex": "vault_id", "contains_str": "vault id"},
            {"regex": "(?i).*username", "contains_str": "user name"},
            {"regex": "(?i).*srp.*guid", "contains_str": "srp guid"}]

    contains = []

    if (type(value) == str):

        for regex_match in value_regex_matches:
            match = re.match(regex_match['regex'], value)

            if (match):
                contains.append(regex_match['contains_str'])

    if (key):
        for regex_match in key_regex_matches:
            match = re.match(regex_match['regex'], key)

            if (match):
                contains.append(regex_match['contains_str'])

    return contains


def _create_produce_basic_data_type(parent_path, v, k):
    # beware k can be None

    global _produces

    # print "Current Key: {0}".format(k)
    # print "Current Value: {0}".format(v)

    if (v is None):
        return

    curr_produce = OrderedDict()

    data_path = parent_path
    data_path += k if k else ''

    curr_produce['data_path'] = data_path

    if(type(v) is str):
        curr_produce['data_type'] = 'string'
    elif(type(v) is int):
        curr_produce['data_type'] = 'numeric'
    elif(type(v) is float):
        curr_produce['data_type'] = 'numeric'
    elif(type(v) is long):
        curr_produce['data_type'] = 'numeric'
    elif(type(v) is bool):
        curr_produce['data_type'] = 'boolean'
    elif(type(v) is unicode):
        curr_produce['data_type'] = 'string'
    else:
        raise Exception("Unknown data type {0} for data_path: {1}"
                        .format(type(v), data_path))

    if _args.add_columns:
        curr_produce['column_name'] = _get_column_name(k) if k else ''

    curr_produce['contains'] = _get_contains(v, k)

    if (data_path in _produces):
        _produces[data_path]['contains'].extend(curr_produce['contains'])

        # eliminate duplicates
        contains_set = set(_produces[data_path]['contains'])
        _produces[data_path]['contains'] = list(contains_set)

        if (_produces[data_path]['data_type'] != curr_produce['data_type']):
            print("data path with 2 diff data_types encountered data_path:"
                  " {0} data_type1: {1} data_type2: {2} will be ignored"
                  .format(data_path, _produces[data_path]['data_type'],
                          curr_produce['data_type']))
    else:
        if (data_path.endswith('.*.')):
            data_path = data_path[:-3]
            curr_produce['data_path'] = data_path
        _produces[data_path] = curr_produce

    # print curr_produce
    return


def _create_produce_list(curr_json, parent_path):

    global indent

    if (len(curr_json) <= 0):
        return

    for item in curr_json:
        indent += 1
        # print str(indent).zfill(indent) + '{0}'.format(item)
        data_path = parent_path
        if (type(item) is OrderedDict):
            _create_produce_dict(item, data_path)
        elif(type(item) is list):
            append_text = '*.' if (data_path.endswith('.')) else '.*.'
            _create_produce_list(item, data_path + append_text)
        else:
            _create_produce_basic_data_type(parent_path, item, None)


def _create_produce_dict(curr_json, parent_path):

    global indent

    for k, v in curr_json.iteritems():
        indent += 1
        # print str(indent).zfill(indent) + '{0}'.format(k)
        data_path = parent_path + k
        # print (type(v))
        if (type(v) is OrderedDict):
            _create_produce_dict(v, data_path + '.')
        elif(type(v) is list):
            _create_produce_list(v, data_path + '.*.')
        else:
            _create_produce_basic_data_type(parent_path, v, k)


if __name__ == "__main__":

    prog_name = sys.argv[0]
    main(sys.argv[1:])
