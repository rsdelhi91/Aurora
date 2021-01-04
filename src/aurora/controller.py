# Dependency
# pip install pyyaml
# pip install -U PyYAML # Needs to be 5.1 or equivalent
# One that worked:
# sudo -H pip3 install --ignore-installed PyYAML
# pip install pyfiglet

import yaml, sys, pyfiglet
from ssh_client import *

ascii_banner = pyfiglet.figlet_format("Aurora")
print("*"*50)
print("*"*50 + "\n")
print(ascii_banner)

step_file = "../steps/" + sys.argv[1]
config_file = "../env/" + sys.argv[2]


# Check if hosts, user, and ssh_pwd are present
def params_present(param, parsed_config):
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


print("*"*50)
print("*"*50 + "\n")
print("Loading Config from: " + config_file + "\n")

# Read the initial configuration including hosts and ssh params
with open(config_file) as file:
  config_list = yaml.load(file, Loader=yaml.FullLoader)

def check_env_var(param):
  if param.startswith("{{") and len(param.split()) == 3:
    return param.split()[1]
  else:
    print("ERROR: " + param + " is not properly formatted")
    sys.exit()


# Installs packages on a standard debian image
def manage_dependencies(connection, session, parsed_steps, config_list, install):
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
      print("ERROR: packages need to be of type list but are of type:", type(config_list[packages]))
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
  if type(services) == list:
    for service in services:
      print("Restart the service: " + service)
      if log:
        connection.exec_command(session, "systemctl restart " + service, log=True)
      else:
        connection.exec_command(session, "systemctl restart " + service)
  else:
    print("ERROR: services is not of type list")
    sys.exit()

# If user is not root then chmod/chown to change ownership, group, and permissions
def transfer_file(connection, session, parsed_steps, config_list):
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
      

print("*"*50 + "\n")
print("Config loaded successfully from: " + config_file + "\n")
print("*"*50)
print("*"*50 + "\n")
print("Loading step file from: " + step_file + "\n")

# Read the setup steps
with open(step_file) as file:
    steps_list = yaml.load(file, Loader=yaml.FullLoader)

print("Step file loaded successfully from: " + step_file + "\n")
print("*"*50 + "\n")
print("Starting Steps for: " + steps_list[0]['name'] + "\n")
print("*"*50)


# Currently printing out all the steps parsed
# print(steps_list)

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
      # Iterate through all tasks one after the other
      for task in steps_list[0]["tasks"]:
        if "install" in task:
          manage_dependencies(connection, session, task["install"], config_list, install=True)
        if "uninstall" in task:
          manage_dependencies(connection, session, task["uninstall"], config_list, install=False)
        if "sftp" in task:
          transfer_file(connection, session, task["sftp"], config_list)
  else:
    print("ERROR: hosts needs to be of type list but is of type", type(config_list[hosts]))
    


# Include as a final test for validating imports from other file

# print("session is")
# print(session)
# print(connection.testme())

# Prints the length of the entries for the host YAML config mapping
#print(len(config_list["hosts"]))
# print("Hosts being configured: " + config_liststeps_list[0]['hosts'])

