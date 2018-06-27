from django.shortcuts import render
from market.models import Category, Goods, UserProfile, Comment, InstationMessage, User, MarkedTable
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.template import loader
from django.http import HttpResponse


# @staff_member_required
# def index(request):
#     context = {}
#     template = loader.get_template('app/index4.html')
#     return HttpResponse(template.render(context, request))


def gentella_html(request):
    context = {}
    # The template to be loaded as per gentelella.
    # All resource paths for gentelella end in .html.

    # Pick out the html file name from the url. And load that template.
    load_template = request.path.split('/')[-1]
    template = loader.get_template('app/' + load_template)
    return HttpResponse(template.render(context, request))


@staff_member_required
def index(request):
    summary = {}
    # Goods info
    goods = Goods.objects.all()
    total_price = 0
    total_visiting = 0
    total_price_last_week = 0
    for item in goods:
        total_price += item.price
        total_visiting += item.seen_times
        # if item.down_time
    average_price = total_price / len(goods)

    summary['user_amount'] = UserProfile.objects.count()
    summary['item_total_amount'] = Goods.objects.count()
    summary['item_on_sale_amount'] = Goods.objects.filter(on_sale=True).count()
    summary['messages_amount'] = InstationMessage.objects.filter(notification=False).count()
    summary['bulletin_amount'] = InstationMessage.objects.filter(notification=True).count()
    summary['avg_price'] = average_price
    summary['total_visiting_times'] = total_visiting

    context_dic = {'Summary': summary}
    return render(request, 'app/index4.html', context_dic)
