#!/usr/bin/env python

import smtplib
import subprocess
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def run_command(cmd):
    proc = subprocess.Popen([cmd], stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    out = str(out).replace('\n','<br>')
    err = str(err).replace('\n','<br>')
    return out, err

def send_email(process, error_message, sender = 'dosenet@dosenet'):
    stopped = process

    try:
        geojson, geojson_err = run_command("stat ~/output.geojson")
    except Exception as e:
        geojson, geojson_err = ("Running on a RPi, ignore this")
    processes, processer_err = run_command("ps aux | grep python | grep -v grep")
    crontab, crontab_err = run_command("crontab -l")

    receivers = 'ucbdosenet@gmail.com'
    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "DoseNet automated message"
    msg['From'] = sender
    msg['To'] = receivers

    text = """Process: {}\n Error message: {}\n Navrit Bal.""".format(stopped, error_message)
    html = """\
<html>
<head></head>
<body>
<h1> Some DoseNet process just stopped! :( </h1>
            <h2> Which process stopped? </h2>
                <code style="background-color: #f8f8ff; padding-right: 20px; padding-left: 20px; padding-bottom: 7px; border-radius: 10px; font-size: 1.5em; margin: 20px auto; border: 2px solid #8ac007;">{}</code>
                <br><br><samp style="background-color: #f8f8ff; border-radius: 10px;">{}</samp>
            <p> Include running/last run process list. </p>
            <br><h2> GeoJSON file properties </h2>
                <code style="background-color: #f8f8ff; padding-right: 20px; padding-left: 20px; padding-bottom: 7px; border-radius: 10px; font-size: 1.5em; margin: 20px auto; border: 2px solid #8ac007;"> stat ~/output.geojson </code>
                <br><br><samp style="background-color: #f8f8ff; border-radius: 10px;">{}</samp>
            <h2> Which Python processes are running </h2>
                <code style="background-color: #f8f8ff; padding-right: 20px; padding-left: 20px; padding-bottom: 7px; border-radius: 10px; font-size: 1.5em; margin: 20px auto; border: 2px solid #8ac007;"> ps aux | grep python | grep -v grep </code>
                <br><br><samp style="background-color: #f8f8ff; border-radius: 10px;">{}</samp>
            <h2> Crontab entries </h2>
                <code style="background-color: #f8f8ff; padding-right: 20px; padding-left: 20px; padding-bottom: 7px; border-radius: 10px; font-size: 1.5em; margin: 20px auto; border: 2px solid #8ac007;"> crontab -l </code>
                <br><br><samp style="background-color: #f8f8ff; border-radius: 10px;">{}</samp>
            <br><p> Navrit Bal </p>
            <p> Maker of DoseNet. </p>
</body>
</html>""".format(stopped, error_message, geojson, processes, crontab)

    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')
    msg.attach(part1)
    msg.attach(part2)
    print msg.as_string()

    try:
       smtpObj = smtplib.SMTP('localhost')
       smtpObj.sendmail(sender, receivers.split(","), msg.as_string())
       smtpObj.quit()
       print "Successfully sent email"
    except Exception as e:
       print str(e)
       print "Error: unable to send email"

if __name__ == "__main__":
    send_email(process = "Test send_email function", error_message = "... Testing email script ...")


"""
PREPROCESSED HTML - EDIT HERE THEN USE http://premailer.dialect.ca/ to convert css to inline

    <style type="text/css">
        samp {
            background-color: #f8f8ff;
            border-radius: 10px;
        },
        code {
            background-color: #f8f8ff;
            margin: 20px auto 20px auto;
            padding-right: 20px;
            padding-left: 20px;
            padding-bottom: 7px;
            border: 2px solid #8AC007;
            border-radius: 10px;
            font-size: 1.5em;
        }
    </style>
        <h1> Some DoseNet process just stopped! :( </h1>
            <h2> Which process stopped? </h2>
                <code>{}</code>
                <br>
                <br>
                <samp>{}</samp>
            <p> Include running/last run process list. </p>
            <br>
            <h2> GeoJSON file properties </h2>
                <code> stat ~/output.geojson </code>
                <br>
                <br>
                <samp>{}</samp>
            <h2> Which Python processes are running </h2>
                <code> ps aux | grep python | grep -v grep </code>
                <br>
                <br>
                <samp>{}</samp>
            <h2> Crontab entries </h2>
                <code> crontab -l </code>
                <br>
                <br>
                <samp>{}</samp>
            <br>
            <p> Navrit Bal </p>
            <p> Maker of DoseNet. </p>

"""
