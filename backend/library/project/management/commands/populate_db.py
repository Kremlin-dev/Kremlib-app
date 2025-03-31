import os
import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from project.models import (
    UserProfile, Category, Book, Rating, Comment, 
    ReadingProgress, Collection, BookContent
)
from django.core.files.base import ContentFile

class Command(BaseCommand):
    help = 'Populate the database with dummy data for testing'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting to populate database with dummy data'))
        
        # Create categories
        self.create_categories()
        
        # Create users with profiles
        self.create_users()
        
        # Create books
        self.create_books()
        
        # Create ratings, comments, reading progress
        self.create_interactions()
        
        self.stdout.write(self.style.SUCCESS('Database populated successfully!'))
    
    def create_categories(self):
        categories = [
            'Education', 'Action', 'Adventure', 'Romance', 'Novel', 
            'African Tales', 'Religious', 'Science Fiction', 'Fantasy',
            'Biography', 'History', 'Self-Help', 'Business', 'Technology'
        ]
        
        for category_name in categories:
            Category.objects.get_or_create(name=category_name)
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(categories)} categories'))
    
    def create_users(self):
        # Create admin user
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@kremlib.com',
                'is_staff': True,
                'is_superuser': True
            }
        )
        
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            UserProfile.objects.get_or_create(
                user=admin_user,
                defaults={
                    'first_name': 'Admin',
                    'last_name': 'User',
                    'bio': 'System administrator',
                    'last_login': timezone.now(),
                    'login_count': 1
                }
            )
        
        # Create regular users
        usernames = ['john_doe', 'jane_smith', 'bob_johnson', 'alice_williams', 'charlie_brown']
        
        for i, username in enumerate(usernames):
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@example.com',
                }
            )
            
            if created:
                user.set_password('password123')
                user.save()
                
                first_name = username.split('_')[0].capitalize()
                last_name = username.split('_')[1].capitalize() if len(username.split('_')) > 1 else ''
                
                UserProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        'first_name': first_name,
                        'last_name': last_name,
                        'bio': f'I am {first_name}, an avid reader.',
                        'last_login': timezone.now() - timedelta(days=i),
                        'login_count': random.randint(1, 20)
                    }
                )
        
        self.stdout.write(self.style.SUCCESS(f'Created users: admin and {len(usernames)} regular users'))
    
    def create_books(self):
        users = User.objects.all()
        categories = Category.objects.all()
        
        book_data = [
            {
                'title': 'The Art of Programming',
                'author': 'John Coder',
                'description': 'A comprehensive guide to programming concepts and practices.',
                'isbn': '9781234567897',
                'category': 'Education',
                'is_public': True
            },
            {
                'title': 'Adventure in the Amazon',
                'author': 'Explorer Jane',
                'description': 'An exciting journey through the Amazon rainforest.',
                'isbn': '9781234567898',
                'category': 'Adventure',
                'is_public': True
            },
            {
                'title': 'Love in Paris',
                'author': 'Romantic Writer',
                'description': 'A heartwarming romance set in the city of love.',
                'isbn': '9781234567899',
                'category': 'Romance',
                'is_public': True
            },
            {
                'title': 'African Folktales',
                'author': 'Cultural Storyteller',
                'description': 'A collection of traditional African stories passed down through generations.',
                'isbn': '9781234567890',
                'category': 'African Tales',
                'is_public': True
            },
            {
                'title': 'The Future of AI',
                'author': 'Tech Visionary',
                'description': 'Exploring the possibilities and implications of artificial intelligence.',
                'isbn': '9781234567891',
                'category': 'Technology',
                'is_public': True
            },
            {
                'title': 'Private Journal',
                'author': 'Anonymous',
                'description': 'A personal journal not meant for public viewing.',
                'isbn': '9781234567892',
                'category': 'Novel',
                'is_public': False
            },
        ]
        
        for book_info in book_data:
            category = Category.objects.get(name=book_info['category'])
            uploader = random.choice(users)
            
            book, created = Book.objects.get_or_create(
                title=book_info['title'],
                defaults={
                    'author': book_info['author'],
                    'description': book_info['description'],
                    'isbn': book_info['isbn'],
                    'category': category,
                    'uploaded_by': uploader,
                    'is_public': book_info['is_public'],
                    'uploaded_on': timezone.now() - timedelta(days=random.randint(1, 100)),
                    'view_count': random.randint(10, 1000),
                    'download_count': random.randint(5, 500),
                }
            )
            
            if created:
                # Create book content
                BookContent.objects.create(
                    book=book,
                    content=f"Sample content for {book.title}. This is just placeholder text for testing purposes."
                )
                
                # Add to some user's collection
                if random.choice([True, False]) and book.is_public:
                    collector = random.choice(users)
                    Collection.objects.get_or_create(user=collector, book=book)
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(book_data)} books'))
    
    def create_interactions(self):
        users = User.objects.all()
        books = Book.objects.filter(is_public=True)
        
        # Create ratings
        for book in books:
            # Each book gets 0-3 ratings
            for _ in range(random.randint(0, 3)):
                user = random.choice(users)
                rating_value = random.randint(1, 5)
                
                Rating.objects.get_or_create(
                    user=user,
                    book=book,
                    defaults={
                        'rating': rating_value,
                        'review': f"{'Great' if rating_value > 3 else 'Average' if rating_value == 3 else 'Poor'} book. {'Highly recommended!' if rating_value == 5 else ''}"
                    }
                )
        
        # Create comments
        for book in books:
            # Each book gets 0-5 comments
            for _ in range(random.randint(0, 5)):
                user = random.choice(users)
                
                Comment.objects.create(
                    user=user,
                    book=book,
                    content=random.choice([
                        "I really enjoyed this book!",
                        "Interesting perspective.",
                        "The characters were well developed.",
                        "I couldn't put it down!",
                        "Looking forward to more from this author.",
                        "Not my favorite, but worth reading.",
                        "This book changed my perspective."
                    ]),
                    created_at=timezone.now() - timedelta(days=random.randint(0, 30))
                )
        
        # Create reading progress
        for book in books:
            # Each book gets 0-3 reading progress entries
            for _ in range(random.randint(0, 3)):
                user = random.choice(users)
                total_pages = random.randint(100, 500)
                current_page = random.randint(1, total_pages)
                completed = current_page == total_pages
                
                ReadingProgress.objects.get_or_create(
                    user=user,
                    book=book,
                    defaults={
                        'current_page': current_page,
                        'total_pages': total_pages,
                        'completed': completed,
                        'last_read': timezone.now() - timedelta(days=random.randint(0, 14))
                    }
                )
        
        self.stdout.write(self.style.SUCCESS('Created ratings, comments, and reading progress entries'))
