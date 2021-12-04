import time
import machine
from machine import Pin
import utime
import socket
import neopixel
import app.wifimgr as wifimgr
import app.ntp as ntp
import gc

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



ntp.settime()
print(machine.RTC().datetime())


def check_updates():
    from app.ota_updater import OTAUpdater
    otaUpdater = OTAUpdater('https://github.com/xilyam/sm-sock', github_src_dir='app', main_dir='app')
    hasUpdated = otaUpdater.install_update_if_available()
    if hasUpdated:
        print("Finally")
        machine.reset()
    else:
        del otaUpdater
        gc.collect()


check_updates()
p1 = Pin(13, Pin.OUT)
p1.off()
p2 = Pin(18, Pin.OUT)
p2.off()
p3 = Pin(19, Pin.OUT)
p3.off()
p4 = Pin(27, Pin.OUT)
p4.off()
p5 = Pin(26, Pin.OUT)
p5.off()
p6 = Pin(25, Pin.OUT)
p6.off()
p7 = Pin(33, Pin.OUT)
p7.off()
p8 = Pin(32, Pin.OUT)
p8.off()
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
        self.time3 = 0
        self.number = number
        self.flag3 = False
        self.iswork = 0
        self.d1 = time.time()

    def set_timer(self, time1, time2, type_of_timer=1, time3=0):
        self.start = utime.ticks_ms()
        self.stop_time()
        self.time1 = time1
        self.time2 = time2
        self.time3 = time3
        if type_of_timer == 1:
            self.iswork = 1
            if self.time1 == 0:
                s_on(self.number)
                self.iswork = 2
        elif type_of_timer == 2:
            self.iswork = 3
            if self.time1 == 0:
                s_off(self.number)
                self.iswork = 4

        elif type_of_timer == 3:
            self.flag3 = True
            self.iswork = 5
            if self.time3 == 0:
                s_on(self.number)
                self.iswork = 6

    def set_date(self, d1, type):
        self.d1 = d1
        if type == 1:
            self.iswork = 7
        if type == 2:
            self.iswork = 8


    def stop_time(self):
        '''Выключаем таймер'''
        self.dt = 0
        self.time1 = 0
        self.time2 = 0
        self.time3 = 0
        self.iswork = 0
        d1 = 0

    def chek_timer(self):
        '''Проверяем, истекло ли время'''
        if self.iswork == 1:  # Розетка выключена, ждём включения
            self.dt = self.time1 - round((utime.ticks_ms() - self.start) / 1000, 1)
            if self.dt <= 0 :
                s_on(self.number)
                self.start = utime.ticks_ms()
                self.iswork = 2
                self.dt = 0
        elif self.iswork == 2:  # Розетка выключена, ждём выключения
            self.dt =self.time2 - round((utime.ticks_ms() - self.start) / 1000, 1)
            if self.dt <= 0:
                s_off(self.number)
                self.stop_time()
        elif self.iswork == 3:  # Розетка включена, ждём выключения
            self.dt = self.time1 - round((utime.ticks_ms() - self.start) / 1000, 1)
            if self.dt <= 0:
                s_off(self.number)
                self.iswork = 4
                self.dt = 0
                self.start = utime.ticks_ms()
        elif self.iswork == 4:  # Розетка выключена, ждём включения
            self.dt =self.time2 - round((utime.ticks_ms() - self.start) / 1000, 1)
            if self.dt <= 0:
                s_on(self.number)
                self.stop_time()
        elif self.iswork == 5:  # Розетка выключена, ждём включения
            self.dt =self.time3 - round((utime.ticks_ms() - self.start) / 1000, 1)
            if self.dt <= 0:
                s_on(self.number)
                self.start = utime.ticks_ms()
                self.iswork = 6
                self.dt = 0
        elif self.iswork == 6:  # Цикл
            if self.flag3:
                self.dt = self.time1 - round((utime.ticks_ms() - self.start) / 1000, 1)
                if self.dt <= 0:
                    s_off(self.number)
                    self.start = utime.ticks_ms()
                    self.dt = 0
                    self.flag3 = False
            elif self.flag3 == False:
                self.dt = self.time2 - round((utime.ticks_ms() - self.start) / 1000, 1)
                if self.dt <= 0:
                    s_on(self.number)
                    self.start = utime.ticks_ms()
                    self.dt = 0
                    self.flag3 = True
        elif self.iswork == 7:
            self.dt = self.d1 - time.time()
            if self.dt <= 0:
                s_on(self.number)
                self.stop_time()
        elif self.iswork == 8:
            self.dt = self.d1 - time.time()
            if self.dt <= 0:
                s_off(self.number)
                self.stop_time()



def do_connect():
    import network
    wlan = network.WLAN(network.STA_IF)
    if not wlan.isconnected():
        wlan.active(True)
        print('connecting to network...')
        wlan.connect(wlan_id, wlan_pass)
    print('network config:', wlan.ifconfig())


def s_on(number):
    p_list[number].value(1)
    if number == 0:
        number = 2
    elif number == 1:
        number = 3
    elif number == 2:
        number = 4
    elif number == 3:
        number = 5
    elif number == 5:
        number = 0
    elif number == 4:
        number = 1
    elif number == 6:
        number = 7
    elif number == 7:
        number = 6
    np[number] = (0, 0, 0)
    np.write()


def s_off(number):
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
        number = 1
    elif number == 5:
        number = 0
    elif number == 6:
        number = 7
    elif number == 7:
        number = 6
    np[number] = (120, 153, 23)
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
        print("time: ", time)
        return time
    except:
        return -1


def web_page(s_value_list, flag_except, use_socket, timer_list):
    s_value_list = str(s_value_list)
    isw = timer_list[use_socket - 1].iswork
    flag3 = timer_list[use_socket - 1].flag3
    if isw == 0:
        type_work = 0
        dt_t = 0
    elif (isw == 1) or (isw == 4) or (isw == 5) or ((isw == 6) and not flag3) or (isw == 7):
        dt_t = timer_list[use_socket - 1].dt
        type_work = 1
    else:
        dt_t = timer_list[use_socket - 1].dt
        type_work = 2
    gc.collect()
    html = """<!DOCTYPE html>
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
		.switch { position: relative; top:5px; display: inline-block; width: 40px; height: 25px;left: 20px}
		.switch input {display:none;}
		.slider { position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0;  background-color: #ccc;}
		.slider:before { position: absolute; content: ""; height: 18px; width: 18px; left: 4px; bottom: 4px;
		 background-color: white;}
		input:checked + .slider { background-color: #7FFF00;}
		input:checked + .slider:before { -webkit-transform: translateX(14px); -ms-transform: translateX(14px);
		 transform: translateX(14px);}
		.button{position: relative;background-color:#256640; font-family: algerian;color: white;border-radius: 5px;
		border: 2px solid #06276F;font-size: 18px;}
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
		<p>Состояние: <label class ="switch"> 
  			<input type ="checkbox" id="switcher" onclick="switchergetvalue()">
  			<span class ="slider"></span></label></p>
		<h2>Таймер</h2>
			<p id = "time_string1"></p>
			<p id = "time_string2"></p>
			<p id = "time_string3"></p>
			<p id = "time_string4"></p>
			<p id = "time_string5"></p>
			<button onclick="stoptimer()" class="button" style="background-color: #CD5C5C">Сбросить таймер</button> 
			<br><br></div>
		
	<div style="float: left">
		<h2>Установить таймер</h2><label>
		<button onclick="show_filds(1)" class="button" style="background-color: #ffffff">0</button> Включить на время<br>
		<button onclick="show_filds(2)" class="button" style="background-color: #ffffff">0</button> Выключить на время<br>
		<button onclick="show_filds(3)" class="button" style="background-color: #ffffff">0</button> Цикл<br>
		<button onclick="show_filds(4)" class="button" style="background-color: #ffffff">0</button> Установить дату включения<br>
		<button onclick="show_filds(5)" class="button" style="background-color: #ffffff">0</button> Установить дату выключения<br>
		<p id = "type_timer1"></p> 
		<input type="text" autocomplete="off" id ="time1" style="width: 60px"><input type="datetime-local" id="date1" style="position: relative;left:10px;top:5px">
		<p id = "type_timer2"></p>
		<input type="text" autocomplete="off" id ="time2" style="width: 60px">
		<p id = "type_timer3"></p>
		<input type="text" autocomplete="off" id ="time3" style="width: 60px">
				
			<center><input type="submit" id="btn" value="Подтвердить" class="button"></center></div></label>
	
	<div style="clear: both"></div><br><br><br><br><br><br><br><br>
	<script type="text/javascript">
		let type_of_timer = 1;
		let using_socket = %d;
		let masofs = %s;
		let dt_time = %d;
		let iswork = %d;
		let word_time
		if (iswork == 1) {word_time = "Времени до включения: ";}
		else if (iswork == 2) {word_time = "Времени до выключения: ";}
		if (masofs[using_socket-1] == 1) {document.getElementById("switcher").checked = true}
		if (iswork == 0) {time_string1.textContent = "";} else {time_string1.textContent = word_time + dt_time;}
		time_string2.textContent;
		time_string3.textContent;
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
  		{    if (masofs[i]) {colorN[i] ="green" ;} else {colorN[i] = "red";}
  		     i++;      }
		s1.style.background = colorN[0];
		s2.style.background = colorN[1];
		s3.style.background = colorN[2];
		s4.style.background = colorN[3];
		s5.style.background = colorN[4];
		s6.style.background = colorN[5];
		s7.style.background = colorN[6];
		s8.style.background = colorN[7];
		let text_link ="http://192.168.43.187"
		async function show_filds(number){
			if (number == 1) {
				type_of_timer = 1
				type_timer1.textContent = "Времени до включения:";
				type_timer2.textContent = "Время работы:";
				type_timer3.textContent = "";
				date1.style.display = "none";
				time2.style.display = "block";
				time3.style.display = "none";} 
			if (number == 2) {
				type_of_timer = 2
				type_timer1.textContent = "Времени до выключения:";
				type_timer2.textContent = "Время отдыха:";
				type_timer3.textContent = "";
				date1.style.display = "none";
				time2.style.display = "block";
				time3.style.display = "none";} 
			if (number == 3) {
				type_of_timer = 3
				type_timer1.textContent = "Время работы:";
				type_timer2.textContent = "Время отдыха:";
				type_timer3.textContent = "Времени до начала цикла:";
				date1.style.display = "none";
				time2.style.display = "block";
				time3.style.display = "block";} 
			if (number == 4) {
				type_of_timer = 4
				type_timer1.textContent = "Дата включения:";
				type_timer2.textContent = "";
				type_timer3.textContent = "";
				date1.style.display = "block";
				time2.style.display = "none";
				time3.style.display = "none";} 
			if (number == 5) {
				type_of_timer = 5
				type_timer1.textContent = "Дата выключения:";
				type_timer2.textContent = "";
				type_timer3.textContent = "";
				date1.style.display = "block";
				time2.style.display = "none";
				time3.style.display = "none";} 
			if (number == 6) {
				type_of_timer = 6
				type_timer1.textContent = "Время включения:";
				type_timer2.textContent = "Время выключения:";
				type_timer3.textContent = "";
				date1.style.display = "none";
				time2.style.display = "block";
				time3.style.display = "none";}} 
		show_filds(1);
		async function btn_number(number) 
			{
				document.location.href = text_link + "/?use" + number;
			}
		async function switchergetvalue()
			{
				let switcher_value = document.getElementById("switcher").checked;
				document.location.href = text_link + "/?"+ switcher_value;
			}
		async function stoptimer(){
			document.location.href = text_link + "/?reset"}
		let btn = document.querySelector("#btn");
		btn.addEventListener("click", sendtime);
		async function sendtime() 
				{	let time1 = document.querySelector("#time1").value;
					let time2 = document.querySelector("#time2").value;
					if (type_of_timer == 1) {document.location.href = text_link + "/?time1&" + time1 + "&" + time2 + "&";}
					if (type_of_timer == 2) {document.location.href = text_link + "/?time2&" + time1 + "&" + time2 + "&";}
					if (type_of_timer == 3) {
						let time3 = document.querySelector("#time3").value;
						document.location.href = text_link + "/?time3&" + time1 + "&" + time2 + "&" + time3 + "&";}
					if (type_of_timer == 4) {
					    if (time1 == "") {time1 = "00";}
						let date1 = document.querySelector("#date1").value;
						let date_S = Date.parse(date1+":"+ time1)/1000 - 946684800;
						document.location.href = text_link + "/?time4&" + date_S + "&";}
					if (type_of_timer == 5) {
					    if (time1 == "") {time1 = "00";}
						let date1 = document.querySelector("#date1").value;
						let date_S = Date.parse(date1+":"+ time1)/1000 - 946684800;
						document.location.href = text_link + "/?time5&" + date_S + "&";}}</script>
	<script type="text/javascript">
		timer = setInterval(function () {
		--dt_time
		if (dt_time < 0){clearInterval(timer)}
		else{time_string1.textContent = word_time + dt_time;}}, 1000)
	</script>
	</body>""" % (use_socket, s_value_list, dt_t, type_work)
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
print("Start working")
s.settimeout(0.5)

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
        get_time1, get_time2 = request.find('/?time1'), request.find('/?time2')
        get_time3, get_time4 = request.find('/?time3'), request.find('/?time4')
        get_time5, get_time6 = request.find('/?time5'), request.find('/?time6')
        sock_on = request.find('/?true')
        sock_off = request.find('/?false')
        time_reset = request.find('/?reset')

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

        elif get_time1 == 6 or get_time2 == 6:
            time_str = request.split('&')
            time_timer1 = time_to_seconds(time_str[1])
            time_timer2 = time_to_seconds(time_str[2])
            if (time_timer1 < 0) or (time_timer2 < 0):
                flag_except = True
            else:
                if get_time1 == 6:
                    timer_list[use_socket - 1].set_timer(time_timer1, time_timer2, 1)
                else:
                    timer_list[use_socket - 1].set_timer(time_timer1, time_timer2, 2)
        elif get_time3 == 6:
            time_str = request.split('&')
            time_timer1 = time_to_seconds(time_str[1])
            time_timer2 = time_to_seconds(time_str[2])
            time_timer3 = time_to_seconds(time_str[3])
            if (time_timer1 < 0) or (time_timer2 < 0) or (time_timer3 < 0):
                flag_except = True
            else:
                timer_list[use_socket - 1].set_timer(time_timer1, time_timer2, 3, time_timer3)
        elif sock_on == 6:
            s_on(use_socket - 1)
        elif sock_off == 6:
            s_off(use_socket - 1)

        elif get_time4 == 6:
            date_mes = request.split('&')
            date = time_to_seconds(date_mes[1])
            if date <= 0:
                flag_except = True
            else:
                timer_list[use_socket - 1].set_date(date, 1)
        elif get_time5 == 6:
            date_mes = request.split('&')
            date = time_to_seconds(date_mes[1])
            if date <= 0:
                flag_except = True
            else:
                timer_list[use_socket - 1].set_date(date, 2)
        elif time_reset == 6:
            timer_list[use_socket-1].stop_time()

        for i in range(0, 8):
            if p_list[i].value():
                s_value_list[i] = 0
            else:
                s_value_list[i] = 1

        conn.send('HTTP/1.1 200 OK\n')
        conn.send('Content-Type: text/html\n')
        conn.send('Connection: close\n\n')
        response = web_page(s_value_list, flag_except, use_socket, timer_list)
        gc.collect()
        try:
            conn.sendall(response)
        except OSError:
            print('error')

        conn.close()
