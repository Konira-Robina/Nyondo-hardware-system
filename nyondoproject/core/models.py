from django.db import models
from django.core.validators import (MinValueValidator,MinLengthValidator,RegexValidator)
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

phone_validator = RegexValidator(
    regex=r'^\+?\d{10,15}$',
    message='Enter a valid phone number'
)

# NIN VALIDATOR
nin_validator = RegexValidator(
    regex=r'^[A-Z0-9]+$',
    message='NIN must contain only capital letters and numbers'
)


# PRODUCTS / STOCK
class Product(models.Model):
    name = models.CharField(max_length=100,validators=[MinLengthValidator(2)])
    category = models.CharField(max_length=100,validators=[MinLengthValidator(2)])
    unit_cost = models.DecimalField(max_digits=10,decimal_places=2,validators=[MinValueValidator(0)])
    selling_price = models.DecimalField(max_digits=10,decimal_places=2,validators=[MinValueValidator(0)])
    stock_quantity = models.IntegerField(validators=[MinValueValidator(0)])
    def clean(self):
        if self.selling_price < self.unit_cost:raise ValidationError("Selling price cannot be less than unit cost.")
    def __str__(self):
        return self.name


# CUSTOMERS
class Customer(models.Model):
    full_name = models.CharField(max_length=200,validators=[MinLengthValidator(3)])
    nin = models.CharField(max_length=20,unique=True,validators=[MinLengthValidator(5),nin_validator])
    phone = models.CharField(max_length=15,unique=True,validators=[phone_validator])
    def __str__(self):
        return self.full_name
# SALES
class Sale(models.Model):
    CUSTOMER_TYPES = (
        ('Retail', 'Retail'),
        ('Wholesale', 'Wholesale'),
    )
    date = models.DateTimeField(auto_now_add=True)
    sales_representative = models.CharField( max_length=200,validators=[MinLengthValidator(3)])
    customer_name = models.CharField(max_length=200,validators=[MinLengthValidator(3)])
    address = models.CharField(max_length=200,validators=[MinLengthValidator(3)])
    phone_number = models.CharField(max_length=20,validators=[phone_validator])
    customer_type = models.CharField(max_length=20,choices=CUSTOMER_TYPES)
    product_name = models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    selling_price = models.DecimalField(max_digits=10,decimal_places=2,validators=[MinValueValidator(0)])
    total_amount = models.DecimalField(max_digits=10,decimal_places=2,validators=[MinValueValidator(0)])
    transport_fee = models.DecimalField(max_digits=10,decimal_places=2,validators=[MinValueValidator(0)])
    def clean(self):
        if self.quantity > self.product_name.stock_quantity:raise ValidationError("Quantity cannot exceed available stock.")
    def __str__(self):
        return self.customer_name

# DEPOSITS
class Deposit(models.Model):
    customer = models.ForeignKey(Customer,on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10,decimal_places=2,validators=[MinValueValidator(1)])
    date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return str(self.customer)

# SUPPLIERS
class Supplier(models.Model):
    PAYMENT_METHODS = (
        ('Cash', 'Cash'),
        ('Mobile Money', 'Mobile Money'),
        ('Bank', 'Bank'),
    )
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    supplier_name = models.CharField(max_length=100,validators=[MinLengthValidator(3)])
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    cost_price = models.DecimalField(max_digits=10,decimal_places=2,validators=[MinValueValidator(0)])
    date = models.DateField()
    method_of_payment = models.CharField(max_length=100,choices=PAYMENT_METHODS,default="Cash")
    amount_paid = models.DecimalField(max_digits=10,decimal_places=2,validators=[MinValueValidator(0)])
    def clean(self):
        if self.amount_paid < 0:raise ValidationError("Amount paid cannot be negative.")
    def __str__(self):
        return self.supplier_name

# CREDIT PURCHASES
class CreditPurchase(models.Model):
    PAYMENT_STATUS = (
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
    )
    customer = models.ForeignKey(Customer,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    price_per_item = models.DecimalField(max_digits=10,decimal_places=2,validators=[MinValueValidator(0)])
    total_amount = models.DecimalField(max_digits=10,decimal_places=2,validators=[MinValueValidator(0)])
    amount_paid = models.DecimalField(max_digits=10,decimal_places=2,validators=[MinValueValidator(0)])
    balance = models.DecimalField(max_digits=10,decimal_places=2,validators=[MinValueValidator(0)])
    payment_status = models.CharField(max_length=20,choices=PAYMENT_STATUS,default='Pending')
    date = models.DateField(auto_now_add=True)
    def clean(self):
        if self.amount_paid > self.total_amount:raise ValidationError("Amount paid cannot exceed total amount.")
        if self.quantity > self.product.stock_quantity:
            raise ValidationError("Quantity exceeds available stock.")
    def __str__(self):
        return self.customer.full_name

# PAYMENTS
class Payment(models.Model):
    credit_purchase = models.ForeignKey(CreditPurchase,on_delete=models.CASCADE)
    amount_paid = models.DecimalField(max_digits=10,decimal_places=2,validators=[MinValueValidator(1)])
    payment_date = models.DateField(auto_now_add=True)
    balance_after_payment = models.DecimalField(max_digits=10,decimal_places=2,validators=[MinValueValidator(0)])
    def clean(self):
        if self.amount_paid > self.credit_purchase.balance:
          raise ValidationError("Payment cannot exceed remaining balance.")
    def __str__(self):
        return str(self.credit_purchase.customer)

# CATEGORY
class Category(models.Model):
    name = models.CharField(max_length=100,unique=True,validators=[MinLengthValidator(2)])
    def __str__(self):
        return self.name

# STOCK MOVEMENT
class StockMovement(models.Model):
    MOVEMENT_TYPES = (
        ('IN', 'IN'),
        ('OUT', 'OUT'),
    )
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    movement_type = models.CharField(max_length=10,choices=MOVEMENT_TYPES)
    quantity = models.IntegerField( validators=[MinValueValidator(1)])
    date = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)
    def __str__(self):
        return self.product.name

# INVOICE
class Invoice(models.Model):
    customer = models.ForeignKey(Customer,on_delete=models.CASCADE)
    invoice_number = models.CharField(max_length=100,unique=True)
    total_amount = models.DecimalField(max_digits=10,decimal_places=2,validators=[MinValueValidator(0)])
    date = models.DateField(auto_now_add=True)
    def __str__(self):
        return self.invoice_number

# NOTIFICATIONS
class Notification(models.Model):
    message = models.TextField(validators=[MinLengthValidator(3)])
    is_read = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.message    
    
class Receipt(models.Model):
    PAYMENT_METHODS = (
        ('Cash', 'Cash'),
        ('Mobile Money', 'Mobile Money'),
        ('Bank', 'Bank'),
    )
    receipt_number = models.CharField(max_length=100,unique=True)
    customer = models.ForeignKey(Customer,on_delete=models.CASCADE)
    sale = models.ForeignKey(Sale,on_delete=models.CASCADE, null=True,blank=True)
    amount_paid = models.DecimalField(max_digits=10,decimal_places=2,validators=[MinValueValidator(0)])
    payment_method = models.CharField(max_length=50,choices=PAYMENT_METHODS)
    date = models.DateTimeField(auto_now_add=True)
    issued_by = models.CharField(max_length=100)
    def __str__(self):
        return self.receipt_number    