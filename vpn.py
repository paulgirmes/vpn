#!/usr/bin/python

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
import subprocess
from subprocess import CalledProcessError, TimeoutExpired
from ansible.module_utils.basic import AnsibleModule

DOCUMENTATION = r'''
---
module: OpenVpn

installs OpenVpnServer on Ubuntu with CA / server Key

# If this is part of a collection, you need to use semantic versioning,
# i.e. the version is of the form "2.5.0" and not "2.4".
version_added: "1.0.0"

description: installs OpenVpnServer on Ubuntu with CA / server Key

options:
    name:
        description: This is the message to send to the test module.
        required: true
        type: str
    new:
        description:
            - Control to demo if the result of this module is changed or not.
            - Parameter description can be a list as well.
        required: false
        type: bool
# Specify this value according to your collection
# in format of namespace.collection.doc_fragment_name
extends_documentation_fragment:
    -

author:
    -
'''

EXAMPLES = r'''
# Pass in a message
- name: Test with a message
  my_namespace.my_collection.my_test:
    name: hello world

# pass in a message and have changed true
- name: Test with a message and changed output
  my_namespace.my_collection.my_test:
    name: hello world
    new: true

# fail the module
- name: Test failure of the module
  my_namespace.my_collection.my_test:
    name: fail me
'''

RETURN = r'''
# These are examples of possible return values, and in general should use
# other names for return values.
original_message:
    description: The original name param that was passed in.
    type: str
    returned: always
    sample: 'hello world'
message:
    description: The output message that the test module generates.
    type: str
    returned: always
    sample: 'goodbye'
'''


def open_vpn_install():
    ovpn_install = subprocess
    try:
        install_result = ovpn_install.run(
            ["apt", "install", "openvpn"], check=True,
            capture_output=True, timeout=300
            )
        if b"already" in install_result.stdout.split():
            changed = False
        else:
            changed = True
        return [0, changed]
    except CalledProcessError as e:
        return [1, str(e)]
    except TimeoutExpired as e:
        return [1, str(e)]


def main():
    module_args = dict(
        name=dict(type='str', required=False),
        new=dict(type='bool', required=False, default=False)
    )

    # seed the result dict in the object
    # we primarily care about changed and state
    # changed is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        changed=False,
        ovpn_install='',
        error='',
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
    )

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        module.exit_json(**result)
    if module.params['name'] == 'failme':
        module.fail_json(msg='You requested this to fail', **result)
    ovpn_install = open_vpn_install()
    if ovpn_install[0] == 0:
        result['ovpn_install'] = 'installation openvpn OK'
        result['changed'] = ovpn_install[1]
        module.exit_json(**result)
    else:
        result['error'] = ovpn_install[1]
        module.fail_json(msg='the installation of OpenVpn Failed', **result)


if __name__ == '__main__':
    main()
