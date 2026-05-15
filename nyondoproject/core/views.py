from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.utils import timezone
from .models import (Customer,Deposit,CreditPurchase,Product,Sale,Supplier,Payment,Invoice,Notification,StockMovement)
def dashboard(request):
    products = Product.objects.count()
    sales = Sale.objects.count()
    return render(request, 'dashboard.html', {
        'products': products,
        'sales': sales
    })

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
    product.delete()
    return redirect('products')
# SALES INFORMATION

# ADD SALE VIEW
def add_sales(request):
    # Fetching all products from the model class
    products = Product.objects.all()
    if request.method == 'POST': # Checking if form is submitted
        # Geting form data
        sales_representative = request.POST.get('sales_representative')
        customer_name = request.POST.get('customer_name')
        address = request.POST.get('address')
        phone_number = request.POST.get('phone_number')
        customer_type = request.POST.get('customer_type')
        product_id = request.POST.get('product_name')
        quantity = int(request.POST.get('quantity'))
        selling_price = float(request.POST.get('selling_price'))
        transport_fee = float(request.POST.get('transport_fee'))
        # Geting selected product
        product = Product.objects.get(id=product_id)
        
        # STOCK VALIDATION
        # Replacing stock_quantity with the actual product stock field
        if quantity > product.stock_quantity:
            messages.error(request,"Not enough stock available")
      

            return redirect('add_sales')
        
        # CALCULATIng THE TOTAL
        total_amount = (quantity * selling_price) + transport_fee
       
        # SAVING SALE
    try:    
        sale = Sale(
            sales_representative=sales_representative,
            customer_name=customer_name,
            address=address,
            phone_number=phone_number,
            customer_type=customer_type,
            product_name=product,
            quantity=quantity,
            selling_price=selling_price,
            total_amount=total_amount,
            transport_fee=transport_fee
        )
        sale.full_clean()
        sale.save()
    # reducig stock
        product.stock_quantity -= quantity
        product.save()
        messages.success(request, "Sale added successfully")
        return redirect('sales')
    except ValidationError as e:
        messages.error(request, e)
        return redirect('add_sales')

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
    context = {
        'sale': sale,
        'products': products
    }
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

def credit_purchases(request):
    credits = CreditPurchase.objects.all().order_by('-date')
    context = {'credits': credits}
    return render(request,'credit_purchases.html',context)

# ADD CREDIT PURCHASE
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

                

        # SAVE CREDIT
        try:
            credit = CreditPurchase(
                customer=customer,
                product=product,
                quantity=quantity,
                price_per_item=price_per_item,
                total_amount=total_amount,
                amount_paid=amount_paid,
                balance=balance,
                payment_status=payment_status
            )
            credit.full_clean()
            credit.save()
            product.stock_quantity -= quantity
            product.save()
            messages.success(request,'Credit purchase added successfully')
            return redirect('credit_purchases')
        except ValidationError as e:
            messages.error(request, e)

# ADD PAYMENT
def add_payment(request):
    credits = CreditPurchase.objects.all()
    if request.method == 'POST':
        try:
            credit = CreditPurchase.objects.get(id=request.POST.get('credit_purchase'))
            amount_paid = float(request.POST.get('amount_paid'))
            if amount_paid > credit.balance:
                messages.error(request,"Payment exceeds balance")
                return redirect('add_payment')
            balance_after_payment = (credit.balance - amount_paid)
            payment = Payment(
                credit_purchase=credit,
                amount_paid=amount_paid,
                balance_after_payment=balance_after_payment
            )
            payment.full_clean()
            payment.save()
            # UPDATE CREDIT
            credit.amount_paid += amount_paid
            credit.balance = balance_after_payment
            if credit.balance <= 0:
                credit.payment_status = 'Paid'
            credit.save()
            messages.success(request,"Payment added successfully")
            return redirect('payments')
        except ValidationError as e:
            messages.error(request, e)
    context = {'credits': credits}
    return render(request, 'add_payment.html', context)

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