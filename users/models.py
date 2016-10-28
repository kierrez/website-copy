from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

from django.db.models import Count
from django.forms import ValidationError
import os
from recommend.models import Recommendation
from movie.models import Rating


def update_filename(instance, filename):
    path = os.path.join("user_files", instance.user.username)
    extension = '.' + filename.split('.')[1]
    fname = datetime.now().strftime("%Y-%m-%d %H-%M-%S") + extension
    return os.path.join(path, fname)


def validate_file_extension(value):
    if not value.name.endswith('.csv'):
        raise ValidationError('Only csv files are supported')


class UserProfile(models.Model):
    user = models.OneToOneField(User)

    imdb_id = models.CharField(blank=True, null=True, max_length=15)
    imdb_ratings = models.FileField(upload_to=update_filename, validators=[validate_file_extension], blank=True, null=True)
    imdb_ratings_used = models.DateTimeField(null=True, blank=True)
    picture = models.ImageField(upload_to=update_filename, blank=True, null=True)
    ratings_last_updated = models.DateTimeField(null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.user.username

    @property
    def count_ratings(self):
        return Rating.objects.filter(user=self.user).annotate(Count('title', distinct=True)).count()


class UserFollow(models.Model):
    user_follower = models.ForeignKey(User, on_delete=models.CASCADE)
    user_followed = models.ForeignKey(User, on_delete=models.CASCADE, related_name='second_user')

    class Meta:
        unique_together = ('user_follower', 'user_followed')
