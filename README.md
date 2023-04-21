# Chatroom:

A Flask-based chat application that allows users to send real-time messages and upload files in a chatroom. It uses Flask-SocketIO for real-time communication, SQLite as a database to store user and message information, and Flask-Login for user authentication.

## Project Structure

This project consists of two main files and two CSS files for styling:

### app.py

This is the main file of the application, which contains the necessary imports, database initialization, and route definitions. The file is organized into the following sections:

* Importing necessary libraries and setting up the application configuration.
* Defining the User class and initializing the login manager.
* Initializing the database and creating the required tables.
* Defining the routes for the index, registration, login, chatroom, and logout pages.
* Defining Socket.IO event listeners for handling incoming messages and file uploads.
* Running the application with Socket.IO support.
  templates

### HTML:

* index.html: The homepage with links to register and log in.
* register.html: The user registration page.
* login.html: The user login page.
* chatroom.html: The main chatroom page, where authenticated users can send messages and upload files.
  <br>
* static/css/style.css:
  This file contains the CSS styles for the application. It includes general styles, such as colors, fonts, and layout, as well as styles specific to each part of the application, such as the chat container, message container, input bar, and file previews.

### Features:

User registration and login system with hashed passwords.
Real-time messaging using WebSockets via Flask-SocketIO.
File uploading and serving with unique filenames.
Chatroom requiring user authentication.
Responsive design with a mobile-friendly layout.
Installation

### Usage:

Register a new user by clicking on "Register" and filling in the required fields.
Log in with your registered username and password.
Once logged in, you will be redirected to the chatroom. Send messages and upload files by using the provided input fields and buttons.
Log out by clicking on the "Logout" link.

###### Requirements:

Python 3.6 or higher.
