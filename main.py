def check_updates():
    import gc
    from ota_updater import OTAUpdater
    otaUpdater = OTAUpdater('https://github.com/rdehuyss/micropython-ota-updater', main_dir='app')
    hasUpdated = otaUpdater.install_update_if_available()
    if hasUpdated:
        machine.reset()
    else:
        del otaUpdater
        gc.collect()
        
        
check_updates()
import time
import machine
from machine import Pin
import utime
import socket
import neopixel
import wifimgr
import ntp_client

wlan = wifimgr.get_connection()

if wlan is None:
    print("Could not initialize the network connection.")
    while True:
        pass
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 80))
    s.listen(5)
except OSError as e:
    machine.reset()
ntp_client.settime()
print(time.localtime(time.mktime()))

p1 = Pin(13, Pin.OUT)
p1.on()
p2 = Pin(18, Pin.OUT)
p2.on()
p3 = Pin(19, Pin.OUT)
p3.on()
p4 = Pin(27, Pin.OUT)
p4.on()
p5 = Pin(26, Pin.OUT)
p5.on()
p6 = Pin(25, Pin.OUT)
p6.on()
p7 = Pin(33, Pin.OUT)
p7.on()
p8 = Pin(32, Pin.OUT)
p8.on()
p_list = [p1, p2, p3, p4, p5, p6, p7, p8]
s_value_list = [0, 0, 0, 0, 0, 0, 0, 0]

knopka_1 = Pin(14, Pin.IN)
knopka_2 = Pin(34, Pin.IN)
knopka_3 = Pin(35, Pin.IN)
knopka_4 = Pin(36, Pin.IN)
knopka_5 = Pin(4, Pin.IN)
knopka_6 = Pin(21, Pin.IN)
knopka_7 = Pin(22, Pin.IN)
knopka_8 = Pin(23, Pin.IN)
knopka_list = [knopka_1, knopka_2, knopka_3, knopka_4, knopka_5, knopka_6, knopka_7, knopka_8]
np = neopixel.NeoPixel(Pin(5), 8)

''' Код подключения к WiFi'''
wlan_id = "nokia"
wlan_pass = "hzhz12hzhz"
IP = "169.254.249.75"  # IP сервера
PORT = 8080

flag1 = False  # Подключение к серверу
flag2 = False  # True при любом изменении, после отправки становится False


class Timer(object):

    def __init__(self, number):
        '''dt - сколько времени прошло, number - номер розетки, iswork - показатель работы
         таймера, 0 - не работает, 1 - работает, 2 - на отдыхе, time1 и time2 - устанавливаемое время'''
        self.dt = 0
        self.time1 = 0
        self.time2 = 0
        self.number = number
        self.iswork = 0

    def settimer(self):
        '''Включаем таймер, time_timer1 время работы, а time_timer2 время отдыха'''
        if time_timer1 != 0:
            self.start = utime.ticks_ms()
            self.iswork = 1
            self.time1 = time_timer1
            self.time2 = time_timer2
            s_on(self.number)
        if time_timer1 == 0 and time_timer2 != 0:
            self.start = utime.ticks_ms()
            self.iswork = 3
            self.time1 = 0
            self.time2 = time_timer2
            s_off(self.number)

    def stop_time(self):
        '''Выключаем таймер'''
        s_off(self.number)
        if self.iswork != 0:
            self.dt = 0
            self.time1 = 0
            self.time2 = 0
            self.iswork = 0

    def chek_timer(self):
        '''Проверяем, истекло ли время'''
        if self.iswork == 2:  # Розетка выключена, ждём включения, работа в цикле
            self.dt = round((utime.ticks_ms() - self.start) / 1000, 1)
            if self.dt >= self.time2:
                self.iswork = 1
                self.dt = 0
                self.start = utime.ticks_ms()
                s_on(self.number)
                self.start = utime.ticks_ms()
        elif self.iswork == 1:  # Включена, ждём выключения
            self.dt = round((utime.ticks_ms() - self.start) / 1000, 1)
            if self.dt >= self.time1:
                if self.time2 == 0:
                    self.stop_time()
                else:
                    self.dt = 0
                    self.iswork = 2
                    self.start = utime.ticks_ms()
                    s_off(self.number)
        elif self.iswork == 3:  # Розетка выключена, ждём включения, без цикла
            self.dt = round((utime.ticks_ms() - self.start) / 1000, 1)
            if self.dt >= self.time2:
                s_on(self.number)
                self.iswork = 0
                self.time2 = 0
                self.dt = 0


def do_connect():
    import network
    wlan = network.WLAN(network.STA_IF)
    if not wlan.isconnected():
        wlan.active(True)
        print('connecting to network...')
        wlan.connect(wlan_id, wlan_pass)
    print('network config:', wlan.ifconfig())


def s_on(number):
    p_list[number].value(0)
    if number == 0:
        number = 2
    elif number == 1:
        number = 3
    elif number == 2:
        number = 4
    elif number == 3:
        number = 5
    elif number == 4:
        number = 0
    elif number == 5:
        number = 1
    elif number == 6:
        number = 7
    elif number == 7:
        number = 6
    np[number] = (120, 153, 23)
    np.write()


def s_off(number):
    p_list[number].value(1)
    if number == 0:
        number = 2
    elif number == 1:
        number = 3
    elif number == 2:
        number = 4
    elif number == 3:
        number = 5
    elif number == 4:
        number = 0
    elif number == 5:
        number = 1
    elif number == 6:
        number = 7
    elif number == 7:
        number = 6
    np[number] = (0, 0, 0)
    np.write()


def time_to_seconds(time):
    # Преобразование времени в секунды
    if time == "":
        return 0
    try:
        a = time.split('%20')
        if len(a) == 1:
            time = int(a[0])
        elif len(a) == 2:
            time = int(a[0]) * 60 + int(a[1])
        elif len(a) == 3:
            time = int(a[0]) * 3600 + int(a[1]) * 60 + int(a[2])
        if time < 0:
            return -1
        print(time)
        return time
    except:
        return -1


def web_page(s_value_list, flag_except, use_socket, timer_list):
    s_value_list = str(s_value_list)
    time1 = timer_list[use_socket - 1].time1
    time2 = timer_list[use_socket - 1].time2
    if timer_list[use_socket - 1].iswork == 1:
        dt_t = time1 - (timer_list[use_socket - 1].dt).round()
        iswork = 1
    elif timer_list[use_socket - 1].iswork == 2:
        dt_t = (time2 - timer_list[use_socket - 1].dt).round()
        iswork = 0
    else:
        dt_t = 0
        iswork = 0
    html = '''<!DOCTYPE html>
<html><meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<head>
	<title>Smart Socket</title>
	<style type="text/css">
		h1 {font-family: algerian;color: white;font-size: 50px;text-align: center}
		h2 {color: white;font-family: calibri;font-size: 25px;text-align: center}
		p {color: white;font-family: calibri;font-size: 20px;}
		label {color: white;font-family: calibri;font-size: 20px;}
		.socketkorpus {float: left;width: 285px;height: 460px;background-color: white;border: solid 3px black;
		 position: relative; left: 80px;top:25px;
	border-radius: 30px;}
		.sb {width: 80px;height: 80px;cursor: pointer;border-radius: 50px;border: solid 2px black; position: 
		relative; top:20px;left:40px;margin: 0px;}
		.sbleft {width: 80px;height: 80px;cursor: pointer;border-radius: 50px;border: solid 2px black; position: 
		relative; top:20px;left:30px;margin: 0px;}
		.sl1 {width: 20px;height: 20px;border-radius: 5px;border: solid 2px black; position: relative; left:15px;}
		.sl2 {width: 20px;height: 20px;	border-radius: 5px;	border: solid 2px black; position: relative; left:55px;}
		.infodiv{float:left; width: 320px}
		.switch { position: relative; top:5px; display: inline-block; width: 40px; height: 25px;}
		.switch input {display:none;}
		.slider { position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0;  background-color: #ccc;}
		.slider:before { position: absolute; content: ""; height: 18px; width: 18px; left: 4px; bottom: 4px;
		 background-color: white;}
		input:checked + .slider { background-color: #7FFF00;}
		input:checked + .slider:before { -webkit-transform: translateX(14px); -ms-transform: translateX(14px);
		 transform: translateX(14px);}
		.button{position: relative;background-color:#256640; font-family: algerian;color: white;border-radius: 5px;
		border: 2px solid #06276F;font-size: 20px;
	float:right;right:120px;}
	</style>
</head>
<body style="background-image: linear-gradient(#00008B, #0969A2);">	
	<h1>Smart socket</h1><hr>
	<div style="float:left; width: 420px">
	<div class = "socketkorpus"><br>
			<button class="sl1" id="s8"> </button>
			<button class="sbleft" id="btn8" onclick="btn_number(8)"> </button>
			<button class="sb" id="btn4" onclick="btn_number(4)";></button>
			<button class="sl2" id="s4"> </button><br><br>
			<button class="sl1" id="s7"> </button>
			<button class="sbleft" id="btn7" onclick="btn_number(7)"></button>
			<button class="sb" id="btn3" onclick="btn_number(3)"></button>
			<button class="sl2" id="s3"> </button><br><br>
			<button class="sl1" id="s6"> </button>
			<button class="sbleft" id="btn6" onclick="btn_number(6)"></button>
			<button class="sb" id="btn2" onclick="btn_number(2)"> </button>
			<button class="sl2" id="s2"> </button><br><br>
			<button class="sl1" id="s5"> </button>
			<button class="sbleft" id="btn5" onclick="btn_number(5)"></button>
			<button class="sb" id="btn1" onclick="btn_number(1)"></button>
			<button class="sl2" id="s1"> </button><br><br></div></div>
	<div class = "infodiv">
		<h2 id="headlinename"></h2>
		<label class ="switch">
  			<input type ="checkbox" id="switcher" onclick="switchergetvalue()">
  			<span class ="slider"></span> 
		</label>
		<h2>Таймер</h2>
			<p id = "time_string1"></p>
			<p id = "time_string2"></p>
			<p id = "time_string3"></p>
			<button onclick="stoptimer()" class="button" style="background-color: #CD5C5C">Сбросить таймер</button> 
			<br><br>
		<h2>Установить таймер</h2><label>
				Время работы:
				<input type="text" autocomplete="off" id ="time1"><br><br>
				Время отдыха:
				<input type="text" autocomplete="off" id ="time2"><br><br></label>
			<center><input type="submit" id="btn" value="Подтвердить" class="button"></center></div>
	<div style="width:520px;float: left">
		<h2>Установить определённое время включения:</h2>
		<input type="datetime-local" id="date1" style="position: relative;left: 50px">
		<input type="submit" id="btnt1" value="Установить" class="button" onclick="btnt1()">
		<h2>Установить определённое время выключения:</h2>
		<input type="datetime-local" id="date2" style="position: relative;left: 50px">
		<input type="submit" id="btnt2" value="Установить" class="button" onclick="btnt2()">
	</div>
	<div style="clear: both"></div><br><br><br><br><br><br>
	<script type="text/javascript">
		let using_socket = %d;
		let masofs = %s;
		let timeL1 = %d;
		let timeL2 = %d;
		let dt_time = %d;
		let iswork = %d;
		let word_time;
		if (iswork == 1) {word_time = " до выключения";}
		else if (iswork == 0) {word_time = " до включения";}
		if (masofs[using_socket-1] == 1) {document.getElementById("switcher").checked = true}
		time_string1.textContent = 'Время работы: ' + timeL1;
		time_string2.textContent = 'Время отдыха: ' + timeL2;
		time_string3.textContent = 'Времени осталось ' + word_time + ": " + dt_time;
		let headname = ["Розетка №1", "Розетка №2", "Розетка №3", "Розетка №4", "Розетка №5", "Розетка №6",
		 "Розетка №7", "Розетка №8"];
		headlinename.textContent = headname[using_socket-1];
		if (using_socket == 1) {btn1.style.background="yellow";} else {btn1.style.background="#F5F5F5";}
		if (using_socket == 2) {btn2.style.background="yellow";} else {btn2.style.background="#F5F5F5";}
		if (using_socket == 3) {btn3.style.background="yellow";} else {btn3.style.background="#F5F5F5";}
		if (using_socket == 4) {btn4.style.background="yellow";} else {btn4.style.background="#F5F5F5";}
		if (using_socket == 5) {btn5.style.background="yellow";} else {btn5.style.background="#F5F5F5";}
		if (using_socket == 6) {btn6.style.background="yellow";} else {btn6.style.background="#F5F5F5";}
		if (using_socket == 7) {btn7.style.background="yellow";} else {btn7.style.background="#F5F5F5";}
		if (using_socket == 8) {btn8.style.background="yellow";} else {btn8.style.background="#F5F5F5";}
		let colorN =[];
		let i = 0;
		while (i < 8)
  		{    if (masofs[i]) {colorN[i] = "red";} else {colorN[i] = "green";}
  		     i++;      }
		s1.style.background = colorN[0];
		s2.style.background = colorN[1];
		s3.style.background = colorN[2];
		s4.style.background = colorN[3];
		s5.style.background = colorN[4];
		s6.style.background = colorN[5];
		s7.style.background = colorN[6];
		s8.style.background = colorN[7];
		let text_link ="http://192.168.43.12"
		async function btnt1() 
			{
				let date1 = document.querySelector("#date1").value;
				document.location.href = text_link + "/?dateOn" + "&" + date1 + "&" ;
			}
		async function btnt2() 
			{
				let date2 = document.querySelector("#date1").value;
				document.location.href = text_link + "/?dateOff"+ "&" + date2 + "&" ;
			}
		async function btn_number(number) 
			{
				document.location.href = text_link + "/?use" + number;
			}
		async function switchergetvalue()
			{
				let switcher_value = document.getElementById("switcher").checked;
				document.location.href = text_link + "/?"+ switcher_value;
			}
		let btn = document.querySelector("#btn");
		btn.addEventListener("click", sendtime);
		async function sendtime() 
				{
					let time1 = document.querySelector("#time1").value;
					let time2 = document.querySelector("#time2").value;
					document.location.href = text_link + "/?timeset&" + time1 + "&" + time2 + "&";
				}</script>
	<script type="text/javascript">
		timer = setInterval(function () {
		--dt_time
		time_string3.textContent = 'Времени осталось' + word_time + ": "+ dt_time;
		if (dt_time <= 0){clearInterval(timer)}
		}, 1000)
	</script>
	</body>''' % (use_socket, s_value_list, time1, time2, dt_t, iswork)
    return html


timer1 = Timer(0)
timer2 = Timer(1)
timer3 = Timer(2)
timer4 = Timer(3)
timer5 = Timer(4)
timer6 = Timer(5)
timer7 = Timer(6)
timer8 = Timer(7)
timer_list = [timer1, timer2, timer3, timer4, timer5, timer6, timer7, timer8]
time_timer1, time_timer2 = 0, 0  # секунды для работы/отдыха

do_connect()

use_socket = 0

flag_except = False

while True:
    '''do_connect()'''
    for i in range(0, 8):
        if p_list[i].value():
            s_value_list[i] = 0
        else:
            s_value_list[i] = 1
    for i in timer_list:
        i.chek_timer()
    for i in range(0, 8):
        if knopka_list[i].value() and not s_value_list[i]:
            s_on(i)
        if knopka_list[i].value() and s_value_list[i]:
            s_off(i)
    try:
        s.settimeout(0.5)
        conn, addr = s.accept()
    except OSError:
        continue
    #  Начало генерации веб страницы
    else:
        s.settimeout(None)
        print('Got a connection from %s' % str(addr))
        while True:
            try:
                request = conn.recv(1024)
                break
            except OSError:
                pass
        request = str(request)
        print('Content = %s' % request)
        flag_except = False

        use1, use5 = request.find('/?use1'), request.find('/?use5')
        use2, use6 = request.find('/?use2'), request.find('/?use6')
        use3, use7 = request.find('/?use3'), request.find('/?use7')
        use4, use8 = request.find('/?use4'), request.find('/?use8')
        get_time = request.find('/?timeset')
        sock_on = request.find('/?true')
        sock_off = request.find('/?false')
        date_on = request.find('/?dateOn')
        date_off = request.find('/?dateOf')

        if use1 == 6:
            use_socket = 1
        elif use2 == 6:
            use_socket = 2
        elif use3 == 6:
            use_socket = 3
        elif use4 == 6:
            use_socket = 4
        elif use5 == 6:
            use_socket = 5
        elif use6 == 6:
            use_socket = 6
        elif use7 == 6:
            use_socket = 7
        elif use8 == 6:
            use_socket = 8

        elif get_time == 6:
            time_str = request.split('&')
            print(time_str)
            time_timer1 = time_to_seconds(time_str[1])
            time_timer2 = time_to_seconds(time_str[2])
            if (time_timer1 < 0) or (time_timer2 < 0):
                flag_except = True
            else:
                timer_list[use_socket - 1].settimer()
        elif sock_on == 6:
            s_on(use_socket - 1)
        elif sock_off == 6:
            s_off(use_socket - 1)

        elif date_on == 6:
            date_mes = request.split('&')
            struct_time = time.strptime(date_mes[1], '%Y-%m-%dT%H:%M')
            d1 = utime.mktime(struct_time)
            time_timer1 = 0
            time_timer2 = round(d1 - utime.time())
            if time_timer2 < 0:
                flag_except = True
            else:
                timer_list[use_socket - 1].settimer()
            time_timer1 = 0
            time_timer2 = 0
        elif date_off == 6:
            date_mes = request.split('&')
            struct_time = time.strptime(date_mes[1], '%Y-%m-%dT%H:%M')
            d1 = utime.mktime(struct_time)
            time_timer1 = round(d1 - utime.time())
            time_timer2 = 0
            if time_timer1 < 0:
                flag_except = True
            else:
                timer_list[use_socket - 1].settimer()
            time_timer1 = 0
            time_timer2 = 0

        for i in range(0, 8):
            if p_list[i].value():
                s_value_list[i] = 0
            else:
                s_value_list[i] = 1

        conn.send('HTTP/1.1 200 OK\n')
        conn.send('Content-Type: text/html\n')
        conn.send('Connection: close\n\n')
        response = web_page(s_value_list, flag_except, use_socket, timer_list)

        try:
            conn.sendall(response)
        except OSError:
            print('error')
        conn.close()
