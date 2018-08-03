# Copyright 2017-present Open Networking Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from abc import abstractmethod
import grpc
from p4.v1 import p4runtime_pb2_grpc as p4runtime_pb2_grpc
from p4.v1 import p4runtime_pb2

from p4.tmp import p4config_pb2

class SwitchConnection(object):
    def __init__(self, name, address='127.0.0.1:50051', device_id=0):
        self.name = name
        self.address = address
        self.device_id = device_id
        self.p4info = None
        self.channel = grpc.insecure_channel(self.address)
        self.client_stub = p4runtime_pb2_grpc.P4RuntimeStub(self.channel)

    @abstractmethod
    def buildDeviceConfig(self, **kwargs):
        return p4config_pb2.P4DeviceConfig()

    def GetForwardingPipelineConfig(self, **kwargs):
        # device_config = self.buildDeviceConfig(**kwargs)
        request = p4runtime_pb2.GetForwardingPipelineConfigRequest()
        request.device_id = self.device_id

        print(self.client_stub.GetForwardingPipelineConfig(request))
        # print request


    def SetForwardingPipelineConfig(self, p4info, dry_run=False, **kwargs):
        device_config = self.buildDeviceConfig(**kwargs)
        request = p4runtime_pb2.SetForwardingPipelineConfigRequest()
        request.device_id = self.device_id
        # request.role_id = 0
        config = request.config
        config.p4info.CopyFrom(p4info)
        config.p4_device_config = device_config.SerializeToString()
        request.action = p4runtime_pb2.SetForwardingPipelineConfigRequest.VERIFY_AND_COMMIT
        if dry_run:
            print "P4 Runtime SetForwardingPipelineConfig:", request
        else:
            self.client_stub.SetForwardingPipelineConfig(request)

    def WriteTableEntry(self, table_entry, dry_run=False):
        request = p4runtime_pb2.WriteRequest()
        request.device_id = self.device_id
        update = request.updates.add()
        update.type = p4runtime_pb2.Update.INSERT
        update.entity.table_entry.CopyFrom(table_entry)
        if dry_run:
            print "P4 Runtime Write:", request
        else:
            self.client_stub.Write(request)

    def ReadTableEntries(self, dry_run=False, **kwargs):
        '''
        :param table_id: If default (0), entries from all tables will be selected and no other filter can be used. Otherwise only the specified table will be considered.

        :param match: If default (unset), all entries from the specified table will be considered. Otherwise, results will be filtered based on the provided match key, which must be a valid match key for the table. The match will be exact, which means at most one entry will be returned. (NOT WORKING)

        :param action: If default (unset), all entries from the specified table will be considered. Otherwise, the client can provide an action_id (for direct tables), which will be use to filter table entries. For this P4Runtime release, this is the only kind of action-based filtering we support: the client cannot filter based on action parameter values and cannot filter indirect table entries based on action profile member id / action profile group id. (NOT WORKING)

        :param priority: If default (0), all entries from the specified table will be considered. Otherwise, results will be filtered based on the provided priority value.

        :param controller_metadata: If default (0), all entries from the specified table will be considered. Otherwise, results will be filtered based on the provided controller_metadata value.

        :param is_default_action: If default (false), all non-default entries from the specified table will be considered. Otherwise, only the default entry will be considered.
        '''

        table_id = kwargs.get("table_id", 0)
        match = kwargs.get("match", None)
        action = kwargs.get("action", None)
        priority = kwargs.get("priority", 0)
        controller_metadata = kwargs.get("controller_metadata", 0)
        is_default_action = kwargs.get("is_default_action", False)

        request = p4runtime_pb2.ReadRequest()
        request.device_id = self.device_id
        entity = request.entities.add()
        table_entry = entity.table_entry
        # set params (defaults are used according to P4Runtime spec)
        table_entry.table_id = table_id
        # match = table_entry.match.add()
        # match.match = match
        # table_entry.match = match
        # table_entry.action = action
        table_entry.priority = priority
        table_entry.controller_metadata = controller_metadata
        table_entry.is_default_action = is_default_action

        if dry_run:
            print "P4 Runtime Read:", request
        else:
            for response in self.client_stub.Read(request):
                yield response

    def ReadCounters(self, counter_id=None, index=None, dry_run=False):
        request = p4runtime_pb2.ReadRequest()
        request.device_id = self.device_id
        entity = request.entities.add()
        counter_entry = entity.counter_entry
        if counter_id is not None:
            counter_entry.counter_id = counter_id
        else:
            counter_entry.counter_id = 0
        if index is not None:
            counter_entry.index = index
        if dry_run:
            print "P4 Runtime Read:", request
        else:
            for response in self.client_stub.Read(request):
                yield response
