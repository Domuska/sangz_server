PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS users(
  user_id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT,
  realname TEXT,
  email TEXT NOT NULL,
  privilege_level INTEGER,
  UNIQUE(user_id, username));

CREATE TABLE if NOT EXISTS login(
	user_id INTEGER PRIMARY KEY,
	password TEXT NOT NULL,
	FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE if NOT EXISTS artists(
	artist_id INTEGER PRIMARY KEY AUTOINCREMENT,
	artist_name TEXT
);

CREATE TABLE if NOT EXISTS albums(
	album_id INTEGER PRIMARY KEY AUTOINCREMENT,
	album_name TEXT,
	artist_id INTEGER,
	FOREIGN KEY (artist_id) REFERENCES artists(artist_id)
);


CREATE TABLE if NOT EXISTS songs(
	song_id INTEGER	PRIMARY KEY AUTOINCREMENT,
	song_name TEXT,
	media_location TEXT NOT NULL,
	media_type TEXT,
	artist_id INTEGER,
	album_id INTEGER,
	uploader_id INTEGER NOT NULL,
	FOREIGN KEY (uploader_id) REFERENCES users(user_id),
	FOREIGN KEY (artist_id) REFERENCES artists(artist_id),
	FOREIGN KEY (album_id) REFERENCES albums(album_id)
);

CREATE TABLE if NOT EXISTS votes(
	vote_id INTEGER PRIMARY KEY AUTOINCREMENT,
	song_id INTEGER NOT NULL,
	user_id INTEGER,
	timestamp INTEGER,
	vote_type TEXT NOT NULL,
	FOREIGN KEY (song_id) REFERENCES songs(song_id),
	FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE if NOT EXISTS chat(
	message_id INTEGER PRIMARY KEY AUTOINCREMENT,
	user_id,
	timestamp INTEGER,
	message TEXT,
	FOREIGN KEY (user_id) REFERENCES users(user_id)
);



COMMIT;
PRAGMA foreign_keys=ON;
