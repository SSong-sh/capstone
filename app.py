import numpy as np
import json
from flask import Flask, request, jsonify, render_template, url_for, redirect
import pandas as pd
import numpy as np
import pvlib
from datetime import datetime, timedelta
import smtplib, ssl, imaplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

id = pd.read_excel('./id_password.xlsx', header=None)

email_user = id[0][0]
email_password = id[1][0]


app = Flask(__name__)

@app.route('/')
def root():
    return redirect(url_for('index'))

@app.route('/test')
def test():
    return jsonify({
        'result': 'abvdcdsa'
    })

@app.route('/abc')
def abc():
    return 'abc'

@app.route('/about')
def about():
   return render_template('about.html')

@app.route('/contact')
def contact():
   return render_template('contact.html')

@app.route('/index')
def index():
   return render_template('index.html')

@app.route('/map')
def map():
   return render_template('map.html')

@app.route('/nav')
def nav():
   return render_template('nav.html')

@app.route('/tech')
def tech():
   return render_template('tech.html')

@app.route('/some')
def home():
   return render_template('some.html')

@app.route('/clear_sky', methods=['POST'])
def clear_sky():
    data = request.get_json()
    capacity = data['capacity'] 
    latitude = data['latitude']
    longitude = data['longitude']

    today = datetime.today()

    start_date = today.replace(hour=0)
    end_date = today.replace(hour=23)

    location = pvlib.location.Location(latitude, longitude, tz='Asia/Seoul')

    times = pd.date_range(start=start_date, end=end_date, freq='1H', tz='Asia/Seoul')

    solpos = location.get_solarposition(times=times)
    dni_extra = pvlib.irradiance.get_extra_radiation(times)
    airmass = pvlib.atmosphere.get_relative_airmass(solpos['apparent_zenith'])
    pressure = pvlib.atmosphere.alt2pres(location.altitude)
    am_abs = pvlib.atmosphere.get_absolute_airmass(airmass, pressure)
    tl = pvlib.clearsky.lookup_linke_turbidity(times, latitude, longitude)

    solis_clearsky = pvlib.clearsky.simplified_solis(solpos['apparent_zenith'], am_abs, tl)
    cs = location.get_clearsky(times, model='simplified_solis')

    capacity = float(capacity)

    system = pvlib.pvsystem.PVSystem(surface_tilt=25, surface_azimuth=180,
                                     module_parameters={'pdc0': capacity, 'gamma_pdc': -0.04},
                                     inverter_parameters={'pdc0': capacity},
                                     modules_per_string=1, strings_per_inverter=1,
                                     temperature_model_parameters={'a': -3.56, 'b': -0.075, 'deltaT': 3})
    mc = pvlib.modelchain.ModelChain(system, location, spectral_model='no_loss', aoi_model='physical')

    mc.run_model(solis_clearsky)

    # Replace NaN values in the 'ac' column with 0
    
    # mc.ac.fillna(0, inplace=True)

    df = pd.DataFrame(mc.results.ac).to_dict('records')

    return jsonify({
        'result': [record for record in df]
    })

@app.route('/process', methods=['POST'])
def process():
    data = request.get_json()
    input_variable = data['input_variable']
    # 받은 input_variable 값을 사용하여 원하는 작업 수행 (여기서는 간단히 문자열을 변환하여 리턴)
    result = process_data(input_variable)
    return jsonify({'result': result})

def process_data(input_variable):
    # 원하는 작업을 수행하고 결과를 리턴하는 함수
    return f'입력된 변수 값: {input_variable}'


def connect_email(user_id):
    """
    input:
        user_id : gmail id (dtype : str)
    
    사용시기:
        메일을 보낼때 연결을 위해서 사용
        보내는 메일은 smtp를 사용
    """
    smtp = smtplib.SMTP('smtp.gmail.com', 587) # send

    smtp.ehlo()
    smtp.starttls()
    smtp.login(user_id, email_password)

    return smtp

def send_email(smtp, recipient, subject, body):
    """
    smtp : smtp connection (dtype : smtplib.SMTP)
    recipient : 수신자 (dtype : str or list)
    subject : 제목 (dtype : str)
    body : 본문 (dtype : str)
    """
    FROM = email_user
    TO = recipient if isinstance(recipient, list) else [recipient]
    SUBJECT = subject
    TEXT = body

    # Prepare actual message
    message = MIMEMultipart("alternative", None, [MIMEText(TEXT, 'html', 'utf-8')])

    message['Subject'] = SUBJECT
    message['From'] = FROM
    message['To'] = ", ".join(TO)

    # Send the mail using the passed smtp connection
    smtp.sendmail(FROM, TO, message.as_string())


@app.route('/contact_mail', methods=['POST'])
def send_mail():
    smtp = connect_email(email_user)
    
    data = request.get_json()
    
    print(data)
    
    # 데이터에서 이름, 연락처, 이메일, 문의 내용을 추출합니다.
    name = data.get('name')
    contact = data.get('contact')
    email = data.get('email')
    using = data.get('using')
    solar = data.get('solar')
    query = data.get('query')
    
    solar_value_list = []
    using_value_list = []

    print(solar)
    print(using)


    # 이메일 내용 구성
    subject = "새로운 문의가 도착했습니다!"
    body = f"이름: {name}<br>연락처: {contact}<br>이메일: {email}<br> 문의 내용: {query}"

    data_frame = pd.DataFrame({'using' : using, 'solar' : solar}).T.to_html()

    total_body = body + data_frame
    recipient_email = "jang0212@tukorea.ac.kr"

    # 이메일 전송
    try:
        send_email(smtp, recipient_email, subject, total_body)
        return jsonify({'status': 'success', 'message': 'Email sent successfully!'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    app.run(debug = True, port=5000)