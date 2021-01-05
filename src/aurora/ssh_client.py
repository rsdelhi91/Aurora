""" Manage SSH connections and perform remote command executions

This file uses paramiko to create and maintain SSH connections 
with the specified remote hosts and provide an interface to run
remote shell command executions passed by the Aurora controller 
file.

It also performs SFTP to transfer files from the /files dir onto 
remote hosts.

Author: Rahul Sharma <sharma1@student.unimelb.edu.au>
"""

import paramiko
import socket

class SSHClient:

  def __init__(self, hostname, username, password):
    self.hostname = hostname
    self.username = username
    self.password = password

  def connect(self):
    """Create an SSH connection with the specified remote host
    """
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  
    try:
      ssh.connect(hostname = self.hostname, username = self.username, password = self.password, timeout = 50000)
    except paramiko.AuthenticationException:
      print("ERROR: Authentication failed, please verify your credential")
    except paramiko.SSHException:
      print("ERROR: Could not establish SSH connection: %s" % paramiko.SSHException)
    except Exception as TimeoutError:
      print("ERROR: Unable to connect, please verify network connectivity")
    except socket.timeout as e:
      print("Connection got timed out")
    else:
      print("\nSSH is successful to device " + self.hostname + "\n")
      return ssh

  def exec_command(self, ssh, command, log=False):
    """Run commands on a connected remote host

    variable inputs:
      ssh - the ssh session to the remote host
      command - the command that will be executed on the remote host
      log - enables verbose logging of steps executed. default is false.
    """
    print("Running command: " + command)
    stdin, stdout, stderr = ssh.exec_command(command, timeout=1000)
    ssh.ssh_output = stdout.readlines()
    ssh.ssh_error = stderr.readlines()
    if ssh.ssh_error:
      print("ERROR: Problem occurred while running command:" + command + " The error is " + str(ssh.ssh_error))
    else:
      print("Command execution completed successfully")
      if log:
        print('\n'.join(ssh.ssh_output))
    print("*"*50 + "\n")

  def sftp_file(self, ssh, src_location, dst_location):
    """Transfer files from the local /files dir to a remote host

    variable inputs:
      ssh - the ssh session to the remote host
      src_location - the local file in the /files dir
      dst_location - the dst path on the remote host
    """
    print("SFTP file: " + src_location + " to " + dst_location)
    sftp = ssh.open_sftp()
    sftp.put(src_location, dst_location)