/*
Testdata for testing in sangz jukebox utility database api. 
*/
INSERT INTO "users" VALUES(1,'Axel f.','Axel Foley','a.foley@lapd.com',1);
INSERT INTO "users" VALUES(2,'Kekkis','Urho Kaleva Kekkonen','ukk@fi.gov',1);
INSERT INTO "users" VALUES(3,'Jokke','Jouko Mauno Karviainen','joke1@gmail.com',0);
INSERT INTO "users" VALUES(4,'malinen','Jaakko Malinen','jake@gmail.com',0);
INSERT INTO "artists" VALUES(1,"Dire Straits");
INSERT INTO "artists" VALUES(2,"Metallica");
INSERT INTO "artists" VALUES(3,"Apulanta");
INSERT INTO "artists" VALUES(4,"Elvis Presley");
INSERT INTO "albums" VALUES(1,"disc1",4);
INSERT INTO "albums" VALUES(2,"Metallica",2);
INSERT INTO "songs" VALUES(1,"Piiskaa prkl","/home/paviaani/media/mp3","mp3",3,1,3);
INSERT INTO "songs" VALUES(2,"Heartbrake hostel","/home/paviaani/media/mp3","mp3",4,NULL,3);
INSERT INTO "songs" VALUES(3,"One","/home/paviaani/media/mp3","mp3",2,2,1);
INSERT INTO "songs" VALUES(4,"testsong","testdir","mp3",2,2,1);
INSERT INTO "votes" VALUES(1,1,1,1456752443, "upvote");
INSERT INTO "votes" VALUES(2,1,2,1456752444, "upvote");
INSERT INTO "votes" VALUES(3,1,3,1456752445, "upvote");
INSERT INTO "chat" values(1,1,1456752439,"Can someone add the new song by avicii?");
INSERT INTO "chat" values(2,2,1456752440,"Kepper of songs, please add all new songs! :P");
INSERT INTO "chat" values(3,3,1456752442,"I'm out, peace");
