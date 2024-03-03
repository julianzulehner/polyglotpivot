import unittest
import os 
from app import app, db 
from app.models import User, Vocable, Practice, Language, Post 

os.environ['DATABASE_URL'] = 'sqlite://'

class TestModels(unittest.TestCase):

    def set_up(self):
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()
    
    def tear_down(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hashing(self):
        u = User(username='Testuser',email='testuser@example.com')
        u.set_password('mypassword')
        self.assertFalse(u.check_password('notmypassword'))
        self.assertTrue(u.check_password('mypassword'))


if __name__ == '__main__':
    unittest.main(verbosity=2)