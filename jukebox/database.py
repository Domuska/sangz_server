'''
 Database engine and connection.
 Modified from the original that was given to our group
 in the excercises.
'''


import time, sqlite3, re, os
#Default paths for .db and .sql files to create and populate the database.
DEFAULT_DB_PATH = 'db/data.db'
DEFAULT_SCHEMA = "db/schema_dump.sql"
DEFAULT_DATA_DUMP = "db/data_dump.sql"

class Engine(object):
    '''
    Abstraction of the database.

    It includes tools to create, configure,
    populate and connect to the sqlite file. You can access the Connection
    instance, and hence, to the database interface itself using the method
    :py:meth:`connection`.

    :Example:

    >>> engine = Engine()
    >>> con = engine.connect()

    :param db_path: The path of the database file (always with respect to the
        calling script. If not specified, the Engine will use the file located
        at *db/data.db*

    '''
    def __init__(self, db_path=None):
        '''
        '''

        super(Engine, self).__init__()
        if db_path is not None:
            self.db_path = db_path
        else:
            self.db_path = DEFAULT_DB_PATH

    def connect(self):
        '''
        Creates a connection to the database.

        :return: A Connection instance
        :rtype: Connection

        '''
        return Connection(self.db_path)

    def remove_database(self):
        '''
        Removes the database file from the filesystem.

        '''
        if os.path.exists(self.db_path):
            #THIS REMOVES THE DATABASE STRUCTURE
            os.remove(self.db_path)

    def clear(self):
        '''
        Purge the database removing all records from the tables. However,
        it keeps the database schema (meaning the table structure)

        '''
        keys_on = 'PRAGMA foreign_keys = ON'
        #THIS KEEPS THE SCHEMA AND REMOVE VALUES
        con = sqlite3.connect(self.db_path)
        #Activate foreing keys support
        cur = con.cursor()
        cur.execute(keys_on)
        with con:
            cur = con.cursor()
            cur.execute("DELETE FROM votes")
            cur.execute("DELETE FROM songs")
            cur.execute("DELETE FROM albums")
            cur.execute("DELETE FROM artists")
            cur.execute("DELETE FROM login")
            cur.execute("DELETE FROM chat")
            cur.execute("DELETE FROM users")
            #NOTE the order of cleanup matters since tables have foreign keys

    #METHODS TO CREATE AND POPULATE A DATABASE USING DIFFERENT SCRIPTS
    def create_tables(self, schema=None):
        '''
        Create programmatically the tables from a schema file.

        :param schema: path to the .sql schema file. If this parmeter is
            None, then *db/schema_dump.sql* is utilized.

        '''
        con = sqlite3.connect(self.db_path)
        if schema is None:
            schema = DEFAULT_SCHEMA
        try:
            with open(schema) as f:
                sql = f.read()
                cur = con.cursor()
                cur.executescript(sql)
        finally:
            con.close()

    def populate_tables(self, dump=None):
        '''
        Populate programmatically the tables from a dump file.

        :param dump:  path to the .sql dump file. If this parmeter is
            None, then *db/data_dump.sql* is utilized.

        '''
        keys_on = 'PRAGMA foreign_keys = ON'
        con = sqlite3.connect(self.db_path)
        #Activate foreing keys support
        cur = con.cursor()
        cur.execute(keys_on)
        #Populate database from dump
        if dump is None:
            dump = DEFAULT_DATA_DUMP
        with open (dump) as f:
            sql = f.read()
            cur = con.cursor()
            cur.executescript(sql)
            
            
            
class Connection(object):
    '''
    API to access the Forum database.

    The sqlite3 connection instance is accessible to all the methods of this
    class through the :py:attr:`self.con` attribute.

    An instance of this class should not be instantiated directly using the
    constructor. Instead use the :py:meth:`Engine.connect`.

    Use the method :py:meth:`close` in order to close a connection.
    A :py:class:`Connection` **MUST** always be closed once when it is not going to be
    utilized anymore in order to release internal locks.

    :param db_path: Location of the database file.
    :type dbpath: str

    '''
    def __init__(self, db_path):
        super(Connection, self).__init__()
        self.con = sqlite3.connect(db_path)

    def close(self):
        '''
        Closes the database connection, commiting all changes.

        '''
        if self.con:
            self.con.commit()
            self.con.close()

    #FOREIGN KEY STATUS
    def check_foreign_keys_status(self):
        '''
        Check if the foreign keys has been activated.

        :return: ``True`` if  foreign_keys is activated and ``False`` otherwise.
        :raises sqlite3.Error: when a sqlite3 error happen. In this case the
            connection is closed.

        '''
        try:
            #Create a cursor to receive the database values
            cur = self.con.cursor()
            #Execute the pragma command
            cur.execute('PRAGMA foreign_keys')
            #We know we retrieve just one record: use fetchone()
            data = cur.fetchone()
            is_activated = data == (1,)
            print "Foreign Keys status: %s" % 'ON' if is_activated else 'OFF'
        except sqlite3.Error, excp:
            print "Error %s:" % excp.args[0]
            self.close()
            raise excp
        return is_activated

    def set_foreign_keys_support(self):
        '''
        Activate the support for foreign keys.

        :return: ``True`` if operation succeed and ``False`` otherwise.

        '''
        keys_on = 'PRAGMA foreign_keys = ON'
        try:
            #Get the cursor object.
            #It allows to execute SQL code and traverse the result set
            cur = self.con.cursor()
            #execute the pragma command, ON
            cur.execute(keys_on)
            return True
        except sqlite3.Error, excp:
            print "Error %s:" % excp.args[0]
            return False

    def unset_foreign_keys_support(self):
        '''
        Deactivate the support for foreign keys.

        :return: ``True`` if operation succeed and ``False`` otherwise.

        '''
        keys_on = 'PRAGMA foreign_keys = OFF'
        try:
            #Get the cursor object.
            #It allows to execute SQL code and traverse the result set
            cur = self.con.cursor()
            #execute the pragma command, OFF
            cur.execute(keys_on)
            return True
        except sqlite3.Error, excp:
            print "Error %s:" % excp.args[0]
            return False



    #API ITSELF STARTS HERE ------------------------------


    #USER TABLE STARTS HERE ----------------------------------------------

    def add_user(self, nickname, real_name, email, privilege_level):

        '''
        Add a new user into table users
        :param user_name: user's real name
        :param nickname: nickname the user has chosen
        :param email: email supplied by user
        :param privilege_level: the level of privileges that the user has
        :return id of the added user, or none if a new user was not added
            into the database
        NOTE: SHOULD PRIVILEGE LEVELS EVEN BE GIVEN IN HERE? 
        SHOULD THERE BE ANOTHER METHOD THAT MODIFIES THESE PRIVILEGES?
        '''

        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        #Activate foreign key support
        self.set_foreign_keys_support()

        statement = 'INSERT INTO users (username, realname, email, privilege_level) VALUES (?,?,?,?)'
        values = (nickname, real_name, email, privilege_level)

        #pass the error on if new user could not be added
        try:
            cur.execute(statement, values)
        except:
            cur.close()
            raise

        self.con.commit()

        if cur.rowcount < 1:
            return False
        return cur.lastrowid


    def modify_user(self, user_ID, username=None, realname=None, email=None, privilege_level=None):
        '''
        A function call to modify user's information. If a field is not
        provided, it is not modified, otherwise the new value will be set for the user
        
        :param user_id: ID of the user's info that is to be modified
        :param username: a new username for the user
        :param realname: new real name for the user
        :param email: new email for the user
        :param privilege_level: new privilege level for the user
        
        :return: the ID of the modified message, or None if no
        message with provided ID was found
        '''

        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        self.set_foreign_keys_support()

        #if supplied values are None, get those values from the database before updating
        #we could alternatively just build the update statement piece by piece

        #if any of the values are none, get the user's info
        if realname is None or username is None or email is None or privilege_level is None:
            user_info = self.get_user(user_ID)

            if realname is None:
                realname = user_info['realname']
                #print realname

            if username is None:
                username = user_info['username']
                #print username

            if email is None:
                email = user_info['email']
                #print email

            if privilege_level is None:
                privilege_level = user_info['privilege_level']
                #print privilege_level


        statement = 'UPDATE users SET username=?, realname = ?, email = ?, privilege_level = ? WHERE user_ID = ?'
        values = (username, realname, email, privilege_level, user_ID)
        #print values
        cur.execute(statement, values)

        self.con.commit()



    def get_user(self, ID):

        '''
        A function to get all information of a particular user
        
        :param ID: ID of the user whose info is to be retreived
        :return: dictionary containing all info of the user in following format:
        'user_id' = user's id, 'realname' = user's real name, 'username' = user's nickname,
        'email' = user's email, 'privilege_level' = users privilege level (normal user or admin)
        OR false if a user with supplied ID was not found
        '''

        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        self.set_foreign_keys_support()

        query = 'SELECT * FROM users WHERE user_id = ?'
        values = (ID,)

        cur.execute(query, values)

        row = cur.fetchone()
        if row is None:
            print 'no user was found with ID'
            return None

        user_info = {'user_id':row[0], 'username':row[1], 'realname':row[2], 'email':row[3], 'privilege_level':row[4]}
        return user_info

    def delete_user(self, ID):

        '''
        A function to delete the a user's information
        :param ID: ID of the user to be removed
        :return: False if user with this ID was not found,
        True otherwise
        
        '''

        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        self.set_foreign_keys_support()

        values = (ID,)
        cur.execute('DELETE FROM users WHERE user_ID = ?', values)

        self.con.commit()

        if cur.rowcount < 1:
            return False
        return True

    def get_users(self, upperlimit=None, offset=0):

        '''
        Function to get all users of the system
        :param offset: the offset where to start gathering user IDs, can be None
        :param upperlimit: the maximum number of IDs to return
        :return: a list containing the IDs found
        '''

        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        self.set_foreign_keys_support()

        #-1 works as 'no limit' in SQLite
        if upperlimit is None:
            upperlimit = -1

        statement = 'SELECT user_ID, username FROM users LIMIT ? OFFSET ?'
        values = (upperlimit, offset)
        cur.execute(statement, values)

        idlist = cur.fetchall()
        cur.close()
        return idlist




    #LOGIN TABLE BEGINS HERE ----------------------------------------------

    def add_credentials(self, ID, password):

        '''
        add credentials to an user
        :param ID: ID of the user whom credentials belong to
        :param password: the new password that is to be set (hopefully hash value)
        '''

        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        self.set_foreign_keys_support()

        statement = 'INSERT INTO login (user_id, password) VALUES (?,?)'
        values = (ID, password)


        try:
            cur.execute(statement, values)
        except:
            cur.close()
            raise

        self.con.commit()

        #pass the error on if password could not be added
        if cur.rowcount < 1:
            return False
        return cur.lastrowid



    def get_credentials(self, ID):
        '''
        Function to get password from one user
        :param ID: ID of the user
        :return: string containing the credentials
        '''

        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        self.set_foreign_keys_support()

        values = (ID,)
        cur.execute('SELECT password FROM login WHERE user_id = ?', values)

        row = cur.fetchone()
        cur.close()
        if row is None:
            return None

        return row['password']

    def delete_credentials(self, ID):

        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        self.set_foreign_keys_support()

        values = (ID,)
        cur.execute('DELETE FROM login WHERE user_id = ?', values)

        self.con.commit()

        if cur.rowcount < 1:
            return False
        return True


    def modify_credentials(self, ID, password):

        '''
        Function for updating login credentials for an user
        :param ID: ID of the user
        :param password: new password to be saved
        :return: ID of the user whose password was updated, None if user was not found
        '''

        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        self.set_foreign_keys_support()

        values = (password, ID)
        statement = 'UPDATE login SET password = ? WHERE user_id = ?'
        cur.execute(statement, values)

        self.con.commit()

        if cur.rowcount == 1:
            return cur.lastrowid

        return None



    #SONGS TABLE BEGINS HERE ----------------------------------------------

    def add_song(self, song_name, media_location, media_type, uploader_ID, artist_ID=None, album_ID=None ):
        '''(String SONG_NAME, String MEDIA_LOC, String MEDIA_TYPE, int ARTIST_ID, int ALBUM_ID, int UPLOADER_ID)'''
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        self.set_foreign_keys_support()

        statement = 'INSERT INTO songs (song_name, media_location, media_type, artist_id, album_id, uploader_id) VALUES  \
        (?, ?, ?, ?, ?, ?)'


        values = (song_name, media_location, media_type, artist_ID, album_ID, uploader_ID)

        #SQLite library inserts NULL instead of None automagically into the database
        try:
            cur.execute(statement, values)
        except:
            cur.close()
            raise

        self.con.commit()

        if cur.rowcount < 1:
            return False
        return cur.lastrowid


    def get_song(self, song_ID):

        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        self.set_foreign_keys_support()

        values = (song_ID,)
        cur.execute('SELECT * FROM songs WHERE song_id = ?', values)

        row = cur.fetchone()
        cur.close()

        if row is None:
            print 'no song with this ID found'
            return None

        song_info = {'song_id': row[0], 'song_name': row[1], 'media_location': row[2],
                     'media_type': row[3], 'artist_ID': row[4], 'album_ID': row[5], 'uploader_ID': row[6]}

        return song_info


    def delete_song(self, song_ID):

        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        self.set_foreign_keys_support()

        values = (song_ID,)
        cur.execute('DELETE FROM songs WHERE song_id = ?', values)

        self.con.commit()

        if cur.rowcount < 1:
            return False
        return True

    def modify_song(self, song_ID, song_name=None, media_location=None, media_type=None, artist_ID=None, album_ID=None, uploader_ID=None):
        '''
        (int SONG_ID, String SONG_NAME, String MEDIA_LOC, String MEDIA_TYPE, int ARTIST_ID, int ALBUM_ID, int UPLOADER_ID)
        '''
        song_info = self.get_song(song_ID)

        if song_info is None:
            return None

        if song_name is None:
            song_name = song_info['song_name']

        if media_location is None:
            media_location = song_info['media_location']

        if media_type is None:
            media_type = song_info['media_location']

        if artist_ID is None:
            artist_ID = song_info['artist_ID']

        if album_ID is None:
            album_ID = song_info['album_ID']

        if uploader_ID is None:
            uploader_ID = song_info['uploader_ID']


        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        self.set_foreign_keys_support()

        values = (song_name, media_location, media_type, artist_ID, album_ID, uploader_ID, song_ID)
        cur.execute('UPDATE songs SET song_name = ?, media_location = ?, media_type = ?, \
        artist_id = ?, album_id = ?, uploader_id = ? WHERE song_id = ?', values)

        self.con.commit()
        cur.close()

        if cur.rowcount < 1:
            return False

        return song_ID




    def get_songs(self, upperlimit=None, offset=0):
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        self.set_foreign_keys_support()

        #-1 works as 'no limit' in SQLite
        if upperlimit is None:
            upperlimit = -1

        values = (upperlimit, offset)
        cur.execute('SELECT song_id, song_name FROM songs LIMIT ? OFFSET ?', values)

        idlist = cur.fetchall()
        cur.close()
        return idlist




    #ARTIST TABLE BEGINS HERE ----------------------------------------------

    def add_artist(self, artist_name):
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        self.set_foreign_keys_support()

        values = (artist_name,)
        cur.execute('INSERT INTO artists (artist_name) VALUES (?)', values)
        self.con.commit()

        if cur.rowcount < 1:
            return False
        return cur.lastrowid

    def get_artist(self, artist_id):
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        self.set_foreign_keys_support()

        values = (artist_id,)
        cur.execute('SELECT * FROM artists WHERE artist_id = ?', values)

        row = cur.fetchone()
        cur.close()

        if row is None:
            print 'no artist with this ID found'
            return None

        artist_info = {'artist_ID':row[0], 'artist_name':row[1]}

        return artist_info

    def delete_artist(self, artist_ID):

        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        self.set_foreign_keys_support()

        values = (artist_ID,)
        cur.execute('DELETE FROM artists WHERE artist_id = ?', values)
        self.con.commit()

        if cur.rowcount < 1:
            return False
        return True

    def modify_artist(self, artist_ID, artist_name):

        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        self.set_foreign_keys_support()

        values = (artist_name, artist_ID)
        cur.execute('UPDATE artists SET artist_name = ? WHERE artist_id = ?', values)

        self.con.commit()


        #ALBUM TABLE BEGINS HERE ----------------------------------------------

    def add_album(self, artist_name):
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        self.set_foreign_keys_support()

        values = (artist_name,)
        cur.execute('INSERT INTO albums (album_name) VALUES (?)', values)
        self.con.commit()

        if cur.rowcount < 1:
            return False
        return cur.lastrowid

    def get_album(self, album_id):
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        self.set_foreign_keys_support()

        values = (album_id,)
        cur.execute('SELECT * FROM albums WHERE album_id = ?', values)

        row = cur.fetchone()
        cur.close()

        if row is None:
            print 'no albums with this ID found'
            return None

        album_info = {'artist_ID':row[0], 'album_name':row[1]}

        return album_info

    def delete_album(self, album_id):

        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        self.set_foreign_keys_support()

        values = (album_id,)
        cur.execute('DELETE FROM albums WHERE album_id = ?', values)
        self.con.commit()

        if cur.rowcount < 1:
            return False
        return True

    def modify_artist(self, album_ID, album_name):

        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        self.set_foreign_keys_support()

        values = (album_name, album_ID)
        cur.execute('UPDATE albums SET album_name = ? WHERE album_id = ?', values)

        self.con.commit()

        #VOTES TABLE BEGINS HERE ----------------------------------------------

    def add_upvotes(self, song_ID, user_id, time):
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        self.set_foreign_keys_support()

        values = (song_ID, user_id, time, 'upvote')

        cur.execute('INSERT INTO votes (song_ID,user_ID, timestamp, vote_type) VALUES (?,?,?,?)', values)
        self.con.commit()

        if cur.rowcount < 1:
            return False
        return cur.lastrowid

    def add_downvotes(self, song_ID, user_id, time):
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        self.set_foreign_keys_support()

        values = (song_ID, user_id, time, 'downvote')
        cur.execute('INSERT INTO votes (song_ID,user_ID, timestamp, vote_type) VALUES (?,?,?,?)', values)
        self.con.commit()

        if cur.rowcount < 1:
            return False
        return cur.lastrowid

    def get_votes_by_user(self, user_ID):
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        self.set_foreign_keys_support()

        values = (user_ID,)
        cur.execute('SELECT * FROM votes WHERE user_ID = ?', values)

        row = cur.fetchone()
        cur.close()

        if row is None:
            print 'user_ID not found'
            return None


        s_id = row[0]
        cur.execute('SELECT * from songs where song_id = ?',s_id,)

        song_info = {'song_id': row[0], 'song_name': row[1], 'media_location': row[2],
                     'media_type': row[3], 'artist_ID': row[4], 'album_ID': row[5], 'uploader_ID': row[6]}

        return song_info

    def get_upvotes_by_song(self, song_ID):

        '''
        Method for getting all upvotes the song has received

        :param song_ID: ID of the song
        :return: a dictionary with 'votes' entry, which has the vote count
        '''

        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        self.set_foreign_keys_support()

        values = (song_ID,)
        cur.execute('SELECT count(*) FROM votes WHERE song_id = ? AND vote_type = "upvote"', values)

        row = cur.fetchone()

        if row is None:
            print 'song_ID not found'
            return None

        song_votes = {'votes': row[0]}

        return song_votes

    def get_downvotes_by_song(self, song_ID):

        '''
        Method for getting all downvotes the song has received

        :param song_ID: ID of the song
        :return: a dictionary with 'votes' entry, which has the vote count
        '''

        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        self.set_foreign_keys_support()

        values = (song_ID,)
        cur.execute('SELECT count(*) FROM votes WHERE song_id = ? AND vote_type = "downvote"', values)

        row = cur.fetchone()

        if row is None:
            print 'song_ID not found'
            return None

        song_votes = {'votes': row[0]}

        return song_votes

    def get_all_songs_votes(self):

        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        self.set_foreign_keys_support()

        # get all song_ids that have a single vote (or in other words a row in votes table)
        statement = "SELECT DISTINCT song_id FROM votes"
        cur.execute(statement, )

        playlist = { }

        for row in cur:
            playlist[str(row[0])] = self.get_upvotes_by_song(row[0])

        return playlist

    def delete_votes_by_user(self, user_ID):

        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        self.set_foreign_keys_support()

        values = (user_ID)
        cur.execute('DELETE from votes WHERE user_id = ?', values)
        if cur.rowcount < 1:
            return False
        return True

    def delete_votes_by_song(self, song_ID):

        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        self.set_foreign_keys_support()

        values = (song_ID)
        cur.execute('DELETE from votes WHERE song_id = ?', values)
        if cur.rowcount < 1:
            return False
        return True

    def delete_vote_all(self):

        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        self.set_foreign_keys_support()

        cur.execute('DELETE * from votes', )
        if cur.rowcount < 1:
            return False
        return True

        self.con.commit()



        #CHAT TABLE BEGINS HERE ----------------------------------------------

    def add_message(self, user_id, message, time):
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        self.set_foreign_keys_support()

        values = (user_id, time, message)
        cur.execute('INSERT INTO chat (user_ID, Timestamp, message) VALUES (?,?,?)', values)
        self.con.commit()

        if cur.rowcount < 1:
            return False
        return cur.lastrowid

    def delete_message(self, message_ID):
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        self.set_foreign_keys_support()

        values = (message_ID,)
        cur.execute('DELETE FROM chat WHERE message_id = ?', values)

        row = cur.fetchone()
        cur.close()

        if cur.rowcount < 1:
            return False
        return cur.lastrowid

    def get_messages_latest(self, no_of_msg=None):

        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        self.set_foreign_keys_support()

        if upperlimit is None:
            upperlimit = 5

        statement = 'SELECT * FROM chat LIMIT ? OFFSET ?'
        values = (upperlimit, offset)
        cur.execute(statement, values)

        msg_list = cur.fetchall()
        cur.close()
        return msg_list


    def get_messages_all(self,):
        '''
        Function for getting all messages in the chat, ever.
        Order the messages by timestamp.

        :return: a list that contains messages as rows. Index 0 is message_id,
                1 is user_id, 2 is timestamp, 3 is message
        '''

        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        self.set_foreign_keys_support()

        cur.execute('SELECT * FROM chat ORDER BY timestamp ASC')

        all_chat_msg = cur.fetchall()
        cur.close()
        return all_chat_msg

        self.con.commit()
        
        
        
    