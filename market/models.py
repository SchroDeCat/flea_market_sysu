from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=32,unique=True)

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete='cascade')
    height = models.PositiveIntegerField(default="30", blank=True, null=True, editable=False)
    width = models.PositiveIntegerField(default="30", blank=True, null=True,  editable=False)
    avatar = models.ImageField(upload_to='profile', height_field='height', width_field='width', blank=True)

    def __str__(self):
        return self.user.username


class Goods(models.Model):
    name = models.CharField(max_length=128)
    description = models.CharField(max_length=512,blank=True)
    trade_location = models.CharField(max_length=32)
    price = models.IntegerField(default=0)
    category = models.ForeignKey(Category, on_delete='cascade')
    picture_url = models.CharField(max_length=128, blank=True)
    picture = models.ImageField(upload_to='goods', blank=True,null=True)
    seller = models.ForeignKey(UserProfile, blank=True, null=True,on_delete='cascade')
    discount = models.IntegerField(default=0, blank=True)
    goods_phone = models.IntegerField(null=True, blank=True)
    goods_qq = models.IntegerField(null=True, blank=True)
    publish_time = models.DateField(auto_now_add=True, null=True, blank=True)
    seen_times = models.IntegerField(default=0, blank=False)

    def __str__(self):
        return self.name


class Comment(models.Model):
    goods = models.ForeignKey(Goods, blank=True, null=True, on_delete='cascade')
    user = models.ForeignKey(UserProfile, blank=True, null=True, on_delete='cascade')
    content = models.CharField(max_length=256)
    comment_time = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.content


class InstationMessage(models.Model):
    receiver = models.ForeignKey(UserProfile, related_name='receiver_id', on_delete='cascade')
    sender = models.ForeignKey(UserProfile, related_name='sender_id', on_delete='cascade')
    content = models.CharField(max_length=140)
    send_time = models.DateField(auto_now_add=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.content
