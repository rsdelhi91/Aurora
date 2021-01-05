""" Main controller file of Aurora

This file uses the ssh_client.py file to connect to
the remote servers as specified in the steps file and 
execute the tasks sequentially based on the keywords 
supported. We currently support the following main 
keywords:

* install
* uninstall
* sftp

Each of these keywords can contain a number of optional 
parameters.

Author: Rahul Sharma <sharma1@student.unimelb.edu.au>
"""

import yaml, sys, pyfiglet, os
from ssh_client import *

def params_present(param, parsed_config):
  """ Checks if the parameters provided are present

  variable inputs:
    param - can be a dictionary, a string, or an integer parameter
    parsed_config - the yaml parsed configuration values
  """
  if param in parsed_config and isinstance(parsed_config[param], list):
    if len(parsed_config[param]) > 0:
        return True
  elif param in parsed_config and isinstance(parsed_config[param], str):
    if parsed_config[param]:
        return True
  elif param in parsed_config and isinstance(parsed_config[param], int):
    if parsed_config[param]:
        return True
  print("ERROR: " + param + " is empty or not present")
  sys.exit()

def check_env_var(param):
  """Check if the env var parameters are formatted correctly

  variable inputs:
    param: env var references used in the step yaml file
  """
  if param.startswith("{{") and len(param.split()) == 3:
    return param.split()[1]
  else:
    print("ERROR: " + param + " is not properly formatted")
    sys.exit()

def manage_dependencies(connection, session, parsed_steps, config_list, install):
  """Installs and Uninstalls packages on a standard debian image

  variable inputs:
    connection - the object reference for the SSHClient class
    session - the ssh session to the remote host
    parsed_steps - the parsed yaml configuration step for installing/uninstalling packages
    config_list - the yaml parsed configuration values
    install - boolean value, true means installing packages, else uninstalling
  """
  if "packages" in parsed_steps:
    packages = check_env_var(parsed_steps["packages"])
    params_present(packages, config_list)
    if "log" in parsed_steps and parsed_steps["log"]:
      connection.exec_command(session, "DEBIAN_FRONTEND=noninteractive apt-get update", log=True)
    else:
      connection.exec_command(session, "DEBIAN_FRONTEND=noninteractive apt-get update")
    if type(config_list[packages]) == list:
      for package in config_list[packages]:
        if install:
          print("Installing...")
          if "log" in parsed_steps and parsed_steps["log"]:
            connection.exec_command(session, "DEBIAN_FRONTEND=noninteractive apt-get install " + package + " -y", log=True)
          else:
            connection.exec_command(session, "DEBIAN_FRONTEND=noninteractive apt-get install " + package + " -y")
        else:
          print("Uninstalling...")
          if "log" in parsed_steps and parsed_steps["log"]:
            connection.exec_command(session, "DEBIAN_FRONTEND=noninteractive apt-get purge --auto-remove " + package + " -y", log=True)
          else:
            connection.exec_command(session, "DEBIAN_FRONTEND=noninteractive apt-get purge --auto-remove " + package + " -y")
    else:
      print("ERROR: packages need to be of type list but is of type:", type(config_list[packages]))
      sys.exit()
    if "restart" in parsed_steps:
      service = check_env_var(parsed_steps["restart"])
      params_present(service, config_list)
      if "log" in parsed_steps:
        restart_service(connection, session, config_list[service], log=True)
      else:
        restart_service(connection, session, config_list[service])
  else:
    print("ERROR: Packages in: " + parsed_steps["packages"] + "is not defined in the right format \{\{ variable \}\}")
    sys.exit()

def restart_service(connection, session, services, log=False):
  """Restart the specified service

  variable inputs:
    connection - the object reference for the SSHClient class
    session - the ssh session to the remote host
    services - the services that require a restart
    log - enables verbose logging of steps executed. default is false.
  """
  if type(services) == list:
    for service in services:
      print("Restart the service: " + service)
      if log:
        connection.exec_command(session, "systemctl restart " + service, log=True)
      else:
        connection.exec_command(session, "systemctl restart " + service)
  else:
    print("ERROR: services needs to be of type list but is of type:", type(services))
    sys.exit()

def transfer_file(connection, session, parsed_steps, config_list):
  """ Transfer a file from local /files dir to remote host and set metadata
  
  variable inputs:
    connection - the object reference for the SSHClient class
    session - the ssh session to the remote host
    parsed_steps - the parsed yaml configuration step for transferring a file to remote host
    config_list - the yaml parsed configuration values
  """
  if "src_location" in parsed_steps and "dst_location" in parsed_steps:
    # check if the configure entry is present
    src_location = check_env_var(parsed_steps["src_location"])
    dst_location = check_env_var(parsed_steps["dst_location"])
    # check if the dev config property is present
    params_present(src_location, config_list)
    params_present(dst_location, config_list)
    # SFTP the file onto the remote server
    connection.sftp_file(session, "../files/" + config_list[src_location], config_list[dst_location])
    if "metadata" in parsed_steps:
      metadata = parsed_steps["metadata"]
      if "owner" in metadata and "group" in metadata:
        owner = check_env_var(metadata["owner"])
        group = check_env_var(metadata["group"])
        params_present(owner, config_list)
        params_present(group, config_list)
        if "log" in parsed_steps:
          connection.exec_command(session, "chown " + 
                                config_list[owner] + ":" + 
                                config_list[group] + " " + 
                                config_list[dst_location],
                                log=True)
        else:
          connection.exec_command(session, "chown " + 
                                  config_list[owner] + ":" + 
                                  config_list[group] + " " + 
                                  config_list[dst_location])
      else:
        print("ERROR: both owner and group are needed for file metadata")
        sys.exit()
      if "mode" in metadata:
        mode = check_env_var(metadata["mode"])
        params_present(mode, config_list)
        print("Updating the mode of " + config_list[dst_location] + " to: " + str(config_list[mode]))
        if "log" in parsed_steps:
          connection.exec_command(session, "chmod " + 
                                  str(config_list[mode]) + " " + 
                                  config_list[dst_location],
                                  log=True)
        else:
          connection.exec_command(session, "chmod " + 
                                  str(config_list[mode]) + " " + 
                                  config_list[dst_location])
    if "restart" in parsed_steps:
      service = check_env_var(parsed_steps["restart"])
      params_present(service, config_list)
      if "log" in parsed_steps:
        restart_service(connection, session, config_list[service], log=True)
      else:
        restart_service(connection, session, config_list[service])
  else:
    print("ERROR: src or dst location are not properly set")
    sys.exit()

# Used to print an ASCII banner for Aurora
ascii_banner = pyfiglet.figlet_format("Aurora")
print("*"*50)
print("*"*50 + "\n")
print(ascii_banner)

if len(sys.argv) < 3:
   print('ERROR: no arguments passed')
   sys.exit()

step_file = "../steps/" + sys.argv[1]
config_file = "../environment/" + sys.argv[2]

print("*"*50)
print("*"*50 + "\n")

if os.path.exists(step_file) and os.path.exists(config_file):
  print("Configuration Step file and values file are valid")
else:
  print("ERROR: The step file and values file need to be checked")
  sys.exit()
  
print("Loading Config from: " + config_file + "\n")

# Read the configuration values like hosts, ssh params, etc
with open(config_file) as file:
  config_list = yaml.load(file, Loader=yaml.FullLoader)

print("*"*50 + "\n")
print("Config loaded successfully from: " + config_file + "\n")
print("*"*50)
print("*"*50 + "\n")
print("Loading step file from: " + step_file + "\n")

# Read the step file from the /steps dir
with open(step_file) as file:
    steps_list = yaml.load(file, Loader=yaml.FullLoader)

print("Step file loaded successfully from: " + step_file + "\n")
print("*"*50 + "\n")
if "name" in steps_list[0]:
  print("Starting Steps for: " + steps_list[0]["name"] + "\n")
else:
  print("ERROR: name needs to be specified for the starting block")
  sys.exit()
print("*"*50)

# Verify that the hosts and ssh related params are specified 
# and are not null
if "hosts" in steps_list[0] and "remote_user" in steps_list[0] and "pwd" in steps_list[0]:
  hosts = check_env_var(steps_list[0]["hosts"])
  user = check_env_var(steps_list[0]["remote_user"])
  pwd = check_env_var(steps_list[0]["pwd"])
  params_present(hosts, config_list)
  params_present(user, config_list)
  params_present(pwd, config_list)
  if type(config_list[hosts]) == list:
    for host in config_list[hosts]:
      connection = SSHClient(host, config_list[user], config_list[pwd])
      session = connection.connect()
      print("*"*50 + "\n")
      for task in steps_list[0]["tasks"]:
        if "name" in task:
          print("Currently executing: " + task["name"] + "\n")
          if "install" in task:
            manage_dependencies(connection, session, task["install"], config_list, install=True)
          if "uninstall" in task:
            manage_dependencies(connection, session, task["uninstall"], config_list, install=False)
          if "sftp" in task:
            transfer_file(connection, session, task["sftp"], config_list)
        else:
          print("ERROR: name needs to be specified for all tasks")
          sys.exit()
  else:
    print("ERROR: hosts needs to be of type list but is of type", type(config_list[hosts]))
    sys.exit()