from typing import List

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_session
from src.schemas.schemas import ContactSchema, ContactSchemaResponse
from src.repository import contacts as contacts_repo

router = APIRouter(prefix='/contacts', tags=["contacts"])


@router.get("/", response_model=List[ContactSchemaResponse])
async def get_contacts(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_session)):
    contacts = await contacts_repo.get_contacts(skip, limit, db)
    return contacts


@router.get("/search", response_model=List[ContactSchemaResponse])
async def search_contacts(name:str = None,
                          surname:str = None,
                          email:str = None,
                          db: AsyncSession = Depends(get_session)):
    tags = await contacts_repo.search_contacts(db, name, surname, email)
    return tags


@router.get("/{contact_id}", response_model=ContactSchemaResponse)
async def get_contact_by_id(contact_id: int, db: AsyncSession = Depends(get_session)):
    contact = await contacts_repo.get_contact(contact_id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Сontact not found!")
    return contact


@router.post("/", response_model=ContactSchemaResponse)
async def create_contact(body: ContactSchema, db: AsyncSession = Depends(get_session)):
    return await contacts_repo.create_contact(body, db)


@router.put("/{contact_id}", response_model=ContactSchemaResponse)
async def put_contact(body: ContactSchema, contact_id: int, db: AsyncSession = Depends(get_session)):
    contact = await contacts_repo.update_contact(contact_id, body, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Сontact not found!")
    return contact


@router.delete("/{contact_id}", response_model=ContactSchemaResponse)
async def delete_contact(contact_id: int, db: AsyncSession = Depends(get_session)):
    contact = await contacts_repo.delete_contact(contact_id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Сontact not found!")
    return contact



