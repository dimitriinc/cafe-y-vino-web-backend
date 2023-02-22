# Backend scripts
Backend scripts for the Café y Vino [website](https://github.com/dimitriinc/cafe-y-vino-web).

## Summary
Three scripts: one to process the data sent via forms, one to listen to a Firestore database
and update a copy of it stored as a SQL database on the server, and one to
provide a specific collection of product for a specified menu category.

All three are Flask applications.

## Functionality
- form-data-responder.py - a collections of route functions, four of them process the form data, which includes storing a document in a Firestore database, constructing an email and sending it to the administration.
The email containing a reservation request contains two buttons for confirmation and rejection, each of which sends a request back to the script, where they are processed by the rest two route functions: the request's status gets updated in the database, and an email is sent to the client's mailbox.
- firestore-to-sql.py - each menu category is stored as a separate collection in the Firestore database. The script's job is to listen to each one of them and maintain the accurate copy in a SQL database on the server, one table for one collection.
- menu-provider.py - one route function, the request contains a table name as an argument. The script fetched the data from the specified table, converts it into a list of dictionaries and sends it to the client as a JSON.

## Technologies
- python 3.10.6
- flask 2.2.2
- flask_cors 3.0.10
- smtplib
- firebase_admin 6.0.1
- sqlite3

## License

This project is licensed under the terms of the MIT license.