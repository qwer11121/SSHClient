This is a simple interactive SSH client on Windows, based on paramiko.
Support password and key file authentication.

Sample:
client=SSHClient("HOSTNAME",username="USERNAME",password="PASSWORD")
output = client.Run("COMMAND")[1]
