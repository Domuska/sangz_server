PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS users(
  user_id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT,
  realname TEXT,
  email TEXT NOT NULL,
  privilege_level INTEGER,
  UNIQUE(user_id, username)
);

CREATE TABLE if NOT EXISTS artists(
	artist_id INTEGER PRIMARY KEY AUTOINCREMENT,
	artist_name TEXT
);

CREATE TABLE if NOT EXISTS albums(
	album_id INTEGER PRIMARY KEY AUTOINCREMENT,
	album_name TEXT,
	artist_id INTEGER REFERENCES artists(artist_id) ON DELETE CASCADE
);

CREATE TABLE if NOT EXISTS songs(
	song_id INTEGER	PRIMARY KEY AUTOINCREMENT,
	song_name TEXT,
	media_location TEXT NOT NULL,
	media_type TEXT,
	artist_id INTEGER DEFAULT 0 REFERENCES artists(artist_id) ON DELETE SET	DEFAULT,
	album_id INTEGER DEFAULT 0 REFERENCES albums(album_id) ON DELETE SET DEFAULT,
	uploader_id INTEGER NOT NULL,
	FOREIGN KEY (uploader_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE if NOT EXISTS votes(
	vote_id INTEGER PRIMARY KEY AUTOINCREMENT,
	song_id INTEGER NOT NULL,
	user_id INTEGER,
	timestamp INTEGER,
	vote_type TEXT NOT NULL,
	FOREIGN KEY (song_id) REFERENCES songs(song_id) ON DELETE CASCADE,
	FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE if NOT EXISTS chat(
	message_id INTEGER PRIMARY KEY AUTOINCREMENT,
	user_id REFERENCES users(user_id) ON DELETE CASCADE ,
	timestamp INTEGER,
	message TEXT
);



COMMIT;
PRAGMA foreign_keys=ON;
