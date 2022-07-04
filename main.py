from google.colab import auth

auth.authenticate_user()
import gspread
from google.auth import default
from oauth2client.client import GoogleCredentials
import random

creds, _ = default()

#gc = gspread.authorize(GoogleCredentials.get_application_default())
gc = gspread.authorize(creds)

form_name = "Inscrições para a Primeira Maratona Interna de 2022 (respostas)"
arquivo_ = gc.open(form_name)
arquivo = arquivo_.sheet1

passwordSize = 6
should_send_email = True

site_number = 1
user_type = 'team'
user_enable = "t"

udesc_number_range = range(2000, 2099)
extern_number_range = range(3000, 3099)
extra_number_range = range(2100, 2199)
ufsc_number_range = range(3100, 3199)
udesc_user_idx = 0
extern_user_idx = 0

boca_fields = { 'usernumber', 'usersitenumber', 'username', 'userpassword', 'usertype', 'userfullname', 'userdesc', 'userenabled', 'usermultilogin'}

#Gera senha aleatoria
def getPassword(tm=6, seed=0):
  random.seed(seed)
  return str(int(random.random() * (10**tm)))

class User():
  def __init__(self, fields):
    for (k, v) in fields.items():
      setattr(self, k, v)
  def __str__(self):
    return self.userfullname
  def boca_str(self):
    return ''.join(f"{f}={getattr(self, f)}\n" for f in boca_fields)
  def __lt__(self, other):
    return self.usernumber < other.usernumber
  
  
  def create_udesc_user(line):
  global udesc_user_idx
  nbr = udesc_number_range[udesc_user_idx]
  user = User({
    'answered_at': str(line[0]),
    'usernumber': nbr,
    'usersitenumber': site_number,
    'username': f"time{udesc_user_idx}",
    'userpassword': getPassword(passwordSize, nbr),
    'usertype': user_type,
    'userfullname': line[1],
    'userdesc': line[1],
    'userenabled': user_enable,
    'usermultilogin': 't',
    'is_udesc': True,
    'users': [s for s in line[2:5] if s],
    'emails': [s for s in line[5:8] if s],
    'cpfs': [s for s in line[9:12] if s],
    'cursos': [s for s in line[12:15] if s],
    'semestres': [s for s in line[15:18] if s],
  })
  udesc_user_idx += 1
  return user

def create_extern_user(line):
  global extern_user_idx
  nbr = extern_number_range[extern_user_idx]
  user = User({
    'answered_at': str(line[0]),
    'usernumber': nbr,
    'usersitenumber': site_number,
    'username': f"externo{extern_user_idx}",
    'userpassword': getPassword(passwordSize, nbr),
    'usertype': user_type,
    'userfullname': line[1],
    'userdesc': line[1],
    'userenabled': user_enable,
    'usermultilogin': 't',
    'is_udesc': False,
    'users': [s for s in line[2:5] if s],
    'emails': [s for s in line[5:8] if s],
  })
  extern_user_idx += 1
  return user

def create_users(lines):
  users = []
  for line in lines:
    is_udesc = (line[8] == "Sim")
    user = create_udesc_user(line) if is_udesc else create_extern_user(line)
    users.append(user)
  return users

lines = arquivo.get_all_values()[1:]
users = create_users(lines)

def create_extras(quantity):
  for i in range(quantity):
    nbr = extra_number_range[i]
    user = User({
      'answered_at': None,
      'usernumber': nbr,
      'usersitenumber': site_number,
      'username': f"extra{i}",
      'userpassword': getPassword(passwordSize, nbr),
      'usertype': user_type,
      'userfullname': f"extra{i}",
      'userdesc': f"extra{i}",
      'userenabled': user_enable,
      'usermultilogin': 't',
      'is_udesc': False,
      'users': [],
      'emails': [],
    })
    users.append(user)

create_extras(10)

def create_ufsc(quantity):
  for i in range(quantity):
    nbr = ufsc_number_range[i]
    user = User({
      'answered_at': None,
      'usernumber': nbr,
      'usersitenumber': site_number,
      'username': f"ufsc{i}",
      'userpassword': getPassword(passwordSize, nbr),
      'usertype': user_type,
      'userfullname': f"ufsc{i}",
      'userdesc': f"ufsc{i}",
      'userenabled': user_enable,
      'usermultilogin': 't',
      'is_udesc': False,
      'users': [],
      'emails': [],
    })
    users.append(user)

create_ufsc(10)

users.sort()

#-----------------------------------------------------------------------------------------------
#GERA OS EMAIL

import os 
import smtplib
from email.message import EmailMessage

EMAIL_ADDRESS = 'bruteudesc@gmail.com'
EMAIL_PASSWORD = 'ledbensaiysddfkc'

smtp = smtplib.SMTP_SSL('smtp.gmail.com', 465)
smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)

def send_email(username, password, email):
  html= """
<!DOCTYPE html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Your HTML Title</title>
  <style>
* {padding: 0;margin: 0;position: relative;font-family: 'Google Sans',Roboto,RobotoDraft,Helvetica,Arial,sans-serif; user-select:none}
  body{width:100%;height:100%;overflow:hidden}
  img {
  width: 100%;
}
.b-main {
    margin: 0 auto;
    width: 500px;
    padding: 24px 30px;
    border: 1px solid #757575;
    border-radius: 10px;
}

.b-body {
    margin: 24px 0;
    border-top: 1px solid #d2d2d2;
    padding: 24px 0 0;
}
.b-footer {
  margin-top:50px;
}

.b-title {
  text-align: center;
  font-weight: 600;
  text-transform: uppercase;
  font-size: 24px;
}

.b-fotter-down {
  text-align: center;
  font-size: 12px;
}
  
  .b-top {
    padding-top: 0px;
}
.b-msg {
    text-align: center;
    font-size: 12px;
}
.b-login {
    padding: 10px;
    margin: 20px auto;
    max-width: 300px;
    display: grid;
    grid-template-columns: 50% 50%;
    
}
.b-logo {
    width: 65px;
    height: 90px;
    position: relative;
    margin: 0 auto;
}
.b-login-user, .b-login-pass {
    border: 1px dashed gray;
    margin: 10px;
    text-align: center;
    padding: 15px;
    border-radius: 40px;
}


.b-login-title {
    position: absolute;
    top: -10px;
    left: 50%;
    font-size: 12px;
    background: white;
    transform: translate(-50%);
    padding: 0 5px;
    color: #3e3e3e;
}
.b-login-data {
    user-select: text;
}

  </style>
  <body>
  <div class='b-main'>
    
    <div class='b-top'>
      <div class='b-logo'><img src='https://imageshack.com/i/pmrCucU1p'></div>
      <div class='b-title' style="padding: 10px 0 0;"> I maratona interna 2022</div>

    </div>
  <div class='b-body'>
    <div class='b-msg'>
      Agradecemos seu interesse em inscrever-se na primeira maratona interna da UDESC em 2022!!!
      Gostaríamos de lembrar que a competição é dia <b>25/06</b> às <b>14:00</b> no site <a href='http://200.19.107.69/boca/' target="_blank">http://200.19.107.69/boca/</a>.
      É de extrema importância testar o ambiente no warm-up que acontecerá dia <b>25/06</b> às <b>10:00</b>.<br>
      Estamos enviando seu login e senha<br>
    </div>
    <div class='b-login'>
      <div class='b-login-user'>
        <div class='b-login-title'>usuário</div>
        <div class='b-login-data'>""" + username + """</div>
      </div>
      <div class='b-login-pass'>
    <div class='b-login-title'>senha</div>
        <div class='b-login-data'>""" + password + """</div>
      </div>
    </div>
    <div class='b-msg'>
      Mais informações em<br>
      <a href='https://bruteudesc.com/domestica-2022/'>https://bruteudesc.com/domestica-2022/</a>
    <div class='b-msg'>
    </div>
    <div class='b-footer'>
      <div class='b-fotter-down'><a href="https://www.bruteudesc.com/">BRUTE</a><p>Competitive Programming</p></div>
    </div>
  <div>
  </body>
</html>"""

  msg = EmailMessage()
  msg["From"] = EMAIL_ADDRESS
  msg["To"] = email
  msg['Subject'] = "UDESC - I Maratona Interna de 2022"
  msg.set_content('')
  msg.add_alternative(html, subtype='html')

  #Enviar um email
  smtp.send_message(msg)

if should_send_email:
  for user in users:
    for email in user.emails:
      email = email.strip()
      print(email)
      send_email(user.username, user.userpassword, email)
      
# CREATE BOCA USER LIST

boca_users = "[user]\n" + "\n".join(u.boca_str() for u in users)
open('user', 'w').write(boca_users)

# CREATE LIST TO PRINT

text = [f"""userfullname = {u.userfullname}
username     = {u.username}
userpassword = {u.userpassword}
""" for u in users if u.is_udesc]
text = "\n".join(text)
# print(text)
open('user_list', 'w').write(text)

# CREATE UFSC LIST

text = [f"""userfullname = {u.userfullname}
username     = {u.username}
userpassword = {u.userpassword}
""" for u in users if u.username.startswith("ufsc")]
text = "\n".join(text)
# print(text)
open('user_ufsc_list', 'w').write(text)

# LISTA PARA GUARITA

ziped = [zip(u.users, u.cpfs) for u in users if u.is_udesc]
alunos = [t for ts in ziped for t in ts]

text = [f"nome = {t[0]}\ncpf  = {t[1]}\n" for t in alunos]
text = '\n'.join(text)

# print(text)
open('lista_guarita', 'w').write(text)
