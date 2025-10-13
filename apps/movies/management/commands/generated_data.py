from typing  import Any 
from random import choice,choices
from datetime import datetime


from django.core.management.base import BaseCommand 
from django.contrib.auth.models import User 
from django.contrib.auth.hashers import make_password
from django.db.models import QuerySet


# import project commands
from apps.movies.models import Film,Comment



class Command(BaseCommand):

    EMAIL_DOMAINS=[
        'example.com',
        'gmail.com',
        'mail.com',
        'sample.org',

    ]
    FIRST_NAMES=[
        'Turarbek','Beknur','Almas',
        'John','Jane','Bob','Alice','Eve'
        'Temirbolat',
    ]

    LAST_NAMES=['Maratuly','Brown','Doe',
      'Smith','Taylor','Johnson','Williams','Jones'
      ,
      ]
    
    WORDS=[
        'lorem','ipsum','dolor','sit','amet',
        'consectetur','adipiscing','elit',
        'sed','do','eiusmod','tempor',
        'incididunt','ut','labore','et',
        'dolore','magna','aliqua',
    ]

    def __generate_users(self,count:int=20)->None:
        created_users:list[User]=[]
        USER_PASSWORD=make_password('password123')
        users_before=User.objects.count()
        for i in range(count):
            username=f'user:{i}'
            email=f'{username}@{choice(self.EMAIL_DOMAINS)}'
            first_name=choice(self.FIRST_NAMES)
            last_name=choice(self.LAST_NAMES)

            user,created=User.objects.update_or_create(
                username=username,
                defaults={
                    'email':email,
                    'first_name':first_name,
                    'last_name':last_name,
                    'password':USER_PASSWORD,
                
                }
            )
            if created:
                created_users.append(user)


            self.stdout.write(
                self.style.SUCCESS(F'Succesfully created {len(created_users)} users')
            )

    

    def __generate_films(self, count: int = 20) -> None:
        """
        Generate random films and save them to the database.
        """
        created_films: list[Film] = []
        films_before = Film.objects.count()

        for _ in range(count):
            title = ' '.join(choices(self.WORDS, k=3)).capitalize()
            description = ' '.join(choices(self.WORDS, k=25)).capitalize() + '.'
            created_films.append(
                Film(
                    title=title,
                    description=description,
                )
            )

        Film.objects.bulk_create(created_films)
        films_after = Film.objects.count()

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {films_after - films_before} films.'
            )
        )

    def __generate_comments(self, count: int = 50) -> None:
        """
        Generate random comments and save them to the database.
        """
        created_comments: list[Comment] = []
        users: QuerySet[User] = User.objects.all()
        films: QuerySet[Film] = Film.objects.all()
        comments_before = Comment.objects.count()

        if not users.exists() or not films.exists():
            self.stdout.write(
                self.style.WARNING(
                    'Cannot create comments. No users or films found.'
                )
            )
            return

        for _ in range(count):
            user = choice(users)
            film = choice(films)
            text = ' '.join(choices(self.WORDS, k=15)).capitalize() + '.'
            created_comments.append(
                Comment(
                    film=film,
                    user=user,
                    text=text,
                )
            )

        Comment.objects.bulk_create(created_comments)
        comments_after = Comment.objects.count()

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {comments_after - comments_before} comments.'
            )
        )

    def handle(self, *args: Any, **options: Any) -> None:
        """
        Command entry point.
        """
        start_time = datetime.now()

        # Clear old data
        self.stdout.write('Deleting old data...')
        Comment.objects.all().delete()
        Film.objects.all().delete()
        User.objects.filter(is_superuser=False, is_staff=False).delete()

        self.stdout.write('Generating new data...')
        self.__generate_users()
        self.__generate_films()
        self.__generate_comments()

        self.stdout.write(
            self.style.SUCCESS(
                f'Data generation completed in {(datetime.now() - start_time).total_seconds():.2f} seconds.'
            )
        )