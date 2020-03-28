#   Copyright (c) 2020 Kurt Jacobson
#      <kurtcjacobson@gmail.com>
#
#   This file is part of QtPyVCP.
#
#   QtPyVCP is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 2 of the License, or
#   (at your option) any later version.
#
#   QtPyVCP is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with QtPyVCP.  If not, see <http://www.gnu.org/licenses/>.
import datetime
import logging

from opcua import Server, ua
from opcua.common.events import Event

# from IPython import embed

from qtpyvcp import PLUGINS
from qtpyvcp.plugins import DataPlugin
from qtpyvcp.utilities.logger import getLogger

LOG = getLogger(__name__)


class OpcUA(DataPlugin):
    def __init__(self):
        super(OpcUA, self).__init__()

        # https://github.com/FreeOpcUa/freeopcua/blob/master/python/examples/server.py

        # setup our server
        self.server = Server()

        address = '0.0.0.0'
        port = 4840

        self.endpoint = "opc.tcp://{}:{}/qtpyvcp/server/".format(address, port)

        self.server.set_endpoint(self.endpoint)

        self.server.set_server_name("QtPyVCP OpcUa Server")

        # setup our own namespace, not really necessary but should as spec
        uri = "http://qtpyvcp.com/"
        self.idx = self.server.register_namespace(uri)

        # get Objects node, this is where we should put our nodes
        self.objects = self.server.get_objects_node()

        opc_ua_objects = dict()

        LOG.debug("objects folder: {}".format(self.objects))

        for name, obj in PLUGINS.items():
            opc_ua_objects[name] = self.objects.add_folder(self.idx, name)
            for chan_name, chan_obj in obj.channels.items():
                if isinstance(chan_obj.value, datetime.datetime):
                    opc_ua_objects[name].add_variable(self.idx, chan_name, chan_obj.value)
                elif isinstance(chan_obj.value, int):
                    opc_ua_objects[name].add_variable(self.idx, chan_name, chan_obj.value)
                elif isinstance(chan_obj.value, float):
                    opc_ua_objects[name].add_variable(self.idx, chan_name, chan_obj.value, ua.VariantType.Float)
                elif isinstance(chan_obj.value, list) or isinstance(chan_obj.value, tuple):
                    print("LIST OR TUPLE", chan_name)
                    folder = opc_ua_objects[name].add_folder(self.idx, chan_name)
                    for index, val in enumerate(chan_obj.value):
                        print(chan_obj.value)
                        if isinstance(chan_obj.value, int):
                            folder.add_variable(self.idx, "{}.{}".format(chan_name, index), chan_obj.value)
                        elif isinstance(chan_obj.value, float):
                            folder.add_variable(self.idx, "{}.{}".format(chan_name, index), chan_obj.value, ua.VariantType.Float)

                # myprop = opc_ua_objects[name].add_property(idx, "myprop", 9.9)
                # myfolder = opc_ua_objects[name].add_folder(idx, "myfolder")

        # uncomment next lines to subscribe to changes on server side
        # sclt = SubHandler()
        # sub = server.create_subscription(100, sclt)
        # handle = sub.subscribe_data_change(myvar) #keep handle if you want to delete the particular subscription later

        ev = Event()        # start ipython shell so users can test things
        # embed()

    def initialise(self):
        # optional: setup logging
        logging.basicConfig(level=logging.WARN)
        logger = logging.getLogger("opcua.address_space")
        logger.setLevel(logging.DEBUG)
        logger = logging.getLogger("opcua.internal_server")
        logger.setLevel(logging.DEBUG)
        logger = logging.getLogger("opcua.binary_server_asyncio")
        logger.setLevel(logging.DEBUG)
        logger = logging.getLogger("opcua.uaprocessor")
        logger.setLevel(logging.DEBUG)

        LOG.debug("Starting OPC UA server at: %s", self.endpoint)
        self.server.start()

    def terminate(self):
        LOG.debug("Stopping OPC UA server...")
        self.server.stop()