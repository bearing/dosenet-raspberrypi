from kromek import Message


class Connection(object):
    def send(self, message):
        """
        Write a message using the transport
        :param message:
        :return:
        """
        return self._send(message)

    def recv(self, message=None):
        """
        Receive a message using the transport
        :param message:
        :return:
        """
        if message is None:
            message = Message()
        self._recv(message)
        return message

    def close(self):
        """
        Close this connection
        """
        pass

    def _send(self, message):
        pass

    def _recv(self, message):
        pass

    def __del__(self):
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class Transport(object):
    """
    A thing that can talk over a given transport
    """

    def discover(self):
        """
        :return: A set of devices using this transport
        """
        return []

    def connect(self, device):
        """
        :param device:
        :return: a connection for a device
        """
        pass
