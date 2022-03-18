from django.shortcuts import render, redirect
from django.db import connection

# Create your views here.
def index(request):
    """Shows the main page"""
    context = {}
    status = ''

    if request.POST:
        ## Check if customer account already exists
        with connection.cursor() as cursor:
            ## Get email
            cursor.execute("SELECT * FROM User1 WHERE Email = %s", [request.POST['email']])
            customer_email = cursor.fetchone()
            print(customer_email)
            ## Get password
            cursor.execute("SELECT * FROM User1 WHERE Pass_word = %s", [request.POST['psw']])
            customer_password = cursor.fetchone()
            print(customer_password)
            ## Check if login with admin account
            if request.POST['email'] == "admin@admin.com" and request.POST['psw'] == "admin123":
                return redirect('appstore_admin')
            elif customer_email != None and customer_password != None:
                return redirect('listing')

    context['status']=status
    return render(request,'app/index.html',context)

# Create your views here.
def appstore_admin(request):
    """Shows the main page"""

    ## Delete customer
    if request.POST:
        if request.POST['action'] == 'delete':
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM User1", [request.POST['id']])

    ## Use raw query to get all objects
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM User1")
        customers = cursor.fetchall()

    result_dict = {'records': customers}

    return render(request,'app/appstore_admin.html',result_dict)

# Create your views here.
def view(request, id):
    """Shows the main page"""
    
    ## Use raw query to get a customer
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM User1", [id])
        customer = cursor.fetchone()
    result_dict = {'cust': customer}

    return render(request,'app/view.html',result_dict)

# Create your views here.
def add(request):
    """Shows the main page"""
    context = {}
    status = ''

    if request.POST:
        ## Check if customerid is already in the table
        with connection.cursor() as cursor:

            cursor.execute("SELECT * FROM User1 WHERE customerid = %s", [request.POST['customerid']])
            customer = cursor.fetchone()
            ## No customer with same id
            if customer == None:
                ##TODO: date validation
                cursor.execute("INSERT INTO User1 VALUES (%s, %s, %s, %s, %s, %s, %s)"
                        , [request.POST['first_name'], request.POST['last_name'], request.POST['email'],
                           request.POST['customerid'] , 0, request.POST['phonenumber'], request.POST['password'] ])
                return redirect('index')    
            else:
                status = 'Customer with ID %s already exists' % (request.POST['customerid'])


    context['status'] = status
 
    return render(request, "app/add.html", context)

# Create your views here.
def edit(request, id):
    """Shows the main page"""

    # dictionary for initial data with
    # field names as keys
    context ={}

    # fetch the object related to passed id
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM User1 WHERE customerid = %s", [id])
        obj = cursor.fetchone()

    status = ''
    # save the data from the form

    if request.POST:
        ##TODO: date validation
        with connection.cursor() as cursor:
            cursor.execute("UPDATE User1 SET first_name = %s, last_name = %s, email = %s, customerid = %s, walletbalance = %s, phonenumber = %s, password = %s WHERE customerid = %s"
                    , [request.POST['first_name'], request.POST['last_name'], request.POST['email'],
                        request.POST['customerid'] , request.POST['walletbalance'], request.POST['phonenumber'], request.POST['password'], id ])
            status = 'Customer edited successfully!'
            cursor.execute("SELECT * FROM customers WHERE customerid = %s", [id])
            obj = cursor.fetchone()


    context["obj"] = obj
    context["status"] = status
 
    return render(request, "app/edit.html", context)

# Create your views here.
def listing(request):
    """Shows the main page"""

    ## Use raw query to get all objects
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM GPU_Listing ORDER BY Listingid")
        listings = cursor.fetchall()

    result_dict = {'records': listings}

    return render(request,'app/listing.html',result_dict)
