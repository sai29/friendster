from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    MALE = 1
    FEMALE = 2
    GENDER_CHOICES = (
        (MALE, 'Male'),
        (FEMALE, 'Female')
    )

    connected_users = models.ManyToManyField("self", through='ConnectionRequest', through_fields=('from_user', 'to_user'), symmetrical=False)
    gender = models.PositiveSmallIntegerField(choices=GENDER_CHOICES, blank=True, null=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

class ConnectionRequest(models.Model):
    PENDING = 1
    ACCEPTED = 2
    REJECTED = 3
    BLOCKED = 4

    STATUS_CHOICES = (
        (PENDING, 'Pending'),
        (ACCEPTED, 'Accepted'),
        (REJECTED, 'Rejected'),
        (BLOCKED, 'Blocked')
    )

    from_user = models.ForeignKey(User, related_name='sender')
    to_user = models.ForeignKey(User, related_name='reciever')
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=PENDING)
    added_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return '%s sent request to %s' % (unicode(self.from_user), unicode(self.to_user))

