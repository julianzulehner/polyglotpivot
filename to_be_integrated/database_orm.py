from typing import List, Optional
from sqlalchemy import ForeignKey, String, create_engine, select, Table, Column, Integer, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session


# == DECLARE DATABASE MODELS ==

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(length=20), unique=True)
    email: Mapped[str] = mapped_column(String(length=30), unique=True)
    password: Mapped[str] = mapped_column(String(length=20))

    languages: Mapped[List["languages"]] = relationship("Language", secondary="userlanguage")

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, username={self.username!r}, email={self.email!r})"
    
class Language(Base):
    __tablename__ = "language"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(length=30), unique=True)
    iso_code: Mapped[str] = mapped_column(String(length=2), unique=True)

    users: Mapped[List["users"]] = relationship("User", secondary="userlanguage")

    def __repr__(self) -> str:
        return f"Language(id={self.id!r}, name={self.name!r}, iso_code={self.iso_code!r})"

class UserLanguage(Base):
    __tablename__ = "userlanguage"
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), primary_key=True)
    language_id: Mapped[int] = mapped_column(ForeignKey('language.id'), primary_key=True)

class Vocable(Base):
    __tablename__ = "vocable"
    id: Mapped[int] = mapped_column(primary_key=True)
    nl: Mapped[str] = mapped_column(String(length=100), nullable=True)
    en: Mapped[str] = mapped_column(String(length=100), nullable=True)
    fr: Mapped[str] = mapped_column(String(length=100), nullable=True)
    de: Mapped[str] = mapped_column(String(length=100), nullable=True)
    it: Mapped[str] = mapped_column(String(length=100), nullable=True)
    es: Mapped[str] = mapped_column(String(length=100), nullable=True)
    is_common: Mapped[bool] = mapped_column(default=False)
    vocablecategory_id: Mapped[int] = mapped_column(ForeignKey('vocablecategory.id'), nullable=True)

    users: Mapped[List["users"]] = relationship("User", secondary="uservocable")

    def __repr__(self) -> str:
        return f"English: {self.en}, Commonly used: {self.is_common}"

class VocableCategory(Base):
    __tablename__ = "vocablecategory"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(length=30))
    
    def __repr__(self) -> str:
        return f"VocableCategory(id={self.id!r}, name={self.name!r})"
    
class UserVocable(Base):
    __tablename__ = "uservocable"
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), primary_key=True)
    vocable_id: Mapped[int] = mapped_column(ForeignKey('vocable.id'), primary_key=True)
    nl_level: Mapped[int] = mapped_column( nullable=True, default=0)
    en_level:  Mapped[int] = mapped_column( nullable=True, default=0)
    fr_level:  Mapped[int] = mapped_column( nullable=True, default=0)
    de_level:  Mapped[int] = mapped_column( nullable=True, default=0)
    it_level:  Mapped[int] = mapped_column( nullable=True, default=0)
    es_level:  Mapped[int] = mapped_column( nullable=True, default=0)



if __name__ == '__main__':
    # == CREATE ENGINE == 
    engine = create_engine(url="sqlite:///database.db",echo=True)
    add_list = []
    if True: 
        Base.metadata.create_all(engine)

    # == CREATE OBJECTS ==
    if True: 
        with Session(engine) as session:

            # Define languages
            english = Language(name="english",iso_code="en")
            german = Language(name="german",iso_code="de")
            spanish = Language(name="spanish", iso_code="es")
            dutch = Language(name="dutch", iso_code="nl")
            french = Language(name="french", iso_code="fr")
            italian = Language(name="italian", iso_code="it")
            
            # Define users
            julian = User(username="Julian",email="julian.zulehner@gmail.com", password="meinpasswort")
            julian.languages = [english, german, dutch, spanish]
            ana = User(username="Ana",email="anasanchezfernandez1997@gmail.com", password="ihrpasswort")
            ana.languages = [english, german, spanish]

            # Define vocable category
            noun = VocableCategory(name="noun")
            verb = VocableCategory(name="verb")
            adjective = VocableCategory(name="adjective")
            pronoun = VocableCategory(name="pronoun")
            interjection = VocableCategory(name="interjection")
            conjunction  = VocableCategory(name="conjunction")
            preposition = VocableCategory(name="preposition")
            add_list.extend([adjective, conjunction, interjection, noun, preposition, pronoun, verb])

            # Define vocabulary
            walk = Vocable(de="gehen",en="walk",nl="gaan",es="andar")
            walk.users = [julian]
            walk.vocablecategory_id = 7
            laugh = Vocable(de="lachen",en="laugh",es="reír")
            laugh.users = [ana]
            laugh.vocablecategory_id = 7
            add_list.extend([english, german, french, italian, dutch, spanish, julian, ana, walk, laugh])

            session.add_all(add_list)
            session.commit()

    # == SIMPLE SELECT ==
    with  Session(engine) as session:
        stmt = select(Language).where(Language.name.in_(['english', 'german']))
        for language in session.scalars(stmt):
            print(language)
        stmt = select(User).where(User.username.in_(['Julian', 'Ana']))
        for user in session.scalars(stmt):
            print(user)
        
        stmt = select(UserLanguage)
        for relation in session.scalars(stmt):
            print(language)
        session.close()


