There are five files in the package:
 - install_dependencies.txt
   ========================
   Install the dependencies and required libraries by running the file as "source install_dependencies.txt"
 
 - config.json
   ===========
   tenant-details:
     tenant-URL: The tenant URL which will be used to fire the API call
     API-token: The API token which will be used to fire the API
     tenant-name: The tenant name 
   NOTE: If you have multiple tenants to be monitored, add another section

   email-details:
     server: The mail-server which will be used to send the email.
     port: Port of the mail-server.
     username: The username which will be used to login on the smtp-server
     password: Password of the SMTP username
     senders-list: The sender email-id from which the email-id will be triggered
     receivers-list: The recepients email-id who would be alerted

   log_file:
    the log file where the script logs will be saved 
   
- host_mgmt_zone.py:
  ================
   It is a python script that will make API calls to collect information about the current running hosts, applications and their consumption. 
   An email will be triggered with the details of host/DEM utilization according to management zone.

How to run the script:
You can schedule the script to execute every week by using a crontab entry as below:
0 0 * * 0 /home/ngoenka/host_mgmt_zone.py > check_host_consumption_script.out

- images/Email_Template_01.jpg and images/Email_Template_03.png
  =============================================================
  Images that will be used in the email

- constant_host_unit.py
  ====================
  Constant file that is used in the script 
