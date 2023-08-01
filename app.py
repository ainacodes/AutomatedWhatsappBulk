import time
import os
from flask import Flask, render_template, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import FileField, TextAreaField, SubmitField
from wtforms.validators import DataRequired
import pandas as pd
import pywhatkit as pwk
import pyautogui

UPLOAD_FOLDER = os.path.join('uploads')

app = Flask(__name__)
# Replace with your own secret key
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER  # Folder to store uploaded files


# Define the form for file upload, message, and image attachment
class BulkWhatsAppForm(FlaskForm):
    csv_file = FileField('CSV File', validators=[DataRequired()])
    message = TextAreaField('Message', validators=[DataRequired()])
    image = FileField('Image')
    submit = SubmitField('Send')


# Define the route for the home page
@app.route('/', methods=['GET', 'POST'])
def home():
    form = BulkWhatsAppForm()
    if form.validate_on_submit():
        # Process the form data and send messages
        return redirect(url_for('send'))

    return render_template('index.html', form=form)


# Define the route for sending messages
@app.route('/send', methods=['GET', 'POST'])
def send():
    # Get the form data
    csv_file = request.files.get('csv_file')
    message = request.form.get('message')
    image = request.files.get('image')

    # Save the uploaded files locally
    csv_filename = os.path.join(app.config['UPLOAD_FOLDER'], csv_file.filename)
    csv_file.save(csv_filename)

    if image:
        image_filename = os.path.join(
            app.config['UPLOAD_FOLDER'], image.filename)
        image.save(image_filename)
    else:
        image_filename = None

    # Read the CSV file using pandas
    df = pd.read_csv(csv_filename)

    # Loop through the recipients in the CSV file and send messages
    for index, row in df.iterrows():
        name = row['name']
        phone_number = str(row['phone_number'])
        phone_number = '+' + phone_number
        # Prepare the message with the recipient's name
        final_message = f'Hi {name}, {message}'

        # Send the message with attachment using pywhatkit
        if image_filename:
            pwk.sendwhats_image(phone_number, image_filename, final_message,
                                wait_time=10)
        else:
            pwk.sendwhatmsg_instantly(phone_number, final_message)

        time.sleep(10)

        # Close the WhatsApp Web tab using pyautogui
        pyautogui.hotkey('ctrl', 'w')

        time.sleep(5)

    return "Messages sent successfully!"


if __name__ == '__main__':
    app.run(debug=True)
