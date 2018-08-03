import socket
import threading
import signal
import time
import sys
import os


config =  {
            "HOST_NAME" : "127.0.0.1",
            "BIND_PORT" : 12345,
            "MAX_REQUEST_LEN" : 1024,
            "CONNECTION_TIMEOUT" : 5
          }


class Server:
    """ The server class """

    def __init__(self, config):
        signal.signal(signal.SIGINT, self.shutdown)     # Shutdown on Ctrl+C
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)             # Create a TCP socket
        self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)    # Re-use the socket
        self.serverSocket.bind((config['HOST_NAME'], config['BIND_PORT'])) # bind the socket to a public host, and a port
        self.serverSocket.listen(10)    # become a server socket
        self.__clients = {}


    def listenForClient(self):
        """ Wait for clients to connect """
        while True:
            (clientSocket, client_address) = self.serverSocket.accept()   # Establish the connection
            self.proxy_thread(clientSocket, client_address)
        self.shutdown(0,0)


    def proxy_thread(self, conn, client_addr):
        """
        *******************************************
        *********** PROXY_THREAD FUNC *************
          A thread to handle request from browser
        *******************************************
        """
        if (os.path.isdir('./cache')):
         print 'ifsdas'
        else:
            # print 'else' 
            os.mkdir('./cache', 0755)
        request = conn.recv(config['MAX_REQUEST_LEN'])        # get the request from browser
        # print 'earlier' + request
        lines = request.split('\n')
        first_line = request.split('\n')[0]                   # parse the first line
        first_line  = first_line.split(' ')
        url = first_line[1]                        # get url

        # find the webserver and port
        http_pos = url.find("://")          # find pos of ://
        if (http_pos==-1):
            temp = url
        else:
            temp = url[(http_pos+3):]       # get the rest of url

        port_pos = temp.find(":")           # find the port pos (if any)

        # find end of web server
        webserver_pos = temp.find("/")
        if webserver_pos == -1:
            webserver_pos = len(temp)
        first_line[1] = temp[webserver_pos:]
        first_line = ' '.join(first_line) 
        webserver = ""
        port = -1
        if (port_pos==-1 or webserver_pos < port_pos):      # default port
            port = 80
            webserver = temp[:webserver_pos]
        else:                                               # specific port
            port = int((temp[(port_pos+1):])[:webserver_pos-port_pos-1])
            webserver = temp[:port_pos]
        # print '\n' + 'webserver and port are ' + str(webserver),str(port) + '\n'
        
        lines[0] =  first_line
        request = '\n'.join(lines) + '\r\n\r\n'
        request1 = '\n'.join(lines)
        request1 = request1.rstrip()
        request1 = request1 + '\n'+'If-Modified-Since: '
       
        line1 = request.split('\n')[0]
        
        # print line1
        slashpos = line1.find('/')
        slashf = line1[slashpos+1:]
        print 'slashf ' + slashf
        filel = slashf.find(' ')
        print 'filel '+str(filel)
        # print slashf
        filename = slashf[:filel]
        filepath = './cache/' + filename
        print 'filepath ' + filepath
        print 'haha ' + filename
        if len(filename)!=0:
            numberOfFiles = 0
            for filecache in os.listdir('./cache'):
                numberOfFiles = numberOfFiles + 1
            print '########################################'
            print 'if'
            count = 0
            filefound = 0
            for filecache in os.listdir('./cache'):  #file checking in cache
                count = count + 1
                print 'dir ' + filecache + '\n'
                print 'file ' + filename + '\n'
                if filecache == filename:
                    filefound = 1
                    print 'found'
                    last_mtime = time.strptime(time.ctime(os.path.getmtime(filepath)), "%a %b %d %H:%M:%S %Y")
                    header = time.strftime("%a %b %d %H:%M:%S %Y", last_mtime)
                    print 'sdfdsfdsfsdfsdf'
                    print header
                    print 'header ended'    
                    request1 += header
                    request1 += '\r\n\r\n'
                    print('########################################')
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(config['CONNECTION_TIMEOUT'])
                    s.connect((webserver, port))
                    print(request1)
                    s.sendall(request1)
                    data = s.recv(config['MAX_REQUEST_LEN'])
                    print data
                    if '304 Not Modified' in data:
                        f = open(filepath)
                        while 1:
                            l = f.readline()
                            print 'inside while'
                            if not l:
                                break
                            else:
                                conn.send(l)
                        f.close()            
                    else:
                        conn.send(data)
                        f= open(filepath,"wb")
                        while 1:
                            data = s.recv(config['MAX_REQUEST_LEN'])          # receive data from web server
                            if len(data):   
                                f.write(data)
                                conn.send(data)                               # send to browser
                            else:
                                break
                        f.close()       
                    print 'final request1'
                      
            if filefound == 0 or count == 0:
                
                f= open(filepath,"wb")
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(config['CONNECTION_TIMEOUT'])
                s.connect((webserver, port))
                s.sendall(request)                           # send request to webserver
                cacheflag = 0
                while 1:
                    data = s.recv(config['MAX_REQUEST_LEN'])          # receive data from web server
                    # print data
                    if 'no-cache' in data:
                        cacheflag = 1
                    if len(data):
                        f.write(data)
                        conn.send(data)                               # send to browser
                    else:
                        break
                s.close()
                f.close()
                if cacheflag == 1:
                    os.remove('./cache/' + filename)
                numberOfFiles = 0
                for filecache in os.listdir('./cache'):
                    numberOfFiles = numberOfFiles + 1
                if(numberOfFiles>3):
                    c = 0
                    for filecache in os.listdir('./cache'):
                        if c == 0:
                            minf = filecache
                            mint = os.path.getmtime('./cache/' + filecache)
                        cft = os.path.getmtime('./cache/' + filecache)
                        c = c+1
                    if cft < mint:
                        mint = cft
                        minf = filecache
                    os.remove('./cache/' + minf)

                    
        # print 'hahahahaha  ' + filename + '\n' 
        # print 'later' + request
        else:
            try:
                # create a socket to connect to the web server
                print '*************************************************'
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(config['CONNECTION_TIMEOUT'])
                s.connect((webserver, port))
                s.sendall(request)                           # send request to webserver

                while 1:
                    data = s.recv(config['MAX_REQUEST_LEN'])          # receive data from web server
                    if len(data):
                        conn.send(data)                               # send to browser
                    else:
                        break
                s.close()
                conn.close()

            except socket.error as error_msg:
                print 'ERROR: ',client_addr,error_msg
                if s:
                    s.close()
                if conn:
                    conn.close()


    def shutdown(self, signum, frame):
        """ Handle the exiting server. Clean all traces """
        self.serverSocket.close()
        sys.exit(0)


if __name__ == "__main__":
    
    server = Server(config)
    server.listenForClient()
