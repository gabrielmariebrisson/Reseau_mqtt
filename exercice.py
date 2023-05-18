
TYPE_PUBLISH = 0x30


def create_mqtt_publish_msg(topic, value, retain=False):
    """ 
    Creates a mqtt packet of type PUBLISH with DUP Flag=0 and QoS=0.
    >>> create_mqtt_publish_msg("temperature", "45", False).hex(" ")
    '30 0f 00 0b 74 65 6d 70 65 72 61 74 75 72 65 34 35'
    >>> create_mqtt_publish_msg("temperature", "45", True).hex(" ")
    '31 0f 00 0b 74 65 6d 70 65 72 61 74 75 72 65 34 35'
    """
    retain_code = 0
    if retain:
        retain_code = 1
    # 0011 0000 : Message Type = Publish ; Dup Flag = 0 ; QoS = 0
    msg_mqtt_flags = (TYPE_PUBLISH + retain_code).to_bytes(1, byteorder='big')
    msg_topic = topic.encode("ascii")
    msg_value = bytes(value, "ascii")
    msg_topic_length = len(msg_topic).to_bytes(2, byteorder='big')
    msg = msg_topic_length + msg_topic + msg_value
    msg_length = len(msg).to_bytes(1, byteorder='big')
    return msg_mqtt_flags + msg_length + msg
