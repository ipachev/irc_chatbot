import socket


class Channel:
    def __init__(self, server, channel):
        self.server = server
        self.channel = channel
        self.irc_sock = None
        self.readbuffer = ""
        self.message_callbacks = []
        self.users = set()

    def connect(self, name):
        if self.irc_sock is None:
            self.irc_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.irc_sock.connect((self.server, 6667))
            user_str = "USER " + name + " " + name + " " + name + " : The best NLP bot\n"
            self.irc_sock.send(bytes(user_str, "UTF-8"))
            nickname_str = "NICK " + name + "\n"
            self.irc_sock.send(bytes(nickname_str, "UTF-8"))
            join_ch_str = "JOIN " + self.channel + "\n"
            self.irc_sock.send(bytes(join_ch_str, "UTF-8"))
            print("CONNECTED")
        else:
            print("Already connected")

    def disconnect(self):
        self.irc_sock.close()

    def add_message_callback(self, callback):
        self.message_callbacks.append(callback)

    def handle_ping(self, line):
        self.irc_sock.send(bytes("PONG %s\r\n" % line[1], "UTF-8"))

    def handle_privmsg(self, line):
        sender = line[0].split("!")[0].lstrip(":")
        print("got message from", sender)
        size = len(line)
        i = 3
        message = ""
        print("line:", line)
        while (i < size):
            message += line[i] + " "
            i = i + 1
        message = message.lstrip(":").rstrip(" ")
        for cb in self.message_callbacks:
            cb(message, sender)

    def handle_user_join(self, line):
        user = line[0].split("!")[0].lstrip(":")
        self.users.add(user)
        print("new user joined:", user, "user list:", self.users)

    def handle_user_left(self, line):
        user = line[0].split("!")[0].lstrip(":")
        self.users.remove(user)
        print("user left:", user, "user list:", self.users)

    def handle_user_list(self, line):
        for name in line[5:]:
            clean_name = name.lstrip(":@")
            self.users.add(clean_name)
        print("got user list:", self.users)

    def send_message(self, msg):
        msg = 'PRIVMSG ' + self.channel + ' :' + msg + '\r\n'
        self.irc_sock.send(bytes(msg, "UTF-8"))

    def recieve_message(self):
        self.readbuffer = self.readbuffer + self.irc_sock.recv(1024).decode("UTF-8")
        temp = self.readbuffer.split("\n")
        self.readbuffer = temp.pop()
        for line in temp:
            line = line.rstrip()
            line = line.split()
            if line[0] == "PING":
                self.handle_ping(line)
            elif line[1] == "PRIVMSG":
                self.handle_privmsg(line)
            elif line[1] == "JOIN":
                self.handle_user_join(line)
            elif line[1] == "QUIT":
                self.handle_user_left(line)
            elif line[1] == "353":
                self.handle_user_list(line)

    def run(self):
        while(True):
            self.recieve_message()
