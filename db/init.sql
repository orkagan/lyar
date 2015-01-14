CREATE TABLE question (
  id INTEGER NOT NULL,
  statement0 TEXT NOT NULL,
  statement1 TEXT NOT NULL,
  statement2 TEXT NOT NULL,
  lie INTEGER NOT NULL,
  creator_id INTEGER,
  name TEXT,
  PRIMARY KEY (id),
  FOREIGN KEY (id) REFERENCES vote (qid),
  FOREIGN KEY (creator_id) REFERENCES user (id)
);
CREATE TABLE vote (
  id INTEGER NOT NULL,
  qid INTEGER NOT NULL,
  vote INTEGER NOT NULL,
  voter_id INTEGER ,
  PRIMARY KEY (id),
  FOREIGN KEY (voter_id) REFERENCES user (id)
);
CREATE TABLE user (
  id INTEGER NOT NULL,
  username TEXT NOT NULL,
  password TEXT NOT NULL,
  points INTEGER NOT NULL,
  PRIMARY KEY (id)
);
