#!/usr/bin/python

try:
    from time import sleep
    from opcua import ua, uamethod, Server
except ImportError as e:
    print(e)

"""
OPC-UA-Server Methods and Events
"""

@uamethod
def getdata(parent, rfid):
    #Test data later from database
    db_value = 1234
    print(f"Method 'getdata' got called with inputParameter: {rfid}")
    return (
                ua.Variant(rfid, ua.VariantType.UInt64),        #RFID
                ua.Variant(db_value, ua.VariantType.UInt64)     #Value from database
            )  
            
if __name__ == "__main__":
    """
    OPC-UA-Server Setup
    """
    server = Server()
    server.set_endpoint("opc.tcp://127.0.0.1:4840")
    server.set_server_name("PythonOpcUaServer")
    security_policy =   [
                            ua.SecurityPolicyType.NoSecurity,
                            #ua.SecurityPolicyType.Basic256Sha256_SignAndEncrypt,
                            #ua.SecurityPolicyType.Basic256Sha256_Sign
                        ]
    server.set_security_policy(security_policy)
    policyIDs =   [
                    "Anonymous", "Basic256Sha256", "Username"
                ]
    server.set_security_IDs(policyIDs)
    address_space = server.register_namespace("http://andreas-heine.net/UA")

    """
    OPC-UA-Modeling
    """
    root_node = server.get_root_node()
    object_node = server.get_objects_node()
    server_node = server.get_server_node()

    #S7-1500 Checks frequently the service level so make sure it has a value (http://documentation.unified-automation.com/uasdkcpp/1.5.3/html/L2ServerRedundancy.html)
    servicelevel_node = server.get_node("ns=0;i=2267") #Service-Level Node
    value = 255 #>=200 Serviclevel good
    dv = ua.DataValue(ua.Variant(value, ua.VariantType.Byte)) #if you want to write a node value with <set_value()> you need to create a DataValue Object
    servicelevel_node.set_value(dv)

    method_obj = server.nodes.objects.add_object(address_space, "Methods")
    method_node = method_obj.add_method(
                                        address_space, 
                                        "getData", 
                                        getdata, 
                                        [
                                            #Input-Arguments:
                                            ua.VariantType.UInt64 #RFID
                                        ], 
                                        [
                                            #Output-Arguments:
                                            ua.VariantType.UInt64, #RFID
                                            ua.VariantType.UInt64  #Value from database
                                        ]
                                    )

    """
    OPC-UA-Server Start
    """
    server.start()
    try:
        while 1:
            sleep(1)
    except KeyboardInterrupt:
        server.stop()

