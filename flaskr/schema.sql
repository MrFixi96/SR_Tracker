--
-- File generated with SQLiteStudio v3.1.1 on Fri Jul 28 16:42:11 2017
--
-- Text encoding used: System
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- Table: changes
DROP TABLE IF EXISTS changes;

CREATE TABLE changes (
    ID_NUM      INTEGER      PRIMARY KEY
                             UNIQUE
                             NOT NULL,
    Name        STRING (25)  NOT NULL,
    Email       STRING (25)  NOT NULL,
    Summary     STRING (140) NOT NULL,
    Description TEXT,
    Approver    STRING (25),
    StartDate   DATE,
    EndDate     DATE,
    AssetTag    STRING (25)  NOT NULL
);


-- Table: closed_incidents
DROP TABLE IF EXISTS closed_incidents;

CREATE TABLE closed_incidents (
    ID_NUM              INTEGER      PRIMARY KEY AUTOINCREMENT
                                     UNIQUE
                                     NOT NULL,
    SR_NUMBER           INTEGER (10) NOT NULL,
    SITE_NAME           STRING (64)  NOT NULL,
    SITE_ID             INTEGER (10) NOT NULL,
    CREATE_DATE         DATE         NOT NULL,
    DAYS_OPEN           INTEGER (3),
    LAST_MODIFIED       DATE,
    NEXT_ACTION_DUE     DATE,
    STATUS              STRING (25),
    SEVERITY            STRING (4)   NOT NULL,
    ISSUE               TEXT (256),
    COMMENT_UPDATE_FLAG STRING (4),
    COMMENTS            TEXT (256),
    CUSTOMER_CONTACT    STRING (20),
    EMC_OWNER           STRING (20),
    PRODUCT             STRING (50),
    SERIAL_NUMBER       STRING (20) 
);


-- Table: customer_sites
DROP TABLE IF EXISTS customer_sites;

CREATE TABLE customer_sites (
    ID_NUM          INTEGER     PRIMARY KEY AUTOINCREMENT
                                UNIQUE
                                NOT NULL,
    SITE_ID         INTEGER     NOT NULL,
    SITE_NAME       STRING (50) NOT NULL,
    PRIMARY_CONTACT STRING (20) NOT NULL
);


-- Table: incidents
DROP TABLE IF EXISTS incidents;

CREATE TABLE incidents (
    ID_NUM              INTEGER      PRIMARY KEY AUTOINCREMENT
                                     UNIQUE
                                     NOT NULL,
    SR_NUMBER           INTEGER (10) NOT NULL,
    SITE_NAME           STRING (64)  NOT NULL,
    SITE_ID             INTEGER (10) NOT NULL
                                     REFERENCES customer_sites (SITE_ID) MATCH SIMPLE,
    CREATE_DATE         DATE         NOT NULL,
    DAYS_OPEN           INTEGER (3),
    LAST_MODIFIED       DATE,
    NEXT_ACTION_DUE     DATE,
    STATUS              STRING (25),
    SEVERITY            STRING (4)   NOT NULL,
    ISSUE               TEXT (256),
    COMMENT_UPDATE_FLAG STRING (4),
    COMMENTS            TEXT (256),
    CUSTOMER_CONTACT    STRING (20),
    EMC_OWNER           STRING (20),
    PRODUCT             STRING (50),
    SERIAL_NUMBER       STRING (20) 
);


-- Table: install_base
DROP TABLE IF EXISTS install_base;

CREATE TABLE install_base (
    ID_NUM         INTEGER      PRIMARY KEY AUTOINCREMENT
                                UNIQUE
                                NOT NULL,
    SERIAL_NUM     STRING (20)  UNIQUE
                                NOT NULL,
    COUNTRY        STRING (20),
    LOCATION_ALIAS STRING,
    ASSET_ALIAS    STRING (20)  UNIQUE,
    PRODUCT        STRING (50)  NOT NULL,
    MODEL          STRING (50)  NOT NULL,
    SITE_ID        INTEGER (10) NOT NULL
                                REFERENCES customer_sites (SITE_ID) MATCH SIMPLE,
    CITY           STRING (20),
    CUSTOMER_NAME  STRING (20)  NOT NULL
                                REFERENCES customer_sites (SITE_NAME) 
);


-- Table: log
DROP TABLE IF EXISTS log;

CREATE TABLE log (
    ID_NUM            INTEGER     PRIMARY KEY AUTOINCREMENT
                                  UNIQUE
                                  NOT NULL,
    SR_NUM            INTEGER     NOT NULL,
    DATE_MODIFIED     DATE,
    ARCHIVED          BOOLEAN (4) NOT NULL,
    SITE_NAME         STRING (50) NOT NULL,
    SOLUTION_MODIFIED STRING (50),
    COMMENTS          TEXT (256) 
);


-- Table: stats
DROP TABLE IF EXISTS stats;

CREATE TABLE stats (
    ID_NUM          INTEGER PRIMARY KEY AUTOINCREMENT
                            NOT NULL
                            UNIQUE,
    DATE            DATE    NOT NULL,
    TIME            TIME    NOT NULL,
    NUM_SR_INBOUND  INTEGER NOT NULL,
    NUM_SR_OUTBOUND INTEGER NOT NULL,
    NUM_SR_TOTAL    INTEGER NOT NULL
);


-- Index: AssetTag
DROP INDEX IF EXISTS AssetTag;

CREATE INDEX AssetTag ON changes (
    AssetTag COLLATE BINARY
);


-- Index: Email
DROP INDEX IF EXISTS Email;

CREATE INDEX Email ON incidents (
    SITE_NAME COLLATE BINARY
);


COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
