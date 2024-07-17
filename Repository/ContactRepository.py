from sqlalchemy.orm import Session

from databaseManagement.database import SessionLocal
from databaseManagement.models.models import ContactModel
from schemas.Contact import ContactBase


class ContactRepository:
    def __init__(self):
        self.__db: Session = SessionLocal()

    def getContacts(self):
        return self.__db.query(ContactModel).all()

    def addContact(self, contact: ContactBase) -> ContactModel:
        dbContact = ContactModel(name=contact.name, email=contact.email, message=contact.message)
        self.__db.add(dbContact)
        self.__db.commit()
        self.__db.refresh(dbContact)
        return dbContact