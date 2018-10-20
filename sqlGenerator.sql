CREATE DATABASE workcouBot;
CREATE TABLE workcouBot.messagesLog (
	id INT NOT NULL,
	creation_datetime DATETIME NOT NULL,
	chat_id INT NOT NULL,
	username varchar(100) NULL,
	message_text varchar(100) NULL,
	PRIMARY KEY ( id )
)
ENGINE=InnoDB
DEFAULT CHARSET=latin1
COLLATE=latin1_swedish_ci;

CREATE TABLE workcouBot.logs (
  id INTEGER UNSIGNED NOT NULL AUTO_INCREMENT,
  creation_epoch INTEGER UNSIGNED NOT NULL,
  log_text varchar(1200) NOT NULL,
  PRIMARY KEY ( id )
)
ENGINE=InnoDB
DEFAULT CHARSET=latin1
COLLATE=latin1_swedish_ci;
