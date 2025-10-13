from django.db import models
from django.conf import settings 
from django.contrib.auth.models import User
class Film(models.Model):
    title=models.CharField(max_length=255)
    description=models.TextField()

    def str(self):
        return self.title
    
class Comment(models.Model):
    film=models.ForeignKey(Film,on_delete=models.CASCADE,related_name='comments')
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    text=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)

    def str(self):
        return f'Comment by {self.user.username} on {self.film.title}'
    


    


