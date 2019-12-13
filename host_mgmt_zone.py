import os
import io
import sys  
import json
import pycurl
import logging
import certifi
import smtplib
import traceback
from constant_host_unit import *
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.MIMEImage import MIMEImage
sys.path.append("")

hostList = [] 

class app:
  def __init__(self):
   self.name = ""
   self.type = ""
   self.entityId = ""
   self.consumption = 0
   self.dem = 0


class email_details:
  def __init__(self):
    self.smtpserver = ""
    self.username = ""
    self.password = ""
    self.port = 0
    self.senders_list = ""
    self.receivers_list = ""

class tenantInfo:
   def __init__(self):
     self.tenant_url = ""
     self.tenant_token = ""
     self.name = ""
#------------------------------------------------------------------------------
# Author: Nikhil Goenka
# Function to initialize the email server
# Returns the smtp_server initialized 
#------------------------------------------------------------------------------
def initialize_email_server(logger, smtp_server_details):
  try:
    logger.info("In initialize_email_server")
    smtp_server = smtplib.SMTP(smtp_server_details.smtpserver,smtp_server_details.port )
    smtp_server.starttls()
    smtp_server.login(smtp_server_details.username, smtp_server_details.password)
    logger.info("Execution sucessfull: initialize_email_server")

  except Exception, e:
    traceback.print_exc()
    logger.error("Received exception while running initialize_email_server", str(e), exc_info = True)

  finally:
    return smtp_server

#------------------------------------------------------------------------------
# Author: Nikhil Goenka
# Function to send an email using the smtp_server initialized
# Returns: nothing 
#------------------------------------------------------------------------------

def send_email(logger, smtp_server, content, smtp_server_details):
  try:
    logger.info("In send_email")
    logger.debug ("send_email: smtp_server = %s", smtp_server)
    logger.debug ("send_email: message = %s", content)
    content["From"] = smtp_server_details.senders_list
    content["To"] = smtp_server_details.receivers_list

    smtp_server.sendmail(smtp_server_details.senders_list, (smtp_server_details.receivers_list).split(','), content.as_string())
    logger.info("Execution sucessfull: send_email")

  except Exception, e:
    traceback.print_exc()
    logger.error("Received exception while running send_email", str(e), exc_info = True) 

#------------------------------------------------------------------------------
# Author: Nikhil Goenka
# Function to make API call using the token defined in constant.py
# Returns the json object returned using the API call 
#------------------------------------------------------------------------------
def dtApiQuery(logger, endpoint, tenant_info, URL=""):
  try: 
    logger.info("In dtApiQuery")
    logger.debug ("dtApiQuery: endpoint = %s", endpoint)
    buffer = io.BytesIO()

    if URL == "":
      URL = tenant_info.tenant_url
    c = pycurl.Curl()
    #print str(URL) + str(endpoint)
    c.setopt(c.URL, URL + endpoint)
    c.setopt(pycurl.CAINFO, certifi.where())
    c.setopt(c.HTTPHEADER, ['Authorization: Api-Token ' + tenant_info.tenant_token] )
    c.setopt(pycurl.WRITEFUNCTION, buffer.write)
    c.perform()
    c.close()
    logger.info("Execution sucessfull: dtApiQuery")

  except Exception,e:
    traceback.print_exc()
    logger.error("Received exception while running dtApiQuery", str(e), exc_info = True) 

  finally:
    return(buffer.getvalue().decode('UTF-8'))

#---------------------------------------------------------------------------------------------
# Author: Nikhil Goenka
# Function to print the entire structure of app_mgmt_zone (will be used for debugging) 
#---------------------------------------------------------------------------------------------
def pretty_print(logger, app_mgmt_zone):
  try:
    logger.info("In pretty_print")
    for mgmt_zone_name in app_mgmt_zone.keys():
        for i in range(len(app_mgmt_zone[mgmt_zone_name])):
          print mgmt_zone_name + " " + str(len(app_mgmt_zone[mgmt_zone_name])) + "." + app_mgmt_zone[mgmt_zone_name][i].name + "\t" + str(app_mgmt_zone[mgmt_zone_name][i].consumption) + "\t" + str(app_mgmt_zone[mgmt_zone_name][i].dem) + "\n"
  except Exception,e:
    traceback.print_exc()
    logger.fatal("Received exception while running pretty_print", str(e), exc_info=True)

def html_header(logger):
    try:
      logger.info("In html_header: ")
      html = """
      <html>
      <head>
      <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
      </head>
      <body bgcolor="#FFFFFF" leftmargin="0" topmargin="0" marginwidth="0" marginheight="0">
      <center>
      <img src="cid:image1" class = "center" width:90%>
      </center>
      <br></br>
      <p> Hi Team, </p>
      <p> Following are the details of DEM/Host Units: </p>
      <br></br>
      <center>
      </style>
    """
    except Exception:
      traceback.print_exc()
      logger.error ("Received error while executing html_header %s", str(e))
    finally:
      return html


def html_body(logger, html, table_list, tenant_info, mgmt_zone, app_mgmt_zone):
    try:
      logger.info("In html_body: ")
      logger.debug("In html_body %s: ", table_list)

      string_tenant = "<p><b>Tenant name</b>: {tenant_name}</p>\n"
      table_header = "<table>\n<style>table, th, td {{ border: 3px solid black; border-collapse: collapse;width:34%;margin:auto}}\n th, td {{ padding: 3px; }}\n</style>\n <tr>\n<th>Management Zone</th>\n<th>Host Unit Consumption</th>\n<th>DEM Unit Consumption</th>\n</tr>\n"

      string = string_tenant + table_header 
      for key in mgmt_zone.keys():
        try:
          total_consumption = 0
          for i in range(len(app_mgmt_zone[key])):
            total_consumption = total_consumption + app_mgmt_zone[key][i].dem
        except KeyError:
          total_consumption = 0.0
        finally:
          str_val = "<tr>\n<td>" + str(key) + "</td>\n<td>" + str(mgmt_zone[key]) + "</td>\n<td>" + str(total_consumption) + "</td></tr>\n"
          string = string + str_val
 
      for key in app_mgmt_zone.keys():
        total_consumption = 0
        for i in range(len(app_mgmt_zone[key])):
          total_consumption = float(total_consumption) + app_mgmt_zone[key][i].dem

        try:
          host_units = mgmt_zone[key]
        except KeyError:
          host_units = "0.0"
        finally:
          str_val = "<tr>\n<td>" + str(key) + "</td>\n<td>" + str(host_units) + "</td>\n<td>" + str(total_consumption) + "</td></tr>\n"
          string = string + str_val
 
      string = string + "</table>"
      html = html + string.format(tenant_name = tenant_info.name) + """ 
      <br></br>
      <br></br>
      <center>
      """

      #html = html.format(tenant_name=tenant_info.name, table=tabulate(table_list, headers="firstrow", tablefmt = "html"))
    except Exception:
      traceback.print_exc()
      logger.error ("Received error while executing html_body %s", str(e))
     
    finally:
      return html, table_list

def html_footer(logger, html, content):
    try:
      logger.info("In html_footer : ")
      logger.debug("In html_footer %s: ", content)

      html = html + """ 
      <center>
      <p style="text-align:left;">Thanks, </p>
      <p style="text-align:left;">Dynatrace Team </p>
      <center>
      <img src="cid:image2">
      </center>
      </body>
      """

      content.attach(MIMEText(html, "html"))
      msgAlternative = MIMEMultipart('alternative')
      content.attach(msgAlternative)

      fp = open('images/Email_Template_01.jpg','rb')
      msgImage = MIMEImage(fp.read())
      fp.close()

      msgImage.add_header('Content-ID', '<image1>')
      content.attach(msgImage)

      fp = open('images/Email_Template_03.jpg','rb')
      msgImage = MIMEImage(fp.read())
      fp.close()

      msgImage.add_header('Content-ID', '<image2>')
      content.attach(msgImage)
     
    except Exception:
      traceback.print_exc()
      logger.error ("Received error while executing html_footer %s", str(e))
     
    finally:
      return content

#------------------------------------------------------------------------
# Author: Nikhil Goenka
# Function to call API and populate the excel file
#------------------------------------------------------------------------
def func(logger, totalHostUnits, smtp_server, smtp_server_details, html, tenant_info, table_list, email_body, mgmt_zone, app_mgmt_zone):
  try:
    logger.info("In func")
    logger.debug("func: totalHostUnits = %s", totalHostUnits)  
    logger.debug("func: smtp_server = %s", smtp_server)
    logger.debug("func: smtp_server = %s", smtp_server_details)

    hostsIO = dtApiQuery(logger, INFRA_API, tenant_info)
    hosts = json.loads(hostsIO)

    for host in hosts:
      key = ""
      #Management Zone
      try:
        zones = host['managementZones']
        for zone in zones:
          key = key + zone['name'] + ","
        key = key[:-1]
      except KeyError:
        key = "No assigned management zone"

      try:
        mgmt_zone[key] = mgmt_zone[key] + float(host['consumedHostUnits'])
      except KeyError:
        mgmt_zone[key] = float(host['consumedHostUnits']) 
    
      #print "Host -> ", host['displayName'] +  " -> " + str(key) + " -> " + str(mgmt_zone[key])

    #First fetch all the applications
    app_mgmt_zone = fetch_application(logger, app_mgmt_zone, tenant_info, FETCH_APPLICATIONS)

    #Now fetch all the synthetic applications 
    app_mgmt_zone = fetch_syn_application(logger, app_mgmt_zone, tenant_info, FETCH_SYN_APPLICATIONS)

    app_mgmt_zone = populate_consumption(logger, app_mgmt_zone, tenant_info, APP_BILLING_API)
    app_mgmt_zone = populate_consumption(logger, app_mgmt_zone, tenant_info, SYN_BILLING_API, 1)
    app_mgmt_zone = populate_consumption(logger, app_mgmt_zone, tenant_info, HTTP_BILLING_API, 2)
    
    #pretty_print(logger, app_mgmt_zone)        
   
    html, table_list = html_body(logger, html, table_list, tenant_info, mgmt_zone, app_mgmt_zone)
    logger.info("Successful execution: func")
    
  except Exception,e:
    traceback.print_exc()
    logger.fatal("Received exception while running func", str(e), exc_info = True)

  finally:
    return table_list, html

#------------------------------------------------------------------------
# Author: Nikhil Goenka
# Function to fetch all the synthetic browsers and append it to the directory "app_mgmt_zone" 
#------------------------------------------------------------------------
def populate_consumption(logger, app_mgmt_zone, tenant_info, query, syn = 0):
  consumption_details = {}
  try:
    logger.info("In populate_consumption")
    logger.debug("populate_consumption = %s", query)
   
    url = (tenant_info.tenant_url).replace("v1","v2")
    applicationIO = dtApiQuery(logger, query, tenant_info, url)
    applications = json.loads(applicationIO)

    if syn == 0:
      apps = applications['metrics']['builtin:billing.apps.web.sessionsWithoutReplayByApplication:fold(value)']['values']
    elif syn == 1:
      apps = applications['metrics']['builtin:billing.synthetic.actions:fold(value)']['values']
    elif syn == 2:
      apps = applications['metrics']['builtin:billing.synthetic.requests:fold(value)']['values']

    for billing in apps:
      dimensions = billing['dimensions']
      if syn == 0:
        if dimensions[1] == "Billed":
          consumption_details[dimensions[0]] = billing['value']
      elif syn >= 0:
          consumption_details[dimensions[0]] = billing['value']
      #print application['metrics']['builtin:billing.apps.web.sessionsByApplication:fold(value)']['values']
    logger.info("Successful execution: populate_consumption")
    
    for key in consumption_details.keys():
      for mgmt_zone_name in app_mgmt_zone.keys():
        for i in range(len(app_mgmt_zone[mgmt_zone_name])):
          if key == app_mgmt_zone[mgmt_zone_name][i].entityId:
            app_mgmt_zone[mgmt_zone_name][i].consumption = app_mgmt_zone[mgmt_zone_name][i].consumption + consumption_details[key]

            if app_mgmt_zone[mgmt_zone_name][i].type == "Synthetic":
              app_mgmt_zone[mgmt_zone_name][i].dem = float(app_mgmt_zone[mgmt_zone_name][i].consumption * 1.0)

            elif app_mgmt_zone[mgmt_zone_name][i].type == "HTTP":
              app_mgmt_zone[mgmt_zone_name][i].dem = float(app_mgmt_zone[mgmt_zone_name][i].consumption * 0.1)

            else: 
              app_mgmt_zone[mgmt_zone_name][i].dem = float(app_mgmt_zone[mgmt_zone_name][i].consumption * 0.25)

  except Exception,e:
    traceback.print_exc()
    logger.fatal("Received exception while running populate_consumption", str(e), exc_info=True)
    
  finally:
    return app_mgmt_zone

#------------------------------------------------------------------------
# Author: Nikhil Goenka
# Function to fetch all the synthetic browsers and append it to the directory "app_mgmt_zone" 
#------------------------------------------------------------------------
def fetch_syn_application(logger, app_mgmt_zone, tenant_info, query):
  try:
    logger.info("In fetch_syn_application")
    logger.debug("fetch_syn_application = %s", query)
   
    #print query
    applicationIO = dtApiQuery(logger, query, tenant_info)
    applications = json.loads(applicationIO)
   
    application = applications['monitors']

    for i in range(len(application)):
      appInfo = app()
      appInfo.name = application[i]['name']

      #For custom-type application, applicationType is not populated, hence the check
      try:
        if application[i]['type'] is not "HTTP":
          appInfo.type = "Synthetic"
        else:
          appInfo.type = "HTTP"
      except KeyError:
        appInfo.type = "Synthetic"
          
      appInfo.entityId = application[i]['entityId']
 
      #Management Zone
      key = ""
      try:
        zones = application[i]['managementZones']
        for zone in zones:
          key = key + zone['name'] + ","
        key = key[:-1]
      except KeyError:
        key = "No management zone"

      if key in app_mgmt_zone.keys():
        app_mgmt_zone[key].append(appInfo)
      else:
        app_mgmt_zone[key] = [appInfo]
 
    logger.info("Successful execution: fetch_sync_application")
    
  except Exception,e:
    traceback.print_exc()
    logger.fatal("Received exception while running fetch_syn_application ", str(e), exc_info=True)

  finally:
    return app_mgmt_zone

#------------------------------------------------------------------------
# Author: Nikhil Goenka
# Function to call API and populate the excel file
#------------------------------------------------------------------------

def fetch_application(logger, app_mgmt_zone, tenant_info, query):
  try:
    logger.info("In fetch_application")
    logger.debug("fetch_application = %s", query)
   
    #print query
    applicationIO = dtApiQuery(logger, query, tenant_info)
    applications = json.loads(applicationIO)

    for application in applications:
      appInfo = app()
      appInfo.name = application['displayName']

      #For custom-type application, applicationType is not populated, hence the check
      try:
        appInfo.type = application['applicationType']
      except KeyError:
        appInfo.type = "Not available"

      appInfo.entityId = application['entityId']
 
      key = ""
      #Management Zone
      try:
        zones = application['managementZones']
        for zone in zones:
          key = key + zone['name'] + ","
        key = key[:-1]
      except KeyError:
        key = "No management zone"

      if key in app_mgmt_zone.keys():
        app_mgmt_zone[key].append(appInfo)
      else:
        app_mgmt_zone[key] = [appInfo]
   
    logger.info("Successful execution: fetch_application")
    
  except Exception,e:
    traceback.print_exc()
    logger.fatal("Received exception while running fetch_application ", str(e), exc_info=True)

  finally:
    return app_mgmt_zone
#------------------------------------------------------------------------
# Author: Nikhil Goenka
# Function to call API and populate the excel file
#------------------------------------------------------------------------
def parse_config(filename):
  try:
    stream = open(filename)
    data = json.load(stream)
  except Exception:
    traceback.print_exc()
    logger.error("Exception encountered in parse_config function : %s ", str(e))
  finally:
    return data

#------------------------------------------------------------------------
# Author: Nikhil Goenka
# Function to call API and populate the excel file
#------------------------------------------------------------------------
def populate_smtp_variable(data, smtp_server_details):
  try:
    smtp_server = data['email-details']
    smtp_server_details.username = smtp_server['username']
    smtp_server_details.password = smtp_server['password'] 
    smtp_server_details.smtpserver = smtp_server['server']
    smtp_server_details.port = int(smtp_server['port'])
    smtp_server_details.senders_list = smtp_server['senders-list'] 
    smtp_server_details.receivers_list = smtp_server['receiver-list']

  except Exception, e:
    traceback_print.exc()
    logger.error("Exception encountered while executing populate_smtp_variable %s ", str(e))
  finally:
    return smtp_server_details

#------------------------------------------------------------------------
# Author: Nikhil Goenka
# Function to call API and populate the excel file
#------------------------------------------------------------------------
def populate_tenant_details(logger, tenant, tenant_info):
  try:
    logger.info("In populate_tenant_details")
    logger.info("In populate_tenant_details %s ", tenant)

    tenant_info.tenant_url = tenant['tenant-URL'] 
    tenant_info.tenant_token = tenant['API-token']
    tenant_info.name = tenant['tenant-name']
  except Exception, e:
    traceback_print.exc()
    logger.error("Exception encountered while executing populate_tenant_details %s ", str(e))
  finally:
    return tenant_info 
  
#------------------------------------------------------------------------
# Author: Nikhil Goenka
# Function to call API and populate the excel file
#------------------------------------------------------------------------

if __name__ == "__main__":
  try:
    totalHostUnits = 0
    filename = "config.json"
    data = parse_config(filename)
    smtp_server_details = email_details()

    
    smtp_server_details = populate_smtp_variable(data, smtp_server_details)

    logging.basicConfig(filename=data['log_file'],
                            filemode='a',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.DEBUG)
    logger = logging.getLogger()
    smtp_server = initialize_email_server(logger, smtp_server_details)
    tenants = data['tenant-details']

    email_body = ""

    content = MIMEMultipart('related')
    content["Subject"] = "ALERT: Host/DEM Unit Consumption"

    html = html_header(logger)
    
    for tenant in tenants:
      table_list = []
      mgmt_zone = {}
      app_mgmt_zone = {} 

      tenant_info = tenantInfo()
      tenant_info = populate_tenant_details(logger, tenant, tenant_info)
      table_list, html = func(logger, totalHostUnits, smtp_server, smtp_server_details, html, tenant_info, table_list, email_body, mgmt_zone, app_mgmt_zone)
    
    content = html_footer(logger, html, content)
    send_email(logger, smtp_server, content, smtp_server_details)

  except Exception, e:
    traceback.print_exc()
    logger.error("Received exception while running main", str(e))
  
  finally:
    smtp_server.close()
