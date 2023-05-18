#! /usr/bin/python3

import socket
import logging
import sys
import os
import traceback
import select
from sys import stdin


PORT = 1883

PROTOCOL_NAME = "MQTT"
PROTOCOL_VERSION = 0x4
QOS_DEFAULT = 0
TYPE_CONNECT = 0x10
TYPE_CONNACK = 0x20
TYPE_DISCONNECT = 0xe0
TYPE_PUBLISH = 0x30
TYPE_SUBSCRIBE = 0x80
TYPE_SUBACK = 0x90

def create_mqtt_connect_msg(client_id):            # paquet CONNECT
    # 0001 x x x x : Message Type = Publish ; Dup Flag = None ; QoS = None
    msg_mqtt_flags =  TYPE_CONNECT.to_bytes(1, byteorder='big')
    
    msg_length_protocole= len(PROTOCOL_NAME).to_bytes(2, byteorder='big')
    msg_protocole = bytes(PROTOCOL_NAME, "utf-8")
    
    msg_mqtt_levels = PROTOCOL_VERSION.to_bytes(1, byteorder='big')
    msg_flags=0x02.to_bytes(1, byteorder='big')
    
    msg_keep_alive = (60).to_bytes (2, byteorder='big')
    msg_id_length=len(client_id).to_bytes(1, byteorder='big')
    msg_client_id=client_id.encode("utf-8")
    
    msg=msg_length_protocole+msg_protocole+msg_mqtt_levels+msg_flags+msg_keep_alive+msg_id_length+msg_client_id
    msg_length = len(msg).to_bytes(1, byteorder='big')
    return msg_mqtt_flags+msg_length+msg


def create_mqtt_connack_msg():                     # paquet CONNACK
    msg_mqtt_flags =  TYPE_CONNACK.to_bytes(1, byteorder='big')
    
    msg=(0).to_bytes(2, byteorder='big')
    msg_length = len(msg).to_bytes(1, byteorder='big')
    return msg_mqtt_flags+msg_length+msg

def create_mqtt_subscribe_msg(topic, packet_id):  # paquet SUBSCRIBE
    msg_mqtt_flags =  TYPE_SUBSCRIBE.to_bytes(1, byteorder='big')

    msg_id=packet_id.to_bytes(2, byteorder='big')
    
    msg_topic = topic.encode("utf-8")
    msg_topic_length = len(msg_topic).to_bytes(2, byteorder='big')

    msg_protocole = QOS_DEFAULT.to_bytes(1, byteorder='big')
    
    msg= msg_id+msg_topic_length+msg_topic+msg_protocole
    msg_length = len(msg).to_bytes(1, byteorder='big')
    return msg_mqtt_flags+msg_length+msg


def create_mqtt_suback_msg(topic, packet_id): # paquet CONNACK
    msg_mqtt_flags =  TYPE_SUBACK.to_bytes(1, byteorder='big')  
    #msg_mqtt_flags = TYPE_CONNACK.to_bytes(1, byteorder='big').hex()
    
    msg_id=packet_id.to_bytes(2, byteorder='big')
    msg_protocole = QOS_DEFAULT.to_bytes(1, byteorder='big')

    msg= msg_id+msg_protocole
    msg_length = len(msg).to_bytes(1, byteorder='big')
    
    return msg_mqtt_flags+msg_length+msg


def create_mqtt_disconnect_msg():               # paquet DISCONNECT
    msg_mqtt_flags=TYPE_DISCONNECT.to_bytes(1, byteorder='big')
    msg_length=(0).to_bytes(1, byteorder='big')
    return msg_mqtt_flags+msg_length
                   

def create_mqtt_publish_msg(topic, value, retain):
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


def run_publisher(addr, topic, pub_id, retain=False):
    """
    Run client publisher.
    """
    # lire la reponse avec .read connait la taille
    # une fois le premier packet recu on connait la taille des packets
    # lire decoder le packet par frame tete et reste
    # decomposer la frame reste dans un tableau
    s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM, 0)
    s.connect(addr)
    # s.listen(1)
    frame=bytes("","utf-8")
    s.sendall(create_mqtt_connect_msg(pub_id))
    frame = s.recv(128)
    msg_type = frame[0:1]
    msg_type = msg_type.hex()
    msg_type= int(msg_type, 16)
    if msg_type==TYPE_CONNACK:
        try:
            for line in stdin:
                msg = line[:-1]         # on supprime le retour à la ligne ('\n')
                pkt = create_mqtt_publish_msg(topic, msg, retain)
                s.sendall(pkt)
                
                # frame = s.recv(128)
                # msg_type = frame[0:1] 

                # msg_type = msg_type.hex()
                # msg_type= int(msg_type, 16)
              
                # if  msg_type==TYPE_DISCONNECT:
                #     s.close()
                #     break

        except KeyboardInterrupt:
            s.sendall(create_mqtt_disconnect_msg())
            s.close()
        
    
        finally:
            s.sendall(create_mqtt_disconnect_msg())
            s.close()


def run_subscriber(addr, topic, sub_id):
    """
    Run client subscriber.
    """
    s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM, 0)
    s.connect((addr))
    # s.listen(1)
    frame_connack=bytes("","utf-8")
    frame_suback=bytes("","utf-8")
    frame_pusblish=bytes("","utf-8")


    s.sendall(create_mqtt_connect_msg(sub_id))
    try:
        frame = s.recv(128)
        msg_type = frame[0:1] 
        msg_type = msg_type.hex()
        msg_type= int(msg_type, 16)

        if msg_type==TYPE_CONNACK:
            pkt = create_mqtt_subscribe_msg(topic,1)
            s.sendall(pkt)
            frame_suback = s.recv(128)

            msg_type=frame_suback[0:1]
            msg_type = msg_type.hex()
            msg_type= int(msg_type, 16)

            if msg_type==TYPE_SUBACK:
                
                while True:
                    frame_pusblish= s.recv(128)
                    if  msg_type==TYPE_DISCONNECT:
                        s.close()
                        break
                    if len(frame_pusblish) == 0:
                        s.sendall(create_mqtt_disconnect_msg())
                        s.close()
                        break
                    msg_type=frame_pusblish[0:1]
                    msg_type = msg_type.hex()
                    msg_type= int(msg_type, 16)

                    if msg_type==TYPE_PUBLISH:
                        msg_taille=frame_pusblish[1:2]
                        msg_taille_topic=frame_pusblish[3:4]
                        msg_topic=frame_pusblish[4:(4+ int.from_bytes(msg_taille_topic,byteorder='big'))]
                        msg_topic=msg_topic.decode("utf-8") 

                        value=frame_pusblish[(4+ int.from_bytes(msg_taille_topic,byteorder='big')):]
                        value= value.decode("utf-8") 

                        print(msg_topic, " :  ",value)


    except KeyboardInterrupt:
        s.sendall(create_mqtt_disconnect_msg())
        s.close()



def run_server(addr):
    """
    Run main server loop
    """

    s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM, 0)
    # print("socket :", s)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(1)
    #s2, addr2 = s.accept()
    frame=bytes("","utf-8")
    tmp = 20000
    value = 10000
    l = []
    try:
        while True:  
            r, _, _ = select.select(l + [s], [], [])
            print(" ")
            for s2 in r:
                if s2 == s:
                    s3, addr3 = s.accept()
                    print("new client:", addr3)
                    l = l + [s3]
                else:
                    # print("on entre dans le else")
                    frame = s2.recv(128)
                    if len(frame) == 0:
                        s2.close()
                        l.remove(s2)
                        continue
                    
                    if len(frame) != 0:
                        msg_entete = frame[0:1] 

                        msg_entete = msg_entete.hex()
                        msg_entete = int(msg_entete, 16)
                    
                    
                    
                    # print(TYPE_CONNECT)

                
                

                    

                    #si se qu'on recoit est connect alors on revoit connack
                    if (msg_entete == TYPE_CONNECT):
                        s3.sendall(create_mqtt_connack_msg())

                    if (msg_entete == TYPE_SUBSCRIBE):
                        msg_taille_topic=frame[3:4]
                        msg_topic=frame[4:(4+ int.from_bytes(msg_taille_topic,byteorder='big'))]
                        msg_topic = msg_topic.decode("utf-8") 
                        s3.sendall(create_mqtt_suback_msg(msg_topic, 1))

                    #puis on regarde si c est un publisher 
                    if (msg_entete == TYPE_PUBLISH or msg_entete == TYPE_PUBLISH + 1):

                        if (msg_entete == TYPE_PUBLISH + 1):
                            
                            msg_taille=frame[1:2]
                            msg_taille_topic=frame[3:4]
                            msg_topic=frame[4:(4+ int.from_bytes(msg_taille_topic,byteorder='big'))]
                            msg_topic=msg_topic.decode("utf-8") 

                            value=frame[(4+ int.from_bytes(msg_taille_topic,byteorder='big')):]
                            value = value.decode("utf-8") 
                            
                            
                        
                        if (msg_entete != TYPE_PUBLISH + 1 or tmp != value):
                        
                            for i in l:
                                #print(i)
                                i.sendall(frame)
                        
                        tmp = value
                  

                    if (msg_entete == TYPE_DISCONNECT):
                        msg_entete = frame[0:1] 
                        msg_entete = msg_entete.hex()
                        msg_entete = int(msg_entete, 16)
                        s2.close()
                        l.remove(s2)

    except KeyboardInterrupt:
        for i in l:
            i.sendall(create_mqtt_disconnect_msg())
            i.close()
        for i in l:
            l.remove(i)