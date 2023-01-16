from django.urls import path
from .views import (HomePageView, faild_number, faild_page_view, show_keys_view, UserPanel,
                    end_sub, selectsubView, go_to_gateway_view, callback_gateway_view, loginView)
urlpatterns = [
    path("", HomePageView.as_view(), name="homepage"),
    path("sub/", selectsubView.as_view(), name="selectsub"),
    path("login/", loginView.as_view(), name="login"),
    path("end_sub/", end_sub, name="endsub"),
    path("faild_number/", faild_number, name="faild_number"),
    path("faild_buy/", faild_page_view, name="faild_buy"),
    path("show_keys/<str:key>/<str:id_subtype>",
         show_keys_view, name="show_keys"),
    path("user/<str:key>", UserPanel.as_view(), name="UserPanel"),
    path("buylink/<int:money>/<str:phonenumber>/<str:key>/<str:id_subtype>",
         go_to_gateway_view),
    path("callback-gateway/<int:money>/<str:phonenumber>/<str:key>/<str:id_subtype>",
         callback_gateway_view),
]
