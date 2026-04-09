from pydantic import BaseModel


class userPayload(BaseModel):
    id: str
    username: str
    email: str | None = None        # now accepts None
    first_name: str | None = None   # now accepts None
    last_name: str | None = None    # now accepts None
    realm_roles: list
    
    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "realm_roles": self.realm_roles,
        }
        
