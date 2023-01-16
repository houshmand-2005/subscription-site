from django.shortcuts import render
from django.views import View
from django.shortcuts import redirect
from django.http import Http404
from azbankgateways import bankfactories, models as bank_models, default_settings as settings
from azbankgateways.exceptions import AZBankGatewaysException
import logging
import base64
import datetime
import time
import random
from .models import GenKey
from .forms import GenKeyForm


class HomePageView(View):
    def get(self, request):
        response = ("frp_core/homepage.html")
        return render(request, response)

    # def post(self, request):
    #     pass


class UserPanel(View):
    def get(self, request, key):
        if license_code_check(key) == "ok":
            timerim = lic_time_rim(key)
            context = {"timerim": timerim}
            response = ("frp_core/user_panel.html")
            return render(request, response, context)
        else:
            response = ("frp_core/subdone.html")
            return render(request, response)

    def post(self, request, key):
        id_prlist = request.POST.get('id_prlist')
        if id_prlist == "1":
            if license_code_check(key) == "ok":
                response = ("frp_core/proxy1.txt")
                return render(request, response)
        elif id_prlist == "2":
            if license_code_check(key) == "ok":
                response = ("frp_core/proxy2.txt")
                return render(request, response)
        else:
            response = ("frp_core/user_panel.html")
            return render(request, response)


class loginView(View):
    def get(self, request):
        response = ("frp_core/login.html")
        return render(request, response)

    def post(self, request):
        license_code = request.POST.get('login_code')
        output_license_code = license_code_check(license_code)
        if output_license_code == "ok":
            response = redirect(f'/user/{license_code}')
            return response
        response = ("frp_core/login.html")
        return render(request, response)


class selectsubView(View):
    def get(self, request):
        response = ("frp_core/selectsubtype.html")
        context = {}
        form = GenKeyForm(request.POST or None, request.FILES or None)
        context['form'] = form
        return render(request, response, context)

    def post(self, request):
        try:
            id_phonenumber = request.POST.get('phonenumber')
            if len(id_phonenumber) > 14 or len(id_phonenumber) < 7:
                response = redirect('/faild_number')
                return response
            id_subtype = request.POST.get("subtype")
            current_time = datetime.datetime.now()
            first_randnum = random.randint(532, 144125)
            second_randnum = random.randint(466, 23133)
            key_with_out_base64_encode = f"{first_randnum}key:{id_phonenumber}+{current_time}+{second_randnum}"
            print(key_with_out_base64_encode)
            key_string_bytes = key_with_out_base64_encode.encode("ascii")
            base64_bytes = base64.b64encode(key_string_bytes)
            keyInBase64 = base64_bytes.decode("ascii")
            keyInBase64 = keyInBase64 + "0y"
        except Exception as e:  # for wrong number input or error like this
            response = redirect('/faild_number')
            return response
        subs_money = {
            "1": 100000,
            "7": 200000,
            "30": 300000,
        }
        money_gen = subs_money.get(id_subtype)
        if money_gen is None:
            money_gen = 520000
        response = redirect(
            f'/buylink/{money_gen}/{id_phonenumber}/{keyInBase64}/{id_subtype}')
        return response


def faild_number(request):
    """if user input a unvalid phone number this function return the faild page"""
    response = ("frp_core/faild_number.html")
    return render(request, response)


def go_to_gateway_view(request, money, phonenumber, key, id_subtype):
    """Preparing the user to connect to the bank portaly"""
    amount = int(money)
    user_mobile_number = phonenumber
    factory = bankfactories.BankFactory()
    try:
        bank = factory.auto_create()
        bank.set_request(request)
        bank.set_amount(amount)
        bank.set_client_callback_url(
            f'/callback-gateway/{money}/{phonenumber}/{key}/{id_subtype}')
        bank.set_mobile_number(user_mobile_number)
        bank_record = bank.ready()
        return bank.redirect_gateway()
    except AZBankGatewaysException as e:
        logging.critical(e)
        response = redirect('/faild_buy')
        return response


def callback_gateway_view(request, money, phonenumber, key, id_subtype):
    """gateway callback view"""
    tracking_code = request.GET.get(settings.TRACKING_CODE_QUERY_PARAM, None)
    traclcodestr = str(tracking_code)
    if not tracking_code:
        logging.debug("URL is not valid")
        raise Http404
    try:
        bank_record = bank_models.Bank.objects.get(tracking_code=tracking_code)
    except bank_models.Bank.DoesNotExist:
        logging.debug("URL is not valid")
        raise Http404
    if bank_record.is_success:
        try:
            obj = GenKey.objects.get(key_code=key)
            key = obj.key_code
            id_subtype = obj.subtype
        except Exception:
            try:
                GenKey.objects.create(key_code=key, phonenumber=phonenumber,
                                      subtype=id_subtype, money_currency=money, payment_ok="true", trackingcode=traclcodestr)
            except Exception:
                response = redirect('/faild_buy')
                return response
        response = redirect(f'/show_keys/{key}/{id_subtype}')
        return response
    response = redirect('/faild_buy')
    return response


def show_keys_view(request, key, id_subtype):
    """Show the key to user"""
    obj = GenKey.objects.get(key_code=key)
    key = obj.key_code
    id_subtype = obj.subtype
    context = {"key": key, "id_subtype": id_subtype}
    response = ("frp_core/show_key.html")
    return render(request, response, context)


def faild_page_view(request):
    """If there is a problem with the purchase, this page will be shown"""
    response = ("frp_core/faild_page.html")
    return render(request, response)


def lic_time_rim(key: str) -> str:
    """Remaining subscription time"""
    license_code = key
    try:
        obj = GenKey.objects.get(key_code=license_code)
    except Exception:
        response = redirect('/end_sub')
        return response
    new_date = obj.buytime + datetime.timedelta(days=int(obj.subtype))
    current_time = time.strftime("%Y-%m-%d %H:%M:%S")
    current_time = datetime.datetime.strptime(
        current_time, "%Y-%m-%d %H:%M:%S")
    new_date = (str(new_date).split("."))
    new_date = str(new_date[0])
    code_time = datetime.datetime.strptime(
        str(new_date), "%Y-%m-%d %H:%M:%S")
    time_rim = code_time - current_time
    return str(time_rim)


def license_code_check(key: str) -> str:
    """Calculate if the user still has the sub"""
    license_code = key
    try:
        obj = GenKey.objects.get(key_code=license_code)
    except Exception:
        response = redirect('/end_sub')
        return response
    new_date = obj.buytime + datetime.timedelta(days=int(obj.subtype))
    current_time = time.strftime("%Y-%m-%d %H:%M:%S")
    current_time = datetime.datetime.strptime(
        current_time, "%Y-%m-%d %H:%M:%S")
    new_date = (str(new_date).split("."))
    new_date = str(new_date[0])
    code_time = datetime.datetime.strptime(
        str(new_date), "%Y-%m-%d %H:%M:%S")
    if current_time > code_time:
        obj.delete()
        response = redirect('/end_sub')
        return response
    if current_time < code_time:
        return "ok"


def end_sub(request):
    response = ("frp_core/subdone.html")
    return render(request, response)
