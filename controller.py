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

def readTableRules(p4info_helper, sw):
    '''
    Reads the table entries from all tables on the switch.
    :param p4info_helper: the P4Info helper
    :param sw: the switch connection
    '''
    print '\n----- Reading tables rules for %s -----' % sw.name
    for response in sw.ReadTableEntries():
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


def main(p4info_file_path, bmv2_file_path, ip, port, set_forwarding, portfwd, readtables, vlanrule):
    p4info_helper = p4runtime_lib.helper.P4InfoHelper(p4info_file_path)

    print('\n----- Connecting to switch at {}:{} -----'.format(ip, port))
    s = p4runtime_lib.bmv2.Bmv2SwitchConnection('s1',
                                                address='{}:{}'.format(ip,port),
                                                device_id=0)

    print('\n [DONE]\n\n')

    if set_forwarding:
        print('\n----- Installing P4 program----')
        s.SetForwardingPipelineConfig(  p4info=p4info_helper.p4info,
                                        bmv2_json_file_path=bmv2_file_path)

    print('\n [DONE]\n\n')

    if portfwd:
        addPortFwdRule(p4info_helper, s, 0, 0)
    if vlanrule:
        addVLANforwardRule(p4info_helper, s, 100, 0 , 0)
    if readtables:
        readTableRules(p4info_helper, s)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='P4Runtime Controller')
    parser.add_argument('--p4info', help='p4info proto in text format from p4c',
                        type=str, action="store", required=True)
    parser.add_argument('--bmv2-json', help='BMv2 JSON file from p4c',
                        type=str, action="store", required=True)
    parser.add_argument('--ip',help='Control IP address of the P4 switch (default: 127.0.0.1)',
                        type=str, action="store",required=False,
                        default='127.0.0.1')
    parser.add_argument('--port',help='Control port of the P4 switch (default : 50051)',
                        type=str, action="store",required=False,
                        default=50051)
    parser.add_argument("--set_forwarding", help="Install forwarding pipeline - reset the whole pipeline (?)",
                        action="store_true", required=False, default=False)
    parser.add_argument('--add_portfwd', help='Adds a simple portfwd rule from port 0 to port 0 if header does not contain VLAN TAG',
                        action="store_true", required=False, default=False)
    parser.add_argument('--read_tables', help='Reads table entries of the switch',
                        action="store_true", required=False, default=False)
    parser.add_argument('--add_vlanrule', help='Adds a vlan rule to match on vid=100, incoming port 0, and send back to port 0',
                        action="store_true", required=False, default=False)
    args = parser.parse_args()

    if not os.path.exists(args.p4info):
        parser.print_help()
        print("\np4info file not found: {}\nHave you run 'make'?".format(args.p4info))
        parser.exit(1)
    if not os.path.exists(args.bmv2_json):
        parser.print_help()
        print("\nBMv2 JSON file not found: {}\nHave you run 'make'?".format(args.bmv2_json))
        parser.exit(1)

    main(args.p4info,
        args.bmv2_json,
        args.ip,
        args.port,
        args.set_forwarding,
        args.add_portfwd,
        args.read_tables,
        args.add_vlanrule)
