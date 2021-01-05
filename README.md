# slack-task-2

## Aurora Documentation

This project contains a custom configuration management tool written in Python called Aurora, to configure remote servers. It uses a YAML based setup script to state the steps needed and gets executed in a sequential manner.

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
    │   ├── bootstrap.sh
    │   └── requirements.txt
    └── steps
        ├── configure-php-log.yaml
        ├── configure-php-no-log.yaml
        ├── uninstall-php-and-apache-log.yaml
        └── uninstall-php-and-apache-no-log.yaml
```
- `src`: This contains the source code and the configuration files needed to configure remote servers.
- `aurora`: This dir contains the controller source files for Aurora along with its dependent classes.
- `environment`: This dir contains the values for the params specified in the YAML based step files. This can be segregated based on environments to dynamically inject secrets and manage configuration.
- `files`: This dir contains files that need to be transferred to remote servers as part of its SFTP capability. Files placed in this dir only will be used for SFTP.
- `scripts`: This dir contains any additional scripts for setup and managing dependencies for Aurora. This currently has a bootstrap script to setup the python dependencies needed to run Aurora.
- `steps`: This dir contains the YAML based step files that are executed sequentially on the remote server. These steps use inputs in the form of variables that are resolved using the values present in the configuration file kept in the `/environment` dir. These steps only accept variable references and not direct hard-coded values.

(**Note:** Currently testing is done manually but this will be automated using the `unittest` library in the future in its own directory)

## Aurora Keywords

Aurora supports the following high level keywords at present:

- `install`: This installs standard debian packages on a remote server.
- `uninstall`: This uninstalls standard debian packages on a remote server.
- `sftp`: This transfers a file from the `/files` dir to a remote server.

Each of these keywords allow further params to be included as part of their execution. Some parameters are optional and are marked as so, the rest are mandatory:

- The `install` and the `uninstall` keyword has the following allowable params:
  - `name`: This specifies a description of the task block.
  - `packages`: This specifies the env var reference of the debian packages that need to be installed/uninstalled on the remote host. The value for this needs to be specified as a `list`.
  - `restart` (Optional): This specifies the env var reference of the packages that need to be restarted as part of this task step. The value for this needs to be specified as a `list`.
  - `log` (Optional): If this is set to `True` it enables verbose mode to view all the steps being executed along with their response. By default this is set to `False`. This needs to be enabled for each task step block.

- The `sftp` keyword has the following allowable params:
  - `name`: This specifies a description of the task block.
  - `src_location`: This specifies the env var reference of the source file in the `/files` dir that needs to be transferred to the remote host. Only files in the `/files` dir will be used by Aurora so the file name alone is needed, not the entire path.
  - `dst_location`: This specifies the env var reference of the destination host path where the local file needs to be transferred to. This is similar to the way the linux `mv` command specifies the end destination.
  - `metadata` (Optional): This specifies the env var reference of the file metadata as given below. Since this is an optional param, the below params are also optional.
    - `owner`: This specifies the env var reference of the file owner, similar to the `user` in the `chown` command. This is a mandatory param if `metadata` is used.
    - `group`: This specifies the env var reference of the group ownership, similar to the `group` in the `chown` command. This is a mandatory param if `metadata` is used.
    - `mode` (Optional): This specifies the env var reference of the access permissions of the file system object. This can be written in an integer format like `0777` or `a+rwx`.
  - `log` (Optional): If this is set to `True` it enables verbose mode to view all the steps being executed along with their response. By default this is set to `False`. This needs to be enabled for each task step block.
  - `restart`(Optional): This specifies the env var reference of the packages that need to be restarted as part of this task step. The value for this needs to be specified as a `list`.

## Examples

- The YAML step file always starts with the following snippet which specifies the env var reference for the remote host and its ssh params. This is used to build and maintain an SSH connection with the remote host(s). The `name` param in the initial block is mandatory, same as the rest of the task blocks. The `tasks` param is used to signify the steps that need to be executed sequentially to configure our remote host. Each of the env var references like `{{ webservers }}`, `{{ user }}`, and `{{ ssh_pwd }}` point to the values specified in the `/environment` dir YAML configuration value file to avoid hard coding values in the steps file. All blocks follow the same syntax, only allowing env var references, with interpolation happening at run time by Aurora based on the configuration value file passed to it when starting Aurora. At present, Aurora only works with password based SSH, not key based.

```
  ---

- name: deploy php web application
  hosts: "{{ webservers }}"
  remote_user: "{{ user }}"
  pwd: "{{ ssh_pwd }}"
  
  tasks:
```

The configuration value file in the `/environment` dir will look as follows (pwd is a random string in this snippet):

```
# Specify IP addresses of hosts that need to be configured
webservers:
  - 54.162.212.238
  - 54.197.201.77

# Specify username and password of hosts for SSH
user: root
ssh_pwd: TESTPWDONLY
```

- The steps in the tasks to be executed follow a similar structure, for instance if we want to install a package on a remote host, we will use the `install` keyword as follows, with the values provided as env var references that are resolved by Aurora at run time:

```
---

- name: deploy php web application
  hosts: "{{ webservers }}"
  remote_user: "{{ user }}"
  pwd: "{{ ssh_pwd }}"

  tasks:
  - name: install dependencies on host
    install: 
      packages: "{{ packages }}"
```

The configuration value file in the `/environment` dir will look as follows (pwd is a random string in this snippet):

```
# Specify IP addresses of hosts that need to be configured
webservers:
  - 54.162.212.238
  - 54.197.201.77

# Specify username and password of hosts for SSH
user: root
ssh_pwd: {{ pwd }}

# Specify packages that need to be configured on the destination host(s)
packages:
  - php
  - libapache2-mod-php
```

- If we want to enable logging to view a more verbose output for this block then we can include the `log` param as follows:

```
---

- name: deploy php web application
  hosts: "{{ webservers }}"
  remote_user: "{{ user }}"
  pwd: "{{ ssh_pwd }}"

  tasks:
  - name: install dependencies on host
    install: 
      packages: "{{ packages }}"
      log: True
```

The `src/steps` dir contains 4 example step files as follows:

- `configure-php-log.yaml`: This step file will configure web servers to host a sample `Hello, world!` PHP application in verbose mode, showing all the output for every step.
- `configure-php-no-log.yaml`: This step file will configure web servers to host a sample `Hello, world!` PHP application showing concise output for every step.
- `uninstall-php-and-apache-log.yaml`: This step file will uninstall the apache2 and php debian packages from the remote servers, showing all the output for every step.
- `uninstall-php-and-apache-no-log.yaml`: This step file will uninstall the apache2 and php debian packages from the remote servers, showing concise output for every step.

The `src/steps` dir also contains 7 test step files as follows:

- `test-missing-owner-and-group-in-metadata.yaml`: This captures the error message when the metadata param is used without the `owner` and `group` params.
- `test-missing-src-location-in-sftp.yaml`: This captures the error message when the `src_location` param is not used in the `sftp` keyword.
- `test-no-name-in-initial-block.yaml`: This captures the error message when the `name` param is not used in the initial block of the step file.
- `test-no-name-in-tasks.yaml`: This captures the error message when the `name` param is not used in the `task` block of the step file.
- `test-no-remote-user-in-initial-block.yaml`: This captures the error message when the ssh `remote_user` param is not used in the initial block of the step file. 
- `test-not-use-env-var.yaml`: This captures the error message when the env var references are not used in the step file. Any of the env var references can be replaced with hard-coded values and the same error message will be captured.
- `test-unknown-keyword.yaml`: This captures the error message when an unknown high level keyword is used in the step file.

There are also checks for less than the two files being passed during execution - the step file and the configuration values file or incorrect file names being passed.

## Environment requirements

- Python 3.6.6 or higher

## Running Aurora:

For initial setup of the dependencies, we need to perform the following steps:
- We need to `cd` into the `/src/scripts` dir where the `bootstrap.sh` script is located.
- Run `. ./bootstrap.sh`. This installs pip3, a virtual env for python3, and packages needed for Aurora as listed in the `requirements.txt` in the same dir.

(**Note:** The `pyyaml` package currently has issues with building `wheel` but is still installed and works without any issues)

To run Aurora, we need to perform the following steps:

- We need to `cd` into the `src/environment` dir where the env var configuration values file is located. In the current project we have `dev.yaml` which serves as this file. In `dev.yaml`, replace the `{{ pwd }}` param with the pwd of the SSH host.
- We need to `cd` into the `/src/aurora/` dir where the `controller.py` file is located. 
- Run the following command: 

```
python3 controller.py configure-php-log.yaml dev.yaml
```

This is of the form:

```
python3 controller.py <step_file.yaml> <env_var_configuration.yaml>
```
The `configure-php-log.yaml` is the step file we write in the `/steps` dir and the `dev.yaml` is the configuration value file we write in the `/environment` dir.

## Author:

- Rahul Sharma <sharma1@student.unimelb.edu.au>