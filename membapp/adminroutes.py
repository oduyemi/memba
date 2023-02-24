from flask import render_template,request,redirect,flash,session,url_for
from sqlalchemy.sql import text

from werkzeug.security import generate_password_hash,check_password_hash
from membapp import app, db
from membapp.models import Party,Topics

@app.route('/admin/', methods=["POST","GET"])
def admin_home():
    if request.method == 'GET':
        return render_template("admin/adminreg.html")
    else:
        username =request.form.get('username')
        pwd=request.form.get('pwd')
        #insert into database
        """convert the plain password to hashed value and insert into db"""
        hashed_pwd = generate_password_hash(pwd)
        if username != "" or pwd !="":
            query = f"INSERT INTO admin SET admin_username='{username}',admin_pwd='{hashed_pwd}'"
            db.session.execute(text(query))
            db.session.commit()
            flash("<div class='alert alert-success'>Registeration successful. Login Here</div>")
            return redirect('/admin/login')
        else:
            flash("<div class='alert alert-danger'>Username and Password must be supplied</div>")
            return redirect('/admin')

@app.route("/admin/login",methods=["POST","GET"])
def login():
    if request.method == "GET":
        return render_template("admin/adminlogin.html")
    else:
        username=request.form.get('username')
        pwd=request.form.get('pwd')
        #write your select query
        query = f"SELECT * FROM admin WHERE admin_username='{username}'"
        result = db.session.execute(text(query))
        total = result.fetchone()#fetch one() or fetchmany(1)
        if total:#the username exists
            pwd_indb = total[2]#hashed password from database
            #compare this hashed with the pwd coming from the form
            chk = check_password_hash(pwd_indb,pwd)#returns True or False
            if chk:# same as if chk == True,
                #login details are correct
                #log user in by saving details in session
                session['loggedin']=username
                return redirect('/admin/dashboard')
            else:
                flash("<div class='alert alert-danger'>Invalid credentials</div>")
                return redirect('/admin/login')
        else:
            flash("<div class='alert alert-danger'>Invalid credentials</div>")
            return redirect('/admin/login')
        

@app.route('/admin/dashboard')
def dashboard():
    if session.get("loggedin") != None:
        return render_template('admin/index.html')
    else:
        return render_template("/admin/login")


@app.route("/admin/logout")
def admin_logout():
    if session.get("loggedin") != None:
        session.pop("loggedin",None)
    return redirect("/admin/login")

@app.route('/admin/party',methods=["POST","GET"])
def parties():
    if session.get("loggedin") == None:
        return redirect('/login')
    else:
        if request.method == 'GET':
            return render_template("admin/adminaddparty.html")
        else:
            partyname = request.form.get('partyname')
            partycode = request.form.get('shortcode')
            partycontact = request.form.get('contact')
            #insert into the party table using ORM Method
            #step1: create an instance of party(ensure that party is imported from models) obj = classname(column1=value,column2=value)
            p = Party(party_name=partyname,party_shortcode=partycode,party_contact=partycontact)
            #step2: add to session
            db.session.add(p)
            #step3: commit the session
            db.session.commit()
            flash("Party Added!")
            return redirect(url_for('all_parties'))

@app.route('/admin/parties')
def all_parties():
    if session.get('loggedin') !=None:
        #we will fetch from db using ORM method
        data = db.session.query(Party).order_by(Party.party_shortcode.desc())
        return render_template('/admin/all_parties.html',data=data )#"Display all the parties here"
    else:
        return redirect('/admin/login')


@app.route('/admin/topics')
def all_topics():
    if session.get("loggedin") == None:
        return redirect('/login')
    else:
        topics=Topics.query.all()
        return render_template("admin/alltopics.html",topics=topics)


@app.route('/admin/topics/delete/<id>')
def delete_post(id):
    #retieve topic that you want to delete
    topicobj = Topics.query.get_or_404(id)
    db.session.delete(topicobj)
    db.session.commit()
    flash('Topic deleted')
    return redirect(url_for('all_topics'))

@app.route('/admin/topic/edit/<id>')
def edit_topic(id):
    if session.get("loggedin") == None:
        return "redirect('/login')"
    else:
        topicdeets= Topics.query.get(id)
        return render_template('admin/edit_topic.html',topicdeets=topicdeets)
    
@app.route("/admin/update_topic", methods =["POST"])
def update_topic():
    if session.get("loggedin") != None:
        newstatus = request.form.get('status')
        topicid = request.form.get('topicid')
        t = Topics.query.get(topicid)
        t.topic_status = newstatus
        db.session.commit()
        flash("Topic successfully updated!")
        return redirect("/admin/topics")
    else:
        return redirect('admin/login')





# for login when password isnt hashed
# @app.route("/admin/login",methods=["POST","GET"])
# def login():
#     if request.method == "GET":
#         return render_template("admin/adminlogin.html")
#     else:
#         username=request.form.get('username')
#         pwd=request.form.get('pwd')
#         #write your select query
#         query = f"SELECT * FROM admin WHERE admin_username='{username}' AND admin_pwd='{pwd}'"
#         result = db.session.execute(text(query))
#         total = result.fetchall()#fetch one() or fetchmany(1)
#         if total:#the login details are correct
#             #log user in by saving details in session
#             session['loggedin']=username
#             return redirect('/admin/dashboard')
#         else:
#             flash("<div class='alert alert-danger'>Invalid credentials</div>")
#             return redirect('/admin/login')
