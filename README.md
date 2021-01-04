# slack-task-2

## Aurora Documentation

This project contains a custom configuration management tool written in Python called Aurora, to configure remote servers. It uses a YAML based setup script to state the steps needed to execute in a sequential manner.

It has the following directory structure:

```
.
├── README.md
└── src
    ├── aurora
    │   ├── controller.py
    │   └── ssh_client.py
    ├── environment
    │   └── dev.yaml
    ├── files
    │   ├── dir.conf
    │   └── php_application.php
    ├── scripts
    │   └── bootstrap.sh
    └── steps
        └── configure-php.yaml
```
- `src`: This contains the source code and the configuration files needed to configure remote servers.
- `aurora`: This dir contains the controller source files for Aurora along with its dependent classes.
- `environment`: This dir contains the values for the params specified in the YAML based step files. This can be segregated based on environments to dynamically inject secrets and manage configuration.
- `files`: This dir contains files that need to be transferred to remote servers as part of its SFTP capability. Files placed in this dir only will be used for SFTP.
- `scripts`: This dir contains any additional scripts for setup and managing dependencies for Aurora. This currently has a bootstrap script to setup the python dependencies needed to run Aurora.
- `steps`: This dir contains the YAML based step files that are executed sequentially on the remote server. These steps use inputs in the form of variables that are resolved using the values present in the configuration file kept in the `/environment` dir. These steps only accept variable references and not direct hardcoded values.

Aurora supports the following high level keywords at present:

- `install`: This installs standard debian packages on a remote server.
- `uninstall`: This uninstalls standard debian packages on a remote server.
- `sftp`: This transfers a file from the `/files` dir to a remote server.

Each of these keywords allow further params to be included as part of their execution. Some parameters are optional and are marked as so, the rest are mandatory:

- The `install` and the `uninstall` keyword has the following allowable params:
  - `packages`: This specifies the env var reference of the debian packages that need to be installed/uninstalled on the remote host. The value for this needs to be specified as a `list`.
  - `restart` (Optional): This specifies the env var reference of the packages that need to be restarted as part of this task step. The value for this needs to be specified as a `list`.
  - `log` (Optional): If this is set to `True` it enables verbose mode to view all the steps being executed along with their response. By default this is set to `False`.

- The `sftp` keyword has the following allowable params:
  - `src_location`: This specifies the env var reference of the source file in the `/files` dir that needs to be transferred to the remote host. Only files in the `/files` dir will be used by Aurora so the file name alone is needed, not the entire path.
  - `dst_location`: This specifies the env var reference of the destination host path where the local file needs to be transferred to. This is similar to the way the linux `mv` command specifies the end destination.
  - `metadata` (Optional): This specifies the env var reference of the file metadata as given below. Since this is an optional param, the below params are also optional.
    - `owner` (Optional): This specifies the env var reference of the file owner, similar to the `user` in the `chown` command.
    - `group` (Optional): This specifies the env var reference of the group ownership, similar to the `group` in the `chown` command.
    - `mode` (Optional): This specifies the env var reference of the access permissions of the file system object. This can be written in an integer format like `0777` or `a+rwx`.
  - `log` (Optional): If this is set to `True` it enables verbose mode to view all the steps being executed along with their response. By default this is set to `False`.
  - `restart`(Optional): This specifies the env var reference of the packages that need to be restarted as part of this task step. The value for this needs to be specified as a `list`.