from app import app, db
from app.models import User, Note, Tag
from datetime import datetime, timedelta
import unittest

class UserModelCase(unittest.TestCase):
	def setUp(self):
		# in-memory SQLite database
		app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
		db.create_all()

	def tearDown(self):
		db.session.remove()
		db.drop_all()

	def test_password_hashing(self):
		u = User(username='user1')
		u.set_password('testing_password')
		self.assertFalse(u.check_password('anything_else'))
		self.assertTrue(u.check_password('testing_password'))

	def test_note_tag(self):
		u = User(username='user1', email='user1@test.com')
		db.session.add(u)
		n = Note(title='title1', body='body1', user_id=u.id)
		db.session.add(n)
		t1 = Tag(name='tag1', user_id=u.id)
		t2 = Tag(name='tag2', user_id=u.id)
		db.session.add_all([t1, t2])
		db.session.commit()

		self.assertFalse(n.is_tagged(t1))
		self.assertFalse(n.is_tagged(t2))
		n.set_tag(t1)
		self.assertTrue(n.is_tagged(t1))
		self.assertFalse(n.is_tagged(t2))
		n.del_tag(t1)
		n.set_tag(t2)
		self.assertFalse(n.is_tagged(t1))
		self.assertTrue(n.is_tagged(t2))
		self.assertEqual(n.tags.count(), 1)
		self.assertEqual(n.tags.first().name, 'tag2')

if __name__ == '__main__':
	unittest.main(verbosity=2)
