import unittest, sqlite3
from jukebox import database

#Path to the database file, different from the deployment db
DB_PATH = 'db/test_data.db'
ENGINE = database.Engine(DB_PATH)

# Constant pre-existing song for testing api
TESTSONG_NAME = 'testsong'
TESTSONG_TYPE = 'mp3'
TESTSONG_DIR = 'testdir'
TESTSONG_ID = 4

NEWSONG_NAME = 'song1'
NEWSONG_TYPE = 'wma'
NEWSONG_DIR = '/home/kekko/audio'

NONEXISTING_ID = 45

class SongsDBAPITestCase(unittest.TestCase):

    '''
    Test cases for the Songs related methods.
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

    def test_get_song(self):
        song = self.connection.get_song(TESTSONG_ID)
        self.assertEqual(song['song_name'],TESTSONG_NAME)
        self.assertEqual(song['media_location'],TESTSONG_DIR)
        self.assertEqual(song['media_type'],TESTSONG_TYPE)

    def test_delete_song(self):
        song = self.connection.get_song(TESTSONG_ID)
        self.assertNotEqual(song, None)
        self.connection.delete_song(TESTSONG_ID)
        song2 = self.connection.get_song(TESTSONG_ID)
        self.assertEqual(song2,None)

    def test_modify_song(self):
        song = self.connection.get_song(TESTSONG_ID)
        newname = song['song_name']+"new"
        newlocation = song['media_location']+"new"
        newtype = song['media_type']+"new"
        self.connection.modify_song(TESTSONG_ID,newname,newlocation,newtype)
        song2 = self.connection.get_song(TESTSONG_ID)
        self.assertEqual(newname,song2['song_name'])
        self.assertEqual(newlocation,song2['media_location'])
        self.assertEqual(newtype,song2['media_type'])

    def test_add_song(self):
        result = self.connection.add_song(NEWSONG_NAME,NEWSONG_DIR,NEWSONG_TYPE,1)
        self.assertNotEqual(result, False)

    def test_get_songs(self):
        result = self.connection.get_songs()
        self.assertGreater(len(result),0)


if __name__ == '__main__':
    print 'Start running Songs tests'
    unittest.main()
