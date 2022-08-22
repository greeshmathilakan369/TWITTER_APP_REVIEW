import re
from flask import Flask,request, render_template, redirect,flash
from db_config import get_db_connection

app=Flask("__name1__")
app.secret_key="greeshma"

#home
@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")

#To add reviews
@app.route('/reviews', methods =["GET", "POST"])
def review():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        pattern='[a-z 0-9]+[\.]?[a-z 0-9]+[@]\w+[.]\w{2,3}$'
        if re.search(pattern,email):
            review=request.form.get("review")
            conn = get_db_connection()
            cur = conn.cursor()
            user=cur.execute("SELECT * FROM public.reviews where email='"+email+"'")
            user1=cur.fetchall()
            if user1 == []:
                cur.execute('INSERT INTO public.reviews (name, email, review)' 'VALUES(%s, %s, %s)', (name,email,review))
                conn.commit()
                flash("User Inserted Successfully")
                cur.close()
                conn.close()
                return redirect('/lists')
            else:
                flash("Email id already in use...")    

        else:
            flash("Invalid email id") 
    return render_template("add_reviews.html")   
    

#To list reviews
@app.route("/lists",methods=["GET","POST"])
def list():
    if request.method == "GET":
        list2 =[]
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM public.reviews")
        list2=cur.fetchall()
        conn.commit()
        cur.close()
        conn.close()
        print(list2)
    return render_template("listdata.html",lists=list2)  

#To delete user data
@app.route("/delete/<int:id>",methods=["GET","POST"]) 
def delete(id):
    if request.method=="GET":
        conn=get_db_connection()
        cur=conn.cursor()
        cur.execute("DELETE from public.reviews where id="+str(id)) 
        conn.commit()
        flash("Deleted sucessfully")
        cur.close()
        conn.close()
    return redirect('/lists')

  
#To modify user data
@app.route("/update/<int:id>",methods=["GET","POST"])
def update(id):
    if request.method == "GET":
        result =[]
        conn=get_db_connection()
        cur=conn.cursor()
        cur.execute("select * from public.reviews where id="+str(id)) 
        result=cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        return render_template("update_new.html",result=result)    
    
    if request.method=="POST":
        conn=get_db_connection()
        cur=conn.cursor()
        id=request.form.get("id")
        name=request.form.get("name")
        email=request.form.get("email")
        review=request.form.get("review")
        pattern='[a-z 0-9]+[\.]?[a-z 0-9]+[@]\w+[.]\w{2,3}$'
        if re.search(pattern,email):
            cur.execute("SELECT * FROM public.reviews where id !=" +str(id)+ "And email='" +email+"'")
            user1=cur.fetchall()
            if user1 == []:
                update_qry= "update public.reviews set name='"+name+"',email='"+email+"', review='"+review+"' where id="+str(id)
                cur.execute(update_qry)
                conn.commit()
                flash("Modified user data sucessfully")
                cur.close()
                conn.close()
                return redirect('/lists')
            else:
                flash("Email id already in use...")
        else:
            flash("Invalid email id") 
    return render_template("post_data_new1.html")   

#To list twitter data 
@app.route("/lists_tweet",methods=["GET","POST"])
def list_tweet():
    if request.method == "GET":
        list2 =[]
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM public.twitter_data ORDER BY tid DESC")
        list2=cur.fetchall()
        print(list2,"staert")
        conn.commit()
        cur.close()
        conn.close()
        print(list2)
    return render_template("list_tweetdata.html",lists=list2)

if __name__=="__main__":
 app.run(debug=True)