import paramiko, time, re, keyring

class SSHClient:
    ANSI_regex=r'(\x1b[^m]*(m|K)|\x0f)'
    Print = False
    
    def __init__(self, hostname, username, password, keyfile, keypass, Print=False):
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
        self.channel.send(command+"\n")
        output, prompt = self.__Receive()
        if self.Print:
            print(command)
            if output != "":
                print(output)
            print(prompt,end='')
        return command, output, prompt

    def __Receive(self, timeout=5000):
        timer=0
        while not self.channel.recv_ready():
            time.sleep(0.1)
            timer+=1
            #print(timer)
            if timer > timeout/100:
                return "", "time out"
        data = self.channel.recv(9999)
        lines=data.split(b'\r\n')
        output=""
        for line in lines[1:-1]:
            output=re.compile(self.ANSI_regex).sub('', line.decode("utf-8"))
            #print(output)
        prompt=re.compile(self.ANSI_regex).sub('', lines[-1].decode("utf-8"))
        #print(prompt, end="")
        return output, prompt

    