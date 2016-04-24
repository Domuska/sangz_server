Authors: Tomi Lamsa, Kalle Lyttinen, Pramod Guruprasad

No external libraries (besides sqlite3, flask and flask.restful) were used.

When you clone the repository, the database should already be populated.
In the root of sangz server, and run: python -m jukebox.resources.
API is available in http://localhost:5000/sangz/api/<resouce_name>,
for example, http://localhost:5000/sangz/api/playlist

Tests for the API are not made yet.

However if you wish to start from scratch, you can delete the data.db from the db folder,
and do the following:

Open up python in command line and import the jukebox.py
initialize an object of the engine class
run the functions create_tables and populate_tables (no arguments needed)


Instructions for database api tests:

python -m test.database_api_tests_users
python -m test.database_api_tests_songs
python -m test.database_api_tests_login

