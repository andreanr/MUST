


CREATE TABLE new_films (
	mdb_id text PRIMARY KEY,
	release_date timestamp NOT NULL,
	title text text NOT NULL,
	description text,
	url text,
	CHECK((SELECT COUNT(*) FROM movie_releases WHERE movie_releases.mbd_id = mdb_id) > 0)
);

CREATE TABLE movie_artists (
	mo_id int PRIMARY KEY,
	name text NOT NULL
);

CREATE TABLE movie_releases (
	mo_id int REFERENCES movie_artists(mo_id),
	Mdb_id text REFERENCES new_films(mdb_id),
	PRIMARY KEY (mo_id, mdb_id)
);

CREATE TABLE users (
	user_id text PRIMARY KEY,
	name text NOT NULL,
	city_id int NOT NULL REFERENCES location(city_id)
);

CREATE TABLE movie_preference (
	user_id text REFERENCES users(user_id),
	mo_id text REFERENCES movie_artists(mo_id),
	PRIMARY KEY (user_id, mo_id)
);

CREATE TABLE location (
	city_id int PRIMARY KEY,
	city_name text NOT NULL,
	country text NOT NULL
);

CREATE TABLE new_music (
	release_id int PRIMARY KEY,
	release_date timestamp NOT NULL,
	name text NOT NULL,
	album_type text,
	url text,
	CHECK(
    (SELECT COUNT(*) FROM available_music WHERE available_music.release_id = release_id) > 0 AND
    (SELECT COUNT(*) FROM available_music 
    WHERE music_releases.release_id = release_id) > 0
  ) 
);

CREATE TABLE concerts (
	event_id int PRIMARY KEY,
	event_date timestamp NOT NULL,
	venue text NOT NULL,
	city_id int NOT NULL REFERENCES location(city_id),
	description text,
	url text,
CHECK(
	(SELECT COUNT(*) FROM concert_performances WHERE concert_performances.event_id = event_id) > 0) 
);

CREATE TABLE musicians (
	mu_id int PRIMARY KEY,
	name text NOT NULL
);

CREATE TABLE available_music (
	release_id int REFERENCES new_music(release_id),
	country text REFERENCES location(country),
	PRIMARY KEY (release_id, country)
);

CREATE TABLE music_releases (
	release_id int REFERENCES new_music(release_id),
	mu_id int REFERENCES musicians(mu_id),
	PRIMARY KEY (release_id, mu_id)
);

CREATE TABLE concert_performances (
	event_id int REFERENCES concerts(event_id),
	mu_id int REFERENCES musicians(mu_id)
	PRIMARY KEY (event_id, mu_id)
);

CREATE TABLE music_preference (
	user_id text REFERENCES users(user_id),
	mu_id text REFERENCES musicians(mu_id),
	PRIMARY KEY (user_id, mu_id)
);

