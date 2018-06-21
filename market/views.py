from django.shortcuts import render
from market.models import Category, Goods, UserProfile, Comment, InstationMessage, User, MarkedTable
from market.forms import UserForm, UserProfieldForm, GoodsForm, CommentForm
from market.email import  send_system_mail

from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required

from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import json

from PIL import Image

# Create your views here.

def index(request):
    if request.user.is_authenticated:
        user = request.user
        user_profile = UserProfile.objects.get(user=user)
        message_unread = InstationMessage.objects.filter(receiver=user_profile, active=True).count()
    else:
        user_profile = []
        message_unread = 0
    category_list = Category.objects.all()
    goods_list = Goods.objects.filter(on_sale=True).order_by('-publish_time')
    context_dic = {'categories': category_list,
                   'user_profile': user_profile,
                   'goodses': goods_list,
                   'message_unread': message_unread}
    return render(request, 'market/index.html', context_dic)


def category(request, category_id):
    if request.user.is_authenticated:
        user = request.user
        user_profile = UserProfile.objects.get(user=user)
    else:
        user_profile = []
    page_list = []
    try:
        category_filter = Category.objects.get(pk=category_id)
        name = category_filter.name
        if request.GET.get('rank'):
            rank = request.GET.get('rank')
            goodses_list = Goods.objects.filter(category=category_filter,on_sale=True).order_by('-'+rank)
        else:
            goodses_list = Goods.objects.filter(category=category_filter,on_sale=True)
        # 实现分页功能
        paginator = Paginator(goodses_list, 12)     # Show 12 items per page
        page = request.GET.get('page')
        goodses = paginator.page(page)              # goods page
    except Category.DoesNotExist:
        pass
    except PageNotAnInteger:
        goodses = paginator.page(1)
    except EmptyPage:
        goodses = paginator.page(paginator.num_pages)

    for i in range(1, paginator.num_pages + 1):
        page_list.append(i)

    context_dic = {'category': category_filter,
                   'category_name': name,
                   'goodses': goodses,
                   'page_list': page_list,
                   'user_profile': user_profile}

    return render(request, 'market/category.html', context_dic)


def goods_page(request, goods_id):
    if request.user.is_authenticated:
        user = request.user
        user_profile = UserProfile.objects.get(user=user)
    else:
        user_profile = []
    comment_form = CommentForm()
    goods = Goods.objects.get(pk=goods_id)
    # record goods' seen times
    goods.seen_times += 1
    goods.save()
    comment_list = Comment.objects.filter(goods=goods)
    context_dic = {'goods': goods, 'comments': comment_list, 'form': comment_form, 'user_profile': user_profile}
    return render(request, 'market/goods.html', context_dic)


@login_required
def add_comment(request, goods_id):
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=True)
            goods = Goods.objects.get(pk=goods_id)
            user = request.user
            user_profile = UserProfile.objects.get(user=user)
            comment.user = user_profile
            comment.goods = goods
            comment.save()
            message = InstationMessage()
            message.sender = user_profile
            message.receiver = goods.seller
            message.content = comment.content
            message.save()
            return goods_page(request,goods_id)
        else:
            print(comment_form.errors)
    else:
        comment_form =CommentForm()
    return render(request, 'market/add_comment.html')


@login_required
def add_goods(request):
    if request.method == 'POST':
        goods_form = GoodsForm(request.POST)
        if goods_form.is_valid():
            goods = goods_form.save(commit=True)
            user = request.user
            user_profile = UserProfile.objects.get(user=user)
            goods.seller = user_profile
            if 'picture' in request.FILES:
                goods.picture = request.FILES['picture']
            print(goods.picture)
            goods.on_sale=True
            goods.report_times=0
            goods.seen_times = 0
            goods.save()
            return index(request)
        else:
            print(goods_form.errors)
    else:
        goods_form = GoodsForm()

    return render(request, 'market/add_goods.html', {'form':goods_form})


def register(request):
    registered = False
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        if len( user_form['email'].value() ) <=0:
            return render(request, 'market/register.html',{'user_form': UserForm(), 'profile_form': UserProfieldForm(), 'registered': registered, 'message':"Email can't be empty"})
        if len( User.objects.filter(email=user_form['email'].value()) ) > 0:
            return render(request, 'market/register.html',{'user_form': UserForm(), 'profile_form': UserProfieldForm(), 'registered': registered, 'message':"The Email has been registered"})

        profile_form = UserProfieldForm(data=request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            #用户未激活
            user.is_active=False
            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            if 'avatar' in request.FILES:
                profile.avatar = request.FILES['avatar']
            profile.save()
            registered = True

            email = user.email
            username = user.username
            token = profile.generate_activate_token().decode('utf-8')
            send_system_mail(request,email,'激活账号 For 用户：'+username,'market/activate_content',token=token,username=username)
            return activate(request)
        else:
            print(user_form.errors,profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = UserProfieldForm()
    return render(request, 'market/register.html', {'user_form': user_form, 'profile_form': profile_form, 'registered': registered})


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = User.objects.filter(username=username)
        if user:
            user = user[0]
            if not user.is_active:
                return render(request, 'market/activate.html', {'message': "请尽快完成激活"})
            user = authenticate(username=username, password=password)
            if user:
                login(request,user)
                return HttpResponseRedirect('/market/')
        return render(request, 'market/login.html',{'failed':'用户名或密码错误'})
    else:
        return render(request, 'market/login.html',{})


@login_required
def about(request):
    return HttpResponse("This is about page.")


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/market/')


def profile(request, user_id):
    if  request.user.is_authenticated and str( request.user.pk ) == user_id :
        user = request.user
        user_profile = UserProfile.objects.get(user = user)

        if request.method == 'POST':

            campus = request.POST.get('campus', None)
            date = request.POST.get('date', None)
            description = request.POST.get('description', None)
            user_profile.campus = campus
            user_profile.date=date
            user_profile.description=description
            if 'avatar' in request.FILES:
                user_profile.avatar = request.FILES['avatar']
            user_profile.save()
        user_profile_top = user_profile
    else:
        user_profile = []
        user = User.objects.get(pk=user_id)
        user_profile_top = UserProfile.objects.get(user=request.user)
    user_profile = UserProfile.objects.get(user=user)
    goodses = Goods.objects.filter(seller=user_profile)
    user_profile.date = str( user_profile.date)
    context_dic = {'profile': user_profile, 'user_profile': user_profile_top, 'goodses': goodses}
    return render(request, 'market/profile.html',context_dic)

def self_profile(request, selector):
    labels = {'on_sale': '在售的商品','marked': '收藏的商品','out_sale': '下架的商品','info': '个人的信息'}
    user = request.user
    user_profile = UserProfile.objects.get(user=user)

    if request.method == 'GET':
        if selector == 'on_sale':
            goodses = Goods.objects.filter(seller=user_profile,on_sale=True).order_by('-publish_time')
        elif selector == 'marked':
            goodses = MarkedTable.objects.filter(user=user_profile)
        elif selector == 'out_sale':
            goodses = Goods.objects.filter(seller=user_profile,on_sale=False).order_by('-down_time')
        elif selector == 'info':
            goodses = None
            user_profile.date = str(user_profile.date)
        context_dic = {'profile':user_profile,'goodses':goodses,'selector':selector,'label':labels[selector]}
        return render(request,'market/self_profile.html',context_dic)
    else:
        if selector == 'info':
            user_profile.campus = request.POST.get('campus', None)
            user_profile.date=request.POST.get('date', None)
            user_profile.description=request.POST.get('description', None)
            if 'avatar' in request.FILES:
                user_profile.avatar = request.FILES['avatar']
            user_profile.save()
            user_profile = UserProfile.objects.get(user=user)
            user_profile.date = str(user_profile.date)
            print('yes')
            return render(request, 'market/self_profile.html', {'profile':user_profile,'selector':selector})


def search(request):
    if request.user.is_authenticated:
        user = request.user
        user_profile = UserProfile.objects.get(user = user)
    else:
        user_profile = []
    key_word = request.GET.get('keyword')
    category_list = Category.objects.all()
    goods_list = Goods.objects.filter(name__icontains=key_word)
    context_dic = {'categories': category_list, 'user_profile': user_profile, 'goodses': goods_list}
    return render(request, 'market/index.html', context_dic)


@login_required
def display_message(request):
    user = request.user
    user_profile = UserProfile.objects.get(user=user)
    messages = InstationMessage.objects.filter(receiver=user_profile).order_by('-send_time')
    for mes in messages:
        mes.active = False
        mes.save()
    context_dic = {'user_profile': user_profile, 'messages':  messages}
    return render(request, 'market/message.html', context_dic)


def activate(request):
    if( 'token' in request.GET ):
        token = request.GET['token']
        result = UserProfile.check_activate_token(token)
        temp = {0:'激活码错误，请重新激活',
                1:'激活码超时，请重新激活',
                2:'不存在此用户，请重新确认'}
        if result in temp.keys():
            result = temp[result]
        else:
            result = "用户："+result.username+" 已完成激活，请点击跳转"
    else:
        result = '请尽快完成激活'
    return render(request,'market/activate.html',{'message':result})

def forget(request):
    if request.method == 'POST':
        mail = request.POST['mail']
        user = User.objects.filter(email=mail)[0]
        if not user.is_active:
            return render(request, 'market/activate.html', {'message': '请先完成账号激活'})
        if user:

            email = user.email
            print(email)
            username = user.username
            user_profile = UserProfile.objects.get(user=user)
            token = user_profile.generate_activate_token().decode('utf-8')
            send_system_mail(request,email,'修改密码 For 用户：'+username,'market/forget_content',token=token,username=username)
            return  render(request,'market/forget.html',{'success':'已发送密码重置邮件，请尽快查看并修改'})
        return render(request,'market/forget.html',{'failed':'不存在此用户'})
    else:
        return render(request, 'market/forget.html')

def reset(request,active_code):
    if request.method == 'POST':
        result = UserProfile.check_activate_token(active_code)
        temp = {0:'验证链接错误，请重新请求',
                1:'验证链接超时，请重新请求',
                2:'不存在此用户，请重新确认'}
        if result in temp.keys():
            result=temp[result]
            return render(request,'market/reset.html',{'message':result})
        else:
            password = request.POST.get('password')
            result.set_password(password)
            result.save()
            return render(request,'market/reset.html',{'message':'修改成功，请点击跳转'})
    else:
        return render(request,'market/reset.html',{'active_code':active_code})

@csrf_exempt
def report(request):
    if(request.method == 'POST'):
        g_id = request.POST['g_id']
        good = Goods.objects.get(pk = g_id)
        good.report_times += 1
        if(good.report_times >= 10):
            good.on_sale=False
            good.down_time=timezone.now()
        good.save()
        return_json = {'report_times':good.report_times}
        print("times",good.report_times,good.down_time)
    else:return_json = {'report_times':-1}
    return HttpResponse(json.dumps(return_json), content_type='application/json')


@csrf_exempt
def down_goods(request):
    print('yes')
    if(request.method == 'POST'):
        g_id = request.POST['g_id']
        good = Goods.objects.get(pk = g_id)
        good.on_sale=False
        good.down_time=timezone.now()
        good.save()
        return_json = {'on_sale':good.on_sale}
    else:return_json = {'on_sale':True}
    print(return_json)
    return HttpResponse(json.dumps(return_json), content_type='application/json')