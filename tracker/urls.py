from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("register", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("transaction", views.transaction, name="transaction"),
    path("profile", views.profile, name="profile"),
    path("dashboard", views.dashboard, name="dashboard")
]