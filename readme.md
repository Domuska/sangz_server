Authors: Tomi Lämsä, Kalle Lyttinen, Pramod Guruprasad

The following python modules are required:
    sqlite3
    flask
    flask.restful
    collection-json

When you clone the repository, the database should already be populated.
In the root of sangz server, run: python -m jukebox.resources, or alternatively just python sangz.py.
API is available in http://localhost:5000/sangz/api/<resouce_name>,
for example, http://localhost:5000/sangz/api/playlist

For a clean, fresh start, delete the data.db file from the cloned repository and follow these steps:
	1. Open up python in command line and import the database (jukebox.database)
	2. Initialize an object of the engine class
	3. Run the functions create_tables and populate_tables (no arguments needed)


Instructions for database api tests:

python -m test.database_api_tests_users
python -m test.database_api_tests_songs
python -m test.database_api_tests_login



List of APIs available: http://docs.pwpsangz.apiary.io/#

Possible issues while exetuing APIs:
It has been found that certain REST clients enfore the trailing "/" for all commands. If the client reports an error, retry by using the trailing "/".
If the API fails, please report the error to us.

in the client_old folder is our original client ideas which we decided not to implement in the end when we decided to do an Android app instead. This can be found in the separate repository sangz_client.