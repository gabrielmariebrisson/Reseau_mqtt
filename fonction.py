import doctest
doctest.testmod()
def create_mqtt_publish_msg(topic, value, retain=False):
    """ Convert string into bytes
    >>> create_mqtt_publish_msg("mydirectory/myTopic","24",False).hex(" ")
    '30 17 00 13 6d 79 64 69 72 65 63 74 6f 72 79 2f 6d 79 54 6f 70 69 63 32 34'
    """
    #30 publish / 0c length / 00  flag 06 / 74 65 6d 70 65 72 temper / 33 = 51 = ! / 32 = 50 / 33 = 51 = ! / 34 = 52 = "
    
    #packet 
    hex_topic=bytes(topic, "utf-8")
    hex_value=bytes(value, "utf-8")
    flags=bytes([0])
   

    if retain:
        #head
        Fixed_header=bytes([49])
    if not(retain):
        #head
        Fixed_header=bytes([48])
        
    #lenght
    len_topic = bytes([len(topic)])
    
    len_packet=bytes([ len( flags + len_topic + hex_topic + hex_value ) ])
    #return Fixed_header + " " + len_packet + " " + flags + " " +  len_topic + " " +  hex_topic + " " +  hex_value        
    return Fixed_header +  len_packet + flags + len_topic + hex_topic + hex_value   
