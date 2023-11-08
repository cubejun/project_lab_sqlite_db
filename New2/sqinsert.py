import sqlite3
import datetime
import random
import time
from sense_hat import SenseHat

conn = sqlite3.connect("measurement_data.db")
cursor = conn.cursor()

cursor.execute('''CREATE TABLE if not exists measurements (
        id INTEGER PRIMARY KEY,
        humid DOUBLE,
        temp DOUBLE,
        x REAL,
        y REAL,
        z REAL
         )''')
conn.commit()

current_time = datetime.datetime.now()

sense = SenseHat()
while True:
    random_humid = sense.get_humidity()
    random_temp = sense.get_temperature()
    random_distance = sense.get_pressure()
    gyro_data = sense.get_gyroscope_raw()
    cursor.execute("INSERT INTO measurements (humid, temp, x, y, z) VALUES (?, ?, ?, ?, ?)",(random_humid, random_temp, gyro_data['x'],gyro_data['y'],gyro_data['z'] ))
    conn.commit()

    #data1 = cursor.execute("SELECT * FROM measurements").fetchall()
    #for row in data1:
     #   print(row)
    time.sleep(2)   
