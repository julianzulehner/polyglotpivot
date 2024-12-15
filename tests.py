import os 
import unittest
from app import db, create_app
from app.models import User, Vocable, Practice, Language, Post 
from config import Config

def helper_create_user():
    user = User(username='Testuser',email='testuser@example.com')
    db.session.add(user)
    db.session.commit()
    
def helper_create_user_with_data():
    source_language = Language(iso='de', name='Deutsch')
    target_language = Language(iso='en', name='English')
    db.session.add_all([source_language, target_language])
    user = User(username='Testuser',email='testuser@example.com')
    db.session.add(user)
    vocable = Vocable(en='hello',de='hallo',es='hola')
    user.vocables.append(vocable)
    db.session.commit()
    
class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    
class UserModelCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        
    def test_create_languages(self):
        languages = list()
        for iso, name in Config.LANGUAGES.items():
            languages.append(Language(iso=iso,name=name))
            db.session.add_all(languages)
            db.session.commit()         
            test_language = db.session.get(Language,1)
            self.assertEqual(test_language.name, Config.LANGUAGES[test_language.iso])
    
    def test_create_user(self): 
        user = User(username='Testuser',email='testuser@example.com')
        db.session.add(user)
        db.session.commit()
        user = db.session.get(User, 1) 
        self.assertEqual(user.username, 'Testuser')
        self.assertEqual(user.email, 'testuser@example.com')
            
    def test_password_hashing(self):
        u = User(username='Testuser',email='testuser@example.com')
        u.set_password('mypassword')
        db.session.add(u)
        db.session.commit()
        self.assertFalse(u.check_password('notmypassword'))
        self.assertTrue(u.check_password('mypassword'))

    def test_create_vocable(self):
        helper_create_user()
        user = db.session.get(User,1)
        vocable = Vocable(en="hello", de="hallo")
        user.vocables.append(vocable)
        db.session.commit()   
        user = db.session.get(User, 1) # retreive user again  
        self.assertEqual(len(user.vocables) ,1) 
        vocable = user.vocables[0] 
        self.assertEqual(vocable.en, 'hello')
        self.assertEqual(vocable.de, 'hallo')
        
    def test_practice(self):
        helper_create_user_with_data()
        user = db.session.get(User, 1)
        source_language = db.session.get(Language, 1)
        target_language = db.session.get(Language, 2)
        vocable = user.get_due_vocable(source_language, target_language)
        vocable = user.vocables[0]
        self.assertEqual(vocable.check_if_studied(), False) # unit was not studied before
        col_name = f"{target_language.iso}_lvl"
        fst_lvl = getattr(vocable, col_name)
        self.assertEqual(fst_lvl, 0) # by default the value should be 0 at start
        # test with correct result
        vocable.check_result_and_set_level('hello', target_language) 
        snd_lvl = getattr(vocable, col_name) # should rise by one because correct
        self.assertEqual(snd_lvl, fst_lvl+1)
        # test with wrong result 
        vocable.check_result_and_set_level('xxx', target_language)
        thd_lvl = getattr(vocable, col_name) # usually should lower but limited to 1
        self.assertEqual(thd_lvl, 1)
        # test with correct result
        vocable.check_result_and_set_level('hello', target_language) 
        fth_lvl = getattr(vocable, col_name) # should be now 2
        self.assertEqual(fth_lvl, 2)
        
        # check upper lvl limit of 6
        for i in range(10):
            vocable.check_result_and_set_level('hello', target_language)
        six_lvl = getattr(vocable, col_name)
        self.assertEqual(six_lvl, 6)
        
        
    
        

if __name__ == '__main__':
    unittest.main(verbosity=2)

