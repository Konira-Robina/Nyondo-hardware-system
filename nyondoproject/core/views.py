from django.shortcuts import render, redirect,get_object_or_404
from .models import Customer, Deposit, CreditProduct, CreditPurchase, Product, Sale, Supplier
from django.db.models import Sum
from django.contrib import messages
# Create your views here.

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
        
            name=request.POST.get('name')
            category=request.POST.get('category')
            unit_cost=int(request.POST.get('unit_cost'))
            selling_price=int(request.POST.get('selling_price'))
            stock_quantity=int(request.POST.get('stock_quantity'))

        # Here am creating/adding a new product    
            product=Product(     
                 name=name,
                 category=category,
                 unit_cost=unit_cost,
                 selling_price=selling_price,
                stock_quantity=stock_quantity
                )
            product.save()
            
           
            
            return redirect('products')
    return render(request, 'add_product.html',)
    


def edit_product(request, id):

    product = get_object_or_404(Product, id=id)
    if request.method=='POST':
        product.name = request.POST.get('name')
        product.category = request.POST.get('category')
        product.unit_cost = int(request.POST.get('unit_cost'))
        product.selling_price = int(request.POST.get('selling_price'))
        product.stock_quantity = int(request.POST.get('stock_quantity'))
        product.save()
        return redirect('products')
    return render(request, 'edit_product.html', {'product': product})

def delete_product(request, id):
    product = get_object_or_404(Product, id=id)
    product.delete()
    return redirect('products')
#return render(request, 'delete_product.html')

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
        Sale.objects.create(
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

        # REDUCING STOCK
        product.stock_quantity -= quantity
        product.save()

        # Message to show up after adding
        messages.success(request,"Sale added successfully")
        return redirect('sales')
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
        sale.sales_representative = request.POST.get('sales_representative')
        sale.customer_name = request.POST.get('customer_name')
        sale.address = request.POST.get('address')
        sale.phone_number = request.POST.get('phone_number')
        sale.customer_type = request.POST.get('customer_type')
        product_id = request.POST.get('product_name')
        product = get_object_or_404( Product, id=product_id)
        sale.product_name = product
        sale.quantity = request.POST.get('quantity')
        sale.selling_price = request.POST.get('selling_price')
        sale.transport_fee = request.POST.get('transport_fee')
        sale.total_amount = (float(sale.quantity)* float(sale.selling_price)) + float(sale.transport_fee)
        sale.save()
        messages.success(request,"Sale updated successfully")
        return redirect('sales')

    context = {'sale': sale}
    return render(request,'edit_sales.html',context)

#DELETING
def delete_sale(request, id):
    sale = get_object_or_404(Sale, id=id)
    sale.delete()
    messages.success(request,"Sale deleted successfully")
    return redirect('sales')

# CUSTOMER DETAILS
def customers(request):
    data = Customer.objects.all()
    return render(request, 'customers.html', {'customers': data})

def add_customer(request):
    if request.method == 'POST':
        Customer.objects.create(
            full_name=request.POST['name'],
            nin=request.POST['nin'],
            phone=request.POST['phone']
        )
        return redirect('customers')
    return render(request, 'add_customer.html')

def credit_purchase(request):
    customers = Customer.objects.all()
    products = CreditProduct.objects.all()

    if request.method == 'POST':
        customer = Customer.objects.get(id=request.POST['customer'])
        product = CreditProduct.objects.get(id=request.POST['product'])
        qty = int(request.POST['quantity'])

        total_cost = product.price * qty

       # balance = get_customer_balance(customer)

        #if total_cost > balance:
          #  return render(request, 'error.html', {'message': 'Insufficient balance'})

        CreditPurchase.objects.create(
            customer=customer,
            product=product,
            quantity=qty,
            total_cost=total_cost
        )
        return redirect('credit_purchase')
    return render(request, 'credit_purchase.html', {
        'customers': customers,
        'products': products
    })

def add_supplier(request):
    #fetching all supplier details from the class
    supplier=Supplier.objects.all()
    if request.method == 'POST': # if form is submitted then get for me these details
        product_id = request.POST.get('stock')
        supplier_name = request.POST.get('supplier_name')
        quantity = int(request.POST.get('quantity'))
        cost_price = float(request.POST.get('cost_price'))
        date = request.POST.get('date')
        payment_method = request.POST.get('payment_method')
        amount_paid = float(request.POST.get('amount_paid'))

        supplier=Product.objects.get(id=product_id)
        total_cost = quantity * cost_price
        
        if payment_method != 'credit':
            amount_paid = total_cost

        
        #supplier=get_object_or_404(
        #product_id = product
        #supplier_name = supplier_name
        #quantity = quantity
        #cost_price = cost_price
        #date = date
        #payment_method = payment_method
        #amount_paid = amount_paid)
       # supplier.save()

        #quantity += quantity
        #products.save()

        return redirect('supplier')
    return render(request, 'add_supplier.html', {'products': products})


def supplier(request):
    supply = Supplier.objects.all()
    return render(request, 'supplier.html', {'supply': supply})


