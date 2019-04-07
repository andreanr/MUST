DROP TABLE IF EXISTS new_films CASCADE;
CREATE TABLE new_films (
	mdb_id text PRIMARY KEY,
	release_date timestamp NOT NULL,
	title text NOT NULL,
	description text,
	url text
	--CHECK((SELECT COUNT(*) FROM movie_releases WHERE movie_releases.mbd_id = mdb_id) > 0)
);

DROP TABLE IF EXISTS movie_artists CASCADE;
CREATE TABLE movie_artists (
	mo_id text PRIMARY KEY,
	name text NOT NULL
);

DROP TABLE IF EXISTS movie_releases;
CREATE TABLE movie_releases (
	mo_id text REFERENCES movie_artists(mo_id),
	Mdb_id text REFERENCES new_films(mdb_id),
	PRIMARY KEY (mo_id, mdb_id)
);

DROP TABLE IF EXISTS country CASCADE;
CREATE TABLE country (
	country text PRIMARY KEY
)

DROP TABLE IF EXISTS city CASCADE;
CREATE TABLE city (
	city_id int PRIMARY KEY,
	city_name text NOT NULL,
	country text NOT null REFERENCES country(country)
);

DROP TABLE IF EXISTS users CASCADE;
CREATE TABLE users (
	username text PRIMARY KEY,
	name text NOT NULL,
        email text NOT NULL,
        password text NOT NULL,
	city_id int NOT NULL REFERENCES city(city_id)
);

DROP TABLE IF EXISTS movie_preference;
CREATE TABLE movie_preference (
	username text REFERENCES users(username),
	mo_id text REFERENCES movie_artists(mo_id),
	PRIMARY KEY (username, mo_id)
);

DROP TABLE IF EXISTS new_music CASCADE;
CREATE TABLE new_music (
	release_id int PRIMARY KEY,
	release_date timestamp NOT NULL,
	name text NOT NULL,
	album_type text,
	url text
	--CHECK(
    --(SELECT COUNT(*) FROM available_music WHERE available_music.release_id = release_id) > 0 AND
    --(SELECT COUNT(*) FROM available_music
    --WHERE music_releases.release_id = release_id) > 0
  --)
);

DROP TABLE IF EXISTS concerts CASCADE;
CREATE TABLE concerts (
	event_id int PRIMARY KEY,
	event_name text,
	event_date timestamp NOT NULL,
	venue text NOT NULL,
	city_id int NOT NULL REFERENCES city(city_id),
	url text,
	event_type text
--CHECK(
	--(SELECT COUNT(*) FROM concert_performances WHERE concert_performances.event_id = event_id) > 0)
);

DROP TABLE IF EXISTS musicians CASCADE;
CREATE TABLE musicians (
	sp_id text PRIMARY KEY,
	sk_id int UNIQUE NOT NULL,
	name text NOT NULL
);

DROP TABLE IF EXISTS available_music;
CREATE TABLE available_music (
	release_id int REFERENCES new_music(release_id),
	country text REFERENCES country(country),
	PRIMARY KEY (release_id, country)
);

DROP TABLE IF EXISTS music_releases CASCADE;
CREATE TABLE music_releases (
	release_id int REFERENCES new_music(release_id),
	sp_id text REFERENCES musicians(sp_id),
	PRIMARY KEY (release_id, sp_id)
);

DROP TABLE IF EXISTS concert_performances;
CREATE TABLE concert_performances (
	event_id int REFERENCES concerts(event_id),
	sk_id int REFERENCES musicians(sk_id),
	PRIMARY KEY (event_id, sk_id)
);

DROP TABLE IF EXISTS music_preference;
CREATE TABLE music_preference (
	username text REFERENCES users(username),
	sp_id text REFERENCES musicians(sp_id),
	PRIMARY KEY (username, sp_id)
);
