# ingestionAPI
New ingestion status API to replace procmail

The Ingestion API is a REST application to replace the communication between WMKO and IPAC for archival messaging.

After cloning it to a repository, you must set up the config.ini file as a config.live.ini file with the proper database connections. To use test, set up the db_conn object to pass test=True in it's constructor. If you just initialize the class, it defaults to true.
