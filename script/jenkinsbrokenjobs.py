import urllib.request, json, smtplib, os
from datetime import datetime

base = "D:/sites/jenkinsbrokenjobs/"
nonblue = json.load(open(base + "nonblue.json"))
alerted = json.load(open(base + "alerted.json"))
servers = ["jenkins_server1", "jenkins_server2"]

def sendEmail(name, color, text):
   FROM = 'from@domain.com'
   TO  = 'user@domain.com'
   SUBJECT = name + " has status: " + color.upper()
   message = """\From: %s\nTo: %s\nSubject: %s\n\n%s """ % (FROM, TO, SUBJECT, text)
   server = smtplib.SMTP('smtpserver.local', 25)
   server.sendmail(FROM, TO, message)
   server.quit()
   
def jobExists(json, name):
   for job in json:
      if job["name"] == name:
         return True
   return False

def isNonBlueTenMinutes(name):
   for job in nonblue:
      if job["name"] == name:
         if job["minutes"] > 9:
            return True
         else:
            return False
   
def addJob(json, name):
   found = False
   for job in json:
      if job["name"] == name:
         minutes = job["minutes"]
         minutes += 1
         job["minutes"] = minutes
         found = True
   if not found:
      json.append({"name": name, "minutes": 1})


def removeJob(json, name):
   index = 0
   for job in json:
      if job["name"] == name:
         json.pop(index)
      index += 1
   
def addMinute(name):
   addJob(nonblue, name)

def log(name, color):
   now = str(datetime.now()).split('.')[0]
   with open(base + "jbjlog.txt", "a") as logfile:
      logfile.write(str(now + " - " + name + " - " + color + "\n"))

for server in servers:
   json_file = "D:/scripts/jenkinsbrokenjobs/" + server
   response = urllib.request.urlretrieve("http://" + server + "/api/json", json_file)
   json_data = open(json_file)
   data = json.load(json_data)
   jobs = data['jobs']

   for job in jobs:
      if 'color' in job:
         color = job['color']
      else:
         continue
      name = job['name']
      url = job['url']
      
      if color == "blue" or color == "blue_anime":
         if jobExists(nonblue, name):
            removeJob(nonblue, name)
         if jobExists(alerted, name):
            sendEmail(name, color, "It used to be non-blue status")
            removeJob(alerted, name)
            log(name, color)
      else:
         if jobExists(nonblue, name):
            addMinute(name)
            if isNonBlueTenMinutes(name):
               if jobExists(alerted, name):
                  pass
               else:
                  sendEmail(name, color, "You better check into it: " + url)
                  addJob(alerted, name)
                  log(name, color)
         else:
            addJob(nonblue, name)
   json_data.close()
with open(base + "nonblue.json", "w") as outfile:
   json.dump(nonblue, outfile)
with open(base + "alerted.json", "w") as outfile:
   json.dump(alerted, outfile)