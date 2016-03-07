Authors: Tomi Lamsa, Kalle Lyttinen

No external libraries (besides sqlite3) were used.

When you clone the repository, the database should already be populated.
However if you wish to start from scratch, you can delete the data.db from the db folder,
and do the following:

Open up python in command line and import the jukebox.py
initialize an object of the engine class
run the functions create_tables and populate_tables (no arguments needed)


Instructions for database api tests:

python -m test.database_api_tests_users
python -m test.database_api_tests_songs
python -m test.database_api_tests_login

