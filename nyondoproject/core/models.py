from django.db import models

# Create your models here.
# PRODUCTS / STOCK
class Product(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    unit_cost = models.IntegerField()
    selling_price = models.IntegerField()
    stock_quantity = models.IntegerField()

    def __str__(self):
        return self.name


# CUSTOMERS (for credit scheme)
class Customer(models.Model):
    full_name = models.CharField(max_length=200)
    nin = models.CharField(max_length=20)
    phone = models.CharField(max_length=15)

    def __str__(self):
        return self.full_name


# SALES
class Sale(models.Model):
    CUSTOMER_TYPES = (
        ('Retail', 'Retail'),
        ('Wholesale', 'Wholesale'),
    )
    date = models.DateTimeField(auto_now_add=True)
    sales_representative = models.CharField(max_length=200)
    customer_name = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=20)
    customer_type = models.CharField( max_length=20,choices=CUSTOMER_TYPES)
    product_name = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    transport_fee = models.DecimalField(max_digits=10, decimal_places=2)
    def __str__(self):
        return self.product_name

# CREDIT SCHEME
class Deposit(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

class CreditProduct(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    def __str__(self):
        return self.name
    
#class Deposit(models.Model):
   # Customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    #amount = models.DecimalField(max_digits=10, decimal_places=2)
    #date = models.DateTimeField(auto_now_add=True)

    #def _str_(self):
     #   return f"{self.customer.full_name} - {self.amount}"

class CreditPurchase(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(CreditProduct, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

class Supplier(models.Model):
    Product = models.ForeignKey(Product, on_delete=models.CASCADE)
    supplier_name = models.CharField(max_length=100)
    quantity = models.IntegerField()
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    method_of_payment = models.CharField(max_length=100,default="Cash")
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.name   