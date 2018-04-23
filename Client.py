import paramiko, time, re, keyring

class SSHClient:
    """
    This class create a workspace to remote host, allow user to run commands.

    ANSI data in output have been removed.
    
    Attributes:
        Print: A boolean indicating if print output to console. Default: False
        Timeout: An integer indicating the timeout when receive data.  Default 5000ms
        BufferSize: An integer of bytes to be received at a time.  Default: 10240byte
    """

    __ANSI_regex = r'(\x1b[^m]*(m|K)|\x0f)'
    Print = False
    Timeout = 5000
    BufferSize = 10240
    
    def __init__(self, hostname, username, password=None, keyfile=None, keypass=None, Print=False):
        """
        Create a workspace to run commands.
        
        To use keyfile, password must be None.
        
        Args:
            hostname: the hostname or ip to be connected
            username: user name
            password: password for user
            keyfile: full path of key file
            keypass: password of key file
            Print: True to print output in console
        """
        self.Print = Print
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)
        if keyfile is None:
            self.ssh.connect(hostname, username = username, password = password)
        else:
            self.key = paramiko.rsakey.RSAKey.from_private_key_file(keyfile,keypass)        
            self.ssh.connect(hostname,username = username,pkey = self.key)
        self.__CreateWorkspace()
        
    def __CreateWorkspace(self):
        self.channel=self.ssh.invoke_shell()
        out,prompt = self.__Receive()
        if self.Print:
            print(prompt,end='')

    def Run(self, command):
        """
        Execute a command and return result

        Args:
            command: command to be executed
            
        Returns
            a list [command, output, new prompt]        
        """
        self.channel.send(command+"\n")
        output, prompt = self.__Receive()
        if self.Print:
            print(command)
            if output != "":
                print(output)
            print(prompt,end = '')
        return command, output, prompt

    def __Receive(self):
        timer = 0
        while not self.channel.recv_ready():
            time.sleep(0.1)
            timer += 1
            if timer > self.Timeout / 100:
                return "", "time out"
        data = self.channel.recv(self.BufferSize)
        lines = data.split(b'\r\n')
        output = []
        for line in lines[1:-1]:
            output.append(re.compile(self.__ANSI_regex).sub('', line.decode("utf-8")))
        prompt = re.compile(self.__ANSI_regex).sub('', lines[-1].decode("utf-8"))
        output = '\r\n'.join(output)
        return output, prompt
