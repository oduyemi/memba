import os, random, string, requests
from flask import render_template, redirect, flash, session, request, url_for, json
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.sql import text
from sqlalchemy import or_
#3rd party importations
from membapp.models import Party,User,Topics, Donation, Payment
from membapp import app, db



@app.route('/')
def home():
    #contact = LoginForm()
    #connect to the endpoint to get the list of properties in JSON format, 
    #Convert to python  dictionary and pass it to our template
    try:
        response = requests.get("http://127.0.0.1:8000/api/v1.0/listall")
        if response:
            rspjson = json.loads(response.text)
        else:
            rspjson = dict()
    
    except:
        rspjson = dict()
    return render_template("user/home.html", rspjson=rspjson) # , contact=contact)

def generate_name():
    filename = random.sample(string.ascii_lowercase,10) # This will return a lst 
    return ''.join(filename) #join every, member of the list filename together



@app.route("/donate", methods=["POST","GET"])
def donation():
    if session.get("user") != None:
        deets = User.query.get(session.get(user))
    else:
        deets =None
    if request.method == "GET":
        return render_template("user/donation_form.html", deets)
    else:
        #retrieve the form data and insert into Donation table
        amount = request.form.get("amount")
        fullname = request.form.get("fullname")
        #ref = int(random.random() * 100000000)
        d =  Donation(don_donor = fullname, don_amt = amount, don_userid = session.get("user"))
        db.session.add(d); db.session.commit()
        #generate the ref no and keep in session
        refno = int(random.random() * 100000000)
        session["reference"] = refno
        session["donation_id"] = d.don_id
        return redirect("/confirm")
        #create a route - /confirm (save dashboard as)
        #create user/confirm.html, and render it within the above route


@app.route("/confirm", methods=["POST","GET"])
def confirm():
    if request.method.get("donation_id") != None:
        if request.method == 'GET':
            donor = db.session.query(Donation.get(session["donation_id"]))
            return render_template("user/confirm.html",refno = session["reference"])

        else:
            p = Payment(pay_donid = session.get("donation_id"), pay_ref = session["reference"])
            db.session.add(p); db.session.commit()
            return "We are connecting to paystack here"
    else:
        return redirect("/donate")



@app.route("/paystack")
def paystack():
    return "Paystack Response"



@app.route('/signup')
def user_signup():
    #fetch all the party from party table so that we can display in a select drop down
    p = db.session.query(Party).all() #Party.query.all() is also an alternative 
    return render_template('user/signup.html',p=p)
    #TO DO within signup.html, loop over p and display it within a select drop down

# @app.route('/signup')
# def user_signup():
#     #fetch all the party from party table so that we can display in a select drop down
#     p = db.session.query(Party).all() #Party.query.all() is also an alternative 
#     return render_template('user/signup.html',p=p)
#     #TO DO within signup.html, loop over p and display it within a select drop down

# ASSIGNMENT: This is where the signup form will be submitted
@app.route('/register', methods=['POST', "GET"])
def register():
    party=request.form.get('partyid')
    email=request.form.get('email')
    pwd=request.form.get('password')
    hashed_pwd = generate_password_hash(pwd)
    if party !='' and email !='' and pwd !='':
         #insert into database using ORM method
        u=User(user_fullname='',user_email=email,user_pwd=hashed_pwd,user_partyid=party)
        #add to session
        db.session.add(u)
        db.session.commit()
        #to get the id of the record that has just been inserted
        userid=u.user_id
        session['user']=userid
        return redirect(url_for('user_login'))
    else:
        flash('You must complete all the fields to signup')
        return redirect(url_for('user_signup'))
        #TO DO: retrieve all the form data and insert into User Table
        #set a session session['user']= keep the email
        #redirect them to profile/dashboard

@app.route('/dashboard')
def user_dashboard():
    #protect this route so that only logged in user can get here 
    if session.get('user') != None:
        #retrive the details of the logged in user 
        id = session['user']
        deets = db.session.query(User).get(id)
        username=deets.user_fullname
        return render_template('user/dashboard.html',deets = deets, username = username)
        
    else:
        return redirect('/login')

@app.route('/login', methods=['GET','POST'])
def user_login():
    if request.method=='GET':
        return render_template('user/login.html')
    else:
        #retrieve the form data
        email=request.form.get('email')
        pwd=request.form.get('pwd')
        #run a query to know if the username exists on the database 
        deets = db.session.query(User).filter(User.user_email==email).first() 
        if deets !=None:
            pwd_indb = deets.user_pwd
            #compare the paswword coming from the form with the hashed password in the db
            chk = check_password_hash(pwd_indb, pwd)
            if chk:
                #log in the person
                id = deets.user_id
                session['user'] = id
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid password')
                return redirect(url_for('user_login'))
        else:
            return redirect(url_for('user_login'))
        
#if the poassword check above is right, we should log them in by keeping heir details (user_id) in session['user'] and redirect them to the dahsboard
            

@app.route('/logout')
def user_logout():
    #pop the session redirect to home page
    if session.get('user')!=None:
        session.pop('user', None)
    return redirect(url_for('user_login'))


@app.route('/profile', methods=['POST', 'GET'])
def user_profile():
    id = session.get('user')
    if id ==None:
        return redirect('user/login.html')
    else:
        if request.method =='GET':
            deets = db.session.query(User).filter(User.user_id==id).first()
            return render_template('user/profile.html',deets=deets)
        else:
            #form was submitted
            #To do: retrieve from data (fullname and phone), save them in respective variables 
            fullname = request.form.get('fullname')
            phone = request.form.get('phone')
            #update query
            userobj = db.session.query(User).get(id)
            userobj.user_fullname=fullname
            userobj.user_phone =phone
            db.session.commit()
            flash('Profile Updated')
            return redirect(url_for('dashboard'))
        #alternatively 
        # deets = db.session.query(User).filter(User.userid==id).first()
        #return redirect(url_for(user_login))
    #return render_template('/profile.html')
    

    #To do, prevent access to those who are not logged in
    #To Do: Write an ORM query to fetch the details of the logged in user

    #return render_template('user/profile.html')



@app.route('/blog') 
def blog():
    #check if logged in
    if session.get('user') != None:
        articles = db.session.query(Topics).filter(Topics.topic_status == '1').all()
        return render_template('user/blog.html', articles = articles) #create this form
    else:
       return redirect(url_for('user_login'))
    
    
@app.route("/blog/<id>/")
def blog_details(id):
    #fetch the topic with id 
    #create blog_details.html and pass blog_deets to it
    blog_deets = db.session.query(Topics).filter(Topics.topic_id == id).first()
    blog_deets = db.session.query(Topics).get_or_404(id)
    blog_deets = Topics.query.get(id)
    return  render_template("user/blog_details.html", blog_deets = blog_deets)


@app.route('/newtopic', methods=['POST', 'GET'])
def topic():
    if session.get('user') !=None:
        if request.method =='GET':
            return render_template('user/newtopic.html')
        else:
            #retrieve form data and validate 
            content = request.form.get('content') #your text area name must be content 
            #insert into database

            if len(content)!=0:
                t=Topics(topic_title=content,topic_userid=session['user'])
                #add to session
                db.session.add(t)
                db.session.commit()
                if t.topic_id:
                    flash('Post successfully submitted for approval')
                else:
                    flash('OOps, something wentr wrong. Please try again')
            else:
                flash('You cannot submit an empty post')
            return redirect(url_for('blog'))    
    else:
        return redirect(url_for('user_login'))























@app.route('/demo2')
def demo2():
    #Method 1 to query db in flask 
    #data = db.session.query(TableClassName).filter(TableClassName.column==1).all()
    #MEthod2:
    #data = db.session.query(Party).filter(Party.oarty_id>1.filter(Party.party_id<=6).all()
    #data = db.session.query(User).filter(User.user_id==1).all()
    #data = db.session.query(Party).get(1)
    #data = db.session.query(Party).filter(Party.party_id>1, Party.party_id<=6).all()

    #data = db.session.query(User).filter(User.user_email==email).filter(User.user_pwd==pwd).all()

    #TO DO: ORM query to get all the users from user table
    #data = db.session.query(User).all()

    #TO JOIN : HAVING SPECIFIED FOREIGN KEY AS BEST PRACTICES
    #data = db.session.query(User.user_fullname).join(Party.party_name).all()

    data = db.session.query(User).join(Party,User.user_partyid).all()

    return render_template('user/test.html',data=data)
    

@app.route('/profile/picture', methods =['POST','GET'])
def profile_picture():
    id = session.get('user')
    if id == None:
        return redirect(url_for('user_login'))
    else:
        if request.method=='GET':
            return render_template('user/profile_picture.html')
        else:
            #retrieve the file
            file = request.files['pix'] 
            filename = file.filename #original filename
            filetype = file.mimetype
            #note to correct the profile_picture.html and name it ppix
            allowed = ['.png', '.jpg','.jpeg']
            if filename !='':
                #upload
                name,ext = os.path.splitext(filename) 
                #import os on line 1
                if ext.lower() in allowed:
                    newname = generate_name()+ext
                    file.save("membapp/static/uploads/"+newname)
                    #update the user table using ORM by keeping the name of the uploaded file for this user, when you are done, redirect the person to dashboard
                    userobj = db.session.query(User).get(session['user'])
                    userobj.user_pix=newname
                    db.session.commit()
                    flash('Picture uploaded')
                    return redirect(url_for('dashboard'))


                    return 'File uploaded'
                else:
                    return 'File extension not allowed '
            else:
                flash('Please chose a file')
                return 'Please chose a file'

@app.route("/demo")
def demo():
    # data =db.session.query(User,Party).join(Party).all()
    #data = db.session.query(User.user_fullname, Party.party_name, Party.party_contact,Party.party_shortcode).join(Party).all()
    

    #data = User.query.join(Party).filter(Party.party_name=='Labour Party').add_columns(Party).all()

    #data = User.query.join(Party).filter(Party.party_shortcode=='LP')
    
    #data = User.query.join(Party).filter(or_(Party.party_id==1, Party.party_id==4)).add_columns(Party).all()

    #data = db.session.query(Party).filter(Party.party_id==1).first()
    #TO DO: 1. How many users are in party 1

    
    data = db.session.query(User).get(8)
    return render_template('user/test.html', data=data)





