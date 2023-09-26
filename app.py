
from flask import Flask,render_template,request,url_for,session,redirect,jsonify
from transformers import DetrImageProcessor, DetrForObjectDetection
import torch
import timm
from PIL import Image
import os
from flask_pymongo import pymongo
from bson import Binary
from flask import  send_from_directory
import bcrypt

app = Flask(__name__)

os.environ['FLASK_SECRET_KEY'] = 'your_secure_'

secret_key = os.environ.get('FLASK_SECRET_KEY')


client = pymongo.MongoClient("mongodb+srv://harshnainwal55:20140282601@cluster0.3vbb9qo.mongodb.net/?retryWrites=true&w=majority")

db = client.get_database("total_records")
records=db.register
processor = DetrImageProcessor.from_pretrained("facebook/detr-resnet-50")
model = DetrForObjectDetection.from_pretrained("facebook/detr-resnet-50")


@app.route('/')
@app.route("/index",methods=['GET','POST'])
def index_page():
    return render_template('index.html')

@app.route("/aboutus")
def aboutus_page():
    return render_template('aboutus.html')

@app.route('/static/scripts/<filename>')
def serve_static(filename):
    return send_from_directory('static/scripts', filename)


@app.route('/aboutus_mail')
def aboutus_mail():
    if(request.method=='POST'):
        user_requirments = request.form('#') # to be discussed


@app.route('/blog1')
def blog1_page():
     return render_template('blog1.html')


@app.route('/blog2')
def blog2_page():
     return render_template('blog2.html')


@app.route('/blog3')
def blog3_page():
     return render_template('blog3.html')


@app.route('/buycheck')
def buycheck_page():
     return render_template('buy-checkout.html')


@app.route("/buy")
def buy_page():
    return render_template('buy.html')


@app.route("/contactUs")
def contactus_page():
    return render_template('contactUs.html')





@app.route('/learningoc')
def learningoc_page():
     return render_template('learningoc.html')


@app.route("/logins",methods=['GET','POST'])
def login_page():
    return render_template('login.html')
  

@app.route('/login_validation',methods=['POST','GET']) 
def login_validation():
    if "email" in session:
        return redirect(url_for("login.html"))
    if request.method=='POST':
        user = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        user_found=records.find_one({"name":user})
        email_found=records.find_one({"email":email})
        if user_found:
            message="alreay exists"
            return render_template('login.html')
        if email_found:
            message="already exists"
            return render_template('login.html')
        
        else:
            hashed=bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt())
            user_input={'name':user,'email':email,'password':hashed}
            records.insert_one(user_input)

            user_data=records.find_one({'email':email})
            new_email=user_data['email']
            return render_template('index.html')

    return render_template('about.html')


@app.route("/logining", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        # Check if email and password are not empty
        if not email or not password:
           
            return redirect(url_for("login_page"))

        email_found = records.find_one({"email": email})
        if email_found:
            email_val = email_found['email']
            passwordcheck = email_found['password']

            if bcrypt.checkpw(password.encode('utf-8'), passwordcheck):
                session["email"] = email_val
                return redirect(url_for('index_page'))
            else:
                
                return redirect(url_for("login_page"))
        else:
        
            return redirect(url_for("login_page"))

    return render_template('login.html')

@app.route('/sellcheckout')
def sellcheckout_page():
     return render_template('sell-checkout.html')

@app.route("/sell")
def sell_page():
    return render_template('sell.html')


@app.route('/upload', methods=['POST'])
def upload():
    if 'file' in request.files:
        file = request.files['file']
        if file.filename != '':
            # Read the uploaded image
            image = Image.open(file.stream)
            
            # Preprocess the image
            inputs = processor(images=image, return_tensors="pt")
            
            # Perform object detection
            outputs = model(**inputs)
            
            # Post-process the results
            target_sizes = torch.tensor([image.size[::-1]])
            results = processor.post_process_object_detection(outputs, target_sizes=target_sizes, threshold=0.9)[0]
            
            # Prepare the response
            detections = []
            for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
                box = [round(i, 2) for i in box.tolist()]
                detection = {
                    "label": model.config.id2label[label.item()],
                    "confidence": round(score.item(), 3),
                    "location": box
                }
                detections.append(detection)
            
            response_data = {
                "message": "Image uploaded and processed successfully!",
                "detections": detections
            }
            
            return jsonify(response_data)

    return 'No file selected for upload. Please select a file.'




if __name__=="__main__":
    app.secret_key='mysecret'
    app.run(debug=True)
