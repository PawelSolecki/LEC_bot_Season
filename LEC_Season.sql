CREATE TABLE Users_points (
  user_id INT,
  points INT,
  answer_amount INT
);

CREATE TABLE Discord_users (
  discord_user_id VARCHAR(255),
  user_name VARCHAR(255),
  user_discord_tag INT(4),
  PRIMARY KEY (discord_user_id)
);

CREATE TABLE Servers (
  discord_server_id VARCHAR(255),
  role_id VARCHAR(255),
  server_name VARCHAR(255),
  is_bonus BOOLEAN,
  channel VARCHAR(255),
  voting_message_id VARCHAR(255),
  PRIMARY KEY (discord_server_id)
);

CREATE TABLE Users (
  user_id INT NOT NULL AUTO_INCREMENT,
  discord_server_id VARCHAR(255),
  discord_user_id VARCHAR(255),
  PRIMARY KEY (user_id),
  FOREIGN KEY (discord_server_id) REFERENCES Servers(discord_server_id),
  FOREIGN KEY (discord_user_id) REFERENCES Discord_users(discord_user_id)
);

CREATE TABLE Server_bonuses (
  discord_server_id VARCHAR(255),
  bonus_id INT,
  week VARCHAR(255),
  day VARCHAR(255)
);

CREATE TABLE Users_votes (
  user_id INT,
  match_id INT,
  team_vote VARCHAR(3),
  score_vote VARCHAR(3)
);

CREATE TABLE Matches (
  match_id INT NOT NULL AUTO_INCREMENT,
  team_1 VARCHAR(255),
  team_2 VARCHAR(255),
  team_1_short VARCHAR(3),
  team_2_short VARCHAR(3),
  winner VARCHAR(255),
  match_day INT,
  match_week INT,
  date VARCHAR(30),
  PRIMARY KEY (match_id)
);

CREATE TABLE Bonuses (
  bonus_id INT NOT NULL AUTO_INCREMENT,
  bonus_description VARCHAR(255),
  bonus_answers JSON,
  PRIMARY KEY (bonus_id)
);
CREATE TABLE Users_bonus_votes (
  user_id INT,
  bonus_id INT,
  vote JSON
);