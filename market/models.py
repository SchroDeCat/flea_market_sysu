# coding=utf-8
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

from itsdangerous import TimedJSONWebSignatureSerializer as Serializer,SignatureExpired
from itsdangerous import BadSignature,SignatureExpired

class Category(models.Model):
    name = models.CharField(max_length=32,unique=True)

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete='cascade')
    height = models.PositiveIntegerField(default="30", blank=True, null=True, editable=False)
    width = models.PositiveIntegerField(default="30", blank=True, null=True,  editable=False)
    avatar = models.ImageField(upload_to='profile',default="profile/default.png", height_field='height', width_field='width', blank=True)
    is_manager = models.BooleanField(default=False)
    date = models.DateField(null=True)
    campus = models.CharField(blank=True,max_length=20)
    description = models.CharField(blank=True,max_length=50)

    def __str__(self):
        return self.user.username

    #create activating code
    def generate_activate_token(self,expires_in=3600):
        s = Serializer(settings.SECRET_KEY,expires_in)
        return s.dumps({'id':self.user.id})

    #check activating code
    @staticmethod
    def check_activate_token(token):
        s = Serializer(settings.SECRET_KEY)
        try:
            data=s.loads(token)
        except BadSignature:
            #return '码错误'
            return 0
        except SignatureExpired:
            # return '超时'
            return 1
        user = User.objects.filter(id=data.get('id'))[0]
        if not user:
            # return 'no this user'
            return 2
        if not user.is_active:
            user.is_active = True
            user.save()
        # return '成功'
        return user

class Goods(models.Model):
    name = models.CharField(max_length=128)
    description = models.CharField(max_length=512,blank=True)
    trade_location = models.CharField(max_length=32)
    price = models.IntegerField(default=0)
    category = models.ForeignKey(Category, on_delete='cascade')
    picture_url = models.CharField(default="/market/media/goods/default.jpg",max_length=128, blank=True)
    picture = models.ImageField(upload_to='goods', blank=True,null=True)
    seller = models.ForeignKey(UserProfile, blank=True, null=True,on_delete='cascade')
    discount = models.IntegerField(default=0, blank=True)
    goods_phone = models.IntegerField(null=True, blank=True)
    goods_qq = models.IntegerField(null=True, blank=True)
    publish_time = models.DateField(auto_now_add=True, null=True, blank=True)
    seen_times = models.IntegerField(default=0, blank=False)
    report_times = models.IntegerField(default=0,blank=False)
    on_sale = models.BooleanField(default=True,blank=False,null=False)
    down_time = models.DateTimeField(auto_now_add=True,null=True,blank=True)

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
    item_id = models.ForeignKey(Goods, blank=True, null=True, on_delete='cascade')
    active = models.BooleanField(default=True)
    notification = models.BooleanField(default=False)

    def __str__(self):
        return self.content

class MarkedTable(models.Model):
    user = models.ForeignKey(UserProfile,on_delete='cascade')
    goods = models.ForeignKey(Goods,on_delete='cascade')
    mark_time = models.DateTimeField(auto_now_add=True)