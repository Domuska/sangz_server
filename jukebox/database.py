'''
 Database engine and connection.
 Modified from the original that was given to our group
 in the excercises.
'''

from datetime import datetime
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
            cur.execute("DELETE FROM messages")
            cur.execute("DELETE FROM users")
            #NOTE since we have ON DELETE CASCADE BOTH IN users_profile AND
            #friends, WE DO NOT HAVE TO WORRY TO CLEAR THOSE TABLES.

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
        
        if cur.rowcount == 1:
            return cur.lastrowid
            
        return None
        
        
        
    def get_user(self, ID):
    
        '''
        A function to get all information of a particular user
        
        :param ID: ID of the user whose info is to be retreived
        :return: dictionary containing all info of the user in following format:
        'name' = user's real name, 'nickname' = user's nickname, 'email' = user's email
        'privilege_level' = users privilege level (normal user or admin)
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

        statement = 'SELECT user_ID FROM users LIMIT ? OFFSET ?'
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

        if song_name is None or media_location is None or media_type is None or artist_ID is None or album_ID is None or uploader_ID is None:
            song_info = self.get_song(song_ID)
            
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
        
        if cur.rowcount == 1:
            return cur.lastrowid
        return None
        
        
    def get_songs(self, upperlimit=None, offset=0):
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        self.set_foreign_keys_support()
    
        #-1 works as 'no limit' in SQLite
        if upperlimit is None:
            upperlimit = -1
        
        values = (upperlimit, offset)
        cur.execute('SELECT song_id FROM songs LIMIT ? OFFSET ?', values)
            
        idlist = cur.fetchall()
        cur.close()
        return idlist
        
        
        
        
    #ARTIST TABLE BEGINS HERE ----------------------------------------------
    
    def add_artist():
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        self.set_foreign_keys_support()
    
    
    
    