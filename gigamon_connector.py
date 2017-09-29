#!/usr/bin/env python2.7
# --
# File: gigamon_connector.py
# --
# -----------------------------------------
# Gigamon sample App Connector python file
# -----------------------------------------

# Phantom App imports
import phantom.app as phantom

from phantom.base_connector import BaseConnector
from phantom.action_result import ActionResult

# Imports local to this App
import json
import requests
import time

# Imports form other files
import gigamon_consts as CONSTS

# disable request warnings about certs (testing only)
requests.packages.urllib3.disable_warnings()


# Define the App Class
class GigamonApiConnector(BaseConnector):

    ACTION_ID_GET_MAP = "get_map"
    ACTION_ID_GET_MAPS = "get_maps"
    ACTION_ID_POST_RULE = "post_rule"
    ACTION_ID_DELETE_RULE = "delete_rule"

    def __init__(self):

        super(GigamonApiConnector, self).__init__()

    def _test_connectivity(self, param):

        # get the asset config
        config = self.get_config()

        # get FM login info
        server = config.get('FM_server')
        user = config.get('FM_user')
        passwd = config.get('FM_password')

        # build gigamon api url
        URL = ("https://"
               + server
               + "/api/version")

        if (not server):
            self.save_progress("FM instance not set")
            return self.get_status()

        # save progress
        self.save_progress("Querying FM to check connectivity")
        self.save_progress(phantom.APP_PROG_CONNECTING_TO_ELLIPSES, server)

        # log in and get the api version
        try:
            access = requests.session()
            access.auth = (user, passwd)
            result = access.get(URL, verify=False)
            access.close()
        except Exception as e:
            self.set_status(phantom.APP_ERROR,
                            CONSTS.GIGAMON_ERR_SERVER_CONNECTION,
                            e)
            self.append_to_message(CONSTS.GIGAMON_ERR_CONNECTIVITY_TEST)
            return self.get_status()

        # check that we are running api v1.3
        version = json.loads(result.content)
        if (version['apiVersion'] != CONSTS.GIGAMON_API_VERSION):
            return self.set_status_save_progress(
                phantom.APP_ERROR,
                CONSTS.GIGAMON_ERR_API_VERSION)

        # check for successful return code
        if (result.status_code == 200):
            return self.set_status_save_progress(
                phantom.APP_SUCCESS,
                CONSTS.GIGAMON_SUCC_CONNECTIVITY_TEST)
        else:
            self.append_to_message(CONSTS.GIGAMON_ERR_CONNECTIVITY_TEST)

        return self.get_status()

    def _get_map(self, param):

        # get the asset config
        config = self.get_config()
        self.debug_print("param", param)

        # Add an action result to the App Run
        action_result = ActionResult(dict(param))
        self.add_action_result(action_result)

        # get FM login info
        server = config.get('FM_server')
        user = config.get('FM_user')
        passwd = config.get('FM_password')

        # build gigamon api url
        clusterId = param['Cluster_ID']
        mapAlias = param['Map_alias']
        URL = ("https://"
               + server
               + "/api/v1.3/maps/"
               + mapAlias
               + "?clusterId="
               + clusterId)

        # log in and get the map
        try:
            access = requests.session()
            access.auth = (user, passwd)
            result = access.get(URL, verify=False)
            access.close()
        except Exception as e:
            action_result.set_status(phantom.APP_ERROR,
                                     CONSTS.GIGAMON_ERR_QUERY,
                                     e)
            return action_result.get_status()

        # modify the output of result.content to add rulecategory,
        # alias, clusterId
        output_content = json.loads(result.content)
        map_content = output_content['map']
        for rules, rule_content in map_content.iteritems():
            if rules == 'rules':
                for key, value in rule_content.iteritems():
                    if key == 'passRules':
                        for pass_rule_item in value:
                            pass_rule_item["rulecategory"] = "pass"
                            pass_rule_item["alias"] = mapAlias
                            pass_rule_item["clusterId"] = clusterId
                    if key == 'dropRules':
                        for drop_rule_item in value:
                            drop_rule_item["rulecategory"] = "drop"
                            drop_rule_item["alias"] = mapAlias
                            drop_rule_item["clusterId"] = clusterId
        action_result.add_data(output_content)

        # successful get map call will return 200. All other status codes are
        # failures
        if (result.status_code != 200):
            return action_result.set_status(
                phantom.APP_ERROR,
                (CONSTS.GIGAMON_ERR_QUERY_RETURNED_NO_DATA
                 + " - Return code: "
                 + str(result.status_code))
            )
        else:
            action_result.set_status(phantom.APP_SUCCESS,
                                     CONSTS.GIGAMON_SUCC_QUERY)

        return action_result.get_status()

    def _get_maps(self, param):

        # get the asset config
        config = self.get_config()
        self.debug_print("param", param)

        # Add an action result to the App Run
        action_result = ActionResult(dict(param))
        self.add_action_result(action_result)

        # get FM login info
        server = config.get('FM_server')
        user = config.get('FM_user')
        passwd = config.get('FM_password')

        # build gigamon api url
        clusterId = param['Cluster_ID']
        URL = ("https://"
               + server
               + "/api/v1.3/maps?clusterId="
               + clusterId)

        # log in and get the maps
        try:
            access = requests.session()
            access.auth = (user, passwd)
            result = access.get(URL, verify=False)
            access.close()
        except Exception as e:
            action_result.set_status(phantom.APP_ERROR,
                                     CONSTS.GIGAMON_ERR_QUERY,
                                     e)
            return action_result.get_status()

        # convert result string to json
        action_result.add_data(json.loads(result.content))

        # successful get map call will return 200. All other status codes are
        # failures
        if (result.status_code != 200):
            return action_result.set_status(
                phantom.APP_ERROR,
                (CONSTS.GIGAMON_ERR_QUERY_RETURNED_NO_DATA
                 + " - Return code: "
                 + str(result.status_code))
            )
        else:
            action_result.set_status(phantom.APP_SUCCESS,
                                     CONSTS.GIGAMON_SUCC_QUERY)

        return action_result.get_status()

    def _post_rule(self, param):

        # get the asset config
        config = self.get_config()
        self.debug_print("param", param)

        # Add an action result to the App Run
        action_result = ActionResult(dict(param))
        self.add_action_result(action_result)

        # get FM login info
        server = config.get('FM_server')
        user = config.get('FM_user')
        passwd = config.get('FM_password')

        # url paramenters
        clusterId = param['Cluster_ID']
        mapAlias = param['Map_alias']

        # map url parameters
        MAP_URL = ("https://"
                   + server
                   + "/api/v1.3/maps/"
                   + mapAlias
                   + "?clusterId="
                   + clusterId)

        # log in and get the map details
        try:
            access = requests.session()
            access.auth = (user, passwd)
            result = access.get(MAP_URL, verify=False)
        except Exception as e:
            action_result.set_status(phantom.APP_ERROR,
                                     CONSTS.GIGAMON_ERR_QUERY,
                                     e)
            return action_result.get_status()

        # get the next rule id
        rule_flag = 0  # flag if this is an empty map
        max_rule_id1 = 0
        max_rule_id2 = 0
        output_content = json.loads(result.content)
        map_content = output_content['map']
        for rules, rule_content in map_content.iteritems():
            if rules == 'rules':
                if 'passRules' in rule_content.keys():
                    max_rule_id1 = rule_content['passRules'][-1]['ruleId']
                if 'dropRules' in rule_content.keys():
                    max_rule_id2 = rule_content['dropRules'][-1]['ruleId']
                next_rule_id = max(max_rule_id1, max_rule_id2) + 1
                rule_flag = 1
                break
        if not rule_flag:
            next_rule_id = 1

        # post url parameters
        ruleType = param['Rule_type']
        POST_URL = ("https://"
                    + server
                    + "/api/v1.3/maps/"
                    + mapAlias
                    + "/rules/"
                    + ruleType
                    + "?clusterId="
                    + clusterId)

        # payload parameters
        payload = {"ruleId": next_rule_id,
                   "comment": "",
                   "bidi": "false",
                   "matches": [{
                       "type": "ip4Src",
                       "value": param['IPv4_Address'],
                       "netMask": "255.255.255.255"}]}

        # log in and post a rule to the map
        try:
            result = access.post(POST_URL,
                                 data=json.dumps(payload),
                                 verify=False)
            access.close()
        except Exception as e:
            action_result.set_status(phantom.APP_ERROR,
                                     CONSTS.GIGAMON_ERR_QUERY,
                                     e)
            return action_result.get_status()

        # return code 201 == success. no api output on success
        if (result.status_code != 201):
            # post calls return no content if successful
            action_result.add_data(json.loads(result.content))
            return action_result.set_status(
                phantom.APP_ERROR,
                (CONSTS.GIGAMON_ERR_QUERY_RETURNED_NO_DATA
                 + " - Return code: "
                 + str(result.status_code))
            )
        else:
            # post calls return no content if successful
            action_result.add_data({'return_code': str(result.status_code)})
            action_result.set_status(phantom.APP_SUCCESS,
                                     CONSTS.GIGAMON_SUCC_QUERY)

        return action_result.get_status()

    def _delete_rule(self, param):

        # get the asset config
        config = self.get_config()
        self.debug_print("param", param)

        # Add an action result to the App Run
        action_result = ActionResult(dict(param))
        self.add_action_result(action_result)

        # get FM login info
        server = config.get('FM_server')
        user = config.get('FM_user')
        passwd = config.get('FM_password')

        # build gigamon api url
        clusterId = param['Cluster_ID']
        mapAlias = param['Map_alias']
        ruleID = param['Rule_ID']
        URL = ("https://"
               + server
               + "/api/v1.3/maps/"
               + mapAlias
               + "/rules/"
               + ruleID
               + "?clusterId="
               + clusterId)

        # log in and delete the rule from the map
        try:
            access = requests.session()
            access.auth = (user, passwd)
            result = access.delete(URL, verify=False)
            access.close()
            # wait 120s for the delete command to take effect
            time.sleep(120)
        except Exception as e:
            action_result.set_status(phantom.APP_ERROR,
                                     CONSTS.GIGAMON_ERR_QUERY,
                                     e)
            return action_result.get_status()

        # return code 204 == success.
        if (result.status_code != 204):
            action_result.add_data(json.loads(result.content))
            return action_result.set_status(
                phantom.APP_ERROR,
                (CONSTS.GIGAMON_ERR_QUERY_RETURNED_NO_DATA
                 + " - Return code: "
                 + str(result.status_code))
            )
        else:
            # delete call returns no data on success
            action_result.add_data({'return_code': str(result.status_code)})
            action_result.set_status(phantom.APP_SUCCESS,
                                     CONSTS.GIGAMON_SUCC_QUERY)

        return action_result.get_status()

    def handle_action(self, param):

        # actions expect success
        ret_val = phantom.APP_SUCCESS
        action_id = self.get_action_identifier()
        # used when debug is true in the app config json file
        self.debug_print("action_id", self.get_action_identifier())

        if (action_id == phantom.ACTION_ID_TEST_ASSET_CONNECTIVITY):
            ret_val = self._test_connectivity(param)
        elif (action_id == self.ACTION_ID_GET_MAP):
            ret_val = self._get_map(param)
        elif (action_id == self.ACTION_ID_GET_MAPS):
            ret_val = self._get_maps(param)
        elif (action_id == self.ACTION_ID_POST_RULE):
            ret_val = self._post_rule(param)
        elif (action_id == self.ACTION_ID_DELETE_RULE):
            ret_val = self._delete_rule(param)

        return ret_val


if __name__ == '__main__':

    import sys
    import pudb
    pudb.set_trace()

    if (len(sys.argv) < 2):
        print "No test json specified as input"
        exit(0)

    with open(sys.argv[1]) as f:
        # action parameters converted to json format
        in_json = f.read()
        in_json = json.loads(in_json)
        print(json.dumps(in_json, indent=4))
        # instantiate the connector with our class
        connector = GigamonApiConnector()
        connector.print_progress_message = True
        # run the desired action
        ret_val = connector._handle_action(json.dumps(in_json), None)
        print (json.dumps(json.loads(ret_val), indent=4))

    exit(0)
