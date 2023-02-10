from fnmatch import fnmatchcase
from colorama import Cursor
from flask import Flask,request,g ,render_template,flash,session,redirect,url_for
import pyodbc
import os
from google.cloud.sql.connector import Connector
import sqlalchemy
from sqlalchemy import text
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="C:/Users/HP/AppData/Roaming/gcloud/legacy_credentials/razah12145@gmail.com/adc.json"

INSTANCE_CONNECTION_NAME = "vaulted-gate-377212:us-central1:car-guru"
DB_USER = "sqlserver"
DB_PASS = "daretodie12345####"
DB_NAME = "car-guru"

connector = Connector()


def getconn():

    conn = connector.connect(
        INSTANCE_CONNECTION_NAME,
        "pytds",
        user=DB_USER,
        password=DB_PASS,
        db=DB_NAME
    )
    return conn


pool = sqlalchemy.create_engine(
    "mssql+pytds://localhost",
    creator=getconn,
)

def executeInsertquery(query: str):
    with pool.connect() as cursor:

        # query = "INSERT INTO [User](name ,CustomerAttribute, dob , email , password) VALUES ('{name}' ,{attr}, {dob}, '{email}', '{password}')".format(
        #     name="Raza haider", attr="1", dob="2002-08-01", email="raza@gmail.com", password="1234567")
        cursor.execute(text(query))
        cursor.commit()
        cursor.close()


def executeAndReturnOneRow(query: str):
    # query = "execute PendingOrders {uid}".format(uid=4)
    with pool.connect() as cursor:
        results = cursor.execute(text(query)).fetchone()
        cursor.close()
    return results


def executeAndReturnManyRows(query: str):
    # query = "execute PendingOrders {uid}".format(uid=4)
    with pool.connect() as cursor:
        results = cursor.execute(text(query)).fetchall()
        cursor.close()
    return results

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
        #conn = connection()
        #cursor = conn.cursor()
        query = "execute check_u_p @uname = '{0}', @pass = '{1}'".format(user_name, password)
        ans = executeAndReturnOneRow(query)
        #cursor.execute("execute check_u_p @uname = ?, @pass = ?",user_name,password)
        #ans = cursor.fetchone()
        print("number of users: ")
        print(ans[0])
        if(ans[0]==0):
            flash("Error! wrong username or password")
        if(ans[0]==1):
            ud.username=user_name
            ud.password = password
            return redirect(url_for("Home"))
        #conn.commit()
        #conn.close()   
    return render_template("index.html")

@carguru.route('/Home')
def Home():
    newsdata = []
    conn = connection()
    cursor = conn.cursor()
    results = executeAndReturnManyRows("SELECT * FROM newss")
    user_name = request.args.get('user_name')
    print(results)
    for row in results:
        newsdata.append({"newsdate":row[0],"title":row[1], "link": ''})
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
        if fullname == '' or email == '' or password == '' or username == '' or phone == '':
            flash("Error! Input fields can't be empty") 
        #conn = connection()
        #cursor = conn.cursor()
        executeInsertquery("Insert into users values('{0}','{1}','{2}','{3}','{4}')".format(fullname,email,password,username,phone))
        results = executeAndReturnOneRow("SELECT * FROM Users where username = '{0}' or password = '{1}' or email = '{2}' or phone = '{3}'".format(username, password, email, phone))
        if results:
            flash("Error! Username or Password or Email or Phone Number already exists")

        #conn.commit()
        #conn.close() 
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
    results = executeAndReturnManyRows('select * from companies')
    for row2 in results:
        company_dd.append({"Company":row2[0]})

    results2 = executeAndReturnManyRows('select * from enginecc')
    for row3 in results2:
        eng.append({"Engine":row3[0]}) 
    
    results3 = executeAndReturnManyRows("SELECT * from carzz")
    for row in results3:
        cars.append({"Name":row[0],"Company":row[1], "Model":row[2], "ExFactory":row[3]})
        carnames.append(row[0])

    if request.method == "POST":
        if request.form.get("filter") == "Company":
            cars = []
            carnames = []
            companyname = request.form.get("company")
            results4 = executeAndReturnManyRows("execute showcars @cn = '{0}'".format(companyname))
            for row5 in results4:
                cars.append({"Name":row5[0],"Company":row5[1], "Model":row5[2], "ExFactory":row5[3]})
                carnames.append(row5[0])
        

        if request.form.get("filter") == "Price":
            lowerbound = request.form.get("lowlimit")
            upperbound = request.form.get("uplimit")
            if (int(lowerbound) >= 0 and int(upperbound) >= int(lowerbound)):
                cars = []
                carnames = []
                results5 = executeAndReturnManyRows("execute pricerange @lowerbound = '{0}', @upperbound = '{1}'".format(lowerbound, upperbound))
                for row4 in results5:
                    cars.append({"Name":row4[0],"Company":row4[1], "Model":row4[2], "ExFactory":row4[3]})
                    carnames.append(row4[0])
            else:
                flash("INVALID PRICE RANGE")

        
        if request.form.get("filter") == "Engine":
            enginesize = request.form.get("engineCC")
            cars = []
            carnames = []
            results6 = executeAndReturnManyRows("execute enginesearch @size = '{0}'".format(enginesize))
            for row6 in results6:
                cars.append({"Name":row6[0],"Company":row6[1], "Model":row6[2], "ExFactory":row6[3]})
                carnames.append(row6[0])


        if request.form.get("sort") == "priceA":
            cars = []
            carnames = []
            results7 = executeAndReturnManyRows('execute ascendingsort');
            for row7 in results7:
                cars.append({"Name":row7[0],"Company":row7[1], "Model":row7[2], "ExFactory":row7[3]})
                carnames.append(row7[0])

        
        if request.form.get("sort") == "priceD":
            cars = []
            carnames = []
            results8 = executeAndReturnManyRows('execute descendingsort')
            for row8 in results8:
                cars.append({"Name":row8[0],"Company":row8[1], "Model":row8[2], "ExFactory":row8[3]})
                carnames.append(row8[0])

        if request.form.get("sort") == "yearA":
            cars = []
            carnames = []
            results9 = executeAndReturnManyRows('SELECT * FROM ascModels')
            for row8 in results9:
                cars.append({"Name":row8[0],"Company":row8[1], "Model":row8[2], "ExFactory":row8[3]})
                carnames.append(row8[0])
            
        if request.form.get("sort") == "yearD":
            cars = []
            carnames = []
            results10 = executeAndReturnManyRows('SELECT * FROM descModels')
            for row8 in results10:
                cars.append({"Name":row8[0],"Company":row8[1], "Model":row8[2], "ExFactory":row8[3]})
                carnames.append(row8[0])
            


        carname  = request.form.get("like")
        model = request.form.get("likem")

        if searcher(carnames, carname) == 1:
            executeInsertquery("execute addtowishlist @cname = '{0}' ,@uname = '{1}', @cyear = '{2}'".format(carname, ud.username, model))
    
    wishcars = []
    favourites = []
    results11 = executeAndReturnManyRows("execute Wishnames @un = '{0}'".format(ud.username))
    print(carnames)
    
    for row in results11:
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
    results = executeAndReturnManyRows("select * from carNames")
    for row in results:
        ddm.append({"CarName":row[0]})

    if request.method == "POST":
        display = 1
        name = request.form.get("cars_dropdown")
        conn = connection()
        cursor = conn.cursor()
        results2 = executeAndReturnManyRows("execute show_review @cname = '{0}'".format(name))
        for row in results2:
            rvz.append({"Review":row[0]})

        results3 = executeAndReturnManyRows("execute showlinks @cn = '{0}'".format(name));
        for row in results3:  
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
    results = executeAndReturnManyRows("select * from carNames")
    for row in results:
        ddm.append({"CarName":row[0]})
    if request.method == "POST":
        name1 = request.form.get("cars_dropdown1")
        results2 = executeAndReturnManyRows("execute compare @cname = '{0}'".format(name1))
        for row in results2:
            car1.append({"Name":row[1], "Engine":row[2], "Type":row[3], "Model":row[4], "Company":row[5], "FuelType":row[6],          "Transmission":row[7], "HorsePower":row[8], "Torque":row[9], "BootCapacity":row[10], "TopSpeed":row[11],
                     "FuelAvg":row[12], "SeatingCapacity":row[13], "TyreSize":row[14], "GroundClearence":row[15] , "AirBags":row[18] , "SunRoof":row[19],"ABSbrakes":row[20],"Infotainment":row[21],"ClimateControl":row[22],"CruiseControl":row[23],"Traction":row[24],"ParkingSense":row[25],"PushStart":row[26], "Price": row[27]})
        name2 = request.form.get("cars_dropdown2")
        results3 = executeAndReturnManyRows("execute compare @cname = '{0}'".format(name2))
        for row in results3:
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
    results = executeAndReturnManyRows("Select * from carNames")
    for row in results:
        ddm.append({"CarName":row[0]})

    results2 = executeAndReturnManyRows("select * from prov_City")
    for row2 in results2:
        ddm2.append({"City":row2[0]})

    if request.method == "POST":
        display = 1
        name = request.form.get("cars_dropdown")
        city = request.form.get("city_dropdown")
        conn = connection()
        cursor = conn.cursor()
        results3 = executeAndReturnManyRows("execute total_cost @cname='{0}', @ctname='{1}'".format(name,city))
        for row in results3:
            orp.append({"totalPrice":row[0]})

    conn.commit()
    conn.close()

    return render_template("orprice.html", ddm = ddm, ddm2 = ddm2, name = name, orp = orp, display = display, user_name_recieved = ud.username)
    
@carguru.route('/Wishlist')
def wishlist():
    cars = []
    conn = connection()
    cursor = conn.cursor()
    results = executeAndReturnManyRows("execute getwishlist @uname = '{0}'".format(ud.username))
    for row in results:
        cars.append({"Name":row[0],"Company":row[1], "Model":row[2], "ExFactory":row[3]})

    userinfo = []
    results2 = executeAndReturnManyRows("execute userdetails @uname = '{0}'".format(ud.username))
    for row in results2:
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
        executeInsertquery("INSERT INTO Contacts VALUES('{0}', '{1}')".format(ud.username, feedback))
        conn.commit()
        conn.close()

    return render_template("contact.html", user_name_recieved = ud.username)

@carguru.route('/<name>')
def AllCars(name):
    specs = []
    conn = connection()
    cursor = conn.cursor()
    results =  executeAndReturnManyRows("execute carDetailz @cname = '{0}'".format(name))
    for row in results:
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


if __name__ == '__main__':
    server_port = os.environ.get('PORT', '8080')
    carguru.run(debug=False, port=server_port, host='0.0.0.0')
