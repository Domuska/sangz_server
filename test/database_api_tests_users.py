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
INITIAL_SIZE = 5


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


    '''
        Test these functions
        def add_user(self, nickname, real_name, email, privilege_level):
        def modify_user(self, user_ID, username=None, realname=None, email=None, privilege_level=None):
        def get_user(self, ID):
        def delete_user(self, ID):
        def get_users(self, upperlimit=None, offset=0):
    '''

if __name__ == '__main__':
    print 'Start running user tests'
    unittest.main()
