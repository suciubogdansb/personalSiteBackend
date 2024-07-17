from datetime import datetime

from pydantic import BaseModel


class ContactBase(BaseModel):
    name: str
    email: str
    message: str


class Contact(ContactBase):
    contactId: str
    creationDate: datetime

    def toJSON(self):
        return {
            "contactId": self.contactId,
            "name": self.name,
            "email": self.email,
            "message": self.message,
            "creationDate": str(self.creationDate)
        }

    class Config:
        orm_mode = True
