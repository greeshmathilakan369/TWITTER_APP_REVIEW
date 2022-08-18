#give twitter dataframe into postgres table.....WORKING
import pandas as pd 
import csv
from logging import root
from unicodedata import name
from flask import Flask,  request, render_template
from review.db_config import get_db_connection #import from sep folder

app=Flask("__name1__")

@app.route("/")
@app.route("/twitter_home",methods =["GET", "POST"])
def twitter_home(): 
    if request.method == "GET":
        
        conn = get_db_connection()
        cur = conn.cursor()
        df=pd.read_csv("tweet_greeshma_nnew.csv") #dataframe
        # print(df)
        for ind in df.index:
            cur.execute('INSERT INTO public.twitter_data (date, username, tweet_text)' 'VALUES(%s, %s, %s)', (df['date'][ind],df['user_name'][ind],df['text'][ind]))
        conn.commit()
        cur.close()
        conn.close()
    return render_template("twitter_home.html")       

#  .....................................TO VIEW DB VALUES AS WEB PAGE..............................
@app.route("/lists",methods=["GET","POST"])
def list():
    if request.method == "GET":
        list2 =[]
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM public.twitter_data")
        list2=cur.fetchall()
        print(list2,"staert")
        conn.commit()
        cur.close()
        conn.close()
        print(list2)
    return render_template("list_tweetdata.html",lists=list2)  

if __name__=="__main__":
 app.run(debug=True)

