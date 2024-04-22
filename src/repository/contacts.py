from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.database.models import Contact
from src.schemas.schemas import ContactSchema


async def get_contacts(skip: int, limit: int, db: AsyncSession) -> [Contact]:
    query = select(Contact).offset(skip).limit(limit)
    res = await db.execute(query)
    return res.scalars().all()


async def search_contacts(db: AsyncSession,
                          name: str = None,
                          surname: str = None,
                          email: str = None,
                          ) -> [Contact]:

    params = {}
    if name:
        params['name'] = name
    if surname:
        params['surname'] = surname
    if email:
        params['email'] = email

    query = select(Contact).filter_by(**params)
    res = await db.execute(query)
    return res.scalars().all()


async def get_contact(contact_id: int, db: AsyncSession) -> Contact:
    query = select(Contact).where(Contact.id == contact_id)
    res = await db.execute(query)
    return res.scalars().first()


async def create_contact(contact: ContactSchema, db: AsyncSession) -> Contact:
    contact = Contact(**contact.dict())
    db.add(contact)
    await db.flush()
    await db.commit()

    return contact


async def update_contact(contact_id: int, contact: ContactSchema, db: AsyncSession) -> Contact | None:
    contact_db = await db.get(Contact, contact_id)
    if contact_db:
        dump = contact.model_dump(exclude_unset=True)
        for key in dump:
            setattr(contact_db, key, dump[key])

        await db.commit()
        await db.refresh(contact_db)

    return contact_db


async def delete_contact(contact_id: int, db: AsyncSession) -> Contact | None:
    contact = await db.get(Contact, contact_id)
    if contact:
        await db.delete(contact)
        await db.flush()
        await db.commit()

    return contact
