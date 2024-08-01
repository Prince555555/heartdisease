from flask import Flask, render_template, request, jsonify,redirect,url_for,flash
import joblib
import pickle
import sqlite3
from flask_mail import Mail, Message

app = Flask(__name__)

#loading the model
file = open("heart_model.pkl" ,'rb')
model = pickle.load(file)
conn = sqlite3.connect('heart_disease.db',check_same_thread=False)
cursor = conn.cursor()
create_table = '''
 CREATE TABLE IF NOT EXISTS User_Details (
 ID INTEGER PRIMARY KEY,
 Name TEXT NOT NULL,
 Email TEXT NOT NULL,
 Password TEXT NOT NULL
 )
'''
conn.execute(create_table)
conn.commit()
@app.route("/", methods=['POST','GET']) 
def index():
 if request.method == 'POST':
        # Getting the user input 
        input_data = request.get_json()
        # Validating the data 
        if not all(key in input_data for key in ("age", "sex","cp", "trestbps", "chol", "fbs", "restecg", "thalach", "exang", "slope", "ca", "thal")):
         return jsonify({"error": "Invalid JSON structure"}), 400

        # Converting the data into a list for prediction 
        input_list = [input_data[key] for key in
                      ["age", "sex", "cp", "trestbps", "chol", "fbs", "restecg", "thalach", "exang",  "slope", "ca", "thal"]]
         #prediction
        prediction = model.predict([input_list])[0]

        if prediction == 1:
            prediction_message = "You are at risk of heart disease."
        else:
            prediction_message = "You are not at risk of heart disease."
            
        insert_sql = '''
                INSERT INTO prediction_table
                (age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, slope, ca, thal, prediction)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    '''
        data_tuple = (
                input_data.get("age"),
                input_data.get("sex"),
                input_data.get("cp"),
                input_data.get("trestbps"),
                input_data.get("chol"),
                input_data.get("fbs"),
                input_data.get("restecg"),
                input_data.get("thalach"),
                input_data.get("exang"),
                input_data.get("slope"),
                input_data.get("ca"),
                input_data.get("thal"),
                prediction_message
                )
        cursor.execute(insert_sql, data_tuple)
        conn.commit()
       
       
        return jsonify({"prediction": prediction_message})
        
 return (render_template('index.html')) 

@app.route("/patient",methods=['POST','GET'])
def show():
    cursor.execute("SELECT * FROM prediction_table")
    data = cursor.fetchall()
    conn.commit()   
    return render_template("patient.html", data=data)

@app.route("/login",methods=['POST','GET'])
def login():
    if request.method == 'POST':
        login_data = request.get_json()
        user_name = login_data.get("user_name")
        email = login_data.get("email")
        password = login_data.get("password")
        query = '''SELECT Name,Email,Password FROM User_Details WHERE Name = ? '''
        cursor.execute(query,(user_name,))
        data_user = cursor.fetchall()
        conn.commit()
        for row in data_user:
         if user_name == row[0] and email == row[1] and password == row[2]:
             status_msg = "login successful"
         else:
             status_msg = "can't login"
         return jsonify({"status_login": status_msg})
    return (render_template("login.html"))

@app.route("/signup",methods=['POST','GET'])
def signup():
    if request.method == 'POST':
        signup_data = request.get_json()
        signup = '''
           INSERT INTO User_Details 
           (name,email,password)
            VALUES(?,?,?)
        '''
        data_tuples = (
            signup_data.get("user_name"),
            signup_data.get("email"),
            signup_data.get("password"),
        )
        conn.execute(signup,data_tuples)
        conn.commit()
        signup_status = "signup successful"
        return jsonify({"status":signup_status})
    
    return (render_template("signup.html"))

if __name__ == "__main__":
    app.run(debug=True)
