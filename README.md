# 3ple~R

### Project Overview
The 3ple~R Management System is a web application designed to streamline the process of managing listed/rented properties. The platform allows property owners to list their properties, manage bookings and communicate with guests, while offering an easy-to-use interface for potential guests to find and book properties.

## Features
* User Authentication: Secure user registration and login system.
* Property Listings: Owners can list their properties, including details such as location, amenities, price and photos.
* Booking System: Guests can browse available properties and make bookings for specific dates.
* Review System: Guests can leave reviews after their stay, providing feedback to the owners and future guests.
* Admin Panel: An admin interface for managing users, properties and bookings.
* Real-time Messaging: A chat system for guests and hosts to communicate directly within the platform.

## Table of Contents
* [Architecture](#architecture)
* [Technologies Used](#technologies-used)
* [Installation](#installation)
* [Usage](#usage)
* [Database Schema](#database-schema)
* [Challenges and Improvements](#challenges-and-improvements)
* [Contributing](#contributing)
* [License](#license)

## Architecture
The application follows a modular design with a clear separation of concerns between the frontend, backend and database layers.
* Frontend: HTML, CSS, JavaScript with Bootstrap framework for dynamic UI.
* Backend: Python with Flask framework for handling API requests and database interactions.
* Database: MariaDB/MySQL for storing user, property, booking and review data.
* Hosting: The application is hosted on a cloud platform like Render.
* Authentication: User login and registration are managed using a secure authentication service.

## Technologies Used
* Frontend:
* * HTML5, CSS3, JavaScript
  * Bootstrap 5 for responsive design
* Backend:
* * Python (Flask) for the routes and REST API
* * MariaDB/MySQL for relational database management
* Other Services:
* * Cloud storage (e.g., Render) for managing property images
* * Messaging service for real-time chat between users
* * Email notification services for booking confirmations

## Installation
* Clone this repository: `git clone "https://github.com/Code021-raelle/bnb.git"`
* Access 3ple~R directory: `cd bnb`
* Install build command: `pip3 install -r requirements.txt`
* Run app(interactively): `python3 run.py` and Enter command
* Run app(production server): `gunicorn app:app`
* Access the app: `go to http://localhost:5000 on your browser to access the app`

## Usage
### Property owners
* Sign up or log in to list properties, set prices and manage bookings.
* Communicate directly with potential guests through the integrated messaging system.
### Guests
* Browse properties, filter by location, price and amenities.
* Make a booking, manage reservations and leave reviews for properties you've stayed in.

## Database Schema
* Users: Stores user details (ID, name, email, password and role).
* Properties: Stores property details (ID, owner, location, amenities and price).
* Bookings: Stores booking information (ID, user, property, check-in/out dates).
* Reviews: Stores guest reviews for properties.
* Messages: Stores messages between users.
* Payments: Stores payment information for bookings.
* Images: Stores property images.
* Notifications: Stores notification information for users.
* Roles: Stores user roles (owner, guest, admin).
* Permissions: Stores user permissions (view, edit, delete).
* Sessions: Stores user session information.
* Tokens: Stores user tokens for authentication.
Example table definitions:
```
flask db init
flask db migrate -m "add commit message"
flask db upgrade
```

## Challenges and Improvements
* Challenges:
+ Integrating the real-time chat features presented challenges with managing asynchronous communication.
+ Optimizing database queries to ensure quick response times with complex filters (e.g., by amenities, price or location).
* Improvements:
+ Enhance the UI/UX to make the booking and review process more intuitive.
+ Add support for more payment gateways to facilitate bookings.
+ Implement a mobile app to extend the platform's usability.

## Contributing
We welcome contributions to the project~ To contribute, follow these steps:
1. Fork the repository.
2. Create a new feature branch ( git checkout -b feature/feature-name ).
3. Commit your changes ( git add . && git commit -m "commit message" ).
4. Push your changes to the remote repository ( git push origin feature/feature-name ).
5. Open a pull request to merge your changes into the main branch.

## Authors
Gabriel Akinshola - [Github](https://github.com/Code021-raelle) / [Linkedin](https://www.linkedin.com/in/gabriel-akinshola)

## License
This project is licensed under the MIT License. See the LICENSE file for more details.