from django.db import models
from django.utils import timezone
# from django.contrib.auth.models import User 
from django.urls import reverse
from accounts.models  import *

# Create your models here.

class Post(models.Model):
    title = models.CharField(max_length = 100)
    content = models.TextField()
    date_posted = models.DateTimeField(default = timezone.now) 
    author = models.ForeignKey(User,on_delete = models.CASCADE)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:post_detail',kwargs={'pk' : self.pk})
    
class comment(models.Model):
    author = models.ForeignKey(User,on_delete=models.CASCADE)
    content = models.CharField(max_length=500)
    date_posted = models.DateTimeField(default=timezone.now)
    post_id = models.ForeignKey(Post,on_delete = models.CASCADE)