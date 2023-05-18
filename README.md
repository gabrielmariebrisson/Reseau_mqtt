# Projet MQTT

Ce projet est une implémentation d'un système de communication basé sur le protocole MQTT (Message Queuing Telemetry Transport). Il comprend un client MQTT qui peut agir en tant que publisher ou subscriber, ainsi qu'un serveur MQTT pour gérer les messages et les connexions.

## Fonctionnalités

- Client Publisher : Permet d'envoyer des messages sur un topic MQTT spécifié.
- Client Subscriber : Permet de recevoir des messages depuis un topic MQTT spécifié.
- Serveur MQTT : Gère les connexions des clients MQTT et distribue les messages aux clients subscribers.

## Configuration requise

- Python 3.x
- Les modules Python requis sont spécifiés dans le fichier `requirements.txt`.

## Installation

1. Clonez ce dépôt de projet sur votre machine locale.
2. Accédez au répertoire du projet.

   ```bash
   cd projet-mqtt/
   ```
3. Installez les dépendances Python requises.

## Utilisation

1. Lancez le serveur MQTT.
   ```bash
   python mqtt_server.py -p 1883
   ```
2. Exécutez le client MQTT en tant que publisher ou subscriber en utilisant les commandes appropriées.

    - Client Publisher :

    ```bash
    python mqtt_client.py pub -H localhost -p 1883 -t topic_name -i publisher_id
    ```
    - Client Subscriber :
    ```bash
    python mqtt_client.py sub -H localhost -p 1883 -t topic_name -i subscriber_id
    ```
Assurez-vous de remplacer les valeurs des arguments (localhost, 1883, topic_name, etc.) par les valeurs appropriées selon votre configuration.

## Auteurs

- Clement Delmas
- Gabriel Marie-Brisson