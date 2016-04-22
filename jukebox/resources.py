
# todo: we should prolly split this file into multiple ones. no point having this one big-ass file

# Instructions:
# navigate to root of sangz server, and run: python -m jukebox.resources
# then open the page on your browser in address http://localhost:5000/sangz/XXX
# for example, http://localhost:5000/sangz/api/playlist





import json

from flask import Flask, request, Response, g, jsonify, _request_ctx_stack, redirect
from flask.ext.restful import Resource, Api, abort
from werkzeug.exceptions import NotFound,  UnsupportedMediaType

from utils import RegexConverter
import database

# Constants for hypermedia formats and profiles
# Copied from the excercise 3 source code
COLLECTIONJSON = "application/vnd.collection+json"
HAL = "application/hal+json"
FORUM_USER_PROFILE ="/profiles/user-profile"
FORUM_MESSAGE_PROFILE = "/profiles/message-profile"
ATOM_THREAD_PROFILE = "https://tools.ietf.org/html/rfc4685"
APIARY_PROFILES_URL = "STUDENT_APIARY_PROJECT/#reference/profiles/"

# Define the application and the api
# Copied from the excercise 3 source code
app = Flask(__name__)
app.debug = True
# Set the database Engine. In order to modify the database file (e.g. for
# testing) provide the database path   app.config to modify the
# database to be used (for instance for testing)
app.config.update({'Engine': database.Engine()})
# Start the RESTful API.
api = Api(app)



# ERROR HANDLERS
# Copied from the excercise 3 source code
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

# Copied from the excercise 3 source code
@app.errorhandler(404)
def resource_not_found(error):
    return create_error_response(404, "Resource not found",
                                 "This resource url does not exit")
# Copied from the excercise 3 source code
@app.errorhandler(400)
def resource_request_malformed(error):
    return create_error_response(400, "Malformed input format",
                                 "The format of the input is incorrect")
# Copied from the excercise 3 source code
@app.errorhandler(500)
def unknown_error(error):
    return create_error_response(500, "Error",
                    "The system has failed. Please, contact the administrator")

# Copied from the excercise 3 source code
@app.before_request
def connect_db():
    '''Creates a database connection before the request is proccessed.

    The connection is stored in the application context variable flask.g .
    Hence it is accessible from the request object.'''

    g.con = app.config['Engine'].connect()


# HOOKS
# Copied from the excercise 3 source code
@app.teardown_request
def close_connection(exc):
    ''' Closes the database connection
        Check if the connection is created. It migth be exception appear before
        the connection is created.'''
    if hasattr(g, 'con'):
        g.con.close()



# get the playlist, for now it just returns a dummy playlist
#todo: implement the real playlist stuff somehow
def get_playlist():
    playList = {'1': 25, '2': 40, '3': 2}
    return playList


#Resources start from here

# The classes are still skeletons, but these will be the resources and methods we will be implementing.
# The skeletons are still missing their proper arguments, add them as you work.
# The original methods from excercise 3 are removed, but take a look at them for help as you work.

class Users(Resource):

    def get(self):
        abort(404)

    def post (self):
        abort(404)


class User(Resource):
    def get(self):
        abort(404)

    def post(self):
        abort(404)


class Songs(Resource):
    def get(self):
        abort(404)

    def post(self):
        abort(404)


class Song(Resource):
    def get(self):
        abort(404)

    def put(self):
        abort(404)

    def delete(self):
        abort(404)

class Playlist(Resource):

    def get(self):

        playlist = get_playlist()

        # look for help in excercise 3 users resource get methods
        envelope = {}
        collection = {}
        envelope["collection"] = collection

        collection['version'] = "1.0"
        collection['href'] = api.url_for(Playlist)
        # todo: add the links when other resources are added to the routes
        #collection['links'] =

        items = []


        for key in playlist:

            # get song's name from db, add with name "song_name"
            # get artist's name from db, add with name "artist_name" (if found from db, optional)
            # get url for the individual song from function Song
            song = { }
            #song['href'] = "sangz/songs/" + playList[key]
            song['value'] = key

            #song['data'] = []
            #value = {'name': 'song_name', 'value': 'Comic Bakery'}
            #song['data'].append(value)
            #value = {'name': 'artist_name', 'value': 'Instant Remedy'}
            # song['data'].append(value)
            # value = {'name': 'vote_count', 'value': '129'}
            # song['data'].append(value)

            items.append(song)

        collection['items'] = items

        string_data = json.dumps(envelope)

        return Response(string_data, 200, mimetype="application/vnd.collection+json")

        # return Response(string_data, 200, mimetype="text/html")


class chat(Resource):

    def get(self):
        abort(404)
    def post(self):
        abort(404)


#Add the Regex Converter so we can use regex expressions when we define the
#routes
app.url_map.converters['regex'] = RegexConverter


#Define the routes

api.add_resource(Playlist, '/sangz/api/playlist',
                 endpoint='playlist')
'''
api.add_resource(Messages, '/forum/api/messages/',
                 endpoint='messages')
api.add_resource(Message, '/forum/api/messages/<regex("msg-\d+"):messageid>/',
                 endpoint='message')
api.add_resource(User_public, '/forum/api/users/<nickname>/public_profile/',
                 endpoint='public_profile')
api.add_resource(User_restricted, '/forum/api/users/<nickname>/restricted_profile/',
                 endpoint='restricted_profile')
api.add_resource(Users, '/forum/api/users/',
                 endpoint='users')
api.add_resource(User, '/forum/api/users/<nickname>/',
                 endpoint='user')
api.add_resource(History, '/forum/api/users/<nickname>/history/',
                 endpoint='history')
'''

#Redirect profile
@app.route('/profiles/<profile_name>')
def redirect_to_profile(profile_name):
    return redirect(APIARY_PROFILES_URL + profile_name)


#Start the application
#DATABASE SHOULD HAVE BEEN POPULATED PREVIOUSLY
if __name__ == '__main__':
    #Debug true activates automatic code reloading and improved error messages
    app.run(debug=True)