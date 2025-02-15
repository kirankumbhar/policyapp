# PolicyApp

policy management app

## Prerequisites

- Python 3.10

## Installation

1. **Install Poetry** (if not already installed)
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. **Clone the repository**
   ```bash
   git clone <your-repository-url>
   cd <project-directory>
   ```

3. **Install dependencies**
   ```bash
   poetry install
   ```

4. **Activate the virtual environment**
   ```bash
   poetry shell
   ```


1. **Create database migrations**
   ```bash
   python manage.py makemigrations
   ```

2. **Apply migrations**
   ```bash
   python manage.py migrate
   ```

3. **Seed data**
   ```bash
   python manage.py seed_data
   ```

## Running the Development Server

1. **Start the Django development server**
   ```bash
   poetry run python manage.py runserver
   ```
   The server will start at `http://127.0.0.1:8000/`