try:
    import rsa
    uses_RSA = True
    decryption_error = rsa.pkcs1.DecryptionError
except:
    try:
        from Crypto.PublicKey import RSA
        uses_RSA = False

        class DecryptionError(Exception): pass

        decryption_error = DecryptionError("Decryption failed")

    except:
        raise ImportError("You cannot use this without the rsa or PyCrypto module. To install this, run 'pip install rsa'.")

import socket

key_request = "Requesting key".encode('utf-8')
size_request = "Requesting key size".encode('utf-8')
end_of_message = '\x03\x04\x17\x04\x03'.encode('utf-8')  # For the ASCII nerds, that's:
                                                         # End of text, End of tx, End of tx block, End of tx, End of text

if uses_RSA:
    """If we're using the rsa module, just map these methods from rsa"""
    newkeys   = rsa.newkeys
    encrypt   = rsa.encrypt
    decrypt   = rsa.decrypt
    sign      = rsa.sign
    verify    = rsa.verify
    PublicKey = rsa.PublicKey
else:

    from Crypto.Hash import MD5, SHA, SHA256, SHA384, SHA512
    """The following table is to make choosing a hash easier"""
    hashtable = {'MD5': MD5,
                 'SHA-1': SHA,
                 'SHA-256': SHA256,
                 'SHA-384': SHA384,
                 'SHA-512': SHA512}


    def newkeys(size):
        """Wrapper for PyCrypto RSA key generation, to better match rsa's method"""
        from Crypto import Random
        from Crypto.PublicKey import RSA
        random_generator = Random.new().read
        key = RSA.generate(size, random_generator)
        return key.publickey(), key

    
    def encrypt(msg, key):
        """Wrapper for PyCrypto RSA encryption method, to better match rsa's method"""
        from Crypto.Cipher.PKCS1_v1_5 import PKCS115_Cipher
        return PKCS115_Cipher(key).encrypt(msg)


    def decrypt(msg, key):
        """Wrapper for PyCrypto RSA decryption method, to better match rsa's method"""
        from Crypto.Cipher.PKCS1_v1_5 import PKCS115_Cipher
        return PKCS115_Cipher(key).decrypt(msg, decryption_error)


    def sign(msg, key, hashop):
        """Wrapper for PyCrypto RSA signing method, to better match rsa's method"""
        from Crypto.Signature import PKCS1_v1_5
        hsh = hashtable.get(hashop).new()
        hsh.update(msg)
        signer = PKCS1_v1_5.PKCS115_SigScheme(key)
        return signer.sign(hsh)


    def verify(msg, sig, key):
        """Wrapper for PyCrypto RSA signature verification, to better match rsa's method"""
        from Crypto.Signature import PKCS1_v1_5
        for hashop in ['SHA-256', 'MD5', 'SHA-1', 'SHA-384', 'SHA-512']:
            hsh = hashtable.get(hashop).new()
            hsh.update(msg)
            check = PKCS1_v1_5.PKCS115_SigScheme(key)
            res = check.verify(hsh, sig)
            if res:
                break
        return res
        

    def PublicKey(n, e):
        """Wrapper for PyCrypto RSA key constructor, to better match rsa's method"""
        return RSA.construct((long(n), long(e)))


class secureSocket(socket.socket):
    """An RSA encrypted and secured socket. Requires either the rsa or PyCrypto module"""
    def __init__(self, sock_family=socket.AF_INET, sock_type=socket.SOCK_STREAM, keysize=1024, suppress_warnings=False):
        super(secureSocket, self).__init__(sock_family, sock_type)
        if not suppress_warnings:
            if (keysize / 8) - 11 < len(end_of_message):
                raise ValueError('This key is too small to be useful')
            elif keysize > 8192:
                raise ValueError('This key is too large to be practical. Sending is easy. Generating is hard.')
        from multiprocessing.pool import ThreadPool as Pool
        self.key_async = Pool().map_async(newkeys, [keysize])  # Gen in background to reduce block
        self.pub, self.priv = None, None    # Temporarily set to None so they can generate in background
        self.keysize = keysize
        self.msgsize = (keysize // 8) - 11
        self.key = None
        self.peer_keysize = None
        self.peer_msgsize = None
        self.buffer = ""
        from functools import partial
        import sys
        if sys.version_info[0] < 3:
            self.__recv = self._sock.recv
        else:
            self.__recv = super(secureSocket, self).recv
        self.send = partial(secureSocket.send, self)
        self.sendall = self.send
        self.recv = partial(secureSocket.recv, self)
        self.dup = partial(secureSocket.dup, self)

    def dup(self, conn=None):
        """Duplicates this secureSocket, with all key information, connected to the same peer"""
        sock = secureSocket(self.family, self.type)
        if not conn:
            sock._sock = socket.socket.dup(self)
        else:
            sock._sock = conn
        sock.pub, sock.priv = self.pub, self.priv
        sock.keysize = self.keysize
        sock.msgsize = self.msgsize
        sock.key = self.key
        sock.peer_keysize = self.peer_keysize
        sock.peer_msgsize = self.peer_msgsize
        sock.buffer = self.buffer
        from functools import partial
        import sys
        if sys.version_info[0] < 3:
            sock.__recv = sock._sock.recv
        else:
            sock.__recv == super(secureSocket, self).recv
        sock.send = partial(secureSocket.send, sock)
        sock.sendall = sock.send
        sock.recv = partial(secureSocket.recv, sock)
        sock.dup = partial(secureSocket.dup, sock)
        return sock

    def mapKey(self):
        """Deals with the asyncronous generation of keys"""
        if self.pub is None:
            self.pub, self.priv = self.key_async.get()[0]
            del self.key_async

    def accept(self):
        """Accepts an incoming connection.
        Like a native socket, it returns a copy of the socket and the connected address"""
        conn, self.addr = super(secureSocket, self).accept()
        sock = self.dup(conn=conn)
        sock.sendKey()
        sock.requestKey()
        return sock, self.addr

    def connect(self, ip):
        """Connects to another secureSocket"""
        super(secureSocket, self).connect(ip)
        self.requestKey()
        self.sendKey()

    def close(self):
        """Closes your connection to another socket, then cleans up metadata"""
        super(secureSocket, self).close()
        self.key = None
        self.peer_keysize = None
        self.peer_msgsize = None

    def send(self, msg):
        """Sends an encrypted copy of your message, and a signed+encrypted copy"""
        self.__send__(msg)
        self.__send__(self.sign(msg))

    def recv(self, size=None):
        """Receives and decrypts a message, then verifies it against the attached signature"""
        if self.buffer != "":
            if size:
                msg = self.buffer[:size]
                self.buffer = self.buffer[size:]
            else:
                msg = self.buffer
                self.buffer = ""
            return msg
        msg = self.__recv__()
        try:
            self.verify(msg, self.__recv__())
        except Exception as error:
            if uses_RSA and type(error) == rsa.pkcs1.VerificationError:
                print(msg)
            else:
                raise error
        if not size:
            return msg
        else:
            self.buffer += msg
            ret = self.buffer[:size]
            self.buffer = self.buffer[size:]
            return ret

    def sign(self, msg, hashop='best'):
        """Signs a message with a given hash, or self-determined one"""
        msg = msg.encode()
        self.mapKey()
        if hashop != 'best':
            return sign(msg, self.priv, hashop)
        elif self.keysize >= 752:
            return sign(msg, self.priv, 'SHA-512')
        elif self.keysize >= 624:
            return sign(msg, self.priv, 'SHA-384')
        elif self.keysize >= 496:
            return sign(msg, self.priv, 'SHA-256')
        elif self.keysize >= 368:
            return sign(msg, self.priv, 'SHA-1')
        else:   # if self.keysize < 360: raises OverflowError
            return sign(msg, self.priv, 'MD5')

    def verify(self, msg, sig, key=None):
        """Verifies a message with a given key (Default: your peer's)"""
        if key is None:
            key = self.key
        return verify(msg, sig, key)

    def __send__(self, msg):
        """Base method for sending a message. Encrypts and sends"""
        if not isinstance(msg, type("a".encode('utf-8'))):
            msg = str(msg).encode('utf-8')
        x = 0
        while x < len(msg) - self.peer_msgsize:
            super(secureSocket, self).sendall(encrypt(msg[x:x+self.peer_msgsize], self.key))
            x += self.peer_msgsize
        super(secureSocket, self).sendall(encrypt(msg[x:], self.key))
        super(secureSocket, self).sendall(encrypt(end_of_message, self.key))

    def __recv__(self):
        """Base method for receiving a message. Receives and decrypts."""
        received = "".encode('utf-8')
        packet = ""
        try:
            while True:
                packet = self.__recv(self.msgsize + 11)
                packet = decrypt(packet, self.priv)
                if packet == end_of_message:
                    return received
                received += packet
        except decryption_error:
            print("Decryption error---Content: " + repr(packet))
            raise decryption_error
        except ValueError as error:
            if error.args[0] == "invalid literal for int() with base 16: ''":
                return 0
            else:
                raise error

    def requestKey(self):
        """Requests your peer's key over plaintext"""
        while True:
            print("Requesting key size")
            super(secureSocket, self).sendall(size_request)
            try:
                self.peer_keysize = int(self.__recv(16))
                self.peer_msgsize = (self.peer_keysize // 8) - 11
                print("Requesting key")
                super(secureSocket, self).sendall(key_request)
                keys = self.__recv(self.peer_keysize)
                if isinstance(keys, type(b'')):
                    keys = keys.decode()
                key = keys.split(",")
                self.key = PublicKey(int(key[0]), int(key[1]))
                print("Key received")
                break
            except EOFError:
                continue
    
    def sendKey(self):
        """Sends your key over plaintext"""
        self.mapKey()
        req = self.__recv(len(size_request))
        if req != size_request:
            raise ValueError("Handshake has failed due to invalid request from peer: %s" % req)
        print("Sending key size")
        super(secureSocket, self).sendall(str(self.keysize).encode("utf-8"))
        req = self.__recv(len(key_request))
        if req != key_request:
            raise ValueError("Handshake has failed due to invalid request from peer")
        print("Sending key")
        super(secureSocket, self).sendall((str(self.pub.n) + "," + str(self.pub.e)).encode('utf-8'))
