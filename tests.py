import os 
os.environ['DATABASE_URL'] = 'sqlite://'

import unittest
from app import app, db 
from app.models import User, Vocable, Practice, Language, Post 
from config import Config




class UserModelCase(unittest.TestCase):

    def setUp(self):
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hashing(self):
        u = User(username='Testuser',email='testuser@example.com')
        u.set_password('mypassword')
        db.session.add(u)
        db.session.commit()
        self.assertFalse(u.check_password('notmypassword'))
        self.assertTrue(u.check_password('mypassword'))

    def test_create_languages(self):
        languages = list()
        for iso, name in Config.LANGUAGES.items():
            languages.append(Language(iso=iso,name=name))
            db.session.add_all(languages)
            db.session.commit()         
            test_language = db.session.get(Language,1)
            self.assertEqual(test_language.name, Config.LANGUAGES[test_language.iso])


    def test_assign_vocable_to_user(self):
        user = User(username='Testuser',email='testuser@example.com')
        db.session.add(user)
        db.session.commit()
        user = db.session.get(User,1)
        vocable = Vocable(en='hello',de='hallo',es='hola')
        user.vocables.append(vocable)
        db.session.commit()
        self.assertEqual(len(user.vocables),1)

if __name__ == '__main__':
    unittest.main(verbosity=2)

    print(Config.LANGUAGES)