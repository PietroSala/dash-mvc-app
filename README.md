# Dash MVC Application

A web application built with Dash and following the Model-View-Controller (MVC) architectural pattern.

## Features

- Multiple pages with URL routing
- User authentication with login/logout
- Dynamic navigation based on login status
- Protected routes for authenticated users only
- Admin capabilities for user management
- Project management functionality
- Pony ORM with SQLite database

## Project Structure

```
project/
├── mvc_app.py            # Main application entry point
├── controller/           # Controller module
│   ├── __init__.py
│   ├── callbacks.py
│   ├── auth.py
│   ├── admin.py
│   ├── projects.py
│   └── routing.py
├── model/                # Model module
│   ├── __init__.py
│   ├── database.py
│   ├── user.py
│   ├── project.py
│   └── operations.py
├── view/                 # View module
│   ├── __init__.py
│   ├── layout.py
│   ├── auth.py
│   ├── navigation.py
│   ├── admin.py
│   ├── projects.py
│   ├── modals.py
│   └── components.py
└── data/                 # Data directory
    └── app_database.sqlite
```

## Installation

1. Clone this repository:
```bash
git clone https://github.com/your-username/dash-mvc-app.git
cd dash-mvc-app
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python mvc_app.py
```

5. Open your browser and navigate to `http://127.0.0.1:8050/`

## Default Users

The application comes with two default users:
- Regular user: username `user1`, password `password1`
- Admin user: username `admin`, password `adminpass`
- Quick admin login: username `a`, password `a`

## MVC Architecture

This application follows the Model-View-Controller (MVC) architectural pattern:

- **Model**: Handles data logic and database operations
- **View**: Manages the UI components and layouts
- **Controller**: Processes user inputs and coordinates the Model and View

## License

This project is licensed under the MIT License - see the LICENSE file for details.