from ina219 import INA219, DeviceRangeError
from time import sleep
from rpi_hardware_pwm import HardwarePWM
from simple_pid import PID

base = HardwarePWM(pwm_channel=0, hz=300000)
 
duty = 100.0 #Wypełnienie sygnału PWM
base.start(duty) #Uruchomienie sygnału PWM

SHUNT_OHMS = 0.00764
MAX_EXPECTED_AMPS = 10.0
ina = INA219(SHUNT_OHMS, MAX_EXPECTED_AMPS)
ina.configure(ina.RANGE_16V)

v_bus = 0.0
a = 0.0
p = 0.0
v_shunt = 0.0

pid = PID(-0.0001, -0.00021, -0.00001, setpoint=1000.0)
pid.sample_time = 0.1
pid.output_limits = (-50.0, 50.0)

def read_ina219():
    global v_bus
    global a
    global p
    global v_shunt
    
    try:
        v_bus = round(ina.voltage(), 2)
        a = round(ina.current(), 2)
        p = round(ina.power(), 2)
        v_shunt = round(ina.shunt_voltage(), 2)
    except DeviceRangeError as e:
        # Current out of device range with specified shunt resister
        print(e)
        
#    print('Bus Voltage: {0:0.2f}V'.format(v_bus))
#    print('Bus Current: {0:0.2f}mA'.format(a))
    print('Power: {0:0.2f}mW'.format(p))
#    print('Shunt Voltage: {0:0.2f}mV\n'.format(v_shunt))
        
try:
    while True:
        read_ina219()
        temp = round(pid(p), 4)
        print("Wynik PID: ", temp)
        
        duty += temp
        print("Duty: ", duty)
        duty = round(duty, 2)
        
        if duty >= 100:
            duty = 100
        elif duty <= 0:
            duty = 0
            
        base.change_duty_cycle(duty)
        print("Wypelnienie: ", duty)
        sleep(0.5)

except KeyboardInterrupt:
    print('Koniec')
 
    base.stop()
        

