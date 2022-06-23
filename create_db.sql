DROP SCHEMA cherrypicker;
CREATE SCHEMA cherrypicker DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE cherrypicker;

DROP TABLE IF EXISTS accounts;
DROP TABLE IF EXISTS cards;
DROP TABLE IF EXISTS events;
DROP TABLE IF EXISTS usercards;

CREATE TABLE `cards` (
	`name`	varchar(20)	NOT NULL,
	`company`	text	NULL,
	`front`	text	NULL
);

CREATE TABLE `accounts` (
	`id`	varchar(20)	NOT NULL,
	`pw`	text	NULL,
	`nickname`	text	NULL
);

CREATE TABLE `usercards` (
	`id`	varchar(20)	NOT NULL,
	`name`	varchar(20)	NOT NULL
);

CREATE TABLE `events` (
	`name`	varchar(20)	NOT NULL,
	`eventname`	text	NULL,
	`findate`	datetime	NULL,
	`describe`	text	NULL
);

ALTER TABLE `cards` ADD CONSTRAINT `PK_CARDS` PRIMARY KEY (
	`name`
);

ALTER TABLE `accounts` ADD CONSTRAINT `PK_ACCOUNTS` PRIMARY KEY (
	`id`
);

ALTER TABLE `events` ADD CONSTRAINT `PK_EVENTS` PRIMARY KEY (
	`name`
);

ALTER TABLE `usercards` ADD CONSTRAINT `FK_accounts_TO_usercards_1` FOREIGN KEY (
	`id`
)
REFERENCES `accounts` (
	`id`
);

ALTER TABLE `usercards` ADD CONSTRAINT `FK_cards_TO_usercards_1` FOREIGN KEY (
	`name`
)
REFERENCES `cards` (
	`name`
);

ALTER TABLE `events` ADD CONSTRAINT `FK_cards_TO_events_1` FOREIGN KEY (
	`name`
)
REFERENCES `cards` (
	`name`
);
