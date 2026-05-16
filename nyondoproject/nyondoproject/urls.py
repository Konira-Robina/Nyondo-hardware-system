"""
URL configuration for nyondoproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('dashboard/',views.dashboard,name='dashboard'),
    path('products/', views.products, name='products'),
    path('add_product/', views.add_product, name='add_product'),
    path('edit_product/<int:id>/',views.edit_product,name='edit_product'),
    path('edit_sale/<int:id>/',views.edit_sale,name='edit_sale'),
    path('delete_sale/<int:id>/',views.delete_sale,name='delete_sale'),
    path('delete_product/<int:id>/', views.delete_product,name='delete_product'),
    path('sales/',views.sales,name='sales'),
    path('add_sales/',views.add_sales,name='add_sales'),
    path('suppliers/',views.suppliers,name='suppliers'),
    path('add_supplier/',views.add_supplier,name='add_supplier'),
    path('edit_supplier/<int:id>/',views.edit_supplier,name='edit_supplier'),
    path('delete_supplier/<int:id>/',views.delete_supplier,name='delete_supplier'),
    path('customers/',views.customers,name='customers'),
    path('add_customer/',views.add_customer,name='add_customer'),
    path('edit_customer/<int:id>/',views.edit_customer,name='edit_customer'),
    path('delete_customer/<int:id>/',views.delete_customer,name='delete_customer'),
    path('deposits/',views.deposits,name='deposits'),
    path('add_deposit/',views.add_deposit,name='add_deposit'),
    path('edit_deposit/<int:id>/',views.edit_deposit,name='edit_deposit'),
    path('delete_deposit/<int:id>/',views.delete_deposit,name='delete_deposit'),
    path('credit_purchases/',views.credit_purchases,name='credit_purchases'),
    path('add_credit_purchase/',views.add_credit_purchase,name='add_credit_purchase'),
    path('stock_movements/', views.stock_movements, name='stock_movements'),
    path('add_stock_movement/', views.add_stock_movement, name='add_stock_movement'),
    path('invoices/', views.invoices, name='invoices'),
    path('add_invoice/', views.add_invoice, name='add_invoice'),
    path('payments/',views.payments,name='payments'),
    path('add_payment/',views.add_payment,name='add_payment'),
    path('payment_receipt/<int:id>/',views.payment_receipt,name='payment_receipt'),
    path('notifications/', views.notifications, name='notifications'),
    path('add_notification/', views.add_notification, name='add_notification'),
    ]


