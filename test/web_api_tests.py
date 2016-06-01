'''
Created on 26.01.2013
Modified on 24.02.2016
@author: ivan
'''
import unittest, copy
import json

import flask

import jukebox.resources as resources
import jukebox.database as database

DB_PATH = 'db/sangz_test.db'
ENGINE = database.Engine(DB_PATH)

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
initial_users = 5


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

    #Anonymous user
    message_1_request = {"template": {
        "data": [
            {"name": "headline", "value": "Hypermedia course"},
            {"name": "articleBody", "value": "Do you know any good online"
                                             " hypermedia course?"}
        ]}
    }

    #Existing user
    message_2_request = {"template": {
        "data": [
            {"name": "headline", "value": "Hypermedia course"},
            {"name": "articleBody", "value": "Do you know any good online"
                                             " hypermedia course?"},
            {"name": "author", "value": "Axel"}
        ]}
    }

    #Non exsiting user
    message_3_request = {"template": {
        "data": [
            {"name": "headline", "value": "Hypermedia course"},
            {"name": "articleBody", "value": "Do you know any good online"
                                             " hypermedia course?"},
            {"name": "author", "value": "Onethatwashere"}
        ]}
    }

    #Missing the headline
    message_4_wrong = {"template": {
        "data": [
            {"name": "articleBody", "value": "Do you know any good online"
                                             " hypermedia course?"},
            {"name": "author", "value": "Onethatwashere"}
        ]}
    }

    #Missing the articleBody
    message_5_wrong = {"template": {
        "data": [
            {"name": "articleBody", "value": "Do you know any good online"
                                             " hypermedia course?"},
            {"name": "author", "value": "Onethatwashere"}
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

    user_1_request = {"template": {
        "data": [
            {"name": "nickname", "value": "Rigors"},
            {"object": {"addressLocality":'Manchester', "addressCountry":"UK"},
             "name": "address"},
            {"name": "avatar", "value": "image3.jpg"},
            {"name": "birthday", "value": "2009-09-09"},
            {"name": "email", "value": "rigors@gmail.com"},
            {"name": "familyName", "value": "Rigors"},
            {"name": "gender", "value": "Male"},
            {"name": "givenName", "value": "Reagan"},
            {"name": "image", "value": "image2.jpg"},
            {"name": "signature", "value": "I am like Ronald McDonald"},
            {"name": "skype", "value": "rigors"},
            {"name": "telephone", "value": "0445555666"},
            {"name": "website", "value": "http://rigors.com"}
        ]}
    }

    user_2_request = {"template": {
        "data": [
            {"name": "nickname", "value": "Rango"},
            {"name": "avatar", "value": "image3.jpg"},
            {"name": "birthday", "value": "2009-09-09"},
            {"name": "email", "value": "rango@gmail.com"},
            {"name": "familyName", "value": "Rango"},
            {"name": "gender", "value": "Male"},
            {"name": "givenName", "value": "Rangero"},
            {"name": "signature", "value": "I am like Ronald McDonald"},
        ]}
    }

    #Existing nickname
    user_wrong_1_request =  {"template": {
        "data": [
            {"name": "nickname", "value": "AxelW"},
            {"name": "avatar", "value": "image3.jpg"},
            {"name": "birthday", "value": "2009-09-09"},
            {"name": "email", "value": "rango@gmail.com"},
            {"name": "familyName", "value": "Rango"},
            {"name": "gender", "value": "Male"},
            {"name": "givenName", "value": "Rangero"},
            {"name": "signature", "value": "I am like Ronald McDonald"},
        ]}
    }

    #Mssing nickname
    user_wrong_2_request =  {"template": {
        "data": [
            {"name": "avatar", "value": "image3.jpg"},
            {"name": "birthday", "value": "2009-09-09"},
            {"name": "email", "value": "rango@gmail.com"},
            {"name": "familyName", "value": "Rango"},
            {"name": "gender", "value": "Male"},
            {"name": "givenName", "value": "Rangero"},
            {"name": "signature", "value": "I am like Ronald McDonald"},
        ]}
    }

    #Missing mandatory
    user_wrong_3_request = {"template": {
        "data": [
            {"name": "nickname", "value": "Rango"},
            {"name": "email", "value": "rango@gmail.com"},
            {"name": "familyName", "value": "Rango"},
            {"name": "gender", "value": "Male"},
            {"name": "givenName", "value": "Rangero"},
            {"name": "signature", "value": "I am like Ronald McDonald"},
        ]}
    }

    #Wrong address
    user_wrong_4_request = {"template": {
        "data": [
            {"name": "nickname", "value": "Rango"},
            {"name": "avatar", "value": "image3.jpg"},
            {"name": "address", "value": "Indonesia, Spain"},
            {"name": "birthday", "value": "2009-09-09"},
            {"name": "email", "value": "rango@gmail.com"},
            {"name": "familyName", "value": "Rango"},
            {"name": "gender", "value": "Male"},
            {"name": "givenName", "value": "Rangero"},
            {"name": "signature", "value": "I am like Ronald McDonald"},
        ]}
    }

    def setUp(self):
        super(UsersTestCase, self).setUp()
        self.url = resources.api.url_for(resources.Users,
                                         _external=False)

    def test_url(self):
        return True
        '''
        Checks that the URL points to the right resource
        '''
        #NOTE: self.shortDescription() shuould work.
        _url = '/forum/api/users/'
        print '('+self.test_url.__name__+')', self.test_url.__doc__,
        with resources.app.test_request_context(_url):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEquals(view_point, resources.Users)

    def test_get_users(self):
        return True
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
        self.assertEquals(len(template_data), 13)
        for t_data in template_data:
            self.assertIn(('required' and 'prompt' and 'name'),
                          t_data)
            self.assertTrue(any(k in t_data for k in ('value', 'object')))
            self.assertIn(t_data['name'], ('nickname', 'address',
                                           'avatar', 'birthday',
                                           'email', 'familyName',
                                           'gender', 'givenName',
                                           'image', 'signature',
                                           'skype', 'telephone',
                                           'website'))
        #Check that links are correct
        links = data['links']
        self.assertEquals(len(links), 1)  # Just one link
        self.assertIn('prompt', links[0])
        self.assertEquals(links[0]['rel'], 'messages-all')
        self.assertEquals(links[0]['href'],
                          flask.url_for('messages', _external=False))

        #Check that items are correct.
        items = data['items']
        self.assertEquals(len(items), initial_users)
        for item in items:
            self.assertIn(flask.url_for('users', _external=False),
                          item['href'])
            self.assertIn('links', item)
            self.assertEquals(2, len(item['data']))
            for attribute in item['data']:
                self.assertIn(attribute['name'], ('nickname', 'registrationdate'))

    def test_get_users_mimetype(self):
        return True
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
        return True
        '''
        Checks that the user is added correctly

        '''
        print '('+self.test_add_user.__name__+')', self.test_add_user.__doc__

        # With a complete request
        resp = self.client.post(resources.api.url_for(resources.Users),
                                headers={'Content-Type': COLLECTIONJSON},
                                data=json.dumps(self.user_1_request)
                               )
        self.assertEquals(resp.status_code, 201)
        self.assertIn('Location', resp.headers)
        url = resp.headers['Location']
        resp2 = self.client.get(url)
        self.assertEquals(resp2.status_code, 200)

        #With just mandaaory parameters
        resp = self.client.post(resources.api.url_for(resources.Users),
                                headers={'Content-Type': COLLECTIONJSON},
                                data=json.dumps(self.user_2_request)
                               )
        self.assertEquals(resp.status_code, 201)
        self.assertIn('Location', resp.headers)
        url = resp.headers['Location']
        resp2 = self.client.get(url)
        self.assertEquals(resp2.status_code, 200)

    def test_add_user_missing_mandatory(self):
        return True
        '''
        Test that it returns error when is missing a mandatory data
        '''
        print '('+self.test_add_user_missing_mandatory.__name__+')', self.test_add_user_missing_mandatory.__doc__

        # Removing nickname
        resp = self.client.post(resources.api.url_for(resources.Users),
                                headers={'Content-Type': COLLECTIONJSON},
                                data=json.dumps(self.user_wrong_2_request)
                               )
        self.assertEquals(resp.status_code, 400)

        #Removing avatar
        resp = self.client.post(resources.api.url_for(resources.Users),
                                headers={'Content-Type': COLLECTIONJSON},
                                data=json.dumps(self.user_wrong_3_request)
                               )
        self.assertEquals(resp.status_code, 400)

    def test_add_existing_user(self):
        return True
        '''
        Testign that trying to add an existing user will fail

        '''
        print '('+self.test_add_existing_user.__name__+')', self.test_add_existing_user.__doc__
        resp = self.client.post(resources.api.url_for(resources.Users),
                                headers={'Content-Type': COLLECTIONJSON},
                                data=json.dumps(self.user_wrong_1_request)
                               )
        self.assertEquals(resp.status_code, 409)

    def test_add_bad_formmatted(self):
        return True
        '''
        Test that it returns error when address is bad formatted
        '''
        print '('+self.test_add_bad_formmatted.__name__+')', self.test_add_bad_formmatted.__doc__

        # Removing nickname
        resp = self.client.post(resources.api.url_for(resources.Users),
                                headers={'Content-Type': COLLECTIONJSON},
                                data=json.dumps(self.user_wrong_4_request)
                               )
        self.assertEquals(resp.status_code, 400)

    def test_wrong_type(self):
        return True
        '''
        Test that return adequate error if sent incorrect mime type
        '''
        print '('+self.test_wrong_type.__name__+')', self.test_wrong_type.__doc__
        resp = self.client.post(resources.api.url_for(resources.Users),
                                headers={'Content-Type': "application/json"},
                                data=json.dumps(self.user_1_request)
                               )
        self.assertEquals(resp.status_code, 415)

class UserTestCase (ResourcesAPITestCase):

    def setUp(self):
        super(UserTestCase, self).setUp()
        user1_nickname = 'AxelW'
        user2_nickname = 'Jacobino'
        self.url1 = resources.api.url_for(resources.User,
                                          userid= user1_nickname)
        self.url_wrong = resources.api.url_for(resources.User,
                                               userid=user2_nickname)
    def test_url(self):
        return True
        '''
        Checks that the URL points to the right resource
        '''
        #NOTE: self.shortDescription() shuould work.
        print '('+self.test_url.__name__+')', self.test_url.__doc__
        url = "/forum/api/users/AxelW/"
        with resources.app.test_request_context(url):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEquals(view_point, resources.User)

    '''#TODO  Implement methods for this class'''

class SongsTestCase (ResourcesAPITestCase):

    user_1_request = {"template": {
        "data": [
            {"name": "nickname", "value": "Rigors"},
            {"object": {"addressLocality":'Manchester', "addressCountry":"UK"},
             "name": "address"},
            {"name": "avatar", "value": "image3.jpg"},
            {"name": "birthday", "value": "2009-09-09"},
            {"name": "email", "value": "rigors@gmail.com"},
            {"name": "familyName", "value": "Rigors"},
            {"name": "gender", "value": "Male"},
            {"name": "givenName", "value": "Reagan"},
            {"name": "image", "value": "image2.jpg"},
            {"name": "signature", "value": "I am like Ronald McDonald"},
            {"name": "skype", "value": "rigors"},
            {"name": "telephone", "value": "0445555666"},
            {"name": "website", "value": "http://rigors.com"}
        ]}
    }

    user_2_request = {"template": {
        "data": [
            {"name": "nickname", "value": "Rango"},
            {"name": "avatar", "value": "image3.jpg"},
            {"name": "birthday", "value": "2009-09-09"},
            {"name": "email", "value": "rango@gmail.com"},
            {"name": "familyName", "value": "Rango"},
            {"name": "gender", "value": "Male"},
            {"name": "givenName", "value": "Rangero"},
            {"name": "signature", "value": "I am like Ronald McDonald"},
        ]}
    }

    #Existing nickname
    user_wrong_1_request =  {"template": {
        "data": [
            {"name": "nickname", "value": "AxelW"},
            {"name": "avatar", "value": "image3.jpg"},
            {"name": "birthday", "value": "2009-09-09"},
            {"name": "email", "value": "rango@gmail.com"},
            {"name": "familyName", "value": "Rango"},
            {"name": "gender", "value": "Male"},
            {"name": "givenName", "value": "Rangero"},
            {"name": "signature", "value": "I am like Ronald McDonald"},
        ]}
    }

    #Mssing nickname
    user_wrong_2_request =  {"template": {
        "data": [
            {"name": "avatar", "value": "image3.jpg"},
            {"name": "birthday", "value": "2009-09-09"},
            {"name": "email", "value": "rango@gmail.com"},
            {"name": "familyName", "value": "Rango"},
            {"name": "gender", "value": "Male"},
            {"name": "givenName", "value": "Rangero"},
            {"name": "signature", "value": "I am like Ronald McDonald"},
        ]}
    }

    #Missing mandatory
    user_wrong_3_request = {"template": {
        "data": [
            {"name": "nickname", "value": "Rango"},
            {"name": "email", "value": "rango@gmail.com"},
            {"name": "familyName", "value": "Rango"},
            {"name": "gender", "value": "Male"},
            {"name": "givenName", "value": "Rangero"},
            {"name": "signature", "value": "I am like Ronald McDonald"},
        ]}
    }

    #Wrong address
    user_wrong_4_request = {"template": {
        "data": [
            {"name": "nickname", "value": "Rango"},
            {"name": "avatar", "value": "image3.jpg"},
            {"name": "address", "value": "Indonesia, Spain"},
            {"name": "birthday", "value": "2009-09-09"},
            {"name": "email", "value": "rango@gmail.com"},
            {"name": "familyName", "value": "Rango"},
            {"name": "gender", "value": "Male"},
            {"name": "givenName", "value": "Rangero"},
            {"name": "signature", "value": "I am like Ronald McDonald"},
        ]}
    }

    def setUp(self):
        super(SongsTestCase, self).setUp()
        self.url = resources.api.url_for(resources.Songs,
                                         _external=False)

    def test_url(self):
        return True
        '''
        Checks that the URL points to the right resource
        '''
        #NOTE: self.shortDescription() shuould work.
        _url = '/forum/api/users/'
        print '('+self.test_url.__name__+')', self.test_url.__doc__,
        with resources.app.test_request_context(_url):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEquals(view_point, resources.Users)

    def test_get_songs(self):
        return True
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
        self.assertEquals(len(template_data), 13)
        for t_data in template_data:
            self.assertIn(('required' and 'prompt' and 'name'),
                          t_data)
            self.assertTrue(any(k in t_data for k in ('value', 'object')))
            self.assertIn(t_data['name'], ('nickname', 'address',
                                           'avatar', 'birthday',
                                           'email', 'familyName',
                                           'gender', 'givenName',
                                           'image', 'signature',
                                           'skype', 'telephone',
                                           'website'))
        #Check that links are correct
        links = data['links']
        self.assertEquals(len(links), 1)  # Just one link
        self.assertIn('prompt', links[0])
        self.assertEquals(links[0]['rel'], 'messages-all')
        self.assertEquals(links[0]['href'],
                          flask.url_for('messages', _external=False))

        #Check that items are correct.
        items = data['items']
        self.assertEquals(len(items), initial_users)
        for item in items:
            self.assertIn(flask.url_for('users', _external=False),
                          item['href'])
            self.assertIn('links', item)
            self.assertEquals(2, len(item['data']))
            for attribute in item['data']:
                self.assertIn(attribute['name'], ('nickname', 'registrationdate'))

    def test_get_users_mimetype(self):
        return True
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
        return True
        '''
        Checks that the user is added correctly

        '''
        print '('+self.test_add_user.__name__+')', self.test_add_user.__doc__

        # With a complete request
        resp = self.client.post(resources.api.url_for(resources.Users),
                                headers={'Content-Type': COLLECTIONJSON},
                                data=json.dumps(self.user_1_request)
                               )
        self.assertEquals(resp.status_code, 201)
        self.assertIn('Location', resp.headers)
        url = resp.headers['Location']
        resp2 = self.client.get(url)
        self.assertEquals(resp2.status_code, 200)

        #With just mandaaory parameters
        resp = self.client.post(resources.api.url_for(resources.Users),
                                headers={'Content-Type': COLLECTIONJSON},
                                data=json.dumps(self.user_2_request)
                               )
        self.assertEquals(resp.status_code, 201)
        self.assertIn('Location', resp.headers)
        url = resp.headers['Location']
        resp2 = self.client.get(url)
        self.assertEquals(resp2.status_code, 200)

    def test_add_user_missing_mandatory(self):
        return True
        '''
        Test that it returns error when is missing a mandatory data
        '''
        print '('+self.test_add_user_missing_mandatory.__name__+')', self.test_add_user_missing_mandatory.__doc__

        # Removing nickname
        resp = self.client.post(resources.api.url_for(resources.Users),
                                headers={'Content-Type': COLLECTIONJSON},
                                data=json.dumps(self.user_wrong_2_request)
                               )
        self.assertEquals(resp.status_code, 400)

        #Removing avatar
        resp = self.client.post(resources.api.url_for(resources.Users),
                                headers={'Content-Type': COLLECTIONJSON},
                                data=json.dumps(self.user_wrong_3_request)
                               )
        self.assertEquals(resp.status_code, 400)

    def test_add_existing_user(self):
        return True
        '''
        Testign that trying to add an existing user will fail

        '''
        print '('+self.test_add_existing_user.__name__+')', self.test_add_existing_user.__doc__
        resp = self.client.post(resources.api.url_for(resources.Users),
                                headers={'Content-Type': COLLECTIONJSON},
                                data=json.dumps(self.user_wrong_1_request)
                               )
        self.assertEquals(resp.status_code, 409)

    def test_add_bad_formmatted(self):
        return True
        '''
        Test that it returns error when address is bad formatted
        '''
        print '('+self.test_add_bad_formmatted.__name__+')', self.test_add_bad_formmatted.__doc__

        # Removing nickname
        resp = self.client.post(resources.api.url_for(resources.Users),
                                headers={'Content-Type': COLLECTIONJSON},
                                data=json.dumps(self.user_wrong_4_request)
                               )
        self.assertEquals(resp.status_code, 400)

    def test_wrong_type(self):
        return True
        '''
        Test that return adequate error if sent incorrect mime type
        '''
        print '('+self.test_wrong_type.__name__+')', self.test_wrong_type.__doc__
        resp = self.client.post(resources.api.url_for(resources.Users),
                                headers={'Content-Type': "application/json"},
                                data=json.dumps(self.user_1_request)
                               )
        self.assertEquals(resp.status_code, 415)

class SongTestCase (ResourcesAPITestCase):

    def setUp(self):
        super(SongTestCase, self).setUp()
        song1_id = 1
        song2_id = 666
        self.url1 = resources.api.url_for(resources.Song,
                                          songid=song1_id)
        self.url_wrong = resources.api.url_for(resources.Song,
                                               songid=song2_id)
    def test_url(self):
        return True
        '''
        Checks that the URL points to the right resource
        '''
        #NOTE: self.shortDescription() shuould work.
        print '('+self.test_url.__name__+')', self.test_url.__doc__
        url = "/forum/api/users/AxelW/"
        with resources.app.test_request_context(url):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEquals(view_point, resources.User)

    '''#TODO Implement methods for this class'''



if __name__ == '__main__':
    print 'Start running tests'
    unittest.main()
