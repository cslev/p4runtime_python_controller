#!/usr/bin/env python2
import argparse
import os
from time import sleep

import p4runtime_lib.bmv2
import p4runtime_lib.helper


def addPortFwdRule(p4info_helper, sw, incoming_port, output_port):
    print("----------- ADD PORT FWD RULE -------------")

    table_entry = p4info_helper.buildTableEntry(
        table_name="MyIngress.port_exact",
        match_fields={
            "standard_metadata.ingress_port": incoming_port
        },
        action_name="MyIngress.portfwd",
        action_params={
            "port": output_port
        })
    sw.WriteTableEntry(table_entry)

def addVLANforwardRule(p4info_helper, sw, vlan, incoming_port, output_port):
    '''
    :param p4info_helper: the P4info helper instance
    :param sw: the switch connection
    :param
    '''

    table_entry = p4info_helper.buildTableEntry(
        table_name="MyIngress.vlan_incoming_exact",
        match_fields={
            "hdr.vlan.vid": vlan,
            "standard_metadata.ingress_port": incoming_port
        },
        action_name="MyIngress.vlan_incoming_forward",
        action_params={
            "port": output_port
    })
    sw.WriteTableEntry(table_entry)
    print ("VLAN FORWARDING RULE IS INSTALLED:")
    # print "Matching on {}/32, action {} called with arguments (MAC: {}, OUTPUT_PORT: {}".format(ip_to_match,action_func,next_hop_mac,output_port)

def readTableRules(p4info_helper, sw, **kwargs):
    '''
    Reads the table entries from all tables on the switch.
    :param p4info_helper: the P4Info helper
    :param sw: the switch connection

    :param table_name: Name of the table to filter
    :param match: table entries that match on 'match' (NOT WORKING)
    :param action: table entries that have the action 'action' (NOT WORKING)
    :param priority: table entries that have the priority 'priority'
    :param controller_metadata: table entries that have controller_metadata 'controller_metadata'
    :param is_default_action: table entries that have default action'
    '''
    table_name = kwargs.get("table_name", 0)

    print '\n----- Reading tables rules for %s -----' % sw.name
    if table_name != "ALL":
        tid=p4info_helper.get_tables_id(table_name)
    else:
        tid=0

    entries = sw.ReadTableEntries(table_id=tid,
                                match=kwargs.get("match", None),
                                action=kwargs.get("action", None),
                                priority=kwargs.get("priority", 0),
                                controller_metadata=kwargs.get("controller_metadata",0),
                                is_default_action=kwargs.get("is_default_action",False))

    for response in entries:
        for entity in response.entities:
            entry = entity.table_entry
            table_name = p4info_helper.get_tables_name(entry.table_id)
            print '%s: ' % table_name,
            for m in entry.match:
                print p4info_helper.get_match_field_name(table_name, m.field_id),
                print '%r' % (p4info_helper.get_match_field_value(m),),
            action = entry.action.action
            action_name = p4info_helper.get_actions_name(action.action_id)
            print '->', action_name,
            for p in action.params:
                print p4info_helper.get_action_param_name(action_name, p.param_id),
                print '%r' % p.value,
            print


def main(**kwargs):
    '''
    :param p4info = p4info file path
    :param bmv2 = bvm2 file path
    :param ip = The IP address of the Switch
    :param port = the port of the switch it listens to
    :param set_forwarding = indicate whether it is intended to install pipelineconfig
    :param get_forwarding = indicate whether it is intended to get the current pipelineconfig
    :param portfwd = indicate whether it is intended to install basic portfwd rule
    :param vlanrule = indicate whethet it is intended to install basic vlanfwd rule
    :param table_name = the name of the table it is intended to request (can be ALL for all)
    '''
    # print kwargs
    p4_info_filepath = kwargs.get("p4info", None)
    bmv2_file_path = kwargs.get("bmv2", None)
    ip = kwargs.get("ip", "127.0.0.1")
    port = kwargs.get("port", 50051)
    set_forwarding = kwargs.get("set_forwarding", False)
    get_forwarding = kwargs.get("get_forwarding", False)
    portfwd = kwargs.get("portfwd", False)
    vlanrule = kwargs.get("vlanrule", False)
    table_name = kwargs.get("table_name", None)

    # print p4_info_filepath

    p4info_helper = p4runtime_lib.helper.P4InfoHelper(p4_info_filepath)

    print('\n----- Connecting to switch at {}:{} -----'.format(ip, port))
    s = p4runtime_lib.bmv2.Bmv2SwitchConnection('s1',
                                                address='{}:{}'.format(ip,port),
                                                device_id=0)

    print('\n [DONE]\n\n')

    if set_forwarding:
        if bmv2_file_path is not None:
            print('\n----- Installing P4 program----')
            s.SetForwardingPipelineConfig(  p4info=p4info_helper.p4info,
                                            bmv2_json_file_path=bmv2_file_path)
            print('\n [DONE]\n\n')
        else:
            print('\n----- No BMV2 File is provided -----')
            print('UNABLE TO SET FORWARDING PIPELINE')
            exit(-1)

    if get_forwarding:
        s.GetForwardingPipelineConfig()

    if portfwd:
        addPortFwdRule(p4info_helper, s, 0, 0)
    if vlanrule:
        addVLANforwardRule(p4info_helper, s, 100, 0 , 0)
    if table_name is not None:
        readTableRules(p4info_helper,
                        s,
                        table_name=table_name,
                        priority=100)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='P4Runtime Controller')
    parser.add_argument('--p4info', help='p4info proto in text format from p4c',
                        type=str, action="store", required=True)
    parser.add_argument('--bmv2-json', help='BMv2 JSON file from p4c',
                        type=str, action="store", required=False, default=None)
    parser.add_argument('--ip',help='Control IP address of the P4 switch (default: 127.0.0.1)',
                        type=str, action="store",required=False,
                        default='127.0.0.1')
    parser.add_argument('--port',help='Control port of the P4 switch (default : 50051)',
                        type=str, action="store",required=False,
                        default=50051)
    parser.add_argument("--set_forwarding", help="Install forwarding pipeline - reset the whole pipeline",
                        action="store_true", required=False, default=False)
    parser.add_argument("--get_forwarding", help="Gets the forwarding pipeline",
                        action="store_true", required=False, default=False)
    parser.add_argument('--add_portfwd', help='Adds a simple portfwd rule from port 0 to port 0 if header does not contain VLAN TAG',
                        action="store_true", required=False, default=False)
    parser.add_argument('--read_table', help='Reads table entries of the specified table (Use ALL for no filters)',
                        type=str, action="store", required=False, default=None)
    parser.add_argument('--add_vlanrule', help='Adds a vlan rule to match on vid=100, incoming port 0, and send back to port 0',
                        action="store_true", required=False, default=False)
    args = parser.parse_args()

    if not os.path.exists(args.p4info):
        parser.print_help()
        print("\np4info file not found: {}\nHave you run 'make'?".format(args.p4info))
        parser.exit(1)
    if (args.bmv2_json is not None and not os.path.exists(args.bmv2_json)):
        parser.print_help()
        print("\nBMv2 JSON file not found: {}\nHave you run 'make'?".format(args.bmv2_json))
        parser.exit(1)

    # print args.read_table
    # exit (-1)
    main(p4info=args.p4info,
        bmv2 = args.bmv2_json,
        ip = args.ip,
        port = args.port,
        set_forwarding = args.set_forwarding,
        get_forwarding = args.get_forwarding,
        portfwd = args.add_portfwd,
        table_name = args.read_table,
        vlanrule = args.add_vlanrule)
