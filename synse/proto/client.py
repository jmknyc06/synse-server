"""Synse Server python client for communicating to plugins via the gRPC API.
"""

import os

import grpc
from synse_plugin import api as synse_api
from synse_plugin import grpc as synse_grpc

from synse.const import BG_SOCKS
from synse.log import logger


class WriteData(object):
    """The WriteData object is a convenient way to group together
    write actions and raw data into a single bundle for a single write
    transaction.

    Multiple WriteData can be specified for a gRPC Write command, e.g.
    it may be the case for an LED that we want to turn it on and change
    the color simultaneously. This can be done with two WriteData objects
    passed in a list to the `SynseInternalClient.write` method, e.g.

      color = WriteData(action='color', raw=[b'ffffff'])
      state = WriteData(action='on')
    """

    def __init__(self, action=None, raw=None):
        """Constructor for the WriteData object.

        Args:
            action (str): The action string for the write.
            raw (list[bytes]): A list of bytes that constitute the raw data
                that will be written by the write request.
        """
        self.action = action if action is not None else ''
        self.raw = raw if raw is not None else []

    def to_grpc(self):
        """Convert the WriteData model into the gRPC model for WriteData.

        Returns:
            synse_plugin.api.WriteData: The gRPC model of the WriteData object.
        """
        return synse_api.WriteData(
            action=self.action,
            raw=self.raw
        )


class SynseInternalClient(object):
    """The `SynseInternalClient` object is a convenience wrapper around a
    grpc client used for communication between Synse and the background
    processes which are its data sources.

    There should be one instance of the `SynseInternalClient` for every
    configured background process.
    """

    _client_stubs = {}

    def __init__(self, name, address, mode):
        """Constructor for a `SynseInternalClient` instance.
        """
        self.name = name
        self.addr = address
        self.mode = mode

        self.channel = self._channel()
        self.stub = self._stub()

        # add it to the tracked stubs
        SynseInternalClient._client_stubs[self.name] = self

    def _channel(self):
        """Convenience method to create the client grpc channel."""
        if self.mode == 'unix':
            target = 'unix:{}'.format(os.path.join(BG_SOCKS, self.name + '.sock'))
        elif self.mode == 'tcp':
            target = self.addr
        else:
            raise ValueError('Invalid mode: {}'.format(self.mode))

        return grpc.insecure_channel(target)

    def _stub(self):
        """Convenience method to create the grpc stub."""
        return synse_grpc.InternalApiStub(self.channel)

    @classmethod
    def get_client(cls, name):
        """Get a client instance for the given name.

        Args:
            name (str): The name of the client. This is also the name
                given to the background process socket.

        Returns:
            SynseInternalClient: The client instance associated with
                the given name.
            None: The given name has no associated client.
        """
        return cls._client_stubs.get(name)

    @classmethod
    def register(cls, name, addr, mode):
        """Register a new client instance.

        Args:
            name (str): The name of the plugin for the client.
            addr (str): The address the plugin will communicate over.
            mode (str): The communication mode of the plugin (either
                'tcp' or 'unix').

        Returns:
            SynseInternalClient: The newly registered client instance.
        """
        SynseInternalClient(name, addr, mode)
        cli = cls._client_stubs[name]

        logger.debug('Registered Client:')
        logger.debug('  name:    {}'.format(cli.name))
        logger.debug('  mode:    {}'.format(cli.mode))
        logger.debug('  address: {}'.format(cli.addr))
        logger.debug('  channel: {}'.format(cli.channel))
        logger.debug('  stub:    {}'.format(cli.stub))
        return cli

    def read(self, rack, board, device):
        """Get a reading from the specified device.

        Args:
            rack (str): The rack which the device resides on.
            board (str): The board which the device resides on.
            device (str): The identifier for the device to read.

        Returns:
            list[synse_plugin.api.ReadResponse]: The reading responses for the
                specified device, if it exists.
        """
        req = synse_api.ReadRequest(
            device=device,
            board=board,
            rack=rack
        )

        resp = []
        for r in self.stub.Read(req):
            resp.append(r)

        return resp

    def metainfo(self, rack=None, board=None):
        """Get all meta-information from a plugin.

        Args:
            rack (str): The rack to filter by.
            board (str): The board to filter by.

        Returns:
            list[synse_plugin.api.MetainfoResponse]: All device meta-information
                provided by the plugin.
        """
        # if the rack or board is not specified, pass it through as an
        # empty string.
        rack = rack if rack is not None else ''
        board = board if board is not None else ''

        req = synse_api.MetainfoRequest(
            rack=rack,
            board=board
        )

        resp = []
        for r in self.stub.Metainfo(req):
            resp.append(r)

        return resp

    def write(self, rack, board, device, data):
        """Write data to the specified device.

        Args:
            rack (str): The rack which the device resides on.
            board (str): The board which the device resides on.
            device (str): The identifier for the device to write to.
            data (list[WriteData]): The data to write to the device.

        Returns:
            synse_plugin.api.Transactions: The transactions that can be used
                to track the given write request(s).
        """
        req = synse_api.WriteRequest(
            device=device,
            board=board,
            rack=rack,
            data=[d.to_grpc() for d in data]
        )

        resp = self.stub.Write(req)
        return resp

    def check_transaction(self, transaction_id):
        """Check the state of a write transaction.

        Args:
            transaction_id (str): The ID of the transaction to check.

        Returns:
            synse_plugin.api.WriteResponse: The WriteResponse detailing the
                status and state of the given write transaction.
        """
        req = synse_api.TransactionId(
            id=transaction_id
        )

        resp = self.stub.TransactionCheck(req)
        return resp


def get_client(name):
    """Get the internal client for the given process name.

    This is a convenience module-level wrapper around the
    `SynseInternalClient.get_client` method.

    Args:
        name (str): The name of the client. This is also the name
            given to the background process socket.

    Returns:
        SynseInternalClient: The client instance associated with
            that name. If a client does not exist for the given name,
            a new one will be created.
    """
    return SynseInternalClient.get_client(name)


def register_client(name, addr, mode):
    """Register a new internal client for a plugin.

    Args:
        name (str): The name of the plugin.
        addr (str): The address which the plugin communicates over.
        mode (str): The communication mode of the plugin (either
            'unix' or 'tcp').

    Returns:
        SynseInternalClient: The client instance associated with the
            name given. If a client does not exist for the given name,
            a new one will be created.
    """
    cli = SynseInternalClient.get_client(name)
    if cli is None:
        cli = SynseInternalClient.register(name, addr, mode)
    return cli