# School System Project

This project is a Django-based school management system designed to facilitate the management of academic terms, classes, and subjects.

## Project Structure

The project consists of the following main components:

- **portal**: The main application that handles the academic setup, including classes and subjects.
  - **migrations**: Contains migration files for database schema changes.
  - **templates**: Holds HTML templates for rendering views.
    - **portal**: Contains specific templates for the portal application.
  - **static**: Directory for static files such as CSS and JavaScript.
  - **admin.py**: Registers models with the Django admin interface.
  - **apps.py**: Configuration for the portal application.
  - **forms.py**: Defines forms for user input.
  - **models.py**: Contains data models for the application.
  - **tests.py**: Contains tests to ensure application functionality.
  - **urls.py**: URL routing for the portal application.
  - **views.py**: Handles requests and responses.

- **school_system**: The main project directory.
  - **settings.py**: Configuration settings for the Django project.
  - **urls.py**: URL routing for the entire project.
  - **wsgi.py**: WSGI configuration for deploying the application.

## Setup Instructions

1. **Clone the Repository**: 
   ```
   git clone <repository-url>
   cd school_system
   ```

2. **Create a Virtual Environment**:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Requirements**:
   ```
   pip install -r requirements.txt
   ```

4. **Run Migrations**:
   ```
   python manage.py migrate
   ```

5. **Create a Superuser** (optional):
   ```
   python manage.py createsuperuser
   ```

6. **Run the Development Server**:
   ```
   python manage.py runserver
   ```

7. **Access the Application**: Open your web browser and go to `http://127.0.0.1:8000/`.

## Usage

- Navigate to the academic setup page to manage terms, classes, and subjects.
- Use the Django admin interface to manage data more efficiently.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.