-- items definition
CREATE TABLE items(    num INTEGER PRIMARY KEY,    name TEXT,     category INTEGER,    a INTEGER,    b INTEGER,    c INTEGER,    d INTEGER,    e INTEGER);
INSERT INTO items (num,name,category,a,b,c,d,e) VALUES
	 (0,'new_item',-1,0,0,0,0,0),
	 (2,'test',-1,0,0,0,0,0);


-- "_item_0_monster" definition
CREATE TABLE _item_0_monster(     monster TEXT,     count INTEGER);
INSERT INTO "_item_0_monster" (monster,count) VALUES
	 ('1',1);

-- "_item_0_map" definition
CREATE TABLE _item_0_map(     map TEXT,     node TEXT,     count INTEGER);


-- "_item_2_monster" definition
CREATE TABLE _item_2_monster(     monster TEXT,     count INTEGER);
INSERT INTO "_item_2_monster" (monster,count) VALUES
	 ('1',1);

-- "_item_2_map" definition
CREATE TABLE _item_2_map(     map TEXT,     node TEXT,     count INTEGER);





-- monsters definition
CREATE TABLE monsters(    id INTEGER PRIMARY KEY AUTOINCREMENT,    name TEXT,    health INT,    strength INT,    xp INT,    items TEXT,    sentences TEXT);
INSERT INTO monsters (name,health,strength,xp,items,sentences) VALUES
	 ('Zombie',20,10,10,'0;2','hallo');

-- "_monster_1" definition
CREATE TABLE "_monster_1" (
	"map" INTEGER,
	node INTEGER
, count INTEGER);





-- maps definition
CREATE TABLE maps(    id INTEGER PRIMARY KEY AUTOINCREMENT,    name TEXT);



INSERT INTO "_map_1_1" ("map",node) VALUES
	 (1,2#);
INSERT INTO "_map_1_2" ("map",node) VALUES
	 (1,1),
	 (2,2);
INSERT INTO "_map_1_3" ("map",node) VALUES
	 (1,2);
INSERT INTO "_map_2_1" ("map",node) VALUES
	 (2,2);
INSERT INTO "_map_2_2" ("map",node) VALUES
	 (2,1);

INSERT INTO map_1 (name,category,connections,sentences_first,sentences_last,monsters,items,commands,additional_data) VALUES
	 ('afca',0,'2;new;0','cup','','1;1','','',NULL),
	 ('New',0,'1;afca;0
3;three;12',NULL,NULL,NULL,NULL,NULL,''),
	 ('three',0,'','news','','','','',NULL);
INSERT INTO map_2 (name,category,connections,sentences_first,sentences_last,monsters,items,commands,additional_data) VALUES
	 ('start',0,'2;next;0',NULL,NULL,NULL,NULL,'',''),
	 ('test_map2',1,'1;last;0',NULL,NULL,NULL,NULL,'','1;2;MapOne;33');
INSERT INTO maps (name) VALUES
	 ('new', "old");

