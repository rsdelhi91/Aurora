# slack-task-2

## Aurora Documentation

This project contains a custom configuration management tool written in Python called Aurora, to configure remote servers. It uses a YAML based setup script to state the steps needed to execute in a sequential manner.

It has the following directory structure:

```
├── README.md
└── src
    ├── aurora
    │   ├── controller.py
    │   └── ssh_client.py
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
- `files`: This dir contains files that need to be transferred to remote servers as part of its SFTP capability. Files placed in this dir only will be used for SFTP.
- `scripts`: This dir contains any additional scripts for setup and managing dependencies for Aurora. This currently has a bootstrap script to setup the python dependencies needed to run Aurora.
- `steps`: This dir contains the step files that are executed sequentially on the remote server.

Aurora supports the following high level keywords at present:

- `install`: This installs standard debian packages on a remote server.
- `uninstall`: This uninstalls standard debian packages on a remote server.
- `sftp`: This transfers a file from the `/files` dir to a remote server.