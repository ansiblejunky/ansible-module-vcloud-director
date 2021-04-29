# Copyright © 2018 VMware, Inc. All Rights Reserved.
# SPDX-License-Identifier: BSD-2-Clause OR GPL-3.0-only

# !/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: vcd_resources
short_description: Add/Delete/Update VCD Infrastructure resources
version_added: "2.4"
description:
    - Add/Delete/Update VCD Infrastructure resources

options:
    user:
        description:
            - vCloud Director user name
        required: false
    password:
        description:
            - vCloud Director user password
        required: false
    host:
        description:
            - vCloud Director host address
        required: false
    org:
        description:
            - Organization name on vCloud Director to access
        required: false
    api_version:
        description:
            - Pyvcloud API version
        required: false
    verify_ssl_certs:
        description:
            - whether to use secure connection to vCloud Director host
        required: false
    nsxt:
        description:
            - Network type of Infrastructure resource
        required: true
    vcenter:
        description:
            - Compute type of Infrastructure resource
        required: true
    state:
        description:
            - state of vcd resource ('present'/'absent'/'update').
        required: false
    operation:
        description:
            - operations on vcd resource ('read').
        required: false

author:
    - mtaneja@vmware.com
'''

EXAMPLES = '''
- name: add vcd resources
  vcd_resources
    nsxt:
        url: ""
        username: ""
        password: ""
        networkProviderScope: ""
    state: "present"
  register: output
'''

RETURN = '''
msg: success/failure message corresponding to resource state
changed: true if resource has been changed
'''

import requests
from ansible.module_utils.vcd import VcdAnsibleModule
from ansible.module_utils.vcd_resources_endpoint import *

VCD_RESOURCES_STATES = ['present', 'absent', 'update']
VCD_RESOURCES_OPERATIONS = ['read']


def vcd_resources_argument_spec():
    return dict(
        nsxt=dict(type='dict', required=False),
        vcenter=dict(type='dict', required=False),
        state=dict(choices=VCD_RESOURCES_STATES, required=True),
    )


class VcdResources(VcdAnsibleModule):
    def __init__(self, **kwargs):
        super(VcdResources, self).__init__(**kwargs)

    def manage_states(self):
        state = self.params.get('state')
        if state == "present":
            return self.add()

        if state == "absent":
            return self.delete()

        if state == "update":
            return self.update()

    def _add_nsxt(self, nsxt):
        data = {
            "url": nsxt.get('url'),
            "username": nsxt.get('username'),
            "password": nsxt.get('password'),
            "networkProviderScope": nsxt.get('networkProviderScope')
        }
        vcdHost = self.params.get('host')
        vcd_end_point = 'http://{0}/{1}'.format(vcdHost, NSXT_MANAGER_ENDPOINT)
        response = requests.post(vcd_end_point, data=data)
        status, text = response.status_code, response

        if status != 200:
            raise Exception("{0}: {1}".format(status, text))

        return status, text

    def _add_vcenter(self, vcenter):
        pass

    def add(self):
        nsxt = self.params.get('nsxt')
        vcenter = self.params.get('vcenter')
        response = dict()
        response['changed'] = False
        response['msg'] = dict()

        if nsxt:
            status, text = self._add_nsxt(nsxt)
            response['msg'].update({
                'nsxt': {
                    'status': status,
                    'msg': text
                }
            })

        if vcenter:
            self._add_vcenter(vcenter)
            response['msg'].update({
                'vcenter': {
                    'status': status,
                    'msg': text
                }
            })

        return response

    def delete(self):
        pass

    def update(self):
        pass

    def read(self):
        pass


def main():
    argument_spec = vcd_resources_argument_spec()
    response = dict(msg=dict(type='str'))
    module = VcdResources(argument_spec=argument_spec, supports_check_mode=True)

    try:
        if module.check_mode:
            response = dict()
            response['changed'] = False
            response['msg'] = "skipped, running in check mode"
            response['skipped'] = True
        elif module.params.get('state'):
            response = module.manage_states()
        elif module.params.get('operation'):
            response = module.manage_operations()
        else:
            raise Exception('Please provide state/operation for resource')
    except Exception as error:
        response['msg'] = error.__str__()
        module.fail_json(**response)
    else:
        module.exit_json(**response)


if __name__ == '__main__':
    main()
