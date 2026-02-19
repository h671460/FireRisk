from pydantic import BaseModel


class authConfiguration(BaseModel):
    server_url: str
    realm: str
    client_id: str
    client_secret: str
    authorization_url: str
    token_url: str
    
    
    def to_dict(self):
        return {
            "server_url": self.server_url,
            "realm": self.realm,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "authorization_url": self.authorization_url,
            "token_url": self.token_url,
        }