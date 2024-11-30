import redis
import json

class RedisManager:
    _instance = None

    def __init__(self):
        self.client = redis.Redis()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
        
    def send_to_api(self, client_id, message):
        self.client.publish(client_id, json.dumps(message))