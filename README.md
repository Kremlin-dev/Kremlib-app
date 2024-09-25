

# Kremlib 📚

Kremlib is a platform where users can explore a wide range of books, read them online, and download them for offline use. In the future, users will also be able to upload their own books and share posts or reviews.

## Features
- **Access Books**: Browse through a curated collection of books.
- **Read Online**: Books are available for reading directly in the browser.
- **Download Books**: Download books in multiple formats for offline use.
- **Future Features**:
  - **Book Upload**: Users will be able to upload their own books to the platform.
  - **Post Sharing**: Users can write and share posts or reviews related to books.

## Tech Stack
- **Backend**: Django, Django REST Framework
- **Frontend**: (React)
- **Authentication**: JWT (JSON Web Tokens) for secure user authentication and authorization
- **Database**: MySQL 
- **Storage**: Cloud storage for managing book uploads and downloads


## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Kremlin-dev/Kremlib-app.git
   cd kremlib-app
   ```

2. **Set Up Virtual Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables**:
   Create a `.env` file in the project root with the following:
   ```bash
   SECRET_KEY=your-secret-key
   DATABASE_URL=your-database-url
   ```

5. **Apply Database Migrations**:
   ```bash
   python manage.py migrate
   ```

6. **Run the Development Server**:
   ```bash
   python manage.py runserver
   ```

## Future Development
- **Book Upload**: Users will be able to upload their own books to Kremlib.
- **Post Creation**: Users can write and share posts or reviews.
- **Recommendations**: Book recommendations based on user preferences and reading history.

## License
Kremlib is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Contact
For questions or support, please contact [yawamp27@gmail.com](mailto:yawam27@gmail.com).
```
