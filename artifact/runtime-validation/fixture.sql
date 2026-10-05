CREATE TABLE fixture (id integer PRIMARY KEY, value integer NOT NULL);
INSERT INTO fixture SELECT id, id * 7 + 3 FROM generate_series(0, 11) AS id;
