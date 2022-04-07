from cmath import log
from curses.ascii import HT
from django.shortcuts import render, redirect
from django.db import connection
from django.http import HttpResponse
import logging
from datetime import datetime
from datetime import date
from datetime import timedelta
from dateutil.relativedelta import relativedelta
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
        with connection.cursor() as cursor:
             cursor.execute("SELECT * FROM User1 WHERE Email = %s", [login_email])
             row = cursor.fetchone()
             if row != None:
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
def appstore_admin(request, yearid=date.today().year):
    """Shows the main page"""
    #use this snippet in everyview function to verify user
    login_email = request.session.get('email', 0)
    logging.debug(login_email)
    if login_email == 0:
        return HttpResponseRedirect(reverse('index'))
    #use this snippet in everyview function to verify user. ends here

    
    ## Use raw query to get all objects
    with connection.cursor() as cursor:
        #Remove expired listing and Update available start day
        cursor.execute("SELECT * FROM GPU_Listing")
        data = cursor.fetchall()
        listingid = 0
        for i in data:
            listingid=i[0]
            if i[4] < date.today() and i[5] >= date.today():
                cursor.execute("UPDATE GPU_Listing SET Available_start_day = %s WHERE Listingid = %s", [date.today(), listingid])
            elif i[5] < date.today():
                cursor.execute("DELETE FROM GPU_Listing WHERE Listingid = %s", [listingid])
        

        # Get year
        cursor.execute("select distinct extract(year from r.start_day) as year from gpu_listing_archive g join rental r on r.listingid=g.listingid order by year desc")
        years= cursor.fetchall()
        year = [int(year[0]) for year in years]
        if len(year) > 0 and year[0] < date.today().year:
            year.insert(0, date.today().year)
        yearid = request.GET.get('year')

        if request.GET.get('reset'):
            yearid = None
        if yearid is None:
            yearid = date.today().year
            cursor.execute("select extract(month from r.start_day) as month, count(*) from rental r where extract(year from r.start_day) = %s group by month", [yearid])
            listing = cursor.fetchall()
        else:
            cursor.execute("select extract(month from r.start_day) as month, count(*) from rental r where extract(year from r.start_day) = %s group by month", [yearid])
            listing = cursor.fetchall()
        month = [month[0] for month in listing]
        count = [count[1] for count in listing]
        total_month_rent = [0,0,0,0,0,0,0,0,0,0,0,0]
        for i in range(len(month)):
            total_month_rent[int(month[i])-1] = count[i]

    result_dict = {'records': listing, 'year': year, 'yearid': yearid, 'total_month_rent': total_month_rent}

    return render(request,'app/appstore_admin.html',result_dict)

# Create your views here.
def customer_details(request):
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

    ## Use raw query to get all objects
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM User1 ORDER BY customerid ASC")
        customers = cursor.fetchall()

    result_dict = {'records': customers}

    return render(request,'app/customer_details.html',result_dict)

# Create your views here.
def view(request, id):
    #use this snippet in everyview function to verify user
    login_email = request.session.get('email', 0)
    logging.debug(login_email)
    if login_email == 0:
        return HttpResponseRedirect(reverse('index'))
    #use this snippet in everyview function to verify user. ends here
    
    ## Use raw query to get a customer
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM User1 WHERE customerid = %s", [id])
        customer = cursor.fetchone()
    result_dict = {'cust': customer}

    return render(request,'app/view.html',result_dict)

# Create your views here.
def signup(request):
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
                cursor.execute("INSERT INTO User1 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                        , [request.POST['first_name'], request.POST['last_name'], request.POST['email'],
                           request.POST['customerid'] , 0, request.POST['phonenumber'], request.POST['password'], request.POST['credit_card_nbr'], request.POST['credit_card_type'] ])

                return redirect('index')
            else:
                status = 'Customer with ID %s already exists' % (request.POST['customerid'])


    context['status'] = status
 
    return render(request, "app/signup.html", context)

# Create your views here.
def add(request):
    #use this snippet in everyview function to verify user
    login_email = request.session.get('email', 0)
    logging.debug(login_email)
    if login_email == 0:
        return HttpResponseRedirect(reverse('index'))
    #use this snippet in everyview function to verify user. ends here
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
                cursor.execute("INSERT INTO User1 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                        , [request.POST['first_name'], request.POST['last_name'], request.POST['email'],
                           request.POST['customerid'] , 0, request.POST['phonenumber'], request.POST['password'], request.POST['credit_card_nbr'], request.POST['credit_card_type'] ])

                return redirect('customer_details')
            else:
                status = 'Customer with ID %s already exists' % (request.POST['customerid'])


    context['status'] = status
 
    return render(request, "app/add.html", context)

# Create your views here.
def edit(request, id):
    #use this snippet in everyview function to verify user
    login_email = request.session.get('email', 0)
    logging.debug(login_email)
    if login_email == 0:
        return HttpResponseRedirect(reverse('index'))
    #use this snippet in everyview function to verify user. ends here

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
            cursor.execute("UPDATE User1 SET first_name = %s, last_name = %s, email = %s, customerid = %s, wallet_balance = %s, phone_number = %s, pass_word = %s, Credit_card_number = %s, Credit_card_type = %s WHERE customerid = %s"
                    , [request.POST['first_name'], request.POST['last_name'], request.POST['email'],
                        request.POST['customerid'] , request.POST['walletbalance'], request.POST['phonenumber'], request.POST['password'], request.POST['credit_card_number'], request.POST['credit_card_number'], id ])
            status = 'Customer edited successfully!'
            cursor.execute("SELECT * FROM User1 WHERE customerid = %s", [id])
            cust = cursor.fetchone()


    context["cust"] = cust
    context["status"] = status
 
    return render(request, "app/edit.html", context)

# Create your views here.
def listing(request):
    """Shows the main page"""
    #use this snippet in everyview function to verify user
    login_email = request.session.get('email', 0)
    logging.debug(login_email)
    if login_email == 0:
        return HttpResponseRedirect(reverse('index'))
    #use this snippet in everyview function to verify user. ends here

    ## Use raw query to get all objects
    with connection.cursor() as cursor:
        cursor.execute("UPDATE User1 SET Email = %s WHERE Email = %s", [login_email,login_email])
        cursor.execute("SELECT * FROM User1 WHERE Email =  %s", [login_email])
        current_user = cursor.fetchone()
        cursor.execute("SELECT COUNT(*) FROM GPU_Listing")
        num = cursor.fetchone()

        filter = request.GET.get('filter')
        min_price_filter = request.GET.get('min_price_filter', 0)
        max_price_filter = request.GET.get('max_price_filter', 1000)
        min_memsize_filter = request.GET.get('mem_min', 0)
        max_memsize_filter = request.GET.get('mem_max', 100)
        dur = request.GET.get('dur')

        # Get Max Price and Max Memsize for HTML range display
        cursor.execute("SELECT MAX(price) FROM GPU_Listing")
        max_price = cursor.fetchone()

        cursor.execute("SELECT MAX(CAST(REGEXP_REPLACE(g.Memory_size,'[[:alpha:]]','','g') AS FLOAT)) FROM GPU g")
        max_memsize = cursor.fetchone()

        if (filter is None or dur is None) or (filter == "Reset" and dur == "Reset" and min_price_filter == "0" and max_price_filter == "100" and min_memsize_filter == "0" and max_memsize_filter == "40"):
            cursor.execute("SELECT * FROM GPU_Listing ORDER BY Listingid DESC")
            listings = cursor.fetchall()
            num2 = len(listings)
        elif filter == "Reset" and dur == "Reset" and (min_price_filter != "0" or max_price_filter != "100" or min_memsize_filter != "0" or max_memsize_filter != "40"):
            price_condition = "gl.price < {} AND gl.price > {}".format(max_price_filter, min_price_filter)
            memsize_condition = "CAST(REGEXP_REPLACE(g.Memory_size,'[[:alpha:]]','','g') AS FLOAT) < {} AND  CAST(REGEXP_REPLACE(g.Memory_size,'[[:alpha:]]','','g') AS FLOAT) > {}".format(max_memsize_filter, min_memsize_filter)
            order_condition = "ORDER BY Listingid DESC"
            cursor.execute("SELECT * FROM GPU_listing gl, GPU g WHERE gl.GPU_model = g.GPU_model AND gl.GPU_brand = g.GPU_brand" + " AND " + price_condition + " AND " + memsize_condition + " " + order_condition)
            listings = cursor.fetchall()
            num2 = len(listings)
        elif filter != "Reset" and dur == "Reset":
            order = ["gl.Available_start_day ASC", "gl.Available_end_day DESC", "gl.Price DESC", "gl.Price ASC"]
            price_condition = "gl.price < {} AND gl.price > {}".format(max_price_filter, min_price_filter)
            memsize_condition = "CAST(REGEXP_REPLACE(g.Memory_size,'[[:alpha:]]','','g') AS FLOAT) < {} AND  CAST(REGEXP_REPLACE(g.Memory_size,'[[:alpha:]]','','g') AS FLOAT) > {}".format(max_memsize_filter, min_memsize_filter)
            order_condition = "ORDER BY {}".format(order[int(filter)-1])
            cursor.execute("SELECT * FROM GPU_listing gl, GPU g WHERE gl.GPU_model = g.GPU_model AND gl.GPU_brand = g.GPU_brand" + " AND " + price_condition + " AND " + memsize_condition + " " + order_condition)
            listings = cursor.fetchall()
            num2 = len(listings)
        elif filter == "Reset" and dur != "Reset":
            if int(dur) == 5:
                    cursor.execute("SELECT * FROM Gpu_Listing g, (SELECT r1.gpu_model AS most_rented_model, r1.gpu_brand AS most_rented_brand, COUNT(*)	FROM rental r1 WHERE r1.start_day > %s GROUP BY r1.gpu_model, r1.gpu_brand HAVING COUNT(*) >= ALL (SELECT COUNT(*) FROM rental r2 WHERE r2.start_day > %s GROUP BY r2.gpu_model, r2.gpu_brand)) r WHERE g.gpu_model=r.most_rented_model AND g.gpu_brand=r.most_rented_brand", [date.today()-timedelta(days=14), date.today()-timedelta(days=14)])
                    listings = cursor.fetchall()
                    num2 = len(listings)
            elif int(dur) == 6:
                    cursor.execute("SELECT * FROM Gpu_Listing g, (SELECT r1.gpu_model AS most_rented_model, r1.gpu_brand AS most_rented_brand, COUNT(*)	FROM rental r1 WHERE r1.start_day > %s GROUP BY r1.gpu_model, r1.gpu_brand HAVING COUNT(*) >= ALL (SELECT COUNT(*) FROM rental r2 WHERE r2.start_day > %s GROUP BY r2.gpu_model, r2.gpu_brand)) r WHERE g.gpu_model=r.most_rented_model AND g.gpu_brand=r.most_rented_brand", [date.today()-timedelta(days=30), date.today()-timedelta(days=30)])
                    listings = cursor.fetchall()
                    num2 = len(listings)
            elif int(dur) == 7:
                    cursor.execute("SELECT * FROM Gpu_Listing g, (SELECT r1.gpu_model AS most_rented_model, r1.gpu_brand AS most_rented_brand, COUNT(*)	FROM rental r1 WHERE r1.start_day > %s GROUP BY r1.gpu_model, r1.gpu_brand HAVING COUNT(*) >= ALL (SELECT COUNT(*) FROM rental r2 WHERE r2.start_day > %s GROUP BY r2.gpu_model, r2.gpu_brand)) r WHERE g.gpu_model=r.most_rented_model AND g.gpu_brand=r.most_rented_brand", [date.today()-relativedelta(months=+6), date.today()-relativedelta(months=+6)])
                    listings = cursor.fetchall()
                    print(listings)
                    num2 = len(listings)
        elif filter != "Reset" and dur != "Reset":
            order = ["gl.Available_start_day DESC", "gl.Available_start_day ASC", "gl.Price DESC", "gl.Price ASC"]
            price_condition = "gl.price < {} AND gl.price > {}".format(max_price_filter, min_price_filter)
            memsize_condition = "CAST(REGEXP_REPLACE(g.Memory_size,'[[:alpha:]]','','g') AS FLOAT) < {} AND  CAST(REGEXP_REPLACE(g.Memory_size,'[[:alpha:]]','','g') AS FLOAT) > {}".format(max_memsize_filter, min_memsize_filter)
            order_condition = "ORDER BY {}".format(order[int(filter)-1])
            filter_sql = "SELECT * FROM GPU_listing gl, GPU g, (SELECT r1.gpu_model AS most_rented_model, r1.gpu_brand AS most_rented_brand, COUNT(*) FROM rental r1 WHERE r1.start_day > %s GROUP BY r1.gpu_model, r1.gpu_brand HAVING COUNT(*) >= ALL (SELECT COUNT(*) FROM rental r2 WHERE r2.start_day > %s GROUP BY r2.gpu_model, r2.gpu_brand)) AS r WHERE gl.gpu_model=r.most_rented_model AND gl.gpu_brand=r.most_rented_brand AND gl.GPU_model = g.GPU_model AND gl.GPU_brand = g.GPU_brand" + " AND " + price_condition + " AND " + memsize_condition + " " + order_condition
            if int(dur) == 5:
                    cursor.execute(filter_sql, [date.today()-timedelta(days=14), date.today()-timedelta(days=14)])
                    listings = cursor.fetchall()
                    num2 = len(listings)
            elif int(dur) == 6:
                    cursor.execute(filter_sql, [date.today()-timedelta(days=30), date.today()-timedelta(days=30)])
                    listings = cursor.fetchall()
                    num2 = len(listings)
            elif int(dur) == 7:
                    cursor.execute(filter_sql, [date.today()-relativedelta(months=+6), date.today()-relativedelta(months=+6)])
                    listings = cursor.fetchall()
                    num2 = len(listings)


    result_dict = {'records': listings, 'current_user': current_user, 'num': num, 'num2': num2, 'max_price': max_price, 'max_memsize': max_memsize}

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
        cursor.execute("SELECT g.GPU_model, g.GPU_brand, g.Memory_size, g.Memory_type, g.Memory_interface, g.Base_clock, g.Memory_clock, g.Shaders, g.TMU, g.ROP FROM GPU_listing gl, GPU g WHERE gl.GPU_model = g.GPU_model AND gl.GPU_brand = g.GPU_brand AND gl.Listingid = {}".format(id))
        view_listing = cursor.fetchone()
    result_dict = {'view_listing': view_listing, 'listingid': id}

    return render(request,'app/view_listing.html',result_dict)



def rental(request, Listingid):
    #use this snippet in everyview function to verify user
    login_email = request.session.get('email', 0)
    logging.debug(login_email)
    if login_email == 0:
        return HttpResponseRedirect(reverse('index'))
    #use this snippet in everyview function to verify user. ends here

    """Shows the main page"""
    status = ''
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM GPU_Listing WHERE Listingid = %s", [Listingid])
        GPU_choice = cursor.fetchall()
        cursor.execute("SELECT * FROM User1 WHERE Email = %s", [request.session['email']])
        Borrower_details = cursor.fetchall()
    if request.POST:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM GPU_Listing WHERE Listingid = %s", [Listingid])
            listing = cursor.fetchone()
            cursor.execute("SELECT * FROM User1 WHERE Email = %s", [request.session['email']])
            Borrower = cursor.fetchone()
            if (datetime.strptime(request.POST['Start_day'], '%Y-%m-%d').date() >= listing[4] and datetime.strptime(request.POST['End_day'], '%Y-%m-%d').date() <= listing[5] and datetime.strptime(request.POST['Start_day'], '%Y-%m-%d').date() <=  datetime.strptime(request.POST['End_day'], '%Y-%m-%d').date()):
                ##TODO: date validation
                #cursor.execute("INSERT INTO Rental VALUES (%s, %s, %s, %s, %s, %s)",[request.POST['Borrower_id'], listing[1], listing[2],
                #           int(Listingid) , request.POST['Start_day'], request.POST['End_day']])
                number_of_days = (datetime.strptime(request.POST['End_day'], '%Y-%m-%d').date()-datetime.strptime(request.POST['Start_day'], '%Y-%m-%d').date()).days + 1
                total_cost = number_of_days * listing[6]
                if int(total_cost) > int(Borrower[4]):
                    return render(request,'app/rental.html', {'status': 'Cost of rental exceeds wallet balance, choose new dates or top up wallet','GPU' : GPU_choice, #'status' : status,
                     'Borrower' : Borrower_details })
                #elif ((datetime.strptime(request.POST['Start_day'], '%Y-%m-%d').date() < listing[4]) or datetime.strptime(request.POST['End_day'], '%Y-%m-%d').date() > listing[5]):
                #    return render(request,'app/rental.html', {'error_message': 'Invalid dates, ensure that the start rental date and end rental date are within range','GPU' : GPU_choice, 'status' : status, 'Borrower' : Borrower_details })
                elif int(total_cost) <= int(Borrower[4]):

                    cost = int(Borrower[4]) - int(total_cost)    
                    cursor.execute("UPDATE User1 SET Wallet_balance = %s WHERE Email = %s", [cost,request.session['email']])

                    cursor.execute("INSERT INTO Rental VALUES (%s, %s, %s, %s, %s, %s)"
                        , [Borrower[3], listing[1], listing[2],
                           int(Listingid) , request.POST['Start_day'], request.POST['End_day']])
                    #cursor.execute("SELECT * FROM GPU_Listing_Archive g1 WHERE g1.listingid >= all (SELECT g2.listingid FROM GPU_Listing_Archive g2)")
                    #last_entry = cursor.fetchone()
                    #cursor.execute("DELETE FROM GPU_Listing WHERE Listingid = %s", [Listingid])
                    #if (datetime.strptime(request.POST['Start_day'], '%Y-%m-%d').date() == listing[4]) and (datetime.strptime(request.POST['End_day'], '%Y-%m-%d').date() == listing[5]):
                    #    return redirect('listing')
                    #elif (datetime.strptime(request.POST['Start_day'], '%Y-%m-%d').date() == listing[4] and (datetime.strptime(request.POST['End_day'], '%Y-%m-%d').date() < listing[5])):
                    #    cursor.execute("INSERT INTO GPU_Listing VALUES(%s, %s,%s,%s,%s,%s,%s)", [last_entry[0] + 1 ,listing[1], listing[2], listing[3], 
                    #                                                                     datetime.strptime(request.POST['End_day'], '%Y-%m-%d').date() + timedelta(days = 1), listing[5], listing[6]])
                        #cursor.execute("INSERT INTO GPU_Listing_Archive VALUES(%s, %s,%s,%s,%s)", [last_entry[0] + 1 ,listing[1], listing[2], listing[3], 
                                                                                          #listing[6]]) 
                    #elif (datetime.strptime(request.POST['Start_day'], '%Y-%m-%d').date() > listing[4]) and (datetime.strptime(request.POST['End_day'], '%Y-%m-%d').date() == listing[5]):
                    #    cursor.execute("INSERT INTO GPU_Listing VALUES(%s, %s,%s,%s,%s,%s,%s)", [last_entry[0] + 1 ,listing[1], listing[2], listing[3], 
                    #                                                                     listing[4], datetime.strptime(request.POST['Start_day'], '%Y-%m-%d').date() - timedelta(days = 1), listing[6]])
                    #elif (datetime.strptime(request.POST['Start_day'], '%Y-%m-%d').date() > listing[4]) and (datetime.strptime(request.POST['End_day'], '%Y-%m-%d').date() < listing[5]):
                        #cursor.execute("INSERT INTO GPU_Listing VALUES(%s, %s,%s,%s,%s,%s,%s)", [last_entry[0] + 1 ,listing[1], listing[2], listing[3], 
                        #                                                                 listing[4], datetime.strptime(request.POST['Start_day'], '%Y-%m-%d').date()  - timedelta(days = 1), listing[6]])
                        #cursor.execute("INSERT INTO GPU_Listing VALUES(%s, %s,%s,%s,%s,%s,%s)", [last_entry[0] + 2 ,listing[1], listing[2], listing[3], 
                        #                                                                 datetime.strptime(request.POST['End_day'], '%Y-%m-%d').date() + timedelta(days = 1), listing[5], listing[6]])
                        #cursor.execute("INSERT INTO GPU_Listing_Archive VALUES(%s, %s,%s,%s,%s)", [last_entry[0] + 1 ,listing[1], listing[2], listing[3], 
                                                                                          #listing[6]])
                        #cursor.execute("INSERT INTO GPU_Listing_Archive VALUES(%s, %s,%s,%s,%s)", [last_entry[0] + 2 ,listing[1], listing[2], listing[3], 
                                                                                         #listing[6]])                                                                     
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
        cursor.execute("SELECT * FROM GPU_Listing WHERE Customerid = %s", [personal[3]])
        personal_listing = cursor.fetchall()
    result_dict['personal_listing'] = personal_listing

    # get current rent of user
    with connection.cursor() as cursor:
        cursor.execute("SELECT r.GPU_Model, r.GPU_Brand, r.Start_day, r.End_day, ((r.End_day-r.Start_day+1)* g.Price) as total_paid FROM Rental r, GPU_Listing_Archive g WHERE r.Listingid=g.Listingid AND r.Borrower_id = %s AND r.End_day > %s", [personal[3], date.today()])
        rent_listing = cursor.fetchall()
    result_dict['rent_listing']= rent_listing

    # get Lend history of user
    with connection.cursor() as cursor:
        cursor.execute("SELECT g.GPU_Model, g.GPU_Brand, r.Start_day, r.End_day, ((r.End_day-r.Start_day+1)* g.Price) as total_earned FROM Rental r, GPU_Listing_Archive g WHERE r.Listingid=g.Listingid AND g.Customerid = %s", [personal[3]])
        lend_history = cursor.fetchall()
    result_dict['lend_history']= lend_history

    # get Rent history of user
    with connection.cursor() as cursor:
        cursor.execute("SELECT r.GPU_Model, r.GPU_Brand, r.Start_day, r.End_day, ((r.End_day-r.Start_day+1)* g.Price) as total_paid FROM Rental r, GPU_Listing_Archive g WHERE r.Listingid=g.Listingid AND r.Borrower_id = %s AND r.End_day < %s", [personal[3], date.today()])
        rent_history = cursor.fetchall()
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

        cursor.execute("SELECT * FROM GPU_Listing_Archive ORDER BY Listingid DESC")
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
            ##cursor.execute("INSERT INTO GPU_Listing_Archive VALUES (%s, %s, %s, %s, %s)"
            ##        ,[next_id, request.POST['gpu_model'], request.POST['gpu_brand'], current_user,
            ##        request.POST['price']])
            return redirect('listing')  

    context['status'] = status
    return render(request, "app/add_listing.html", context)

#to-do: integrity check on top up, only accept positive values
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
        cursor.execute("SELECT * FROM User1 WHERE Email =  %s", [login_email])
        temp = cursor.fetchone()
        user_balance = int(temp[4])
        
        if request.POST:
            card_nbr = int(request.POST['card_number'])
            if card_nbr != int(temp[7]):
                return render(request,'app/top_up.html', {'user_balance': user_balance,'error_message': 'Payment failed! Key in your correct credit card number', })
            else:
                new_balance = user_balance + int(request.POST['value'])
                cursor.execute("UPDATE User1 SET Wallet_balance = %s WHERE Email = %s", [new_balance, login_email])
                return redirect('listing')  
    context['status'] = status
    result_dict = {'user_balance': user_balance}
    return render(request,'app/top_up.html',result_dict)

# Create your views here.
def admin_listing(request,custid=None):
    """Shows the main page"""
    #use this snippet in everyview function to verify user
    login_email = request.session.get('email', 0)
    logging.debug(login_email)
    if login_email == 0:
        return HttpResponseRedirect(reverse('index'))
    #use this snippet in everyview function to verify user. ends here

    ## Use raw query to get all objects
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM User1 WHERE Email = %s", [login_email])
        cursor.execute("SELECT * FROM User1 ORDER BY customerid ASC")
        customers = cursor.fetchall()
        customers_name = [customer[3] for customer in customers]
        custid = request.GET.get('cust')
        if request.GET.get('reset'):
            custid = None
        if custid is None or custid=="Reset":
            cursor.execute("select u.customerid, u.first_name, u.last_name, g.gpu_model, g.gpu_brand, g.price, g.available_start_day, g.available_end_day from user1 u left outer join (select g1.customerid as customerid, g1.gpu_model as gpu_model, g1.gpu_brand as gpu_brand, g1.price as price, g2.available_start_day as available_start_day, g2.available_end_day as available_end_day from gpu_listing_archive g1, gpu_listing g2 where g1.gpu_model=g2.gpu_model and g1.gpu_brand=g2.gpu_brand and g1.listingid=g2.listingid) g on u.customerid=g.customerid order by u.customerid asc")
            custinfo = cursor.fetchall()
        else:
            cursor.execute("select u.customerid, u.first_name, u.last_name, g.gpu_model, g.gpu_brand, g.price, g.available_start_day, g.available_end_day from user1 u left outer join (select g1.customerid as customerid, g1.gpu_model as gpu_model, g1.gpu_brand as gpu_brand, g1.price as price, g2.available_start_day as available_start_day, g2.available_end_day as available_end_day from gpu_listing_archive g1, gpu_listing g2 where g1.gpu_model=g2.gpu_model and g1.gpu_brand=g2.gpu_brand and g1.listingid=g2.listingid) g on u.customerid=g.customerid where u.customerid= %s", [custid])
            custinfo = cursor.fetchall()
        

    result_dict = {'custinfo': custinfo, 'customers': customers, 'customers_name': customers_name}

    return render(request,'app/admin_listing.html',result_dict)

def admin_rental(request,custid=None):
    """Shows the main page"""
    #use this snippet in everyview function to verify user
    login_email = request.session.get('email', 0)
    logging.debug(login_email)
    if login_email == 0:
        return HttpResponseRedirect(reverse('index'))
    #use this snippet in everyview function to verify user. ends here

    ## Use raw query to get all objects
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM User1 ORDER BY customerid ASC")
        customers = cursor.fetchall()
        customers_name = [customer[3] for customer in customers]
        custid = request.GET.get('cust')
        if request.GET.get('reset'):
            custid = None
        if custid is None or custid=="Reset":
            cursor.execute("SELECT u.customerid, u.first_name, u.last_name, j.gpu_model, j.gpu_brand, j.price, j.start_day, j.end_day FROM User1 u LEFT OUTER JOIN (SELECT r.borrower_id AS borrower_id, r.GPU_Model AS GPU_model, r.GPU_Brand AS GPU_Brand, r.start_day AS start_day, r.end_day AS end_day, g.price AS price FROM GPU_Listing_Archive g, Rental r WHERE g.listingid=r.listingid) AS j ON u.customerid=j.borrower_id ORDER BY u.customerid ASC")
            custinfo = cursor.fetchall()
        else:
            cursor.execute("SELECT u.customerid, u.first_name, u.last_name, j.gpu_model, j.gpu_brand, j.price, j.start_day, j.end_day FROM User1 u LEFT OUTER JOIN (SELECT r.borrower_id AS borrower_id, r.GPU_Model AS GPU_model, r.GPU_Brand AS GPU_Brand, r.start_day AS start_day, r.end_day AS end_day, g.price AS price FROM GPU_Listing_Archive g, Rental r WHERE g.listingid=r.listingid) AS j ON u.customerid=j.borrower_id WHERE u.customerid= %s", [custid])
            custinfo = cursor.fetchall()
        

    result_dict = {'custinfo': custinfo, 'customers': customers, 'customers_name': customers_name}

    return render(request,'app/admin_rental.html',result_dict)

