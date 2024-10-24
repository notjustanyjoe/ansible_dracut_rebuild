#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
import subprocess

def run_dracut(initramfs_dest, kernel_version, modules, force):
    cmd = ["dracut"]

    if force:
        cmd.append("--force")

    # Add each module with a separate --add flag
    if isinstance(modules, list):
        for module in modules:
            cmd.append("--add")
            cmd.append(module)
    else:
        # If for some reason it's a single string (combined by mistake), split and add each one
        for module in modules.split(','):
            cmd.append("--add")
            cmd.append(module)

    cmd.append(initramfs_dest)
    cmd.append(kernel_version)

    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, text=True)
        return {"changed": True, "stdout": result.stdout, "stderr": result.stderr}
    except subprocess.CalledProcessError as e:
        return {"changed": False, "stdout": e.stdout, "stderr": e.stderr, "failed": True}


def main():
    module_args = dict(
        name=dict(type='str', required=True),  # initramfs destination
        kernel=dict(type='str', required=True),  # kernel version
        add_dracut_modules=dict(type='list', required=False, default=[]),  # list of dracut modules to add (e.g., nfs, rdma)
        force=dict(type='bool', required=False, default=False),  # force the dracut rebuild
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=False
    )

    initramfs_dest = module.params['name']
    kernel_version = module.params['kernel']
    modules = module.params['add_dracut_modules']
    force = module.params['force']

    # Ensure that modules are passed correctly as a list of separate --add flags
    result = run_dracut(initramfs_dest, kernel_version, modules, force)

    if result.get("failed"):
        module.fail_json(msg="Dracut command failed", **result)
    else:
        module.exit_json(**result)


if __name__ == '__main__':
    main()
