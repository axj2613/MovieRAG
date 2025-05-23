:param {
  // Define the file path root and the individual file names required for loading.
  // https://neo4j.com/docs/operations-manual/current/configuration/file-locations/
  file_path_root: 'file:///', // Change this to the folder your script can access the files at.
  file_0: 'name.basics.csv',
  file_1: 'title.basics.csv',
  file_2: 'title.genres.csv',
  file_3: 'title.principals.csv'
};

// CONSTRAINT creation
// -------------------
//
// Create node uniqueness constraints, ensuring no duplicates for the given node label and ID property exist in the database. This also ensures no duplicates are introduced in future.
//
// NOTE: The following constraint creation syntax is valid for database version 4.4.0 and above.
CREATE CONSTRAINT `nconst_Person_uniq` IF NOT EXISTS
FOR (n: `Person`)
REQUIRE (n.`nconst`) IS UNIQUE;
CREATE CONSTRAINT `tconst_Movie_uniq` IF NOT EXISTS
FOR (n: `Movie`)
REQUIRE (n.`tconst`) IS UNIQUE;
CREATE CONSTRAINT `year_Year_uniq` IF NOT EXISTS
FOR (n: `Year`)
REQUIRE (n.`year`) IS UNIQUE;
CREATE CONSTRAINT `name_Genre_uniq` IF NOT EXISTS
FOR (n: `Genre`)
REQUIRE (n.`name`) IS UNIQUE;

:param {
  idsToSkip: []
};

// NODE load
// ---------
//
// Load nodes in batches, one node label at a time. Nodes will be created using a MERGE statement to ensure a node with the same label and ID property remains unique. Pre-existing nodes found by a MERGE statement will have their other properties set to the latest values encountered in a load file.
//
// NOTE: Any nodes with IDs in the 'idsToSkip' list parameter will not be loaded.
LOAD CSV WITH HEADERS FROM ($file_path_root + $file_0) AS row
WITH row
WHERE NOT row.`nconst` IN $idsToSkip AND NOT row.`nconst` IS NULL
CALL {
  WITH row
  MERGE (n: `Person` { `nconst`: row.`nconst` })
  SET n.`nconst` = row.`nconst`
  SET n.`name` = row.`primaryName`
} IN TRANSACTIONS OF 10000 ROWS;

LOAD CSV WITH HEADERS FROM ($file_path_root + $file_1) AS row
WITH row
WHERE NOT row.`tconst` IN $idsToSkip AND NOT row.`tconst` IS NULL
CALL {
  WITH row
  MERGE (n: `Movie` { `tconst`: row.`tconst` })
  SET n.`tconst` = row.`tconst`
  SET n.`primaryTitle` = row.`primaryTitle`
  SET n.`originalTitle` = row.`originalTitle`
  SET n.`isAdult` = toLower(trim(row.`isAdult`)) IN ['1','true','yes']
  SET n.`runtimeMinutes` = toInteger(trim(row.`runtimeMinutes`))
} IN TRANSACTIONS OF 10000 ROWS;

LOAD CSV WITH HEADERS FROM ($file_path_root + $file_1) AS row
WITH row
WHERE NOT row.`startYear` IN $idsToSkip AND NOT toInteger(trim(row.`startYear`)) IS NULL
CALL {
  WITH row
  MERGE (n: `Year` { `year`: toInteger(trim(row.`startYear`)) })
  SET n.`year` = toInteger(trim(row.`startYear`))
} IN TRANSACTIONS OF 10000 ROWS;

LOAD CSV WITH HEADERS FROM ($file_path_root + $file_2) AS row
WITH row
WHERE NOT row.`genres` IN $idsToSkip AND NOT row.`genres` IS NULL
CALL {
  WITH row
  MERGE (n: `Genre` { `name`: row.`genres` })
  SET n.`name` = row.`genres`
} IN TRANSACTIONS OF 10000 ROWS;


// RELATIONSHIP load
// -----------------
//
// Load relationships in batches, one relationship type at a time. Relationships are created using a MERGE statement, meaning only one relationship of a given type will ever be created between a pair of nodes.
LOAD CSV WITH HEADERS FROM ($file_path_root + $file_3) AS row
WITH row 
WHERE row.`category` = 'actor'
CALL {
  WITH row
  MATCH (source: `Person` { `nconst`: row.`nconst` })
  MATCH (target: `Movie` { `tconst`: row.`tconst` })
  MERGE (source)-[r: `ACTED`]->(target)
} IN TRANSACTIONS OF 10000 ROWS;

LOAD CSV WITH HEADERS FROM ($file_path_root + $file_1) AS row
WITH row 
CALL {
  WITH row
  MATCH (source: `Movie` { `tconst`: row.`tconst` })
  MATCH (target: `Year` { `year`: toInteger(trim(row.`startYear`)) })
  MERGE (source)-[r: `RELEASED`]->(target)
} IN TRANSACTIONS OF 10000 ROWS;

LOAD CSV WITH HEADERS FROM ($file_path_root + $file_2) AS row
WITH row 
CALL {
  WITH row
  MATCH (source: `Movie` { `tconst`: row.`tconst` })
  MATCH (target: `Genre` { `name`: row.`genres` })
  MERGE (source)-[r: `FROM`]->(target)
} IN TRANSACTIONS OF 10000 ROWS;

LOAD CSV WITH HEADERS FROM ($file_path_root + $file_3) AS row
WITH row 
WHERE row.`category` = 'actress'
CALL {
  WITH row
  MATCH (source: `Person` { `nconst`: row.`nconst` })
  MATCH (target: `Movie` { `tconst`: row.`tconst` })
  MERGE (source)-[r: `ACTED`]->(target)
} IN TRANSACTIONS OF 10000 ROWS;

LOAD CSV WITH HEADERS FROM ($file_path_root + $file_3) AS row
WITH row 
WHERE row.`category` = 'director'
CALL {
  WITH row
  MATCH (source: `Person` { `nconst`: row.`nconst` })
  MATCH (target: `Movie` { `tconst`: row.`tconst` })
  MERGE (source)-[r: `DIRECTED`]->(target)
} IN TRANSACTIONS OF 10000 ROWS;

LOAD CSV WITH HEADERS FROM ($file_path_root + $file_3) AS row
WITH row 
WHERE row.`category` = 'writer'
CALL {
  WITH row
  MATCH (source: `Person` { `nconst`: row.`nconst` })
  MATCH (target: `Movie` { `tconst`: row.`tconst` })
  MERGE (source)-[r: `WROTE`]->(target)
} IN TRANSACTIONS OF 10000 ROWS;

LOAD CSV WITH HEADERS FROM ($file_path_root + $file_3) AS row
WITH row 
WHERE row.`category` = 'producer'
CALL {
  WITH row
  MATCH (source: `Person` { `nconst`: row.`nconst` })
  MATCH (target: `Movie` { `tconst`: row.`tconst` })
  MERGE (source)-[r: `PRODUCED`]->(target)
} IN TRANSACTIONS OF 10000 ROWS;

LOAD CSV WITH HEADERS FROM ($file_path_root + $file_3) AS row
WITH row 
WHERE row.`category` = 'composer'
CALL {
  WITH row
  MATCH (source: `Person` { `nconst`: row.`nconst` })
  MATCH (target: `Movie` { `tconst`: row.`tconst` })
  MERGE (source)-[r: `COMPOSED`]->(target)
} IN TRANSACTIONS OF 10000 ROWS;

LOAD CSV WITH HEADERS FROM ($file_path_root + $file_3) AS row
WITH row 
WHERE row.`category` = 'cinematographer'
CALL {
  WITH row
  MATCH (source: `Person` { `nconst`: row.`nconst` })
  MATCH (target: `Movie` { `tconst`: row.`tconst` })
  MERGE (source)-[r: `CINEMATOGRAPHED`]->(target)
} IN TRANSACTIONS OF 10000 ROWS;

LOAD CSV WITH HEADERS FROM ($file_path_root + $file_3) AS row
WITH row 
WHERE row.`category` = 'editor'
CALL {
  WITH row
  MATCH (source: `Person` { `nconst`: row.`nconst` })
  MATCH (target: `Movie` { `tconst`: row.`tconst` })
  MERGE (source)-[r: `EDITED`]->(target)
} IN TRANSACTIONS OF 10000 ROWS;

LOAD CSV WITH HEADERS FROM ($file_path_root + $file_3) AS row
WITH row 
WHERE row.`category` = 'production_designer'
CALL {
  WITH row
  MATCH (source: `Person` { `nconst`: row.`nconst` })
  MATCH (target: `Movie` { `tconst`: row.`tconst` })
  MERGE (source)-[r: `DESIGNED PRODUCTION`]->(target)
} IN TRANSACTIONS OF 10000 ROWS;

LOAD CSV WITH HEADERS FROM ($file_path_root + $file_3) AS row
WITH row 
WHERE row.`category` = 'self'
CALL {
  WITH row
  MATCH (source: `Person` { `nconst`: row.`nconst` })
  MATCH (target: `Movie` { `tconst`: row.`tconst` })
  MERGE (source)-[r: `SELF`]->(target)
} IN TRANSACTIONS OF 10000 ROWS;

LOAD CSV WITH HEADERS FROM ($file_path_root + $file_3) AS row
WITH row 
WHERE row.`category` = 'casting_director'
CALL {
  WITH row
  MATCH (source: `Person` { `nconst`: row.`nconst` })
  MATCH (target: `Movie` { `tconst`: row.`tconst` })
  MERGE (source)-[r: `DIRECTED CASTING`]->(target)
} IN TRANSACTIONS OF 10000 ROWS;

LOAD CSV WITH HEADERS FROM ($file_path_root + $file_3) AS row
WITH row 
WHERE row.`category` = 'archive_footage'
CALL {
  WITH row
  MATCH (source: `Person` { `nconst`: row.`nconst` })
  MATCH (target: `Movie` { `tconst`: row.`tconst` })
  MERGE (source)-[r: `ARCHIVED FOOTAGE`]->(target)
} IN TRANSACTIONS OF 10000 ROWS;

LOAD CSV WITH HEADERS FROM ($file_path_root + $file_3) AS row
WITH row 
WHERE row.`category` = 'archive_sound'
CALL {
  WITH row
  MATCH (source: `Person` { `nconst`: row.`nconst` })
  MATCH (target: `Movie` { `tconst`: row.`tconst` })
  MERGE (source)-[r: `ARCHIVED SOUND`]->(target)
} IN TRANSACTIONS OF 10000 ROWS;
