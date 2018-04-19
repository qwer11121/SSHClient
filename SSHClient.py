import paramiko, time, re, keyring

class SSHClient:
    """
    This class create a workspace to remote host, allow user to run commands

    ANSI data in output have been filted.

    Sample:
    client=SSHClient("HOSTNAME",username="USERNAME",password="PASSWORD")
    output = client.SendCommand("COMMAND")[1]
    """

    ANSI_regex=r'(\x1b[^m]*(m|K)|\x0f)'
    Print = False
    Timeout=5000
    BufferSize=9999
    
    def __init__(self, hostname, username, password=None, keyfile=None, keypass=None, Print=False):
        """
        Create a workspace for future commands

        :param hostname: the hostname or ip to be connected
        :param username: user name
        :param password: password for user
        :param keyfile: if use key file for authentication, spacify key file location
        :param keypass: password of key file
        :param Print: True to print output in console
        :type hostname: string
        :type username: string
        :type password: string
        :type keyfile: string
        :type keypass: string
        :type Print: bool       

        .. note:: to use key file authentication, password must be None
        """
        self.Print=Print
        self.ssh=paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)
        if keyfile is None:
            # password authentication
            self.ssh.connect(hostname, username=username, password=password)
        else:
            # RSA key file authentication
            self.key=paramiko.rsakey.RSAKey.from_private_key_file(keyfile,keypass)        
            self.ssh.connect(hostname,username=username,pkey=self.key)
        self.__CreateWorkspace()
        

    def __CreateWorkspace(self):
        self.channel=self.ssh.invoke_shell()
        out,prompt = self.__Receive()
        if self.Print:
            print(prompt,end='')

    def SendCommand(self, command):
        """
        Execute a command and return result

        :param command: command to be executed
        :returns: command, output, new prompt
        :rtype: string list
        """
        self.channel.send(command+"\n")
        output, prompt = self.__Receive()
        if self.Print:
            print(command)
            if output != "":
                print(output)
            print(prompt,end='')
        return command, output, prompt

    def __Receive(self):
        timer=0
        while not self.channel.recv_ready():
            time.sleep(0.1)
            timer+=1
            if timer > self.Timeout/100:
                return "", "time out"
        data = self.channel.recv(self.BufferSize)
        lines=data.split(b'\r\n')
        output=""
        for line in lines[1:-1]:
            output+=re.compile(self.ANSI_regex).sub('', line.decode("utf-8"))+'\r\n'
        prompt=re.compile(self.ANSI_regex).sub('', lines[-1].decode("utf-8"))
        return output, prompt

