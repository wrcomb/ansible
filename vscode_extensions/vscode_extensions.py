#!/usr/bin/python

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = r'''
---
module: vscode_extensions
'''

EXAMPLES = r'''
- name: Install Visual Studio Code extensions
  vscode_extensions:
    name:
        - ms-python.python
        - golang.go-nightly
    state: installed

- name: Unstall Visual Studio Code extensions
  vscode_extensions:
    name:
        - ms-python.python
        - golang.go-nightly
    state: unstalled
'''

RETURN = r'''
'''

from ansible.module_utils.basic import AnsibleModule

def is_install(module, name):
    CODE_PATH = module.get_bin_path('code-insiders', required=True)
    cmd = f"{CODE_PATH} --list-extensions"
    rc, stdout, stderr = module.run_command(cmd)
    if rc != 0:
        module.fail_json(msg="failed to list extensions", stdout=stdout, stderr=stderr)
    for line in stdout.splitlines():
        line = line.strip()
        if line == name:
            return True
    return False

def install(module, names):
    CODE_PATH = module.get_bin_path('code-insiders', required=True)
    extensions = []
    for name in names:
        if not is_install(module, name):
            extensions.append(name)
    if not extensions:
        module.exit_json(changed=False, msg="extension(s) already installed")
    names_arg = "--install-extension " + " --install-extension ".join(extensions)
    cmd = f"{CODE_PATH} {names_arg}"
    rc, stdout, stderr = module.run_command(cmd)
    if rc != 0:
        module.fail_json(msg=f"failed to enable {' '.join(extensions)}", stdout=stdout, stderr=stderr)
    module.exit_json(changed=True, msg=f"installed vscode extensions: {' '.join(extensions)}")

def uninstall(module, names):
    CODE_PATH = module.get_bin_path('code-insiders', required=True)
    extensions = []
    for name in names:
        if is_install(module, name):
            extensions.append(name)
    if not extensions:
        module.exit_json(changed=False, msg="extension(s) already uninstalled")
    names_arg = "--uninstall-extension " + " --uninstall-extension ".join(extensions)
    cmd = f"{CODE_PATH} {names_arg}"
    rc, stdout, stderr = module.run_command(cmd)
    if rc != 0:
        module.fail_json(msg=f"failed to unstall {' '.join(extensions)}", stdout=stdout, stderr=stderr)
    module.exit_json(changed=True, msg="uninstalled vscode extension(s): {' '.join(extensions)}")

def main():
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(type='str', default='installed', choices=['unstalled', 'installed']),
            name=dict(type='list', required = True)
        )
    )

    p = module.params

    if p['state'] == 'installed':
        install(module, p['name'])
    elif p['state'] == 'unstalled':
        uninstall(module, p['name'])

if __name__ == '__main__':
    main()