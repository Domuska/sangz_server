import unittest, sqlite3
from jukebox import database

#Path to the database file, different from the deployment db
DB_PATH = 'db/test_data.db'
ENGINE = database.Engine(DB_PATH)

TESTCREDENTIALS_ID = 1
TESTCREDENTIALS_HASH = """nogoospassword"""



class LoginDBAPITestCase(unittest.TestCase):

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

    def test_get_credentials(self):
        '''
        This function tests get credentials api function
        :return: nothinng
        '''
        cred = self.connection.get_credentials(TESTCREDENTIALS_ID)
        self.assertEqual(cred, TESTCREDENTIALS_HASH)




''' test theese methods:
    def modify_credentials(self, ID, password):
    def delete_credentials(self, ID):
    def add_credentials(self, ID, password):

'''
if __name__ == '__main__':
    print 'Start running user tests'
    unittest.main()
