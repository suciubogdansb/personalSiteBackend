from Repository.ContactRepository import ContactRepository
from schemas.Contact import Contact, ContactBase
from utils import contactToDTO


class ContactService:
    def __init__(self, repository: ContactRepository):
        self.__contactRepository = repository

    def getAll(self) -> list[Contact]:
        contacts = self.__contactRepository.getContacts()
        return [contactToDTO(contact) for contact in contacts]

    def addContact(self, contact: ContactBase) -> Contact:
        return contactToDTO(self.__contactRepository.addContact(contact))



