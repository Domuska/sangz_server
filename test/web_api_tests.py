import unittest, copy
import json

import flask

import jukebox.resources as resources
import jukebox.database as database

DB_PATH = 'db/sangz_test.db'
ENGINE = database.Engine(DB_PATH)

APPJSON = "application/json; charset=utf-8"
COLLECTIONJSON = "application/vnd.collection+json"
HAL = "application/hal+json"

# Do we need these?

SANGZ_PROFILE ="http://docs.pwpsangz.apiary.io/#reference/hypermedia-profiles"

#Tell Flask that I am running it in testing mode.
resources.app.config['TESTING'] = True
#Necessary for correct translation in url_for
resources.app.config['SERVER_NAME'] = 'localhost:5000'

#Database Engine utilized in our testing
resources.app.config.update({'Engine': ENGINE})

#Other database parameters.
initial_messages = 20
initial_users = 4


class ResourcesAPITestCase(unittest.TestCase):
    #INITIATION AND TEARDOWN METHODS
    @classmethod
    def setUpClass(cls):
        ''' Creates the database structure. Removes first any preexisting
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
        #This method load the initial values from forum_data_dump.sql
        ENGINE.populate_tables()
        #Activate app_context for using url_for
        self.app_context = resources.app.app_context()
        self.app_context.push()
        #Create a test client
        self.client = resources.app.test_client()

    def tearDown(self):
        '''
        Remove all records from database
        '''
        ENGINE.clear()
        self.app_context.pop()

class ChatTestCase (ResourcesAPITestCase):
    """
    Class for testing Chat resource of sangz server
    """

    # TODO write some test data based on this example below

    #Anonymous user
    message_1_request = {"template": {
        "data": [
            {"name": "headline", "value": "Hypermedia course"},
            {"name": "articleBody", "value": "Do you know any good online"
                                             " hypermedia course?"}
        ]}
    }

    url = "/forum/api/chat/"

    def test_url(self):
        return True
        '''
        Checks that the URL points to the right resource
        '''
        #NOTE: self.shortDescription() shuould work.
        print '('+self.test_url.__name__+')', self.test_url.__doc__,
        with resources.app.test_request_context(self.url):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEquals(view_point, resources.Messages)

    def test_get_messages(self):
        return True
        '''
        Checks that GET Messages return correct status code and data format
        '''
        print '('+self.test_get_messages.__name__+')', self.test_get_messages.__doc__

        #Check that I receive status code 200
        resp = self.client.get(flask.url_for('messages'))
        self.assertEquals(resp.status_code, 200)

        # Check that I receive a collection and adequate href
        data = json.loads(resp.data)['collection']
        self.assertEquals(resources.api.url_for(resources.Messages,
                                                _external=False),
                          data['href'])

        #Check that template is correct
        template_data = data['template']['data']
        self.assertEquals(len(template_data), 4)
        for t_data in template_data:
            self.assertIn('required' and 'prompt' and 'name' and 'value',
                          t_data)
            self.assertIn(t_data['name'], ('headline', 'articleBody',
                                           'author', 'editor'))
        #Check that links are correct
        links = data['links']
        self.assertEquals(len(links), 1)  # Just one link
        self.assertIn('prompt', links[0])
        self.assertEquals(links[0]['rel'], 'users-all')
        self.assertEquals(links[0]['href'],
                          flask.url_for('users', _external=False))

        #Check that items are correct.
        items = data['items']
        self.assertEquals(len(items), initial_messages)
        for item in items:
            self.assertIn(flask.url_for('messages', _external=False),
                          item['href'])
            self.assertIn('links', item)
            self.assertEquals(1, len(item['data']))
            self.assertEquals('headline', item['data'][0]['name'])
            self.assertIn('value', item['data'][0])

    def test_get_messages_mimetype(self):
        return True
        '''
        Checks that GET Messages return correct status code and data format
        '''
        print '('+self.test_get_messages_mimetype.__name__+')', self.test_get_messages_mimetype.__doc__

        #Check that I receive status code 200
        resp = self.client.get(flask.url_for('users'))
        self.assertEquals(resp.status_code, 200)
        self.assertEquals(resp.headers.get('Content-Type',None),
                          COLLECTIONJSON+";"+SANGZ_PROFILE)

    def test_add_message(self):
        return True
        '''
        Test adding messages to the database.
        '''
        print '('+self.test_add_message.__name__+')', self.test_add_message.__doc__

        resp = self.client.post(resources.api.url_for(resources.Messages),
                                headers={'Content-Type': COLLECTIONJSON},
                                data=json.dumps(self.message_1_request)
                               )
        self.assertTrue(resp.status_code == 201)
        url = resp.headers.get('Location')
        self.assertIsNotNone(url)
        resp = self.client.get(url)
        self.assertTrue(resp.status_code == 200)

        resp = self.client.post(resources.api.url_for(resources.Messages),
                                headers={'Content-Type': COLLECTIONJSON},
                                data=json.dumps(self.message_2_request)
                               )
        self.assertTrue(resp.status_code == 201)
        url = resp.headers.get('Location')
        self.assertIsNotNone(url)
        resp = self.client.get(url)
        self.assertTrue(resp.status_code == 200)

        resp = self.client.post(resources.api.url_for(resources.Messages),
                                headers={'Content-Type': COLLECTIONJSON},
                                data=json.dumps(self.message_3_request)
                               )
        self.assertTrue(resp.status_code == 201)
        url = resp.headers.get('Location')
        self.assertIsNotNone(url)
        resp = self.client.get(url)
        self.assertTrue(resp.status_code == 200)

    def test_add_message_wrong_media(self):
        return True
        '''
        Test adding messages with a media different than json
        '''
        print '('+self.test_add_message_wrong_media.__name__+')', self.test_add_message_wrong_media.__doc__
        resp = self.client.post(resources.api.url_for(resources.Messages),
                                headers={'Content-Type': 'text'},
                                data=self.message_1_request.__str__()
                               )
        self.assertTrue(resp.status_code == 415)

    def test_add_message_incorrect_format(self):
        return True
        '''
        Test that add message response correctly when sending erroneous message
        format.
        '''
        print '('+self.test_add_message_incorrect_format.__name__+')', self.test_add_message_incorrect_format.__doc__
        resp = self.client.post(resources.api.url_for(resources.Messages),
                                headers={'Content-Type': COLLECTIONJSON},
                                data=json.dumps(self.message_4_wrong)
                               )
        self.assertTrue(resp.status_code == 400)

        resp = self.client.post(resources.api.url_for(resources.Messages),
                                headers={'Content-Type': COLLECTIONJSON},
                                data=json.dumps(self.message_5_wrong)
                               )
        self.assertTrue(resp.status_code == 400)

class UsersTestCase (ResourcesAPITestCase):

    new_user_request = {
        "template": {
            "data": [
                {
                    "name": "Username",
                    "value": "Test_user1"
                },
                {
                    "name": "Real_Name",
                    "value": "Tahvo Testaaja"
                },
                {
                    "name": "Email",
                    "value": "maili1@abc.com"
                }
            ]
        }
    }


    new_user_request2 = {
        "template": {
            "data": [
                {
                    "name": "Username",
                    "value": "Test_user2"
                },
                {
                    "name": "Real_Name",
                    "value": "Touko Testaaja"
                },
                {
                    "name": "Email",
                    "value": "maili2@abc.com"
                }
            ]
        }
    }

    #Missing mandatory
    new_user_request_missing = {
        "template": {
            "data": [
                {
                    "name": "Real_Name",
                    "value": "Tahvo Testaaja"
                },
                {
                    "name": "Email",
                    "value": "maili1@abc.com"
                }
            ]
        }
    }

    #Invalid format
    new_user_bad_format = {
        "template": {
            "data": [
                {
                    "badname": "Real_Name",
                    "value": "Tahvo Testaaja"
                },
                {
                    "namn": "Email",
                    "value": "maili1@abc.com"
                }
            ]
        }
    }


    def setUp(self):
        super(UsersTestCase, self).setUp()
        self.url = resources.api.url_for(resources.Users,
                                         _external=False)

    def test_url(self):
        '''
        Checks that the URL points to the right resource
        '''
        #NOTE: self.shortDescription() shuould work.
        _url = '/sangz/api/users/'
        print '('+self.test_url.__name__+')', self.test_url.__doc__,
        with resources.app.test_request_context(_url):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEquals(view_point, resources.Users)

    def test_get_users(self):
        '''
        Checks that GET users return correct status code and data format
        '''
        print '('+self.test_get_users.__name__+')', self.test_get_users.__doc__
        #Check that I receive status code 200
        resp = self.client.get(flask.url_for('users'))
        self.assertEquals(resp.status_code, 200)

        # Check that I receive a collection and adequate href
        data = json.loads(resp.data)['collection']
        self.assertEquals(resources.api.url_for(resources.Users,
                                                _external=False),
                          data['href'])

        #Check that template is correct
        template_data = data['template']['data']
        self.assertEquals(len(template_data), 3)
        t_item = template_data[0]
        self.assertIn(('value' and 'prompt' and 'name'), t_item)

        #Check that items are correct.
        items = data['items']
        self.assertEquals(len(items), initial_users)
        for item in items:
            self.assertIn(flask.url_for('users', _external=False),
                          item['href'])

    def test_get_users_mimetype(self):
        '''
        Checks that GET Messages return correct status code and data format
        '''
        print '('+self.test_get_users_mimetype.__name__+')', self.test_get_users_mimetype.__doc__

        #Check that I receive status code 200
        resp = self.client.get(self.url)
        self.assertEquals(resp.status_code, 200)
        self.assertEquals(resp.headers.get('Content-Type',None),
                          COLLECTIONJSON+";"+SANGZ_PROFILE)

    def test_add_user(self):
        '''
        Checks that the user is added correctly
        '''
        print '('+self.test_add_user.__name__+')', self.test_add_user.__doc__

        # With a complete request
        resp = self.client.post(resources.api.url_for(resources.Users),
                                headers={'Content-Type': APPJSON},
                                data=json.dumps(self.new_user_request)
                                )
        self.assertEquals(resp.status_code, 201)


        #With just mandaaory parameters
        resp = self.client.post(resources.api.url_for(resources.Users),
                                headers={'Content-Type': APPJSON},
                                data=json.dumps(self.new_user_request2)
                                )
        self.assertEquals(resp.status_code, 201)


    def test_add_user_missing_mandatory(self):
        '''
        Test that it returns error when is missing a mandatory data
        '''
        print '('+self.test_add_user_missing_mandatory.__name__+')', self.test_add_user_missing_mandatory.__doc__

        # Removing nickname
        resp = self.client.post(resources.api.url_for(resources.Users),
                                headers={'Content-Type': APPJSON},
                                data=json.dumps(self.new_user_request_missing)
                                )
        self.assertEquals(resp.status_code, 400)


    def test_add_bad_formmatted(self):
        '''
        Test that it returns error when address is bad formatted
        '''
        print '('+self.test_add_bad_formmatted.__name__+')', self.test_add_bad_formmatted.__doc__

        # Removing nickname
        resp = self.client.post(resources.api.url_for(resources.Users),
                                headers={'Content-Type': APPJSON},
                                data=json.dumps(self.new_user_bad_format)
                                )
        self.assertEquals(resp.status_code, 400)

class UserTestCase (ResourcesAPITestCase):

    def setUp(self):
        super(UserTestCase, self).setUp()
        user1_id = 1
        user2_id = 2
        self.url1 = resources.api.url_for(resources.User,
                                          userid= user1_id)
        self.url_wrong = resources.api.url_for(resources.User,
                                               userid=user2_id)

    def test_url(self):
        '''
        Checks that the URL points to the right resource
        '''
        #NOTE: self.shortDescription() shuould work.
        print '('+self.test_url.__name__+')', self.test_url.__doc__
        url = "/sangz/api/users/1"
        with resources.app.test_request_context(url):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEquals(view_point, resources.User)

    def test_get_user(self):
        """
        Checks if values returned for single user are correct
        :return: None, creates assertion on error
        """
        print '('+self.test_get_user.__name__+')', self.test_get_user.__doc__
        #Check that I receive status code 200
        resp = self.client.get(flask.url_for('user', userid=1))
        self.assertEquals(resp.status_code, 200)

        data = json.loads(resp.data)
        self.assertEquals(data['id'], "1")
        self.assertEquals(data['realname'], "Axel Foley")



    # TODO: Test for PUT

    # TODO: Test for DELETE



class SongsTestCase (ResourcesAPITestCase):

    song_1_data = {
      "template": {
        "data": [
          {
            "name": "album",
            "value": "new album"
          },
          {
            "name": "artist",
            "value": "new artist"
          },
          {
            "name": "song_name",
            "value": "new song"
          },
          {
            "name": "user_id",
            "value": "1"
          },
          {
            "name": "media_location",
            "value": "Desktop/music"
          }
        ]
      }
    }


    def setUp(self):
        super(SongsTestCase, self).setUp()
        self.url = resources.api.url_for(resources.Songs,
                                         _external=False)

    def test_url(self):
        '''
        Checks that the URL points to the right resource
        '''
        #NOTE: self.shortDescription() shuould work.
        _url = '/sangz/api/songs/'
        print '('+self.test_url.__name__+')', self.test_url.__doc__,
        with resources.app.test_request_context(_url):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEquals(view_point, resources.Songs)

    # TODO complete the tests

if __name__ == '__main__':
    print 'Start running tests'
    unittest.main()
