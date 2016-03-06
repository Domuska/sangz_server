import unittest, sqlite3
from jukebox import database

#Path to the database file, different from the deployment db
DB_PATH = 'db/test_data.db'
ENGINE = database.Engine(DB_PATH)

#CONSTANTS DEFINING DIFFERENT USERS AND USER PROPERTIES
USER1_NICKNAME = 'Axel f.'
USER1_REAL_NAME = 'Axel Foley'
USER1_ID = 1
USER1_EMAIL = 'a.foley@lapd.com'
USER1_PRIVILEGES = 1
'''
INSERT INTO "users" VALUES(1,'Axel f.','Axel Foley','a.foley@lapd.com',1);
'''

NEW_USER = {'nicname': 'Commando',
            'realname': 'John Matrix',
            'email': 'secretmail@logcabin.com',
            'privilege_level' : 1
            }
USER_WRONG_NICKNAME = 'Batty'
INITIAL_SIZE = 4


class UserDBAPITestCase(unittest.TestCase):

    '''
    Test cases for the Users related methods.
    '''
    #INITIATION AND TEARDOWN METHODS
    @classmethod
    def setUpClass(cls):
        ''' Creates the database structure. cRemoves first any preexisting
            database file
        '''
        print "Testing ", cls.__name__
        ENGINE.remove_database()
        ENGINE.create_tables()

    @classmethod
    def tearDownClass(cls):
        '''Remove the testing database'''
        print "Testing ENDED for ", cls.__name__
        ENGINE.remove_database()

    def setUp(self):
        '''
        Populates the database
        '''
        #This method load the initial values from data_dump.sql
        ENGINE.populate_tables()
        #Creates a Connection instance to use the API
        self.connection = ENGINE.connect()

    def tearDown(self):
        '''
        Close underlying connection and remove all records from database
        '''
        self.connection.close()
        ENGINE.clear()


    def test_get_user(self):
        '''
        tests get_user(self, ID) method
        '''


        print '('+self.test_get_user.__name__+')', \
            self.test_get_user.__doc__

        #Test with an existing user
        user = self.connection.get_user(USER1_ID)
        gotid = user.get('user_id')
        realname = user.get('realname')
        nickname = user.get('username')
        email = user.get('email')
        privileges = user.get('privilege_level')

        self.assertEqual(gotid, USER1_ID)
        self.assertEqual(realname, USER1_REAL_NAME)
        self.assertEqual(nickname, USER1_NICKNAME)
        self.assertEqual(email, USER1_EMAIL)
        self.assertEqual(privileges, USER1_PRIVILEGES)

    def test_add_user(self):
        '''
        tests add_user(self, nickname, real_name, email, privilege_level function
        '''

        result = self.connection.add_user(NEW_USER['nicname'], NEW_USER['realname'], NEW_USER['email'], NEW_USER['privilege_level']);
        self.assertNotEqual(result, False)

        #Test with an new user
        user = self.connection.get_user(result)
        realname = user.get('realname')
        nickname = user.get('username')
        email = user.get('email')
        privileges = user.get('privilege_level')

        self.assertEqual(realname, NEW_USER['realname'])
        self.assertEqual(nickname, NEW_USER['nicname'])
        self.assertEqual(email, NEW_USER['email'])
        self.assertEqual(privileges, NEW_USER['privilege_level'])


    def test_modify_user(self):
        '''
        test  modify_user(self, user_ID, username=None, realname=None, email=None, privilege_level=None)
        '''

        # get info from existing user
        user = self.connection.get_user(USER1_ID)
        gotid = user.get('user_id')
        realname = user.get('realname')
        nickname = user.get('username')
        email = user.get('email')
        privileges = user.get('privilege_level')

        # modify that info
        self.connection.modify_user(USER1_ID,USER1_NICKNAME+"_MOD",USER1_REAL_NAME+"_MOD",USER1_EMAIL+"_MOD")

        user2 = self.connection.get_user(USER1_ID)

        # get info again to see it actually changed
        self.assertEqual(user2['user_id'],USER1_ID)
        self.assertEqual(user2['realname'],USER1_REAL_NAME+"_MOD")
        self.assertEqual(user2['username'],USER1_NICKNAME+"_MOD")
        self.assertEqual(user2['email'],USER1_EMAIL+"_MOD")

        # revert changes
        self.connection.modify_user(USER1_ID,USER1_NICKNAME,USER1_REAL_NAME,USER1_EMAIL)

    def test_delete_user(self):
        '''
        tests         def delete_user(self, ID)
        '''
        user = self.connection.get_user(USER1_ID)
        self.assertNotEqual(user, None)
        self.connection.delete_user(USER1_ID)
        user = self.connection.get_user(USER1_ID)
        self.assertEqual(user,None)

    def test_wrong_ID(self):
        user = self.connection.get_user(8321439824)
        self.assertEqual(user,None)

'''
    Discussion needed about how get_users() should actually behave
    def test_get_users(self):

        users = self.connection.get_users()

        self.assertEqual(users.)
'''


if __name__ == '__main__':
    print 'Start running user tests'
    unittest.main()
