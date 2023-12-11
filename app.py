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
    # smtp.sendmail(FROM, TO, message.as_string())


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

    # print(solar)
    # print(using)


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



summer_price = [84.8, 84.8, 84.8, 84.8, 84.8,
                84.8, 84.8, 84.8, 137.7, 137.7,
                137.7, 219.8, 137.7, 219.8, 219.8,
                219.8, 219.8, 219.8, 137.7, 137.7,
                137.7, 137.7, 84.8, 84.8]

normal_price = [84.8, 84.8, 84.8, 84.8, 84.8,
                84.8, 84.8, 84.8, 107.3, 107.3,
                107.3, 138, 107.3, 138, 138,
                138, 138, 138, 107.3, 107.3,
                107.3, 107.3, 84.8, 84.8]

winter_price = [91.8, 91.8, 91.8, 91.8, 91.8, 
                91.8, 91.8, 91.8, 137.9, 195.4,
                195.4, 195.4, 137.9, 137.9, 137.9,
                137.9, 195.4, 195.4, 195.4, 137.9,
                137.9, 137.9, 91.8, 91.8]

winter_max = [9, 10, 11, 16, 17, 18]
winter_mid = [8, 12, 13, 14, 15, 19, 20, 21]
winter_min = [0, 1, 2, 3, 4, 5, 6, 7, 22, 23]

other_max = [11, 13, 14, 15, 16, 17]
other_mid = [8, 9, 10, 12, 18, 19, 20, 21]
other_min = [0, 1, 2, 3, 4, 5, 6, 7, 22, 23]

price_dict = {"winter": winter_price, "spring": normal_price, "summer": summer_price, "fall": normal_price}

time_dict = {"winter_max": winter_max, "winter_mid": winter_mid, "winter_min": winter_min,
             "spring_max": other_max, "spring_mid": other_mid, "spring_min": other_min}


from math import *
import random
import sys


class Particle:
    def __init__(self, max_iter, initial_position=None):
        if initial_position:  # If an initial position is provided
            self.position = initial_position.copy()
        else:
            self.position = [0.0]*24  # particle current position
        self.velocity = [random.uniform(-1, 1) for _ in range(24)]  # particle current velocity
        self.best_position = [0.0]*24  # particle best position
        self.fitness = sys.maxsize   # particle fitness
        self.best_fitness = sys.maxsize  # particle best fitness
        self.iteration = 0  # iteration count
        self.max_iter = max_iter
        self.history = []

    def evaluate_fitness(self, fitness_func):
        self.fitness = fitness_func(self.position)
        if self.fitness < self.best_fitness:
            self.best_position = self.position.copy()
            self.best_fitness = self.fitness

    def update_velocity(self, global_best_position):
        w_min = 0.5
        w_max = 1
        self.iteration += 1
        w = w_max - ((w_max - w_min) * self.iteration / self.max_iter)
        c1 = 1
        c2 = 1.5
        for i in range(len(self.position)):
            r1 = random.random()
            r2 = random.random()
            cognitive_velocity = c1 * r1 * (self.best_position[i] - self.position[i])
            social_velocity = c2 * r2 * (global_best_position[i] - self.position[i])
            self.velocity[i] = w * self.velocity[i] + cognitive_velocity + social_velocity

    def update_position(self, bounds):
        for i in range(len(self.position)):
            self.position[i] += self.velocity[i]
            if self.position[i] < bounds[i][0]:
                self.position[i] = bounds[i][0]
            elif self.position[i] > bounds[i][1]:
                self.position[i] = bounds[i][1]
        self.history = (self.iteration, self.position.copy(), self.fitness)

class PSO:
    def __init__(self, fitness_function, bounds, num_particles, max_iter, initial_positions=None):
        self.fitness_func = fitness_function
        self.bounds = bounds
        self.num_particles = num_particles
        self.max_iter = max_iter
        self.global_best_position = [0.0]*24
        self.global_best_fitness = sys.maxsize
        self.history = []
        if initial_positions:
            self.swarm = [Particle(max_iter, initial_position=pos) for pos in initial_positions]
        else:
            self.swarm = [Particle(max_iter) for _ in range(num_particles)]

    def run_result(self):
        for i in range(self.max_iter):
            for j in range(self.num_particles):
                self.swarm[j].evaluate_fitness(self.fitness_func)
                if self.swarm[j].fitness < self.global_best_fitness:
                    self.global_best_position = self.swarm[j].position.copy()
                    self.global_best_fitness = self.swarm[j].fitness
            for j in range(self.num_particles):
                self.swarm[j].update_velocity(self.global_best_position)
                self.swarm[j].update_position(self.bounds)
            self.history.append((i, self.global_best_position.copy(), self.global_best_fitness))
        return self.global_best_position, self.global_best_fitness, self.history

def compute_group_mean(data, prices):
    price_groups = {}
    # Group data by prices
    for d, p in zip(data, prices):
        if p not in price_groups:
            price_groups[p] = []
        price_groups[p].append(d)
    # Compute mean for each group
    group_means = {k: np.mean(v) for k, v in price_groups.items()}
    return group_means


def find_peak_group(season_price, power_use):
    # Create a dictionary to map price to hours
    price_to_hours = {}
    for hour, price in enumerate(season_price):
        if price not in price_to_hours:
            price_to_hours[price] = []
        price_to_hours[price].append(hour)
    
    # Identify the group with the highest power use
    max_power = -float('inf')
    peak_group = None
    for price, hours in price_to_hours.items():
        total_power = sum([power_use[hour] for hour in hours])
        if total_power > max_power:
            max_power = total_power
            peak_group = hours

    return peak_group


def fitness_func(position, season, power_generated, power_use):
    total_cost = 0
    cumulative_generated = 0
    cumulative_used = 0
    consumption_pattern = []
    season_price = price_dict[season]
    for i in range(24):
        cumulative_generated += power_generated[i]
        cumulative_used += position[i]
        if cumulative_used > cumulative_generated:  # Cannot use more than generated
            return sys.maxsize
        consumption_pattern.append(power_use[i] - position[i])
        total_cost += (power_use[i] - position[i]) * season_price[i]

        if position[i] > power_use[i] * 0.9 :
            return sys.maxsize
        
    return total_cost

def variance_fitness_func_with_group_mean(position, base_cost, season, power_generated, power_use):
    total_cost = 0
    cumulative_generated = 0
    cumulative_used = 0
    consumption_pattern = []
    season_price = price_dict[season]
    
    for i in range(24):
        cumulative_generated += power_generated[i]
        cumulative_used += position[i]
        
        if cumulative_used > cumulative_generated:
            return sys.maxsize
        
        if position[i] > power_use[i] * 0.9 :
            return sys.maxsize
        
        consumption_pattern.append(power_use[i] - position[i])
        total_cost += (power_use[i] - position[i]) * season_price[i]
    
    if total_cost > base_cost:
        return sys.maxsize
    
    group_means = compute_group_mean(consumption_pattern, season_price)
    peak_group = find_peak_group(season_price, power_use)
    
    weighted_deviation = sum([(consumption_pattern[i] - group_means[season_price[i]])**2 for i in peak_group])

    # peak_weight = 0.8  
    # total_deviation = (peak_weight * weighted_deviation) + (1 - peak_weight) * sum([(consumption_pattern[i] - group_means[season_price[i]])**2 for i in range(24) if i not in peak_group])

    return weighted_deviation

def cal_price_with_variance_optimization_updated(power_generated, power_use, weather):
    power_generated = np.array(power_generated).astype(float)
    power_use = np.array(power_use).astype(float)
    bounds = [(0, power_use[i] * 0.9) for i in range(24)]
    initial_positions = [(power_generated*0.2).tolist() if i < 125 else [0]*24 for i in range(250)] 
    pso_price = PSO(lambda x: fitness_func(x, weather, power_generated, power_use), bounds, num_particles = 10, max_iter = 200, initial_positions=initial_positions)
    best_position_price, best_fitness_price, history = pso_price.run_result()
    
    initial_positions_variance = [best_position_price for _ in range(200)]
    pso_variance = PSO(lambda x: variance_fitness_func_with_group_mean(x, best_fitness_price, weather, power_generated, power_use), 
                       bounds, num_particles=10, max_iter=100, initial_positions=initial_positions_variance)
    best_position_variance, _ , his_2 = pso_variance.run_result()
    
    weather_price = {"winter": winter_price, "spring": normal_price, "summer": summer_price, "fall": normal_price}
    best_fitness_price = np.dot(np.array(power_use) - np.array(best_position_variance), weather_price[weather])
    before_price = np.dot(power_use, weather_price[weather])
    before_optimal_price = np.dot(np.array(power_use) - np.array(power_generated), weather_price[weather])

    return best_position_variance, best_fitness_price, before_optimal_price, before_price, history, his_2



@app.route('/calculate_price', methods=['POST'])
def calculate_price():
    data = request.get_json()
    power_generated = data['power_generated']
    power_used = data['power_used']

    # Validating the input lengths (each should have 24 values)
    if len(power_generated) != 24 or len(power_used) != 24:
        return jsonify({'error': 'Invalid input length. Both power_generated and power_used should have 24 values each.'})

    # Here we fix the weather parameter to 'summer'
    weather = 'summer'

    # Call the optimization function
    best_position_variance, best_fitness_price, before_optimal_price, before_price, history, his_2 = cal_price_with_variance_optimization_updated(power_generated, power_used, weather)

    # Return the result
    return jsonify({
        'hour':list(range(24)),
        'best_position_variance': best_position_variance,
        'best_fitness_price': best_fitness_price,
        'before_optimal_price': before_optimal_price,
        'before_price': before_price,
        'history': history,
        'his_2': his_2,
        'before_solar':power_generated
    })



@app.route('/optimize_and_plot', methods=['POST'])
def optimize_and_plot():
    data = request.get_json()
    power_generated = data['power_generated']
    power_used = data['power_used']

    # Example optimization logic (placeholder)
    optimized_power = [min(g, u) for g, u in zip(power_generated, power_used)]

    # Example graph data generation
    graph_data = {
        'hours': list(range(24)),
        'total_power': power_used,
        'solar_power': power_generated,
        'optimized_power': optimized_power  # Example optimized data
    }

    return jsonify(graph_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug = True, port=5000)
    
    

 