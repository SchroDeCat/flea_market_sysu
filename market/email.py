from __future__ import unicode_literals
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import render
from django.conf import settings




def send_activate_mail(request,to, subject, template, **kwargs):
    html = render(request, template+'.html',{'token':kwargs['token'],'username':kwargs['username'],'domain':settings.DOMAIN+'market/' })
    # text = render(request, template+'.txt', {'token':kwargs['token'],'username':kwargs['username'],'domain':settings.DOMAIN })
    text = "账号激活--SYSU二手信息发布平台"
    msg = EmailMultiAlternatives(subject, text, settings.EMAIL_HOST_USER, [to])
    msg.attach_alternative(html.content.decode('utf-8'), "text/html")

    msg.send()