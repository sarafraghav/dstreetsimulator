from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
# Create your views here.
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from .forms import *
from .models import *

UserModel = get_user_model()
from .forms import SignUpForm

@login_required
def Lauth(request):
        company = request.user
        if request.method == 'POST':
            form = leagueuserauth(request.POST)
            if form.is_valid():
              a = form.save(commit = False)
              if league.objects.filter(game_code=a.game_code).exists():
                  s = league.objects.get(game_code=a.game_code)
                  s.users.add(company)
                  s.save()
                  y = lauth(user=company,league=s,balance=100000)
                  y.save()
              elif a.game_code == "DSTREET01":
                  s = league(name="Dstreet",description="Check",starting_balance= 1500000,game_code=a.game_code, trading_active= True)
                  s.save()
                  s.users.add(company)
                  s.save()
                  y = lauth(user=company,league=s,balance=1500000)
                  y.save()
                
              else:
                  messages.error(request, "Incorrect Gamecode")
    
              return HttpResponseRedirect("/")

        else:
          form = leagueuserauth()
        context = {'form':form}
        template = "registration/lauth.html"
        return render(request, template, context)


def signup(request):
    if request.method == 'GET':
        return render(request, 'registration/signup.html')
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        # print(form.errors.as_data())
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            mail_subject = 'Activate your account.'
            message = render_to_string('registration/acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                mail_subject, message, to=[to_email]
            )
            email.send()
            return HttpResponse('Please confirm your email address to complete the registration')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = UserModel._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return HttpResponseRedirect(reverse_lazy("login"))
    else:
        return HttpResponse('Activation link is invalid!')


@login_required
def home(request):
    items = stocks.objects.filter(league = request.user.lauth.league)
    context = {'items': items}
    template = "simulator/myspace.html"
    return render(request, template, context)
    

@login_required
def portfolio(request):
    items = holdings.objects.filter(user = request.user, league = request.user.lauth.league).select_related('stock')
    template = "simulator/portfolio.html"
    cp = []
    for x in items:
        cv = {'stock':x.stock,'quantity':x.quantity,'average_price':x.average_price,'price':x.stock.price,'cp':x.quantity * x.stock.price,'type':x.type}
        cp.append(cv)
    context = {'items': cp}
    return render(request, template, context) 
    

@login_required
def thistory(request):
    items = transaction.objects.filter(league = request.user.lauth.league,user=request.user)
    context = {'items': items}
    template = "simulator/transaction_history.html"
    return render(request, template, context) 
    

@login_required
def orderbook(request):
    return render(request,"simulator/order_book.html")

@login_required
def pnl(request):
    cp = []
    for x in request.user.lauth.league.users.all().exclude(username='admin'):
        pvalue = x.lauth.balance
        y = holdings.objects.filter(user=x,league = x.lauth.league).select_related('stock')
        for z in y:
            pvalue += z.stock.price * z.quantity
        cv = {'user':x,'pvalue':pvalue}
        cp.append(cv)
    context = {'items': cp}
    template = "simulator/pnl.html"
    return render(request, template, context) 
   

@login_required
def News(request):
    items = news.objects.filter(league = request.user.lauth.league)
    context = {'items': items}
    template = "simulator/news.html"
    return render(request, template, context)  

@login_required
def News_v(request,newsid):
    x = news.objects.filter(id = newsid)
    if x.exists():
      item = x[0]
      context = {'item': item}
      template = "simulator/news_v.html"
      return render(request, template, context)
    else:
        return HttpResponseRedirect(reverse_lazy('news'))  

@login_required
def Ipo(request):
    items = ipo.objects.filter(league = request.user.lauth.league).select_related('stock')
    r = ipo_application.objects.filter(user = request.user).select_related('ipo')
    g = []
    for x in items:
        t =r.filter(ipo=x)
        if(t):
           status = t[0].status
        else:
          status = "Not Applied"
        g.append({'id':x.id,'stock':x.stock,"total_quantity":x.total_quantity,"quantity_per_user":x.quantity_per_user,'status':status})

    context = {'items': g}
    template = "simulator/ipo.html"
    return render(request, template, context)  

@login_required
def ipomanage(request,newsid):
    if request.user.is_superuser:
      items = ipo_application.objects.filter(ipo = newsid) 
      context = {'items': items,'id':newsid,'status':ipo.objects.get(id=newsid).status}
      template = "simulator/ipomanage.html"
      return render(request, template, context)
    else:
     return HttpResponseRedirect(reverse_lazy('ipo'))  

@login_required
def ipoapply(request,newsid):
    items = ipo.objects.filter(id = newsid)
    if(items):
        if not (ipo_application.objects.filter(user = request.user,ipo=items[0])):
          p = ipo_application(ipo= items[0],user=request.user,status="Applied")
          p.save()
    return HttpResponseRedirect(reverse_lazy('ipo'))  

@login_required
def ipodistribute(request,newsid):
   ipo_b = ipo.objects.filter(id=newsid).select_related('stock') 
   ipo_a = ipo_b[0]
   if(ipo_a.status != "Completed"):
    items = ipo_application.objects.filter(ipo = newsid)
    total_users = ipo_a.total_quantity / ipo_a.quantity_per_user
    users = items[:total_users]
    price = ipo_a.stock.price
    stock = ipo_a.stock
    total_cost = ipo_a.quantity_per_user*price
    for x in users:
        x.status = "Allocated"
        t =  x.user.lauth
        if(t.balance>total_cost):
           z = holdings(stock = stock,quantity = ipo_a.quantity_per_user,average_price = price, user = x.user, league = x.user.lauth.league,type='Equity')
           y = transaction(ttype='BUY',stock=stock,quantity = ipo_a.quantity_per_user,buy_price=price,total_investment=total_cost,user=x.user, league = x.user.lauth.league)
           t.balance -= total_cost
           t.save()
           z.save()
           y.save()
           x.save()
    ipo_a.status = "Completed"
    ipo_a.save()
   return HttpResponseRedirect(reverse_lazy('ipo'))  


@login_required
def equity_transactions(request):
        if request.method == 'POST':
            form = transactionadder(request.user.lauth.league, request.POST)
            if form.is_valid():
             a = form.save(commit = False)
             if a.quantity > 0:
              b_price = stocks.objects.get(id=a.stock.id).price
              a.buy_price = b_price
              a.total_investment = b_price * a.quantity
              a.user = request.user 
              a.league = request.user.lauth.league
              hs = holdings.objects.filter(user=request.user, league=request.user.lauth.league,stock = a.stock,type='Equity').select_related('stock')
              t = request.user.lauth
              if a.ttype == "BUY":
                if a.total_investment > request.user.lauth.balance:
                  messages.error(request,'Not enough balance')
                  return HttpResponseRedirect(reverse_lazy('transact'))
                t.balance -= a.total_investment 
                if hs.exists():
                  z = hs[0]
                  z.average_price = ((hs[0].average_price * hs[0].quantity) + (a.buy_price * a.quantity))/(hs[0].quantity+a.quantity) 
                  z.quantity += a.quantity 
                  z.save()
                else: 
                  z = holdings(stock = a.stock,quantity = a.quantity,average_price = a.buy_price, user = request.user, league = a.league)
                  z.save()    
              elif a.ttype == "SELL":
                  if hs.exists():
                       z = hs[0]
                       if z.quantity >= a.quantity:
                          z.quantity -= a.quantity 
                       else:
                           messages.error(request, "Sell Quantity cant be more than owned quantity")
                           return HttpResponseRedirect(reverse_lazy('transact'))
                       z.save()
                       t.balance += a.total_investment 
                       if z.quantity == 0:
                              z.delete()
                  else:
                           messages.error(request, "Stock not owned")
                           return HttpResponseRedirect(reverse_lazy('transact'))
              #--------SHORT---------------------
              hs = holdings.objects.filter(user=request.user, league=request.user.lauth.league,stock = a.stock,type='Short').select_related('stock')
           
              
              if a.ttype == "SHORT":
                hls = holdings.objects.filter(user=request.user, league=request.user.lauth.league,type='Short').select_related('stock')
                inv_sum = a.total_investment
                for x in hls:
                    inv_sum += x.average_price*x.quantity
                if inv_sum > 700000:
                  messages.error(request,'Max short volume 700,000')
                  return HttpResponseRedirect(reverse_lazy('transact'))
                if a.total_investment > request.user.lauth.balance:
                  messages.error(request,'Not enough balance')
                  return HttpResponseRedirect(reverse_lazy('transact'))
                if a.total_investment > 700000:
                  messages.error(request,'Max short volume 700,000')
                  return HttpResponseRedirect(reverse_lazy('transact'))
                t.balance -= a.total_investment 
                if hs.exists():
                  z = hs[0]
                  z.average_price = ((hs[0].average_price * hs[0].quantity) + (a.buy_price * a.quantity))/(hs[0].quantity+a.quantity) 
                  z.quantity += a.quantity 
                  z.save()
                else: 
                  z = holdings(stock = a.stock,quantity = a.quantity,average_price = a.buy_price, user = request.user, league = a.league,type='Short')
                  z.save()    
              elif a.ttype == "SQUARE OFF":
                 if hs.exists():
                       z = hs[0]
                       price_diff = z.average_price - b_price
                       current_p = z.average_price + price_diff
                       a.total_investment = current_p * a.quantity     
                       t.balance += a.total_investment 
                       if z.quantity >= a.quantity:
                          z.quantity -= a.quantity 
                       else:
                           messages.error(request, "Sell Quantity cant be more than owned quantity")
                           return HttpResponseRedirect(reverse_lazy('transact'))
                       z.save()
                       if z.quantity == 0:
                              z.delete()
              
              a.save()
              t.save()
             else:
                 messages.error(request,'Quantity Must Be Above 0') 
                 return HttpResponseRedirect(reverse_lazy('transact'))
             return HttpResponseRedirect(reverse_lazy('portfolio'))

        else:
          form = transactionadder(request.user.lauth.league)
        context = {'form':form}
        if(request.user.lauth.league.trading_active):
          template = "simulator/transact.html"
        else:
            template = "simulator/order_book.html"
        return render(request, template, context)
  
@login_required
def transfers(request):
        if request.method == 'POST':
            form = transfermaker(request.user,request.POST)
            if form.is_valid():
             a = form.save(commit = False)
             if a.quantity > 0: 
              a.to_user = request.user
              a.league = request.user.lauth.league
              a.status = 'PENDING'
              a.active = True
              a.save()
             else: 
                 messages.error(request,"Transfer Quantity Must Be Above 0")
                 return HttpResponseRedirect(reverse_lazy('transfers'))
             return HttpResponseRedirect(reverse_lazy('trequests'))
        else:
          form = transfermaker(request.user)
        context = {'form':form}
        template = "simulator/tclose.html"
        return render(request, template, context)

@login_required
def trequests(request):
      stock = transfer.objects.filter(to_user = request.user,league = request.user.lauth.league)
      othr = transfer.objects.filter(from_user = request.user,league = request.user.lauth.league)
      context = {'stock': stock, 'othr':othr}
      template = "simulator/requests.html"
      return render(request, template, context)


@login_required
def trd(request,stockid):
    stock = transfer.objects.get(id=stockid)
    stock.delete()
    return HttpResponseRedirect(reverse_lazy('trequests'))
    

@login_required
def trr(request,stockid):
    stock = transfer.objects.get(id=stockid)
    stock.status = 'DECLINED'
    stock.active = False
    stock.save()
    return HttpResponseRedirect(reverse_lazy('trequests'))

@login_required
def tra(request,stockid):
    stock = transfer.objects.get(id=stockid)
    hs = holdings.objects.filter(user=request.user, league=request.user.lauth.league,stock = stock.stock)
    if hs.exists():
        print('Step1')
        z = hs[0]
        if z.quantity >= stock.quantity:
            print('Step2')
            if z.user == stock.from_user:
                print('Step3')
                t = holdings.objects.filter(user=stock.to_user, league=request.user.lauth.league,stock = stock.stock)
                if t.exists():
                    print('Step4')
                    r = t[0]
                    r.quantity += stock.quantity
                    z.quantity -= stock.quantity
                    r.save()
                else:
                    print('Step4')
                    r = holdings(stock=stock.stock,quantity = stock.quantity,average_price = 0,user=stock.to_user,league=request.user.lauth.league)
                    r.save()
                    z.quantity -= stock.quantity
                    r.save()
                z.save()
                if z.quantity == 0:
                        z.delete()        
                stock.status = 'ACCEPTED'
                stock.active = False
                stock.save()  
            else:
                stock.status = 'INVALID'
                stock.active = False
                stock.save()
        else:
          stock.status = 'INVALID'
          stock.active = False
          stock.save()

    else:
        stock.status = 'INVALID'
        stock.active = False
        stock.save()
    return HttpResponseRedirect(reverse_lazy('trequests'))
