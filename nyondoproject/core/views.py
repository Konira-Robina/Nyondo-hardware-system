from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db.models import Sum
from decimal import Decimal
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import (Customer,Deposit,CreditPurchase,Product,Sale,Supplier,Payment,Invoice,Notification,StockMovement, Cart, CartItem)

def index(request):
    return render(request,'index.html')
@login_required
def dashboard(request):
    # COUNTS
    total_products = Product.objects.count()
    total_sales = Sale.objects.count()
    total_customers = Customer.objects.count()
    total_suppliers = Supplier.objects.count()
    total_credit_purchases = CreditPurchase.objects.count()
    total_deposits = Deposit.objects.count()

    # TOTAL REVENUE
    total_revenue = Sale.objects.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    # TOTAL DEPOSITS AMOUNT
    total_deposit_amount = Deposit.objects.aggregate(Sum('amount'))['amount__sum'] or 0
    
    # TOTAL CREDIT BALANCE
    total_credit_balance = CreditPurchase.objects.aggregate(Sum('balance'))['balance__sum'] or 0

    # LOW STOCK PRODUCTS
    low_stock_products = Product.objects.filter(stock_quantity__lt=10)

    # RECENT SALES
    recent_sales = Sale.objects.all().order_by('-date')[:5]

    # RECENT SUPPLIERS
    recent_suppliers = Supplier.objects.all().order_by('-date')[:5]
    
    context = {
        'total_products': total_products,
        'total_sales': total_sales,
        'total_customers': total_customers,
        'total_suppliers': total_suppliers,
        'total_credit_purchases': total_credit_purchases,
        'total_deposits': total_deposits,
        'total_revenue': total_revenue,
        'total_deposit_amount': total_deposit_amount,
        'total_credit_balance': total_credit_balance,
        'low_stock_products': low_stock_products,
        'recent_sales': recent_sales,
        'recent_suppliers': recent_suppliers,
    }
    return render(request,'dashboard.html',context)

@login_required
def products(request):
    products = Product.objects.all()
    return render(request, 'products.html', {'products': products})

def add_product(request):
    if request.method == 'POST':
        try:
            product = Product(
                name=request.POST.get('name'),
                category=request.POST.get('category'),
                unit_cost=request.POST.get('unit_cost'),
                selling_price=request.POST.get('selling_price'),
                stock_quantity=request.POST.get('stock_quantity')
            )
            product.full_clean()
            product.save()
            messages.success(request, "Product added successfully")
            return redirect('products')
        except ValidationError as e:
            messages.error(request, e)
            return redirect('add_product')
    return render(request, 'add_product.html')

def edit_product(request, id):
    product = get_object_or_404(Product, id=id)
    if request.method == 'POST':
        try:
            product.name = request.POST.get('name')
            product.category = request.POST.get('category')
            product.unit_cost = request.POST.get('unit_cost')
            product.selling_price = request.POST.get('selling_price')
            product.stock_quantity = request.POST.get('stock_quantity')
            product.full_clean()
            product.save()
            messages.success(request, "Product updated successfully")
            return redirect('products')
        except ValidationError as e:
            messages.error(request, e)
    return render(request, 'edit_product.html', {'product': product})

def delete_product(request, id):
    product = get_object_or_404(Product, id=id)
    product.save()
    product.delete()
    messages.success(request, "Product deleted successfully")
    return redirect('products')
# SALES INFORMATION

# ADD SALE VIEW
from decimal import Decimal
from django.core.exceptions import ValidationError

# ADD SALES

@login_required
def add_sales(request):

    # FETCH PRODUCTS
    products = Product.objects.all()
    if request.method == 'POST':
        try:
            # GET FORM DATA
            sales_representative = request.POST.get('sales_representative')
            customer_name = request.POST.get('customer_name')
            address = request.POST.get('address')
            phone_number = request.POST.get('phone_number')
            customer_type = request.POST.get('customer_type')
            product_id = request.POST.get('product_name')
            quantity = int(request.POST.get('quantity'))
            selling_price = Decimal(request.POST.get('selling_price'))
            distance = Decimal(request.POST.get('distance'))

            # GET PRODUCT
            product = get_object_or_404(Product,id=product_id)

            # STOCK VALIDATION
            if quantity > product.stock_quantity:
                messages.error(request,"Not enough stock available")
                return redirect('add_sales')

            # CALCULATE GOODS TOTAL
            goods_total = (quantity * selling_price)

            # TRANSPORT RULE
            if goods_total >= Decimal('500000') and distance <= Decimal('10'):
                transport_fee = Decimal('0')
            else:
                transport_fee = Decimal('30000')

            # FINAL TOTAL
            total_amount = (goods_total + transport_fee)

            # CREATE SALE
            sale = Sale(sales_representative=sales_representative,
                customer_name=customer_name,
                address=address,
                phone_number=phone_number,
                customer_type=customer_type,
                product_name=product,
                quantity=quantity,
                selling_price=selling_price,
                transport_fee=transport_fee,
                total_amount=total_amount
            )
            # MODEL VALIDATION
            sale.full_clean()
            # SAVE SALE
            sale.save()

            # REDUCE STOCK
            product.stock_quantity -= quantity
            product.save()
            messages.success(request,"Sale added successfully")
            return redirect('sales')
        except ValidationError as e:
            messages.error(request, e)
        except ValueError:
            messages.error(request,"Please enter valid numbers")
        except Exception as e:
            messages.error(request,f"Error: {e}")
    # GET REQUEST
    context = {'products': products}
    return render(request,'add_sales.html',context)

# SALES LIST VIEW
def sales(request):
    # Fetch all sales
    sales = Sale.objects.all().order_by('-date')
    context = {'sales': sales}
    return render( request,'sales.html',context)

# EDIT SALE
def edit_sale(request, id):
    sale = get_object_or_404(Sale, id=id)
    products = Product.objects.all()
    if request.method == 'POST':
        try:
            # RESTORE OLD STOCK
            old_product = sale.product_name
            old_product.stock_quantity += sale.quantity
            old_product.save()
            # NEW PRODUCT
            product_id = request.POST.get('product_name')
            product = Product.objects.get(id=product_id)
            quantity = int(request.POST.get('quantity'))
            # VALIDATE STOCK
            if quantity > product.stock_quantity:
                messages.error(request, "Not enough stock available")
                return redirect('edit_sale', id=id)
            # UPDATE FIELDS
            sale.sales_representative = request.POST.get('sales_representative')
            sale.customer_name = request.POST.get('customer_name')
            sale.address = request.POST.get('address')
            sale.phone_number = request.POST.get('phone_number')
            sale.customer_type = request.POST.get('customer_type')
            sale.product_name = product
            sale.quantity = quantity
            sale.selling_price = request.POST.get('selling_price')
            sale.transport_fee = request.POST.get('transport_fee')
            sale.total_amount = (float(sale.quantity)* float(sale.selling_price)) + float(sale.transport_fee)
            sale.full_clean()
            sale.save()
            # REDUCE NEW STOCK
            product.stock_quantity -= quantity
            product.save()
            messages.success(request, "Sale updated successfully")
            return redirect('sales')
        except ValidationError as e:
            messages.error(request, e)
    context = {'sale': sale,'products': products}
    return render(request, 'edit_sales.html', context)

#Deleting Sales
def delete_sale(request, id):
    sale = get_object_or_404(Sale, id=id)
    product = sale.product_name
    product.stock_quantity += sale.quantity
    product.save()
    sale.delete()
    messages.success(request, "Sale deleted successfully")
    return redirect('sales')

@login_required
def cart(request):
    cart_id = request.session.get('cart_id')
    if cart_id:
        cart = Cart.objects.get(id=cart_id)
    else:
        cart = Cart.objects.create()
        request.session['cart_id'] = cart.id
    items = cart.items.all()
    total = sum(item.subtotal for item in items)
    context = {
        'cart': cart,
        'items': items,
        'total': total
    }
    return render(request, 'cart.html', context)

# STEP 5 — ADD TO CART 
@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product,id=product_id)
    quantity = int(request.POST.get('quantity'))

    # STOCK VALIDATION
    if quantity > product.stock_quantity:
        messages.error(request,'Not enough stock available')
        return redirect('products')

    # GET OR CREATE CART
    cart_id = request.session.get('cart_id')
    if cart_id:
        cart = Cart.objects.get(id=cart_id)
    else:
        cart = Cart.objects.create()
        request.session['cart_id'] = cart.id

    # CHECK EXISTING ITEM
    item = CartItem.objects.filter(cart=cart,product=product).first()
    subtotal = Decimal(quantity) * product.selling_price
    if item:
        item.quantity += quantity
        item.subtotal += subtotal
        item.save()
    else:
        CartItem.objects.create(
            cart=cart,
            product=product,
            quantity=quantity,
            selling_price=product.selling_price,
            subtotal=subtotal
        )
    messages.success(request,'Product added to cart')
    return redirect('cart')

# REMOVE ITEM FROM CART
@login_required
def remove_cart_item(request, id):
    item = get_object_or_404(CartItem,id=id)
    item.delete()
    messages.success(request,'Item removed from cart')
    return redirect('cart')

@login_required
def checkout(request):
    cart_id = request.session.get('cart_id')
    if not cart_id:
        messages.error(request,'Cart is empty')
        return redirect('cart')
    cart = Cart.objects.get(id=cart_id)
    items = cart.items.all()
    if not items:
        messages.error( request,'Cart is empty')
        return redirect('cart')

    for item in items:
        product = item.product
        # REDUCE STOCK
        product.stock_quantity -= item.quantity
        product.save()
        # SAVE SALE RECORD
        Sale.objects.create(
            sales_representative=request.user.username,
            customer_name='Walk In Customer',
            address='N/A',
            phone_number='N/A',
            customer_type='Retail',
            product_name=product,
            quantity=item.quantity,
            selling_price=item.selling_price,
            transport_fee=0,
            total_amount=item.subtotal
        )
    # CLEAR CART
    cart.items.all().delete()
    del request.session['cart_id']
    messages.success(request,'Checkout completed successfully')
    return redirect('sales')

# CUSTOMERS LIST
def customers(request):
    customers = Customer.objects.all().order_by('-id')
    context = {'customers': customers}
    return render(request,'customers.html',context)
# ADD CUSTOMER
def add_customer(request):
    if request.method == 'POST':
        try:
            customer = Customer(
                full_name=request.POST.get('full_name'),
                nin=request.POST.get('nin'),
                phone=request.POST.get('phone')
            )
            customer.full_clean()
            customer.save()
            messages.success(request, "Customer added successfully")
            return redirect('customers')
        except ValidationError as e:
            messages.error(request, e)
    return render(request, 'add_customer.html')

# EDIT CUSTOMER
def edit_customer(request, id):
    customer = get_object_or_404(Customer,id=id)
    if request.method == 'POST':
        customer.full_name = request.POST.get('full_name')
        customer.nin = request.POST.get('nin')
        customer.phone = request.POST.get('phone')
        customer.save()
        messages.success(request,"Customer updated successfully")
        return redirect('customers')
    context = {'customer': customer}
    return render(
        request,'edit_customer.html',context)

# DELETE CUSTOMER
def delete_customer(request, id):
    customer = get_object_or_404(Customer,id=id)
    customer.delete()
    messages.success(request,"Customer deleted successfully")
    return redirect('customers')
   
# ADD SUPPLIER
def add_supplier(request):
    # FETCH ALL PRODUCTS
    products = Product.objects.all()
    if request.method == 'POST':
        # GET FORM DATA
        product_id = request.POST.get('product')
        supplier_name = request.POST.get('supplier_name')
        quantity = int(request.POST.get('quantity'))
        cost_price = float(request.POST.get('cost_price'))
        date = request.POST.get('date')
        method_of_payment = request.POST.get('method_of_payment')
        amount_paid = float(request.POST.get('amount_paid'))
        total_cost = quantity * cost_price
        balance = total_cost - amount_paid
        if balance <= 0:
            payment_status = 'Paid'
        elif amount_paid > 0:
            payment_status = 'Partial'
        else:
            payment_status = 'Pending'
        # GET PRODUCT

        product = Product.objects.get(id=product_id)
        # SAVE SUPPLIER RECORD
        Supplier.objects.create(product=product,
            supplier_name=supplier_name,
            quantity=quantity,
            cost_price=cost_price,
            date=date,
            method_of_payment=method_of_payment,
            amount_paid=amount_paid
        )
        # AUTO STOCK INCREASE
        product.stock_quantity += quantity
        product.save()

        messages.success(request,"Supplier added successfully")
        return redirect('suppliers')
    context = {'products': products}
    return render(request,'add_supplier.html',context)

# SUPPLIER LIST
@login_required
def suppliers(request):
    suppliers = Supplier.objects.all().order_by('-date')
    context = {'suppliers': suppliers}
    return render(request,'suppliers.html',context)

# EDIT SUPPLIER

def edit_supplier(request, id):
    supplier = get_object_or_404(Supplier,id=id)
    products = Product.objects.all()

    if request.method == 'POST':
        # RESTORE OLD STOCK FIRST
        old_quantity = supplier.quantity
        old_product = supplier.product
        old_product.stock_quantity -= old_quantity
        old_product.save()

        # NEW FORM DATA
        product_id = request.POST.get('product')
        supplier.product = Product.objects.get(id=product_id)
        supplier.supplier_name = request.POST.get('supplier_name')
        supplier.quantity = int(request.POST.get('quantity'))
        supplier.cost_price = float(request.POST.get('cost_price'))
        supplier.date = request.POST.get('date')
        supplier.method_of_payment = request.POST.get('method_of_payment')
        supplier.amount_paid = float( request.POST.get('amount_paid'))

        # ADD NEW STOCK
        supplier.product.stock_quantity += supplier.quantity
        supplier.product.save()
        # SAVE SUPPLIER
        supplier.save()
        messages.success(request,"Supplier updated successfully")
        return redirect('suppliers')
    context = {'supplier': supplier,'products': products}
    return render(request,'edit_supplier.html',context)

# DELETE SUPPLIER
def delete_supplier(request, id):
    supplier = get_object_or_404(Supplier,id=id)
    # REDUCE STOCK AGAIN
    supplier.product.stock_quantity -= supplier.quantity
    supplier.product.save()

    # DELETE RECORD
    supplier.delete()
    messages.success(request,"Supplier deleted successfully")
    return redirect('suppliers')

# DEPOSIT LIST
@login_required
def deposits(request):
    deposits = Deposit.objects.all().order_by('-date')
    context = {'deposits': deposits}
    return render(request,'deposits.html',context)

# ADD DEPOSIT
def add_deposit(request):
    customers = Customer.objects.all()
    if request.method == 'POST':
        try:
            customer = Customer.objects.get(id=request.POST.get('customer'))
            deposit = Deposit(customer=customer,amount=request.POST.get('amount'))
            deposit.full_clean()
            deposit.save()
            messages.success(request,'Deposit saved successfully')
            return redirect('deposits')
        except ValidationError as e:
            messages.error(request, e)
    context = {'customers': customers}
    return render(request, 'add_deposit.html', context)   
# EDIT DEPOSIT
def edit_deposit(request, id):
    deposit = get_object_or_404(Deposit, id=id)
    customers = Customer.objects.all()
    if request.method == 'POST':
        try:
            customer = Customer.objects.get(id=request.POST.get('customer'))
            deposit.customer = customer
            deposit.amount = request.POST.get('amount')
            deposit.full_clean()
            deposit.save()
            messages.success(request,'Deposit updated successfully')
            return redirect('deposits')
        except ValidationError as e:
            messages.error(request, e)
    context = {
        'deposit': deposit,
        'customers': customers
    }
    return render(request, 'edit_deposit.html', context)
# DELETE DEPOSIT
def delete_deposit(request, id):
    deposit = get_object_or_404(Deposit,id=id)
    deposit.delete()
    messages.success(request,'Deposit deleted successfully')
    return redirect('deposits')

# CREDIT PURCHASES LIST
@login_required
def credit_purchases(request):
    credits = CreditPurchase.objects.all().order_by('-date')
    context = {'credits': credits}
    return render(request,'credit_purchases.html',context)

# ADD CREDIT PURCHASE
@login_required
def add_credit_purchase(request):
    customers = Customer.objects.all()
    products = Product.objects.all()
    if request.method == 'POST':
        customer_id = request.POST.get('customer')
        product_id = request.POST.get('product')
        quantity = int(request.POST.get('quantity'))
        price_per_item = float(request.POST.get('price_per_item'))
        amount_paid = float(request.POST.get('amount_paid'))

        # GET OBJECTS
        customer = Customer.objects.get(id=customer_id)
        product = Product.objects.get(id=product_id)

        # STOCK VALIDATION
        if quantity > product.stock_quantity:
            messages.error(request,'Not enough stock available')
            return redirect('add_credit_purchase')

        # CALCULATIONS
        total_amount = quantity * price_per_item
        balance = total_amount - amount_paid

        # PAYMENT STATUS
        if balance <= 0:
            payment_status = 'Paid'
        else:
            payment_status = 'Pending'

        # SAVE CREDIT PURCHASE
        CreditPurchase.objects.create(
            customer=customer,
            product=product,
            quantity=quantity,
            price_per_item=price_per_item,
            total_amount=total_amount,
            amount_paid=amount_paid,
            balance=balance,
            payment_status=payment_status
        )

        # REDUCE STOCK
        product.stock_quantity -= quantity
        product.save()
        messages.success(request,'Credit purchase added successfully')
        return redirect('credit_purchases')

    # GET REQUEST
    context = {
        'customers': customers,
        'products': products
    }
    return render(request,'add_credit_purchase.html',context)
# ADD PAYMENT

@login_required
def add_payment(request):
    # SHOW ONLY PENDING CREDIT PURCHASES
    credits = CreditPurchase.objects.filter(payment_status='Pending')

    if request.method == 'POST':
        try:
            # GET CREDIT PURCHASE
            credit = get_object_or_404(CreditPurchase,id=request.POST.get('credit_purchase'))

            # GET AMOUNT
            amount_paid = Decimal(request.POST.get('amount_paid'))
          
            # VALIDATION
            if amount_paid <= 0:
                messages.error(request,"Amount must be greater than zero")
                return redirect('add_payment')

            # PREVENT OVERPAYMENT
            if amount_paid > credit.balance:
                messages.error(request,"Payment exceeds customer balance")
                return redirect('add_payment')

            # CALCULATE NEW BALANCE
            balance_after_payment = (credit.balance - amount_paid)

            # SAVE PAYMENT
            payment = Payment(
                credit_purchase=credit,
                amount_paid=amount_paid,
                balance_after_payment=balance_after_payment
            )
            payment.full_clean()
            payment.save()

            # UPDATE CREDIT PURCHASE
            credit.amount_paid += amount_paid
            credit.balance = balance_after_payment

            # UPDATE STATUS
            if credit.balance <= 0:
                credit.payment_status = 'Paid'
            else:
                credit.payment_status = 'Pending'
            credit.save()
            messages.success(request,"Payment recorded successfully")
            return redirect('payments')
        except ValidationError as e:messages.error(request,e)
        except Exception as e:
            messages.error(request,f"Error: {e}")
    context = {'credits': credits}
    return render( request,'add_payment.html',context)
# STOCK MOVEMENTS LIST

def stock_movements(request):
    movements = StockMovement.objects.all().order_by('-date')
    context = {'movements': movements}
    return render(request,'stock_movements.html',context)
# ADD STOCK MOVEMENT

def add_stock_movement(request):
    products = Product.objects.all()
    if request.method == 'POST':
        try:
            product_id = request.POST.get('product')
            movement_type = request.POST.get('movement_type')
            quantity = int(request.POST.get('quantity'))
            description = request.POST.get('description')
            product = Product.objects.get(id=product_id)
            # STOCK OUT VALIDATION
            if movement_type == 'OUT':
                if quantity > product.stock_quantity:
                    messages.error(request,"Not enough stock available")
                    return redirect('add_stock_movement')
                product.stock_quantity -= quantity
            else:
                product.stock_quantity += quantity
            product.save()
            movement = StockMovement(
                product=product,
                movement_type=movement_type,
                quantity=quantity,
                description=description)
            movement.full_clean()
            movement.save()
            messages.success(request,"Stock movement added successfully")
            return redirect('stock_movements')
        except ValidationError as e:
            messages.error(request, e)
    context = {'products': products}
    return render(request,'add_stock_movement.html',context)

# INVOICES LIST
@login_required
def invoices(request):
    invoices = Invoice.objects.all().order_by('-date')
    context = {'invoices': invoices}
    return render(request, 'invoices.html', context)
# ADD INVOICE

def add_invoice(request):
    customers = Customer.objects.all()
    if request.method == 'POST':
        try:
            customer_id = request.POST.get('customer')
            customer = Customer.objects.get(id=customer_id)
            invoice = Invoice(
                customer=customer,
                invoice_number=request.POST.get('invoice_number'),
                total_amount=request.POST.get('total_amount')
            )
            invoice.full_clean()
            invoice.save()
            messages.success(request,"Invoice created successfully")
            return redirect('invoices')
        except ValidationError as e:
            messages.error(request, e)
    context = {'customers': customers}
    return render(request, 'add_invoice.html', context)

# NOTIFICATIONS
def notifications(request):
    notifications = Notification.objects.all().order_by('-date')
    context = {'notifications': notifications}
    return render(request,'notifications.html',context)
# ADD NOTIFICATION

def add_notification(request):
    if request.method == 'POST':
        try:
            notification = Notification(
                message=request.POST.get('message')
            )
            notification.full_clean()
            notification.save()
            messages.success(
                request,
                "Notification added successfully"
            )
            return redirect('notifications')
        except ValidationError as e:
            messages.error(request, e)
    return render(request, 'add_notification.html')

# PAYMENTS LIST

def payments(request):
    payments = Payment.objects.all().order_by('-payment_date')
    context = {'payments': payments}
    return render(request,'payments.html',context)

# PAYMENT RECEIPT VIEW

@login_required
def payment_receipt(request, id):
    # GET PAYMENT
    payment = get_object_or_404(Payment,id=id)
    # SEND DATA TO TEMPLATE
    context = {'payment': payment}
    # RENDER TEMPLATE
    return render(request,'payment_receipt.html',context)


@login_required
def reports(request):
    # COUNTS
    total_products = Product.objects.count()
    total_sales_count = Sale.objects.count()
    total_customers = Customer.objects.count()
    total_suppliers = Supplier.objects.count()
    # SALES TOTAL
    total_sales = Sale.objects.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    # PAYMENTS TOTAL
    total_payments = Payment.objects.aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
    # CREDIT BALANCE
    outstanding_credit = CreditPurchase.objects.aggregate(Sum('balance'))['balance__sum'] or 0
    # LOW STOCK
    low_stock_products = Product.objects.filter(stock_quantity__lt=10)
    # RECENT DATA
    recent_sales = Sale.objects.order_by('-date')[:5]
    recent_payments = Payment.objects.order_by('-payment_date')[:5]
    recent_suppliers = Supplier.objects.order_by('-date')[:5]
    pending_credits = CreditPurchase.objects.filter( payment_status='Pending').order_by('-date')[:5]
    context = {
        'total_products': total_products,
        'total_sales_count': total_sales_count,
        'total_customers': total_customers,
        'total_suppliers': total_suppliers,
        'total_sales': total_sales,
        'total_payments': total_payments,
        'outstanding_credit': outstanding_credit,
        'low_stock_products': low_stock_products,
        'recent_sales': recent_sales,
        'recent_payments': recent_payments,
        'recent_suppliers': recent_suppliers,
        'pending_credits': pending_credits,
    }
    return render(request,'reports.html',context) 

# LOGIN VIEW
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        # AUTHENTICATE USER
        user = authenticate(request,username=username,password=password)
        # CHECK USER
        if user is not None:
            login(request, user)
            messages.success(request,'Login successful')
            return redirect('dashboard')
        else:
            messages.error(request,'Invalid username or password')
    return render(request,'login.html')
# LOGOUT VIEW
def logout_view(request):
    logout(request)
    messages.success(request,'Logged out successfully')
    return redirect('login')

