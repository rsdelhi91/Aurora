# import paramiko

# ssh = paramiko.SSHClient()
# ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
# a = ssh.connect(hostname = hostname, username = user, password = password, timeout = 5000)

# command = "ls"

# try:
#     ssh.connect(hostname = hostname, username = user, password = password, timeout = 5000)
# except paramiko.AuthenticationException:
#     print("Authentication failed, please verify your credential")
# except paramiko.SSHException:
#     print("Could not establish SSH connection: %s" % paramiko.SSHException)
# except Exception as TimeoutError:
#     print("Unable to connect, please verify network connectivity")
# except socket.timeout as e:
#     print("Connection got timed out")
# else:
#     print('SSH is successful to device ' + hostname)
#     stdin, stdout, stderr = ssh.exec_command(command, timeout=10)
#     ssh.ssh_output = stdout.readlines()
#     ssh.ssh_error = stderr.readlines()
#     if ssh.ssh_error:
#         print("Problem occurred while running command:" + command + " The error is " + ssh.ssh_error)
#     else:
#         print("Command execution completed successfully")
#         print('\n'.join(ssh.ssh_output))


import paramiko
import socket

class SSHClient:
  def __init__(self, hostname, username, password):
    self.hostname = hostname
    self.username = username
    self.password = password

  def connect(self):
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
    print("SFTP file: " + src_location + " to " + dst_location)
    sftp = ssh.open_sftp()
    sftp.put(src_location, dst_location)