from fnmatch import fnmatchcase
from colorama import Cursor
from flask import Flask,request,g ,render_template,flash,session,redirect,url_for
import pyodbc
import os
import psycopg2

def searcher(arr, car):
    for i in arr:
        #print(i)
        if(i == car):
            return 1;

    return 0


class User:
    def __innit__(self,username,password):
        self.username = username
        self.password =password


ud = User()
carguru = Flask(__name__)
carguru.secret_key = "abc"
@carguru.route('/',methods =["GET", "POST"])
def Login():
    if request.method == "POST":
        user_name = request.form.get("username")
        password = request.form.get("password")
        print("Your username is "+user_name +", Password: "+ password)
        conn = connection()
        cursor = conn.cursor()
        cursor.execute("execute check_u_p @uname = ?, @pass = ?",user_name,password)
        ans = cursor.fetchone()
        print("number of users: ")
        print(ans[0])
        if(ans[0]==0):
            flash("Error! wrong username or password")
        if(ans[0]==1):
            ud.username=user_name
            ud.password = password
            return redirect(url_for("Home"))
        conn.commit()
        conn.close()   
    return render_template("index.html")

@carguru.route('/Home')
def Home():
    newsdata = []
    conn = connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM newss")
    user_name = request.args.get('user_name')
    for row in cursor.fetchall():
        newsdata.append({"newsdate":row[0],"title":row[1], "link": row[2]})
    conn.commit()
    conn.close()
    
    return render_template("home.html",newsdata = newsdata,user_name_recieved = ud.username)

@carguru.route('/register',methods =["GET", "POST"])
def Register():
    if request.method == "POST":
        fullname = request.form.get("fname")
        password = request.form.get("password")
        email = request.form.get("email")
        username = request.form.get("username")
        phone = request.form.get("phone")
        print("Your username is "+username +", Password: "+ password+" Fullname: "+fullname+" Email: "+email+" Phone: "+phone)
        conn = connection()
        cursor = conn.cursor()
        cursor.execute("Insert into users values(?,?,?,?,?)",fullname,email,password,username,phone)
        for row in cursor.fetchall():
            if (row[0] == 1):
                flash("Error! Username or Password or Email or Phone Number already exists")
            elif(row[0] == 2):
                flash("Error! Input fields can't be empty")
        conn.commit()
        conn.close() 
    return render_template("register.html")

@carguru.route('/Cars', methods = ["GET","POST"])
def carz():
    cars = []
    carnames = []
    company_dd = []
    eng = []

    wishcars = []
    favourites = []

    conn = connection()
    cursor = conn.cursor()
    cursor.execute('select * from companies')
    for row2 in cursor.fetchall():
        company_dd.append({"Company":row2[0]})

    cursor.execute('select * from enginecc')
    for row3 in cursor.fetchall():
        eng.append({"Engine":row3[0]}) 
    
    cursor.execute("SELECT * from carzz")
    for row in cursor.fetchall():
        cars.append({"Name":row[0],"Company":row[1], "Model":row[2], "ExFactory":row[3]})
        carnames.append(row[0])

    if request.method == "POST":
        if request.form.get("filter") == "Company":
            cars = []
            carnames = []
            companyname = request.form.get("company")
            cursor.execute('execute showcars @cn = ?', companyname)
            for row5 in cursor.fetchall():
                cars.append({"Name":row5[0],"Company":row5[1], "Model":row5[2], "ExFactory":row5[3]})
                carnames.append(row5[0])
        

        if request.form.get("filter") == "Price":
            lowerbound = request.form.get("lowlimit")
            upperbound = request.form.get("uplimit")
            if (int(lowerbound) >= 0 and int(upperbound) >= int(lowerbound)):
                cars = []
                carnames = []
                cursor.execute('execute pricerange @lowerbound = ?, @upperbound = ?', lowerbound, upperbound)
                for row4 in cursor.fetchall():
                    cars.append({"Name":row4[0],"Company":row4[1], "Model":row4[2], "ExFactory":row4[3]})
                    carnames.append(row4[0])
            else:
                flash("INVALID PRICE RANGE")

        
        if request.form.get("filter") == "Engine":
            enginesize = request.form.get("engineCC")
            cars = []
            carnames = []
            cursor.execute('execute enginesearch @size = ?', enginesize)
            for row6 in cursor.fetchall():
                cars.append({"Name":row6[0],"Company":row6[1], "Model":row6[2], "ExFactory":row6[3]})
                carnames.append(row6[0])


        if request.form.get("sort") == "priceA":
            cars = []
            carnames = []
            cursor.execute('execute ascendingsort')
            for row7 in cursor.fetchall():
                cars.append({"Name":row7[0],"Company":row7[1], "Model":row7[2], "ExFactory":row7[3]})
                carnames.append(row7[0])

        
        if request.form.get("sort") == "priceD":
            cars = []
            carnames = []
            cursor.execute('execute descendingsort')
            for row8 in cursor.fetchall():
                cars.append({"Name":row8[0],"Company":row8[1], "Model":row8[2], "ExFactory":row8[3]})
                carnames.append(row8[0])

        if request.form.get("sort") == "yearA":
            cars = []
            carnames = []
            cursor.execute('SELECT * FROM ascModels')
            for row8 in cursor.fetchall():
                cars.append({"Name":row8[0],"Company":row8[1], "Model":row8[2], "ExFactory":row8[3]})
                carnames.append(row8[0])
            
        if request.form.get("sort") == "yearD":
            cars = []
            carnames = []
            cursor.execute('SELECT * FROM descModels')
            for row8 in cursor.fetchall():
                cars.append({"Name":row8[0],"Company":row8[1], "Model":row8[2], "ExFactory":row8[3]})
                carnames.append(row8[0])
            


        carname  = request.form.get("like")
        model = request.form.get("likem")

        if searcher(carnames, carname) == 1:
            cursor.execute("execute addtowishlist @cname = ? ,@uname = ?, @cyear = ?",carname, ud.username, model)
    
    wishcars = []
    favourites = []
    cursor.execute("execute Wishnames @un = ?", ud.username)
    print(carnames)
    
    for row in cursor.fetchall():
        wishcars.append(row[0])
    
    print(wishcars)

    for i in range(len(carnames)):
        if (searcher(wishcars,carnames[i]) != 0): 
            favourites.append(1)
        else:
            favourites.append(0)
        
    print(favourites)
    conn.commit()
    conn.close()
    return render_template("cars.html", company_dd = company_dd, eng_dd = eng, car_arr = cars ,favourites = favourites,user_name_recieved=ud.username)


@carguru.route('/Reviews', methods =["GET", "POST"])
def reviewz():
    name=' '
    ddm = []
    rvz = []
    link = []
    display = 0
    conn =connection()
    cursor = conn.cursor()
    cursor.execute("select * from carNames")
    for row in cursor.fetchall():
        ddm.append({"CarName":row[0]})

    if request.method == "POST":
        display = 1
        name = request.form.get("cars_dropdown")
        conn = connection()
        cursor = conn.cursor()
        cursor.execute("execute show_review @cname = ?",name)
        for row in cursor.fetchall():
            rvz.append({"Review":row[0]})

        cursor.execute("execute showlinks @cn = ?", name);
        for row in cursor.fetchall():  
            link.append({"Link": row[0]})


    conn.commit()
    conn.close()
    return render_template("reviews.html", ddm = ddm, review = rvz,name = name, display = display, link = link, user_name_recieved = ud.username)

@carguru.route('/Comparison',methods =["GET", "POST"])
def comparison():
    car1 = []
    car2 = []
    ddm = []
    conn = connection()
    cursor = conn.cursor()
    cursor.execute("select * from carNames")
    for row in cursor.fetchall():
        ddm.append({"CarName":row[0]})
    if request.method == "POST":
        name1 = request.form.get("cars_dropdown1")
        cursor.execute("execute compare @cname = ?",name1)
        for row in cursor.fetchall():
            car1.append({"Name":row[1], "Engine":row[2], "Type":row[3], "Model":row[4], "Company":row[5], "FuelType":row[6],          "Transmission":row[7], "HorsePower":row[8], "Torque":row[9], "BootCapacity":row[10], "TopSpeed":row[11],
                     "FuelAvg":row[12], "SeatingCapacity":row[13], "TyreSize":row[14], "GroundClearence":row[15] , "AirBags":row[18] , "SunRoof":row[19],"ABSbrakes":row[20],"Infotainment":row[21],"ClimateControl":row[22],"CruiseControl":row[23],"Traction":row[24],"ParkingSense":row[25],"PushStart":row[26], "Price": row[27]})
        name2 = request.form.get("cars_dropdown2")
        cursor.execute("execute compare @cname = ?",name2)
        for row in cursor.fetchall():
            car2.append({"Name":row[1], "Engine":row[2], "Type":row[3], "Model":row[4], "Company":row[5], "FuelType":row[6],          "Transmission":row[7], "HorsePower":row[8], "Torque":row[9], "BootCapacity":row[10], "TopSpeed":row[11],
                     "FuelAvg":row[12], "SeatingCapacity":row[13], "TyreSize":row[14], "GroundClearence":row[15] , "AirBags":row[18] , "SunRoof":row[19],"ABSbrakes":row[20],"Infotainment":row[21],"ClimateControl":row[22],"CruiseControl":row[23],"Traction":row[24],"ParkingSense":row[25],"PushStart":row[26], "Price": row[27]})
        conn.commit()
        conn.close()
    return render_template("comparison.html",car1 = car1,car2 = car2,ddm = ddm, user_name_recieved = ud.username)

@carguru.route('/On-Road Price', methods =["GET", "POST"])
def totalcost():
    name = ' '
    city = ' '
    ddm = []
    ddm2 = []
    orp = []
    display = 0
    conn =connection()
    cursor = conn.cursor()
    cursor.execute("Select * from carNames")
    for row in cursor.fetchall():
        ddm.append({"CarName":row[0]})

    cursor.execute("select * from prov_City")
    for row2 in cursor.fetchall():
        ddm2.append({"City":row2[0]})

    if request.method == "POST":
        display = 1
        name = request.form.get("cars_dropdown")
        city = request.form.get("city_dropdown")
        conn = connection()
        cursor = conn.cursor()
        cursor.execute("execute total_cost @cname=?, @ctname=?",name,city)
        for row in cursor.fetchall():
            orp.append({"totalPrice":row[1]})

    conn.commit()
    conn.close()

    return render_template("orprice.html", ddm = ddm, ddm2 = ddm2, name = name, orp = orp, display = display, user_name_recieved = ud.username)
    
@carguru.route('/Wishlist')
def wishlist():
    cars = []
    conn = connection()
    cursor = conn.cursor()
    cursor.execute("execute getwishlist @uname = ?",ud.username)
    for row in cursor.fetchall():
        cars.append({"Name":row[0],"Company":row[1], "Model":row[2], "ExFactory":row[3]})

    userinfo = []
    cursor.execute("execute userdetails @uname = ?",ud.username)
    for row in cursor.fetchall():
        userinfo.append({"Name":row[0],"Email":row[1], "Password":row[2], "Username":row[3], "Phone":row[4]})

    conn.commit()
    conn.close()
    return render_template("wishlist.html",cars = cars, userinfo = userinfo, user_name_recieved = ud.username)

@carguru.route('/Contact', methods =["GET", "POST"])
def Contact():
    feedback = ' '

    if request.method == "POST":
        feedback = request.form.get("feedback")
        conn = connection()        
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Contacts VALUES(?,?)", ud.username, feedback)
        conn.commit()
        conn.close()

    return render_template("contact.html", user_name_recieved = ud.username)

@carguru.route('/<name>')
def AllCars(name):
    specs = []
    conn = connection()
    cursor = conn.cursor()
    cursor.execute("execute carDetailz @cname = ?", name)
    for row in cursor.fetchall():
         specs.append({"NAME":row[1], "ENGINE":row[2], "TYPE":row[3], "MODEL":row[4], "COMPANY":row[5], "FUELTYPE":row[6],
                     "TRANSMISSION":row[7], "HORSEPOWER":row[8], "TORQUE":row[9], "BOOTCAPACITY":row[10], "TOPSPEED":row[11],
                     "FUELAVG":row[12], "SEATINGCAPACITY":row[13], "TYRESIZE":row[14], "GROUNDCLEARENCE":row[15], "AIRBAGS": row[18], 
                     "SUNROOF": row[19], "ABSBRAKES": row[20], "Infotainment": row[21], "ClimateControl": row[22], "CruiseControl": row[23], 
                     "Traction": row[24], "ParkingSense": row[25], "PushStart": row[26], "Price": row[27]})
         print(row[1])
         print(row[4])

    return render_template("altis.html",specs = specs, user_name_recieved = ud.username)

def connection():
    conn = pyodbc.connect('Driver={SQL SERVER};'
                      'Server=DESKTOP-C8I7AT8;'
                      'Database=Project;'
                      'Trusted_Connection=yes;')
    #return conn
    #os.environ['DATABASE_URL'] = 'postgres://csxmxamzdfsrjg:85baef34b4aed44992b0a8594fbcd61f7809254199dc7b9432ce690544b3838f@ec2-107-23-76-12.compute-1.amazonaws.com:5432/d2oneh81j2ljo8'
    #DATABASE_URL = os.environ['DATABASE_URL']
    #conn = psycopg2.connect(DATABASE_URL, sslmode = 'require')
    return conn


if (__name__ == "__main__"):
    carguru.run(debug = True)

#uhzjfshyon
#O30M38M6GU2B4156$