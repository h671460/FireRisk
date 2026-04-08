import time
import requests
import json
from datetime import datetime, timedelta, timezone

import paho.mqtt.client as paho
from paho import mqtt

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import src.mqtt.connector.publisher as mqtt_publisher
import src.mqtt.connector.configuration as mqtt_configuration

import os
# Keycloak config
KEYCLOAK_TOKEN_URL = os.getenv("KEYCLOAK_TOKEN_URL")
MQTT_CLIENT_ID = os.getenv("MQTT_KEYCLOAK_CLIENT_ID")
MQTT_CLIENT_SECRET = os.getenv("MQTT_KEYCLOAK_CLIENT_SECRET")

# Fire risk API
FIRERISK_API_URL = os.getenv("FIRERISK_API_URL")

# How often to publish (seconds)
PUBLISH_INTERVAL = int(os.getenv("PUBLISH_INTERVAL", 30))  


class TokenManager:

    def __init__(self):
        self.access_token = None
        self.expires_at = None

    def fetch_token(self):
        print("Fetching new token from Keycloak...")

        response = requests.post(KEYCLOAK_TOKEN_URL, data={
            "grant_type": "client_credentials",
            "client_id": MQTT_CLIENT_ID,
            "client_secret": MQTT_CLIENT_SECRET
        }, verify=False)

        response.raise_for_status()
        data = response.json()

        self.access_token = data["access_token"]
        self.expires_at = datetime.now(timezone.utc) + timedelta(seconds=data["expires_in"] - 30)

        print("Token fetched successfully.")
        

    def get_token(self) -> str:
        if self.access_token is None or self.is_expired():
            self.fetch_token()
        return self.access_token

    def is_expired(self) -> bool:
        return datetime.now(timezone.utc) >= self.expires_at


class FireriskPublisher:

    def __init__(self, config_file: str, longitude: float, latitude: float):

        self.config = mqtt_configuration.ClientConfiguration(config_file)
        self.publisher_client = mqtt_publisher.PublisherClient(self.config)

        self.longitude = longitude
        self.latitude = latitude

        self.token_manager = TokenManager()

    def fetch_firerisk(self) -> dict:
        token = self.token_manager.get_token()

        
        start_time = (datetime.now(timezone.utc) - timedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%SZ")
        end_time =( datetime.now(timezone.utc) + timedelta(days=2) ).strftime("%Y-%m-%dT%H:%M:%SZ")
        params = {
            "lat": self.latitude,
            "lon": self.longitude,
            "start_time": start_time,
            "end_time": end_time
        }

        headers = {
            "Authorization": f"Bearer {token}"
        }


        response = requests.get(FIRERISK_API_URL, params=params, headers=headers, verify=False)
        response.raise_for_status()

        return response.json()

    def publish_firerisk(self):
        data = self.fetch_firerisk()
        self.publisher_client.publish_one(json.dumps(data))
        print(f"Published fire risk data for lat={self.latitude} lon={self.longitude}")

    def run(self):
        print("Starting FireriskPublisher...")

        # while True:
        try:
            self.publish_firerisk()

        except requests.HTTPError as e:
            print(f"API error: {e}")

        except Exception as e:
            print(f"Unexpected error: {e}")

        print(f"Waiting {PUBLISH_INTERVAL} seconds...")
        # time.sleep(PUBLISH_INTERVAL)
        


if __name__ == "__main__":

    # config_file = 'src/mqtt/connector/config-ada502-pub.yml'
    
    config_file = mqtt_configuration.get_config_file()
    
    latitude=60.383
    longitude=5.3327

    publisher = FireriskPublisher(config_file,longitude=longitude, latitude=latitude)

    publisher.run()