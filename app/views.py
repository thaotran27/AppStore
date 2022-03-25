from cmath import log
from curses.ascii import HT
from django.shortcuts import render, redirect
from django.db import connection
from django.http import HttpResponse
import logging
from datetime import datetime
from datetime import date
from datetime import timedelta
from django.urls import reverse
from django.http import HttpResponseRedirect

# Create your views here.
def index(request):
    """Shows the main page"""
    context = {}
    status = ''
    login_email = request.session.get('email', 0)
    if login_email == "admin@admin.com":
        return HttpResponseRedirect(reverse('appstore_admin'))
    elif login_email != 0:
        # return HttpResponse(login_email)
        return HttpResponseRedirect(reverse('listing'))

    if request.POST:
        ## Check if customer account already exists
        with connection.cursor() as cursor:
            ## Get email
            request.session['email'] = request.POST['email']
            cursor.execute("SELECT * FROM User1 WHERE Email = %s", [request.POST['email']])
            customer_email = cursor.fetchone()
            # logging.debug(customer_email)

            ## Get password
            cursor.execute("SELECT * FROM User1 WHERE Pass_word = %s", [request.POST['psw']])
            customer_password = cursor.fetchone()
            # logging.debug(customer_password)

            ## Check if login with admin account
            if request.POST['email'] == "admin@admin.com" and request.POST['psw'] == "admin123":
                return redirect('appstore_admin')
            elif customer_email != None and customer_password != None:
                return redirect('listing')
            else:
                # return HttpResponse('<h1>No such user</h1>')
                return render(request,'app/index.html', {'error_message': ' Login Failed! Enter the username and password correctly', })


    context['status']=status
    return render(request,'app/index.html',context)

def log_out(request):
    """Shows the main page"""
    context = {}
    status = ''
    login_email = request.session.get('email', 0)
    if login_email != 0:
        # return HttpResponse(login_email)
        del request.session['email']
        return HttpResponseRedirect(reverse('index'))
    else:
        return HttpResponseRedirect(reverse('index'))

# Create your views here.
def appstore_admin(request):
    """Shows the main page"""
    #use this snippet in everyview function to verify user
    login_email = request.session.get('email', 0)
    logging.debug(login_email)
    if login_email == 0:
        return HttpResponseRedirect(reverse('index'))
    #use this snippet in everyview function to verify user. ends here

    ## Delete listing
    if request.POST:
        if request.POST['action'] == 'delete':
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM User1 WHERE Customerid = %s", [request.POST['id']])
            print(request.POST['id'])

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
        cust = cursor.fetchone()

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
            cust = cursor.fetchone()


    context["cust"] = cust
    context["status"] = status
 
    return render(request, "app/edit.html", context)

# Create your views here.
def listing(request,id=1):
    """Shows the main page"""
    #use this snippet in everyview function to verify user
    login_email = request.session.get('email', 0)
    logging.debug(login_email)
    if login_email == 0:
        return HttpResponseRedirect(reverse('index'))
    #use this snippet in everyview function to verify user. ends here

    ## Use raw query to get all objects
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM User1 WHERE Email =  %s", [login_email])
        current_user = cursor.fetchone()
        if int(id) ==1:
            cursor.execute("SELECT * FROM GPU_Listing ORDER BY Listingid DESC")
            listings = cursor.fetchall()
        elif int(id) == 2:
            cursor.execute("SELECT * FROM GPU_Listing ORDER BY Listingid")
            listings = cursor.fetchall()
        elif int(id) == 3:
            cursor.execute("SELECT * FROM GPU_Listing ORDER BY Price DESC")
            listings = cursor.fetchall()
        elif int(id) == 4:
            cursor.execute("SELECT * FROM GPU_Listing ORDER BY Price")
            listings = cursor.fetchall()
        

    result_dict = {'records': listings, 'current_user': current_user}

    return render(request,'app/listing.html',result_dict)

# Create your views here.
def view_listing(request, id):
    """Shows the main page"""
    #use this snippet in everyview function to verify user
    login_email = request.session.get('email', 0)
    logging.debug(login_email)
    if login_email == 0:
        return HttpResponseRedirect(reverse('index'))
    #use this snippet in everyview function to verify user. ends here
    
    ## Use raw query to get a GPU
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM GPU", [id])
        view_listing = cursor.fetchone()
    result_dict = {'view_listing': view_listing}

    return render(request,'app/view_listing.html',result_dict)



def rental(request, Listingid):
    #use this snippet in everyview function to verify user
    login_email = request.session.get('email', 0)
    logging.debug(login_email)
    if login_email == 0:
        return HttpResponseRedirect(reverse('index'))
    #use this snippet in everyview function to verify user. ends here

    """Shows the main page"""
    #context = {}
    status = ''
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM GPU_Listing WHERE Listingid = %s", [Listingid])
        GPU_choice = cursor.fetchall()
        cursor.execute("SELECT * FROM User1 WHERE Email = %s", [request.session['email']])
        Borrower_details = cursor.fetchall()
    if request.POST:
        ## Check if customerid is already in the table
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM GPU_Listing WHERE Listingid = %s", [Listingid])
            listing = cursor.fetchone()
            cursor.execute("SELECT * FROM User1 WHERE Email = %s", [request.session['email']])
            Borrower = cursor.fetchone()
            ## No customer with same id
            if (datetime.strptime(request.POST['Start_day'], '%Y-%m-%d').date() >= listing[4] and datetime.strptime(request.POST['End_day'], '%Y-%m-%d').date() <= listing[5]):
                ##TODO: date validation
                #cursor.execute("INSERT INTO Rental VALUES (%s, %s, %s, %s, %s, %s)",[request.POST['Borrower_id'], listing[1], listing[2],
                #           int(Listingid) , request.POST['Start_day'], request.POST['End_day']])
                number_of_days = (datetime.strptime(request.POST['End_day'], '%Y-%m-%d').date()-datetime.strptime(request.POST['Start_day'], '%Y-%m-%d').date()).days + 1
                total_cost = number_of_days * listing[6]
                if int(total_cost) > int(Borrower[3]):
                    return render(request,'app/rental.html', {'error_message': ' Cost of rental exceeds wallet balance, choose new dates' })

                elif int(total_cost) <= int(Borrower[3]):

                    Borrower[3] = int(Borrower[3]) - int(total_cost)    
                    cursor.execute("UPDATE User1 SET Wallet_balance = %s WHERE Email = %s", [Borrower[3],request.session['email']])

                    cursor.execute("INSERT INTO Rental VALUES (%s, %s, %s, %s, %s, %s)"
                        , [Borrower[3], listing[1], listing[2],
                           int(Listingid) , request.POST['Start_day'], request.POST['End_day']])
                    cursor.execute("DELETE FROM GPU_Listing WHERE Listingid = %s", [Listingid])
                    cursor.execute("SELECT * FROM GPU_Listing g1 WHERE g1.listingid >= all (SELECT g2.listingid FROM GPU_Listing g2)")
                    last_entry = cursor.fetchone()
                    if (datetime.strptime(request.POST['Start_day'], '%Y-%m-%d').date() == listing[4]):
                        cursor.execute("INSERT INTO GPU_Listing VALUES(%s, %s,%s,%s,%s,%s,%s)", [last_entry[0] + 1 ,listing[1], listing[2], listing[3], 
                                                                                         datetime.strptime(request.POST['End_day'], '%Y-%m-%d').date() + timedelta(days = 1), listing[5], listing[6]])
                        cursor.execute("INSERT INTO GPU_Listing_Archive VALUES(%s, %s,%s,%s,%s)", [last_entry[0] + 1 ,listing[1], listing[2], listing[3], 
                                                                                          listing[6]])                                                                     
                    if (datetime.strptime(request.POST['Start_day'], '%Y-%m-%d').date() > listing[4]):
                        cursor.execute("INSERT INTO GPU_Listing VALUES(%s, %s,%s,%s,%s,%s,%s)", [last_entry[0] + 1 ,listing[1], listing[2], listing[3], 
                                                                                         listing[4], datetime.strptime(request.POST['Start_day'], '%Y-%m-%d').date()  - timedelta(days = 1), listing[6]])
                        cursor.execute("INSERT INTO GPU_Listing VALUES(%s, %s,%s,%s,%s,%s,%s)", [last_entry[0] + 2 ,listing[1], listing[2], listing[3], 
                                                                                         datetime.strptime(request.POST['End_day'], '%Y-%m-%d').date() + timedelta(days = 1), listing[5], listing[6]])
                        cursor.execute("INSERT INTO GPU_Listing_Archive VALUES(%s, %s,%s,%s,%s)", [last_entry[0] + 1 ,listing[1], listing[2], listing[3], 
                                                                                          listing[6]])
                        cursor.execute("INSERT INTO GPU_Listing_Archive VALUES(%s, %s,%s,%s,%s)", [last_entry[0] + 2 ,listing[1], listing[2], listing[3], 
                                                                                         listing[6]])                                                                     
                    return redirect('listing')    
            else:
                status = 'Invalid Rental Dates'

    result_dict = {'GPU' : GPU_choice, 'status' : status, 'Borrower' : Borrower_details}
    #context['status'] = status
 
    return render(request, "app/rental.html", result_dict)

#def check_out(request,Listingid):
#    #use this snippet in everyview function to verify user
#    login_email = request.session.get('email', 0)
#    logging.debug(login_email)
#    if login_email == 0:
#        return HttpResponseRedirect(reverse('index'))
#    #use this snippet in everyview function to verify user. ends here

#    with connection.cursor() as cursor:
#        cursor.execute("SELECT * FROM GPU_Listing WHERE Listingid = %s", [Listingid])
#        GPU_choice = cursor.fetchall()
#        cursor.execute("SELECT * FROM User1 WHERE Email = %s", [request.session['email']])
#        Borrower_details = cursor.fetchall()

#    rental 


#    result_dict = {'GPU' : GPU_choice, 'Borrower' : Borrower_details}
#    return render(request, "app/check_out.html", result_dict)




# Create your views here.
def personal(request, id):
    """Shows the main page"""
    #use this snippet in everyview function to verify user
    login_email = request.session.get('email', 0)
    logging.debug(login_email)
    if login_email == 0:
        return HttpResponseRedirect(reverse('index'))
    #use this snippet in everyview function to verify user. ends here

    # dictionary for initial data with
    # field names as keys
    result_dict ={}
    status = ''

    # get currently login user
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM User1 WHERE Email = %s", [login_email])
        personal = cursor.fetchone()


    # get current lend of user
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM GPU_Listing WHERE Customerid = %s AND Available_end_day >= %s", [personal[3], date.today()])
        personal_listing = cursor.fetchall()
    result_dict['personal_listing'] = personal_listing

    # get current rent of user
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM Rental WHERE Borrower_id = %s AND End_day >= %s", [personal[3], date.today()])
        rent_listing = cursor.fetchall()
    result_dict['rent_listing']= rent_listing

    # get Lend history of user
    with connection.cursor() as cursor:
        cursor.execute("SELECT g.GPU_Model, g.GPU_Brand, g.Available_start_day, g.Available_end_day, (r.End_day-r.Start_day+1) as duration, g.Price FROM Rental r, GPU_Listing g WHERE r.Listingid=g.Listingid AND g.Customerid = %s AND g.Available_end_day < %s", [personal[3], date.today()])
        lend_history = cursor.fetchall()
        if (len(lend_history)>0):
            lend_history_conv = list(lend_history[0])
            lend_history_conv.append(rent_history_conv[5]*rent_history_conv[4])    
            result_dict['rent_history_conv'] = rent_history_conv
    result_dict['lend_history']= lend_history

    # get Rent history of user
    with connection.cursor() as cursor:
        cursor.execute("SELECT r.GPU_Model, r.GPU_Brand, r.Start_day, r.End_day, (r.End_day-r.Start_day+1) as duration, g.Price FROM Rental r, GPU_Listing g WHERE r.Listingid=g.Listingid AND r.Borrower_id = %s AND r.End_day < %s", [personal[3], date.today()])
        rent_history = cursor.fetchall()
        if (len(rent_history)>0):
            rent_history_conv = list(rent_history[0])
            rent_history_conv.append(rent_history_conv[5]*rent_history_conv[4])    
            result_dict['rent_history_conv'] = rent_history_conv
    result_dict['rent_history']= rent_history
    

    result_dict["personal"] = personal
    result_dict["status"] = status
 
    return render(request, "app/personal.html", result_dict)

def add_listing(request):
    #use this snippet in everyview function to verify user
    login_email = request.session.get('email', 0)
    logging.debug(login_email)
    if login_email == 0:
        return HttpResponseRedirect(reverse('index'))
    #use this snippet in everyview function to verify user. ends here
    context = {}
    status = ''
    current_user = login_email
    with connection.cursor() as cursor:

        cursor.execute("SELECT * FROM GPU_Listing ORDER BY Listingid DESC")
        listing_data = cursor.fetchall()
        next_id = listing_data[0][0] + 1
        cursor.execute("SELECT * FROM User1 WHERE Email = %s", [login_email])
        customer2 = cursor.fetchall()
        current_user = customer2[0][3]

        if request.POST:
                    ##TODO: date validation
            if listing_data == None:  
                next_id = 1
            cursor.execute("INSERT INTO GPU_Listing VALUES (%s, %s, %s, %s, %s, %s, %s)"
                    ,[next_id, request.POST['gpu_model'], request.POST['gpu_brand'], current_user,
                    request.POST['start_date'] , request.POST['end_date'], request.POST['price']])
            cursor.execute("INSERT INTO GPU_Listing_Archive VALUES (%s, %s, %s, %s, %s)"
                    ,[next_id, request.POST['gpu_model'], request.POST['gpu_brand'], current_user,
                    request.POST['price']])
            return redirect('listing')  

    context['status'] = status
    return render(request, "app/add_listing.html", context)

def top_up(request):
    #use this snippet in everyview function to verify user
    login_email = request.session.get('email', 0)
    logging.debug(login_email)
    if login_email == 0:
        return HttpResponseRedirect(reverse('index'))
    #use this snippet in everyview function to verify user. ends here
    context = {}
    status = ''
    current_user = login_email
    with connection.cursor() as cursor:
        cursor.execute("SELECT Wallet_balance FROM User1 WHERE Email =  %s", [login_email])
        user_balance = int(cursor.fetchone()[0])
        
        if request.POST:
            new_balance = user_balance + int(request.POST['value'])
            cursor.execute("UPDATE User1 SET Wallet_balance = %s WHERE Email = %s", [new_balance, login_email])
            return redirect('listing')  
    context['status'] = status
    result_dict = {'user_balance': user_balance}
    return render(request,'app/top_up.html',result_dict)

   

