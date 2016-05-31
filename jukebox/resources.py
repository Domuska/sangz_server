
# todo: we should prolly split this file into multiple ones. no point having this one big-ass file

# Instructions:
# navigate to root of sangz server, and run: python -m jukebox.resources
# then open the page on your browser in address http://localhost:5000/sangz/XXX
# for example, http://localhost:5000/sangz/api/playlist
# Also make sure you have flask and flask-restful libraries installed





import json

from flask import Flask, request, Response, g, jsonify, _request_ctx_stack, redirect
from flask.ext.restful import Resource, Api, abort
from werkzeug.exceptions import NotFound,  UnsupportedMediaType
from collection_json import Collection
from collection_json import Item
from collection_json import Data

import unicodedata
import database
import time
from datetime import datetime

# todo: edit these to actually present things in our project
# Constants for hypermedia formats and profiles
# Copied from the exercise 3 source code

MIME_TYPE_COLLECTION_JSON = "application/vnd.collection+json; charset=utf-8"
MIME_TYPE_APPLICATION_JSON = "application/json; charset=utf-8"
MIME_TYPE_HAL = "application/hal+json"
FORUM_USER_PROFILE ="/profiles/user-profile"
FORUM_MESSAGE_PROFILE = "/profiles/message-profile"
SANGZ_USER_PROFILE ="/profiles/user-profile"
SANGZ_SONG_PROFILE = "/profiles/song-profile"

ATOM_THREAD_PROFILE = "https://tools.ietf.org/html/rfc4685"
APIARY_PROFILES_URL = "http://docs.pwpsangz.apiary.io/#reference/hypermedia-profiles"

VOTES_TYPE_UPVOTE = 'upvote'
VOTES_TYPE_DOWNVOTE = 'downvote'


# Define the application and the api
# Copied from the exercise 3 source code
app = Flask(__name__)
app.debug = True
# Set the database Engine. In order to modify the database file (e.g. for
# testing) provide the database path   app.config to modify the
# database to be used (for instance for testing)
app.config.update({'Engine': database.Engine()})
# Start the RESTful API.
api = Api(app)

# ERROR HANDLERS
# Copied from the exercise 3 source code
# http://soabits.blogspot.no/2013/05/error-handling-considerations-and-best.html
# I should define a profile for the error.
def create_error_response(status_code, title, message=None):
    ''' Creates a: py: class:`flask.Response` instance when sending back an
      HTTP error response
     : param integer status_code: The HTTP status code of the response
     : param str title: A short description of the problem
     : param message: A long description of the problem
     : rtype:: py: class:`flask.Response`

    '''
    resource_type = None
    resource_url = None
    ctx = _request_ctx_stack.top
    if ctx is not None:
        resource_url = request.path
        resource_type = ctx.url_adapter.match(resource_url)[0]
    response = jsonify(title=title,
                       message=message,
                       resource_url=resource_url,
                       resource_type=resource_type)
    response.status_code = status_code
    return response

# Copied from the exercise 3 source code
@app.errorhandler(404)
def resource_not_found(error):
    return create_error_response(404, "Resource not found",
                                 "This resource url does not exit")
# Copied from the exercise 3 source code
@app.errorhandler(400)
def resource_request_malformed(error):
    return create_error_response(400, "Malformed input format",
                                 "The format of the input is incorrect")
# Copied from the exercise 3 source code
@app.errorhandler(500)
def unknown_error(error):
    return create_error_response(500, "Error",
                                 "The system has failed. Please, contact the administrator")

# Copied from the exercise 3 source code
@app.before_request
def connect_db():
    '''Creates a database connection before the request is proccessed.

    The connection is stored in the application context variable flask.g .
    Hence it is accessible from the request object.'''

    g.con = app.config['Engine'].connect()


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response


# HOOKS
# Copied from the exercise 3 source code
@app.teardown_request
def close_connection(exc):
    ''' Closes the database connection
        Check if the connection is created. It migth be exception appear before
        the connection is created.'''
    if hasattr(g, 'con'):
        g.con.close()


# todo: implement the real playlist stuff somehow
def get_playlist():
    '''
    Function for getting the currently playing playlist
    :return: A dictionary that has song_id: vote count as key-value pairs
    '''

    return g.con.get_all_songs_votes()


#Resources start from here

# The classes are still skeletons, but these will be the resources and methods we will be implementing.
# The skeletons are still missing their proper arguments, add them as you work.
# The original methods from exercise 3 are removed, but take a look at them for help as you work.

class Frontpage(Resource):

    def get(self):
        return Response("you're at the front page of sangz service", 200, mimetype="text/html")

class Users(Resource):

    def get(self):
        #get users from database
        users = g.con.get_users()

        template = {
            "data": [
                {'name': 'nickname', 'value': '', 'prompt': ''}
            ]
        }

        links = [{"href": "www.sangz.com","rel": "home"},
                 {"href": api.url_for(Songs), "rel": "Songs", 'prompt': 'See the list of all songs'},
                 {"href": api.url_for(Playlist), "rel": "Playlist", "prompt":"See the current playlist"},
                 {"href": api.url_for(Chat), "rel": "Chat", "prompt": "See the conversation"}
                 ]

        #links = {}
        collection = Collection(api.url_for(Users), template=template, links=links)
        collection.version = "1.0"
        for user in users:
            item = Item(api.url_for(User, userid = user[0]))
            item.data.append(Data("Id", user[0]))
            item.data.append(Data("nickname", user[1]))
            collection.items.append(item)

        string_data = str(collection)
        return Response(string_data, 200, mimetype="application/vnd.collection+json"+";"+SANGZ_USER_PROFILE)

    def post (self):
        if MIME_TYPE_APPLICATION_JSON != request.headers.get('Content-type', '').lower():
            return create_error_response(415, UnsupportedMediaType,
                                         'Use JSON format in the request and use a proper header')
        username = None
        real_name = None
        email = None
        # BadRequest exception will be thrown if JSON is not valid

        try:
            request_json = request.get_json(force=True)
            template = request_json['template']
            data = template['data']
            for d in data:
                if d['name'] == 'Username' and username is None:
                    username = d['value']
                elif d['name'] == 'Real_Name' and real_name is None:
                    real_name = d['value']
                elif d['name'] == 'Email' and email is None:
                    email = d['value']

            if username is None or real_name is None or email is None:
                raise KeyError

        except:
            return create_error_response(400, "Wrong request format",
                                         "Please use the correct template a")

        string_data = "you sent Username: " + str(username) + ", Real_Name: " + str(real_name) + " Email " + str(email)

        # At this point it is clear that message was formed correctly
        # Todo: should this check if username already exists?

        g.con.add_user(username, real_name, email, 0)
        return Response(string_data, 201, mimetype="text/html")


class User(Resource):
    def get(self, userid):
        user = g.con.get_user(userid)

        if user is None:
            abort(404)

        response = {}

        try:
            url = api.url_for(User, userid=userid)
            links= {"self": {"href": url}}
            response['_links'] = links

            response['id'] = userid
            response['username'] = user['username']
            response['realname'] = user['realname']
            response['email'] = user['email']

        except KeyError:
            abort(500)

        string_data = json.dumps(response)
        return Response(string_data, 200, mimetype=MIME_TYPE_HAL + ";" + SANGZ_USER_PROFILE)

    def put(self, userid):
        user = g.con.get_user(userid)
        if user is None:
            abort(404)

        request_json = request.get_json(force=True)

        new_realname = None
        new_username = None
        new_email = None
        try:
            new_realname = request_json['realname']
        except KeyError:
            pass
        try:
            new_username = request_json['username']
        except KeyError:
            pass
        try:
            new_email = request_json['email']
        except KeyError:
            pass

        g.con.modify_user(userid, new_username, new_realname, new_email)

        return User.get(self , userid)

    def delete(self, userid):
        # Todo: some authentication?
        if g.con.delete_user(userid):
            return Response(status=200)
        return Response(status=404)


class Songs(Resource):
    def get(self):
        #connect to the db
        songs_db = g.con.get_songs()

        links = [{"href": "www.sangz.com", "rel": "home"},
                 {"href": api.url_for(Users), "rel": "Users", "prompt": "Get the list of all users"},
                 {"href": api.url_for(Playlist), "rel": "Playlist", "prompt": "See the current playlist"},
                 {"href": api.url_for(Chat), "rel": "Chat", "prompt": "See the conversation"}
                 ]

        template = {
            "data": [
            {"prompt": "", "name":"user_id",
             "value":""},
            {"prompt": "", "name":"song_name",
             "value":""}
             #{"prompt": "", "name":"media_location",
             #"value":""},
             #{"prompt": "", "name":"media_type",
             #"value":""},
             #{"prompt": "", "name":"artist_id",
             #"value":""},
             #{"prompt": "", "name":"album_id",
             #"value":""},
             #{"prompt": "", "name":"user_id",
             #"value":""}
            ]
        }
        collection = Collection(api.url_for(Songs), template = template, links=links)
        collection.version = "1.0"
        #create items
        print songs_db
        for song in songs_db:
            print song
            item = Item(api.url_for(Song, songid=song[0]))
            item.data.append(Data("ID",song[0]))
            item.data.append(Data("songname",song[1]))
            item.data.append(Data("uploader",api.url_for(User,userid=song[2])))
            #links to artist and album are unavailable because they are not implemented
            collection.items.append(item)
            
        string_data = str(collection)
        return Response(string_data, 200, mimetype="application/vnd.collection+json"+";"+SANGZ_SONG_PROFILE)

    def post(self):

        if MIME_TYPE_COLLECTION_JSON != request.headers.get('Content-Type','').lower():
            return create_error_response(415, "UnsupportedMediaType",
                                         "Use a JSON compatible format")
        request_body = request.get_json(force=True)

        try:
            data = request_body['template']['data']
            song_name = None
            media_location = None
            media_type = None
            artist_id = None
            album_id = None
            user_id = None

            for d in data:
                #This code has a bad performance. We write it like this for
                #simplicity. Another alternative should be used instead.
                if d['name'] == 'song_name':
                    song_name = d['value']
                elif d['name'] == 'media_location':
                    media_location = d['value']
                elif d['name'] == 'media_type':
                    media_type = d['value']
                elif d['name'] == 'artist_id':
                    artist_id = d['value']
                elif d['name'] == 'album_id':
                    album_id = d['value']
                elif d['name'] == 'user_id':
                    user_id = d['value']
                

            #CHECK THAT DATA RECEIVED IS CORRECT
            if not song_name or not media_location:
                return create_error_response(400, "Wrong request format",
                                             "Be sure you include song name and location")
        except:
            #This is launched if either title or body does not exist or if
            # the template.data array does not exist.
            return create_error_response(400, "Wrong request format",
                                         "Be sure you include song name and location")
        #Create the new message and build the response code'
        newsongid = g.con.add_song(song_name, media_location, media_type, user_id, artist_id, album_id)
        if not newsongid:
            return create_error_response(500, "Cannot access the database")

        #Create the Location header with the id of the message created
        url = api.url_for(Songs, songid=newsongid)

        #RENDER
        #Return the response
        return Response(status=201, headers={'Location': url})


class Song(Resource):
    def get(self, songid):
        songs_db = g.con.get_song(songid)
        print songs_db
        if not songs_db:
            errormessage = create_error_response(404, "Resource not found", "No song found here!")
            return (errormessage)

        response = {}
        try:
            self_url = api.url_for(Song, songid=songid)
            print self_url

            links = [
                {'prompt': 'Go back to home page',
                 'rel': 'homepage',
                 'href': api.url_for(Frontpage)},
                {"href": api.url_for(Users),
                 "rel": "Users",
                 "prompt": "Get the list of all users"},
                {"href": api.url_for(Songs),
                 "rel": "Songs",
                 "prompt": "Get the list of all available songs"},
                {'prompt': 'See the current playlist',
                 'rel': 'Playlist',
                 'href': api.url_for(Playlist)},
                {'prompt': 'See the chat',
                 'rel': 'Chat',
                 'href': api.url_for(Chat)}
            ]
            response['links'] = links



            href_object = {'votes': api.url_for(Votes, songid=songid)}
            response['links'].append(href_object)
            href_object = {'self': self_url}
            response['links'].append(href_object)
            href_object = {'adder': api.url_for(User, userid=songs_db['uploader_ID'])}
            response['links'].append(href_object)
            href_object = {'playlist': api.url_for(Playlist)}
            response['links'].append(href_object)

            response['id'] = songid

            response['songname'] = songs_db['song_name']

            # get the album and artist names
            try:
                artist_db = g.con.get_artist(songs_db['artist_ID'])

                if artist_db is None:
                    response['Artist_name'] = ""
                else:
                    response['Artist_name'] = artist_db['artist_name']
            #if there is no entry in DB with album ID, album_name is set to empty
            except KeyError:
                response['Artist_name'] = ""


            try:
                album_db = g.con.get_album(songs_db['album_id'])

                if album_db is None:
                    response['Album_name'] = ""
                else:
                    response['Album_name'] = album_db['album_name']
            except KeyError:
                response['Album_name'] = ""


        except KeyError:
            abort(500)

        string_data = json.dumps(response)

        return Response(string_data, 200, mimetype="application/hal+json"+";"+SANGZ_SONG_PROFILE)

    def put(self, songid):
        #CHECK THAT SONG EXISTS
        songs_db = g.con.get_song(songid)
        if not songs_db:
            errormessage = create_error_response(404, "Resource not found", "No song found here!")
            return (errormessage)

        content_type = request.headers.get('Content-Type','').lower()
        if MIME_TYPE_APPLICATION_JSON != content_type:
            return create_error_response(415, "UnsupportedMediaType1",
                                         "1- Use a JSON compatible format and and utf-8 encoding")


        #PARSE THE REQUEST
        #Extract the request body. In general would be request.data
        #Since the request is JSON I use request.get_json
        #get_json returns a python dictionary after serializing the request body
        #get_json returns None if the body of the request is not formatted
        # using JSON
        request_dict = request.get_json(force=True)
        print request_dict
        if not request_dict:
            return create_error_response(415, "Unsupported Media Type2",
                                         "2- Use a JSON compatible format"
                                        )

        try:
            # data = request_body['template']['data']
            song_name = None
            media_location = None
            media_type = None
            artist_id = None
            album_id = None
            user_id = None

            try:
                song_name = request_dict['songname']
            except KeyError:
                pass
            try:
                media_location = request_dict['medialocation']
            except KeyError:
                pass
            try:
                media_type = request_dict['mediatype']
            except KeyError:
                pass
            try:
                artist_id = request_dict['Artist_ID']
            except KeyError:
                pass
            try:
                album_id = request_dict['Album_ID']
            except KeyError:
                pass

            #CHECK THAT DATA RECEIVED IS CORRECT
            if not song_name or not media_location:
                return create_error_response(400, "Wrong request format1",
                                             "Be sure you include song name and location")
        except:
            #This is launched if either title or body does not exist or if
            # the template.data array does not exist.
            return create_error_response(400, "Wrong request format2",
                                         "Be sure you include song name and location")
        #Create the new message and build the response code'

        newsongid = g.con.modify_song(songid, song_name, media_location, media_type, artist_id, album_id, user_id)
        if not newsongid:
            return create_error_response(500, "Problem with the database",
                                         "Cannot access the database")
        

    def delete(self, songid):
        if g.con.delete_song(songid):
            return Response(status=200)
        else:
            #Send error message
            return create_error_response(404, "Unable to delete",
                                         "There is no song with this ID"
                                        )


class Votes(Resource):


    def post(self, songid):

        '''
        Post a new up vote for a particular song

        Media type supported: application/JSON
        Fields required:
        'type': 'upvote' or 'downvote
        'uploader_id': ID of the user casting a vote
        'song_id': song on which the up- or downvote is cast on

        Response status codes
        201 if a new vote is added////
        400 if the sent message does not include all required fields
        404 if the supplied song_id is faulty
        415 if the wrong content type is used
        '''

        if MIME_TYPE_APPLICATION_JSON != request.headers.get('Content-type', '').lower():
            return create_error_response(415, UnsupportedMediaType,
                                         'Use JSON format in the request and use a proper header')

        # BadRequest exception (401) will be thrown if JSON is not valid
        request_body = request.get_json(force=True)


        try:
            type = request_body['type']
            uploader_id = request_body['voter_id']
            # song_id = request_body['song_id']

            songs_db = g.con.get_songs(songid)
            if not songs_db:
                error_message = create_error_response(404, "Resource not found", "No song found here!")
                return error_message


            if VOTES_TYPE_UPVOTE == type:
                g.con.add_upvotes(songid, uploader_id, int(time.time()))
                return Response(201)
            elif VOTES_TYPE_DOWNVOTE == type:
                g.con.add_downvotes(songid, uploader_id, int(time.time()))
                return Response(201)

            else:
                return create_error_response(404, "Resource not found",
                                             "Be sure you include attribute 'type' and use"
                                             " either code 'upvote' or 'downvote'")

        except:
            return create_error_response(400, "Wrong request format",
                                         "Be sure you include voter_id, song_id and type")




class Playlist(Resource):

    def get(self):
        '''
        Get the playlist as it currently is on the server

        RESPONSE:

        Media type: application/vnd.collection+json

        Profile: Playlist profile

        Link relations in items: song, artist

        Link relations: self, song, songs

        Response status codes
        200 if all is okay

        '''

        playlist = get_playlist()


        links = [{"href": "www.sangz.com", "rel": "home"},
                 {"href": api.url_for(Users), "rel": "Users", "prompt": "Get the list of all users"},
                 {"href": api.url_for(Chat), "rel": "Chat", "prompt": "Get chat messages"},
                 {'prompt': 'see the full list of songs',
                  'rel': 'Songs',
                  'href': api.url_for(Songs)}
                 ]

        envelope = {}
        collection = {}
        envelope['collection'] = collection

        collection['links'] = links
        collection['version'] = "1.0"
        collection['href'] = api.url_for(Playlist)
        # todo: add the links when other resources are added to the routes

        items = []

        # the "items" in response is filled
        for key in playlist:
            song = { }
            song['href'] = api.url_for(Song, songid=key)
            # song['href_vote'] = api.url_for(Votes, songid=key)

            song['links'] = []
            href_object = {'href': api.url_for(Votes, songid=key)}
            song['links'].append(href_object)

            # get an individual song's details using the key in playlist dictionary
            song_db = g.con.get_song(key)

            # get the artist's id from song_db and use it to get the artist's info from db
            artist_db = g.con.get_artist(song_db.get('artist_ID', 'None'))

            upvote_count = g.con.get_upvotes_by_song(key)
            downvote_count = g.con.get_downvotes_by_song(key)
            final_vote_count = upvote_count.get('votes') - downvote_count.get('votes')


            song['data'] = []
            value = {'name': 'song_name', 'value': song_db.get('song_name')}
            song['data'].append(value)

            # no artist for this song
            if artist_db is None:
                value = {'name': 'artist_name', 'value': ''}

            else:
                value = {'name': 'artist_name', 'value': artist_db.get('artist_name')}

            song['data'].append(value)
            value = {'name': 'vote_count', 'value': final_vote_count}
            song['data'].append(value)

            items.append(song)

        collection['items'] = items

        string_data = json.dumps(envelope)

        return Response(string_data, 200, 
        mimetype="application/vnd.collection+json")


class Chat(Resource):

    def get(self):

        '''
        Function for getting the whole chat backlog

        RESPONSE:

        Media type: application/vnd.collection+json

        Profile: Chat profile

        Link relations in items: None

        Link relations: self, front page

        Response status codes
        200 if all is okay

        '''
        envelope = {}
        collection = {}
        envelope['collection'] = collection

        collection['version'] = '1.0'
        collection['href'] = api.url_for(Chat)
        # todo: add links when other resources are added to the routes

        collection['links'] = [
            {'prompt': 'Go back to home page',
             'rel': 'homepage',
             'href': api.url_for(Frontpage)},
            {"href": api.url_for(Users),
             "rel": "Users",
             "prompt": "Get the list of all users"},
            {"href": api.url_for(Songs),
             "rel": "Songs",
             "prompt": "Get the list of all available songs"},
            {'prompt': 'See the current playlist',
             'rel': 'playlist',
             'href': api.url_for(Playlist)},
        ]

        items = []

        chat_db = g.con.get_messages_all()

        # add the messages
        # go through the rows in the returned array to get details
        for message_row in chat_db:
            message = {}
            # todo: not really nice to just use mysterious array rows, figure out better way

            user_db = g.con.get_user(message_row[1])

            message['data'] = []

            value = {'name': 'message_body', 'value': message_row[3]}
            message['data'].append(value)

            timestamp = message_row[2]
            if timestamp is None:
                value = {'name': 'timestamp', 'value': ''}
            else:
                value = {'name': 'timestamp', 'value': message_row[2]}

            message['data'].append(value)

            value = {'name': 'sender', 'value': user_db.get('username')}
            message['data'].append(value)

            items.append(message)

        collection['items'] = items

        # add the template
        collection['template'] = {
            'data': [
                {'prompt': '', 'name': 'message_body',
                 'value': '', 'required': True},

                {'prompt': '', 'name': 'sender',
                 'value': '', 'required': True},
            ]
        }

        string_data = json.dumps(envelope)

        return Response(string_data, 200, mimetype="application/vnd.collection+json")

    def post(self):

        '''
        Post a new message to the chat

        Media type supported: application/JSON
        Fields required:
        'sender_id': ID of the sender
        'message_body': body of the message

        Response status codes
        201 if a new message is added
        400 if the sent message does not include all required fields
        415 if the wrong content type is used
        '''

        if MIME_TYPE_APPLICATION_JSON != request.headers.get('Content-type', '').lower():
            return create_error_response(415, UnsupportedMediaType,
                                         'Use JSON format in the request and use a proper header')

        # BadRequest exception will be thrown if JSON is not valid
        request_json = request.get_json(force=True)

        # todo: not good idea to have client send user_id, look at authentication and figure out a better way

        sender_id = None
        message_body = None

        try:
            data = request_json['template']['data']

            entries = []

            # maybe not the best way to do this, but get the name and body
            # from the data array
            sender_id = data[0]['value']
            message_body = data[1]['value']

            if sender_id is None or message_body is None:
                return create_error_response(400, 'Wrong request format',
                                             'Please include sender_id and message_body.')
        except:
            return create_error_response(400, "Wrong request format",
                                         "Please use the correct template a")

        string_data = "you sent id: " + sender_id + ", message: " + message_body

        g.con.add_message(sender_id, message_body, time.time())

        return Response(string_data, 201, mimetype="text/html")




#Define the routes
api.add_resource(Users, '/sangz/api/users/',
                 endpoint='users')
api.add_resource(User, '/sangz/api/users/<userid>',
                 endpoint = 'user')
api.add_resource(Frontpage, '/sangz/api/',
                 endpoint='')
api.add_resource(Playlist, '/sangz/api/playlist/',
                 endpoint='playlist')
api.add_resource(Songs, '/sangz/api/songs/',
                 endpoint='songs')
api.add_resource(Song, '/sangz/api/songs/<songid>/',
                 endpoint='song')
api.add_resource(Chat, '/sangz/api/chat/',
                 endpoint='chat')
api.add_resource(Votes, '/sangz/api/votes/<songid>/',
                 endpoint='votes')


# won't be implemented
# api.add_resource(Artists, '/sangz/api/artists/',
#                  endpoint='artists')
# api.add_resource(Artist, '/sangz/api/artists/<artistid>/',
#                  endpoint='artist')
# api.add_resource(Albums, '/sangz/api/albums/',
#                  endpoint='albums')
# api.add_resource(Album, '/sangz/api/albums/<albumid>',
#                  endpoint='albums')

#Redirect profile
@app.route('/profiles/<profile_name>')
def redirect_to_profile(profile_name):
    return redirect(APIARY_PROFILES_URL + profile_name)


#Start the application
#DATABASE SHOULD HAVE BEEN POPULATED PREVIOUSLY
if __name__ == '__main__':
    #Debug true activates automatic code reloading and improved error messages
    app.run(debug=True)
