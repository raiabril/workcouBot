CREATE TABLE workcouBot.messagesLog (
	id INT NOT NULL,
	`date` INT NOT NULL,
	chat_id INT NOT NULL,
	username varchar(100) NULL,
	`text` varchar(100) NULL
)
ENGINE=InnoDB
DEFAULT CHARSET=latin1
COLLATE=latin1_swedish_ci;
