#%%

from flask import Flask, json, jsonify, request, redirect, render_template, url_for
from flask.templating import render_template
from flask_pymongo import PyMongo
import scrape_news
from multiprocessing import Value 
from config import db_user, db_password, db_host, db_port, db_name
from sqlalchemy import create_engine
import pandas as pd
from datetime import datetime 

#%%
################ FLASK SETUP ################
# Postgres Database set up or maybe I could create a csv or JSON file in my flask app... and then do ETL on it?
engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')

# Creates an instance of Flask
app = Flask(__name__)

#%%
################ DATABASE SETUP ################
engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')
print(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')

#%%
################ DEFINE FLASK ROUTS ################

#%%
# ROUTE #1: Default route to display home page
@app.route("/")
def index():
    return render_template("index.html")

# ROUTE #2: Route to display backlog 
@app.route("/backlog")
def backlog():
    return render_template("backlog.html")

#%%
# ROUTE #3: Route to generate the form and/or POST data.

# Takes in user input and routes it to our database. 
@app.route('/send', methods = ["GET", "POST"])
def send():
    
    # connect to our database
    conn = engine.connect()

        # evaluate if the this is a POST request
    if request.method == "POST":

    # # Returns input into a new SQL database (will need to add to / modify this)
        conn = engine.connect()
        
        #use `request.form` to pull form attributes and datetime.now for timestamp
        user_input = request.json["userInput"]
        time_stamp = datetime.now()
            
        # convert to a DataFrame so that we can use to_sql
        searches_df = pd.DataFrame({
            
            'user_input':[user_input],
            'time_stamp':[time_stamp]
        })

        # post the update to the DB
        searches_df.to_sql('stocks_crypto', con=conn, if_exists='append', index=False)

        # close our database connection
        conn.close()

        # send the user to the endpoint that contains the data listing
        return redirect('/send')

# if the method is NOT POST (otherwise, GET, then send the user to the app)
    conn.close()
    return render_template("index.html")

#%%
# ROUTE #4: Route to view the data
@app.route("/api/data")
def searches_list():

    # connect to db engine
    conn = engine.connect()

    # query the database using Pandas
    stocks_crypto_df = pd.read_sql('SELECT * FROM stocks_crypto', con=conn)

    #convert results to json
    stocks_crypto_json = stocks_crypto_df.to_json(orient='records')

    #close connection
    conn.close()

    #return json to the client
    return stocks_crypto_json


# ROUTE #5: AMY's STUFF

# Use flask_pymongo to set up mongo connection
app.config["MONGO_URI"] = "mongodb://localhost:27017/stock_db"
mongo = PyMongo(app)

# @app.route("/")
# def index():
#     stock = mongo.db.stock.find_one()["data"]
#     return render_template("index.html", stock=stock)


@app.route("/scrape/<ticker>")
def scrape(ticker):
    stock = mongo.db.stock 
    print(ticker)
    stock_data = scrape_news.get_news(ticker)

    return jsonify(stock_data)

    #stock.update({}, {'data': stock_data, 'ticker': ticker } , upsert=True)
    #return redirect('/', code=302)


#%%
##################### RUN APP #####################
if __name__ == "__main__":
    app.run(debug=False)

