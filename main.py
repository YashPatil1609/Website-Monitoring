import requests
import smtplib
import os
import paramiko
import boto3
import schedule
import time

EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
CONTAINERID = "08427882d2a5"
INSTANCEID = "i-0957edd97041a63c7"

ec2_client = boto3.client('ec2')
reservations = ec2_client.describe_instances(InstanceIds=[INSTANCEID])['Reservations']
HOSTIP = reservations[0]['Instances'][0]['PublicIpAddress']

USERNAME = "ubuntu"


def send_notification(body):
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        subject = "Website Monitor Alert"
        message = f"Subject: {subject}\n\n{body}"

        smtp.sendmail(EMAIL_ADDRESS, EMAIL_ADDRESS, message)

def restart_application():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=HOSTIP, port=22, username = USERNAME, key_filename=r"C:\Users\yapat\.ssh\demo_keypair.pem")
    stdin, stdout, stderr = ssh.exec_command(f'docker restart {CONTAINERID}')
    ssh.close()

def restart_server():
    ec2_client = boto3.client('ec2')
    ec2_reboot = ec2_client.reboot_instances(InstanceIds=[INSTANCEID])

    # Restart application after server reboot
    while True:
        ec2_client = boto3.client('ec2')
        ec2_status = ec2_client.describe_instance_status(InstanceIds=[INSTANCEID], IncludeAllInstances=True)
        status = ec2_status['InstanceStatuses'][0]

        if status['InstanceState']['Name'] == 'running' and status['SystemStatus']['Status'] == 'ok' and \
                status['InstanceStatus']['Status'] == 'ok':
            restart_application()
            break

def monitor_application():
    try:
        response = requests.get("http://ec2-44-201-128-169.compute-1.amazonaws.com:8081")
        if False:
            print("Application is up and running!")
        else:
            print("Application down, sending mail!")
            send_notification(f"Application down, sent status code : {response.status_code} . Please Fix it! ")
            print("Mail sent!")

            # Restart the docker container
            print("Restarting the application...")
            restart_application()
            print("Application restarted!")


    except requests.exceptions.ConnectionError as CE:
        send_notification(f"Connection error : {CE}\n The Server might be down, please check")

        # Trying to reboot the server
        print("Restarting the server...")
        restart_server()
        print("Server restarted!")

schedule.every(30).seconds.do(monitor_application)

while True:
    schedule.run_pending()
    time.sleep(1)

