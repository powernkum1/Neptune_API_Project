"""
This project basically uses the neptune api to extract data from the neptune server. 
An initial connection is made to GIS to obtain the address and account information from the GIS feature class specifically - Service_Locations_Saint_Cloud_revised.
These records are also filtered out from the featureclass - same account duplicate addresses, same address and duplicate accounts. This is important so that there wouldn't be any conflicts when aligning
the account numbers from the neptune server to the account numbers in GIS. In this case, we will only be dealing with unique accounts only.
Some of the modules that were imported include the requests module - 2.11, requests_cache - version -0.5.2, IPython - version 2.10, tqdm -version-4.9
"""
import arcpy
import requests
import json
import time
import os
import pandas as pd
from copy import deepcopy
import math
from collections import OrderedDict
import requests_cache
from IPython.core.display import clear_output
import pandas as pd
from tqdm import tqdm
import dateutil.parser
import datetime
from datetime import datetime, timedelta
import datetime as DT
#import datetime as DT
from dateutil.relativedelta import relativedelta
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

#requests_cache.install_cache() original
requests_cache.install_cache('teeminus10_cache', expire_after=24*60*60)
requests_cache.clear()

# Reading through the text files or spreadsheets to get the addresses and account numbers that will be filtered out

file1 = r"C:\Users\GISSRV\Documents\ArcGIS\saint_cloud\account.txt" # update the file path

file2 = r"C:\Users\GISSRV\Documents\ArcGIS\saint_cloud\address.txt" # update the file path

Neptune = "C:\\Users\\GISSRV\\Documents\\ArcGIS\\saint_cloud\\Saint_Cloud.gdb\\Neptune_Parcel"

saint_cloud_original = "C:\\Users\\GISSRV\\Documents\\ArcGIS\\saint_cloud\\Saint_Cloud.gdb\\Service_Locations_Saint_Cloud_revised"

saint_cloud = "C:\\Users\\GISSRV\\Documents\\ArcGIS\\Default.gdb\\saint_cloud_temp"

my_file = r"C:\Users\GISSRV\Documents\ArcGIS\saint_cloud\Narcoossee_IR_Meters.csv" # path for the narcoosee spreadsheet

# Declaring these global variables
objectid_list = []
objectid_list_update = []
list_accounts = []
begin_date =""
end_date = ""

edited_reponse = [] # final results including water consumption information

reference_list_mius = []
responses = [] # list of endpoint objects
list_mius = [] # list of mius
list_mius_post = [] # list of consumption request objects received from sent the api server

try:
    #import random
    # initializing
    scriptSuccess = True
    failmessage =""
    # Email function for sending emails.
    # Defining a function that will be used to send emails to the recipients
    def send_email(subject, message, from_email, to_email=[], attachment=[]):
        """
        :param subject: email subject
        :param message: Body content of the email (string), can be HTML/CSS or plain text
        :param from_email: Email address from where the email is sent
        :param to_email: List of email recipients, example: ["a@a.com", "b@b.com"]
        :param attachment: List of attachments, exmaple: ["file1.txt", "file2.txt"]
        """
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = from_email
        msg['To'] =  ", ".join(to_email)
        msg.attach(MIMEText(message, 'plain'))
        msg['X-Priority'] =  '2'
        msg['X-MSMail-Priority'] =  'Medium'
            
            #attachment =[r"C:\Users\arcgisuser.TOHO_MAIN_HQ\test_email.txt"]
            
        for f in attachment:
            with open(f, 'rb') as a_file:
                basename = os.path.basename(f)
                part = MIMEApplication(a_file.read(), Name=basename)

            part['Content-Disposition'] = 'attachment; filename="%s"' % basename
            msg.attach(part)

        email = smtplib.SMTP('smtp.tohowater.com')
        email.sendmail(from_email, to_email, msg.as_string())

                 
    # take the email list and use it to send an email to connected users.
    #TO = emailList
    today2 = DT.date.today() # Defining today's date tha will be used to create the text file that will be exported.
    month = today2.strftime("%B")
    subject = "Narcoossee Water Consumption Monthly Irrigation Report"
    message = "Please review the attached water consumption monthly report for "
    message+= month +'\n\r'
    message1 = "***Replies to this email are not monitored***.\nThank you!\nGISSRV\n\r"
    message += message1
    from_email = 'GISSRV@tohowater.com'

    # defines the class which lists multiple fields that can be stored for the same key
    class dd_list(dict):
        def __missing__(self,k):
            r = self[k] = []
            return r

    # Defining a class for dynamic dates
    class dynamic_dates():
        def __init__(self):
            self.x = 0
            self.today = DT.date.today()
            while self.x<4:
                end_date = self.today.strftime('%Y-%m-%d %H:%M:%S').split(' ')[0]
                self.begin_date1  = self.today-DT.timedelta(days=6)
                begin_date = self.begin_date1.strftime('%Y-%m-%d %H:%M:%S').split(' ')[0]
                # sending a request to the api server to get the water consumption in bits
                post_waterconsump_instance = post_water_comsumption({'Authorization':'Bearer {}'.format(json_file_object['AccessToken'])},'v1/consumption')
                #post_waterconsump_instance.sending_request({'limit':100,"begin_date": end_date,"end_date": "2022-06-28","actual_consumption": 'true'},list_mius_post,post_waterconsump_instance) # sending limit information and passing and instance of the water consumption object in the request.
                post_waterconsump_instance.function_tuple(post_waterconsump_instance) #self.mius_post = []
                #del responses # delete responses reinialize responses = [] 
                #del dict1 # delete responses # re-initialize dict1 = {}
                #del post_endpoints_instance # delete post_endpoints_instance # re-initialize post_endpoints_instance = {}
                post_waterconsump_instance.restructure_json_file(post_waterconsump_instance.mius_post) # calling method to restructure the response object for the water consumption

                print("stuff, carry out operations")
                print("begin_date,end_date",begin_date,end_date)
                self.today = self.begin_date1-DT.timedelta(days=1) # subtract one day
                self.x+=1

    # defining a class to check existence of paths for file geodatabases and sde
    class Check_file():
        # create the constructor function
        def __init__(self,connection_name):
            self.root = r"C:\Users\GISSRV\Documents\ArcGIS\Default.gdb"

        # check the existence of the file
        def check_file_existence(self,connection_name,filegeod):
            self.path = self.root + "\\" + connection_name

            #filegeod = 1
            try:
                # delete paths for geodatabases
                if (arcpy.Exists(self.path)) and filegeod == 1:
                    arcpy.Delete_management(self.path)
                    print("deleted")
                elif (arcpy.Exists(self.path)) and filegeod == 2: # deleting paths for the sde connections
                    os.unlink(self.path)
                    print("deleted")
            except:
                # delete paths for sde connections
                #os.unlink(self.path)
                pass

    dict1 = dd_list() #creating an instance of dd_list() class 
    dict2 = dd_list() #creating an instance of dd_list() class
    dict3 = dd_list() #creating an instance of dd_list() class

    #Defining a class to filter out the duplicate accounts and duplicate addresses from the saint cloud feature class
    class filter_saintcloud_records():
        def openfile(self,file1,file2):
            global tuple_address
            global tuple_account
            self.dict_address = {}
            self.dict_account = {}
            self.list_status = []
            self.list_status_2 = []
            if os.path.exists(file1) and os.path.exists(file2) :
                self.file_1 = open(file1,'r')
                self.list_status = self.file_1.readlines() # read all lines into a list object with back slash \n for each variable when "readlines" property is used so we've to 
                self.file_1.close() # close file and re-open it again
                #recon_status = str(list_status[0])[:-1] # remove \n from the text file
                #return recon_status #
                self.file_2 = open(file2,'r')
                self.list_status_2 = self.file_2.readlines() # read all lines into a list object with back slash \n for each variable when "readlines" property is used so we've to 
                self.file_2.close()
            x= 0
            y =0

            # address with multiple account numbers 
            for i in self.list_status:
                self.dict_account[str(self.list_status[x])[:-1].strip()]=str(self.list_status[x])[:-1].strip()
                x=x+1
                            
            self.dict_account_copy = deepcopy(self.dict_account)

            x = 0
            y = 0
                    
            tuple_account = tuple(self.dict_account_copy.keys()) # convert account to tuple

            if len(tuple_account) == 1:
                tuple_account = str(tuple_account).replace(",", "")
            if len(tuple_account) == 0:
                tuple_account = str(('',)).replace(",", "")

            #account number with multiple addresses
            for i in self.list_status_2:
                self.dict_address[str(self.list_status_2[x])[:-1].strip()]=str(self.list_status_2[x])[:-1].strip()
                x = x+1

            self.dict_address_copy = deepcopy(self.dict_address)
                    
            tuple_address = tuple(self.dict_address_copy.keys()) # convert address to tuple

            if len(tuple_address) == 1:
                tuple_address = str(tuple_address).replace(",", "")
            if len(tuple_address) == 0:
                tuple_address = str(('',)).replace(",", "")

        # Defining a clip method to clip the saint cloud accounts to the narcoossee boundary
        def getClip(self,queryFeatureClass,clipFeatureClass,output):
            arcpy.AddMessage(queryFeatureClass)
            arcpy.AddMessage(clipFeatureClass)
            arcpy.Clip_analysis(in_features=queryFeatureClass, clip_features = clipFeatureClass, out_feature_class=output, cluster_tolerance="")


    # defining function to filter out the accounts and addresses that will have to be looked at manually
    class filter_records():
        global saint_cloud_filter_1
        def __init__(self):
            pass
        # A method that creates an address field for the following parameters below
        def address_temps(self,numb,prefix,streetname,suffix,unit,city):
            self.address_lst = [numb,prefix,streetname,suffix,unit,city]
            self.full_address = ""
            for i in self.address_lst:
                if i:
                    self.full_address += i.strip() + " "
            self.address_temp = " ".join(self.full_address.split()).strip()
            return self.address_temp

        def narcoossee(self,my_file):
            #my_file = r"C:\Users\mnkum\Desktop\Neptune_Projects\Narcoossee_IR_Meters.csv"
            #my_file = r"C:\Users\mnkum\Desktop\Neptune_Projects\narcoossee_IR_Meters_sample.txt"
            global dict_narcoossee
            global list
            self.my_file = my_file
            # check the existence of the file
            if os.path.exists(self.my_file):
                self.file = open(self.my_file,'r')
                self.list = self.file.readlines() # read all lines into a list object with back slash \n for each variable when "readlines" property is used so we've to create a new list(list_file_
                self.list_total = len(self.list)
                print("list_total",self.list_total)
                self.list_file = [0]*self.list_total*2 # initializes the new empty list
                self.file.close() # close file and re-open it again
                self.file_reopen = open(self.my_file,'r')
                self.x1=0
                self.y1=1
                #row[2] = str.zfill(str(dict[address][0][0]),8)
                dict_narcoossee = {}
                for i in self.list:
                    try:
                        #dict_narcoossee[int(list[y].split(',')[0])] = [int(list[y].split(',')[1])]
                        dict_narcoossee[str.zfill(str(self.list[self.y1].split(',')[0]),8)] = [str(self.list[self.y1].split(',')[1]),str(self.list[self.y1].split(',')[2]).split('\n')[0]] 
                        self.y1 = self.y1+1 # increase count in the original list
                    except:
                        pass
                        
                # close the file
                self.file_reopen.close()
        
        def filter(self,saint_cloud):
            self.saint_cloud = saint_cloud
            self.address_field = ["ADDRESS_TWA","OBJECTID","ACCOUNT_NUMBER","NUMB","PREFIX","STREETNAME","SUFFIX","UNIT","CITYCD","SOURCE","SHAPE@X","SHAPE@Y"]
            with arcpy.da.SearchCursor(self.saint_cloud,self.address_field,"(NOT ADDRESS_TWA IS NULL OR NOT ADDRESS_TWA = '') AND (NOT ACCOUNT_NUMBER IN "+str(tuple_account)+") AND (NOT ADDRESS_TWA IN "+str(tuple_address)+") AND (NOT ACCOUNT_NUMBER IS NULL OR NOT ACCOUNT_NUMBER = '')") as saint_cloud_filter_1:
                for row in saint_cloud_filter_1:
                    try:
                        self.address = self.address_temps(row[3],row[4],row[5],row[6],row[7],row[8])
                        #print "self.address,account",self.address,row[2]
                        self.account = str(row[2]) # not needed anymore since it's pointing to the a copy of the service locations
                        dict1[self.account] = [self.address,{'miu_id':[]},{'meter_number':[]}]
                        #dict1[self.account] = [self.address] #2)dict1['000337831'].append('address2') appending other subsequent ones
                        #dict1[row[2]].append([self.address]) #row[2] = str.zfill(str(dict[address][0][0]),8) # update account number since account number 
                    except:
                        pass
            # defining a method to delete all accounts from the dict1 that are not present in the Narcoossee_IR_Meters spreadsheet
            for key in dict1.keys():
                if not key in dict_narcoossee.keys():
                    try:
                        print("deleting key",dict1[key])
                        del dict1[key]
                    except:
                        pass
                else:
                    print("key is maintained",dict1[key])
            # creating an initial list of mius from the spreadsheet in respect to the account numbers
            for key,value in dict_narcoossee.items():
                try:
                    reference_list_mius.append(dict_narcoossee[key][1]) #dict_narcoossee['00029097'][1].split('\n')[0]
                except:
                    pass
            
     
        # method to get the count of the number of records in a row
        def totalcount(self,inspec_table):
            self.count = 0
            self.saint_cloud_filter =inspec_table
            for row in self.saint_cloud_filter:
                    self.count +=1
            self.saint_cloud_filter.reset()
            print "number of records/rows",self.count
            return self.count
                            

    # Creating a class to get responses from the server
    class get_responses:
        def __init__(self,headers,endpoint):
            headers['x-api-key'] = ''
            headers['Accept'] = 'application/json'
            headers['client-secret'] = ''
            headers['client-id'] = ''
            self.baseurl = 'https://o3lez36n4h.execute-api.us-east-1.amazonaws.com/api/'
            self.requesturl = self.baseurl + str(endpoint)
            self.headers = headers
        # calling the requests module for get
        def response_server(self,params):
            self.params = params
            response = requests.get(self.requesturl,params = self.params,headers = self.headers)
            return response

    # defining a class to use the send_request_method
    class get_chunks_data():
        def __init__(self,headers,endpoint):
            self.page = 1
            self.total_pages = 60000 # this is just a dummy number so the loop starts
            #dict3[self.miu_id1] = [str(self.date_variable),self.k]
            pass
        # defining a method to run a loop and get the endpoints using cache
        def sending_request(self,params,responses_req,object_request): # supply the limit as key in the params during call up
            #self.page = 1
            #self.total_pages = 60000 # this is just a dummy number so the loop starts
            while self.page <= self.total_pages:
                #params = {'site_id': '34769','limit': 5000,'page': self.page} #params = {'site_id': '34769','self.page': self.page}
                params['site_id'] = '34769'
                #params['limit'] = 5000
                params['page']=self.page
                    
                # print some output so we can see the status
                print("Requesting self.page {}/{}".format(self.page, int(self.total_pages)))
                # clear the output to make things neater
                clear_output(wait = True)
                #print('params/json,responses_req,self.headers',params,len(responses_req),self.headers)
                # make the API call but check the time to see if it's not more than 8 minutes elapsed
                t1 = time.clock() - self.t0 # recalculate the time difference and get new authorization
                if t1 > 300: #360 secom
                    requests_cache.clear() # clear the cache
                    init_response = get_responses({},'v1/token')
                    second_response = init_response.response_server({})
                    json_response = json_convertion(second_response)
                    json_file_object = json_response.jsonstring_object()
                    object_request.headers['Authorization'] = 'Bearer {}'.format(json_file_object['AccessToken'])#{'Authorization':'Bearer {}'.format(json_file_object['AccessToken'])}
                    self.t0 = time.clock() # redefine the time clock or start time in obtaining the token. # newly added
                    response = object_request.response_server(params) # polymorphism at display, reponse_server method is the same but depending on the instance of object passed,different method will be called
                else:
                    #continue with the process
                    response = object_request.response_server(params) # polymorphism at display, reponse_server method is the same but depending on the instance of object passed,different method will be called
                # if we get an error, print the response and halt the loop
                print('response.status_code',response.status_code)
                if response.status_code != 200:
                    requests_cache.clear()
                    print(response.text)
                    self.page += 1
                    break
                try:
                    # extract pagination info
                    self.page = int(response.json()['paging']['page']) # gets the page number
                    self.total_pages = (int(response.json()['paging']['total'])/float(params['limit']))+1 # 1 added to take care of the rest of the smallest pieces of endpoints
                except:
                    pass
                    print('self.page',self.page)
                    #self.total_pages = (int(len(list_mius))/float(params['limit']))+1 # 1 added to take care of the rest of the smallest pieces of endpoints
                    self.total_pages = self.page

                # append response
                responses_req.append(response) # depending on the object or list that is passed, different responses will be appended. 

                # if it's not a cached result, sleep
                if not getattr(response, 'from_cache', False):
                    time.sleep(0.25)

                # increment the self.page number
                #self.page += 1</code>
                self.page += 1
                #self.total_pages += 1
  
        def __init__(self,headers,endpoint):
            self.page = 1
            self.total_pages = 60000 # this is just a dummy number so the loop starts
            pass
        # defining a method to run a loop and get the endpoints using cache
        def sending_request(self,params,responses_req,object_request): # supply the limit as key in the params during call up
            #self.page = 1
            #self.total_pages = 60000 # this is just a dummy number so the loop starts
            while self.page <= self.total_pages:
                #params = {'site_id': '34769','limit': 5000,'page': self.page} #params = {'site_id': '34769','self.page': self.page}
                params['site_id'] = '34769'
                #params['limit'] = 5000
                params['page']=self.page
                    
                # print some output so we can see the status
                print("Requesting self.page {}/{}".format(self.page, int(self.total_pages)))
                # clear the output to make things neater
                clear_output(wait = True)
                #print('params/json,responses_req,self.headers',params,len(responses_req),self.headers)
                # make the API call but check the time to see if it's not more than 8 minutes elapsed
                t1 = time.clock() - self.t0 # recalculate the time difference and get new authorization
                if t1 > 300: #360 secom
                    requests_cache.clear() # clear the cache
                    init_response = get_responses({},'v1/token')
                    second_response = init_response.response_server({})
                    json_response = json_convertion(second_response)
                    json_file_object = json_response.jsonstring_object()
                    object_request.headers['Authorization'] = 'Bearer {}'.format(json_file_object['AccessToken'])#{'Authorization':'Bearer {}'.format(json_file_object['AccessToken'])}
                    self.t0 = time.clock() # redefine the time clock or start time in obtaining the token. # newly added
                    #self.t01 = time.clock()
                    print("Time in sending initial request to api server",self.t0)
                    response = object_request.response_server(params) # polymorphism at display, reponse_server method is the same but depending on the instance of object passed,different method will be called
                    self.diff = time.clock()-self.t0
                    print("Time in receiving response request to api server",self.diff)
                    
                else:
                    #continue with the process
                    self.t02 = time.clock()
                    print("Time in sending initial request to api server",self.t02)
                    response = object_request.response_server(params) # polymorphism at display, reponse_server method is the same but depending on the instance of object passed,different method will be called
                # if we get an error, print the response and halt the loop
                    self.diff = time.clock()-self.t02
                    print("Time in receiving response request to api server",self.diff)
                print('response.status_code',response.status_code)
                if response.status_code != 200:
                    requests_cache.clear()
                    print(response.text)
                    self.page += 1
                    break
                try:
                    # extract pagination info
                    self.page = int(response.json()['paging']['page']) # gets the page number
                    self.total_pages = (int(response.json()['paging']['total'])/float(params['limit']))+1 # 1 added to take care of the rest of the smallest pieces of endpoints
                except:
                    pass
                    print('self.page',self.page)
                    #self.total_pages = (int(len(list_mius))/float(params['limit']))+1 # 1 added to take care of the rest of the smallest pieces of endpoints
                    self.total_pages = self.page

                # append response
                responses_req.append(response) # depending on the object or list that is passed, different responses will be appended. 

                # if it's not a cached result, sleep
                if not getattr(response, 'from_cache', False):
                    time.sleep(0.25)

                # increment the self.page number
                #self.page += 1</code>
                self.page += 1
                #self.total_pages += 1

        # defining a function to recreate the dict1 dictionary through a loop in the response by populating the values with mius, meter number from the endpoints with account as keys
        def recreate_dict1(self,responses_endpoints):
            self.x=0
            self.y=0
            self.z =0
            for i in responses_endpoints:
                response1 = responses_endpoints[self.x].json()
                for j in response1['endpoints']:
                    #response1 = responses[self.x].json()
                    try:
                        self.account_number = response1['endpoints'][self.y]["account_number"] # checking to see whether the "account_number" exists in the json file before proceeding to the next step below
                        #print('account_number',dict1[self.account_number])
                        self.miu_id = str(response1['endpoints'][self.y]["miu_id"])
                        # checking to see whether miu exists in the reference miu list on the spreadsheet before proceeding to the next step
                        if self.miu_id in reference_list_mius:
                            self.meter_number = str(response1['endpoints'][self.y]["meter_number"])
                            dict1[self.account_number][1]['miu_id'].append(self.miu_id)
                            dict1[self.account_number][2]['meter_number'].append(self.meter_number)
                            list_mius.append(self.miu_id) # creating a list of mius
                            print('account_number',dict1[self.account_number])
                        self.y+=1
                    except:
                        self.y+=1
                        pass
                self.x+=1
                self.y=0

            #defining a method to recreate a new dictionary that will have mius as keys and account number, address as values
            for key,value in dict1.items():
                try:
                    for key1 in dict1[key][1]['miu_id']:
                        dict2[key1].append([str(key),str(dict1[key][0])])
                except:

                    pass

            # code to delete mius in dict2 that are not present in the narcoossee dictionary
            # defining a function to delete all accounts from the dict1 that are not present in the spreadsheet
            """
            for key in dict2.keys():
                if not key in dict_narcoossee.keys():
                    try:
                        del dict2[key]
                    except:
                        pass
                    """
        #defining a method to restructure the objects in self.mius_post response object to include the account number and address based on the mius
        # NB: Creating account number and address keys in the response object by using the mius in the response object and comparing it with one in dict2 to obtain corresponding a/c and address
        # original method
        def  restructure_json_file(self,responses_req):
            self.x=0
            self.y=0
            self.z =0
            #self.edited_reponse = []
            for i in responses_req:
                initial_response = responses_req[self.x]
                response1 = initial_response.json()
                for j in response1['endpoints']:
                    #print('test')
                    try:
                        # creating account number key
                        self.accountnumber = dict2[str(response1['endpoints'][self.y]["miu_id"])][0][0] # mius is key now in dict2, a/c - dict4['114528458'][0][0], address - dict4['114528458'][0][1]
                        self.address1 = dict2[str(response1['endpoints'][self.y]["miu_id"])][0][1]
                        #response1['endpoints'][self.y]["account_number"] = dict2[str(response1['endpoints'][self.y]["miu_id"])][0][0] # mius is key now in dict2, a/c - dict4['114528458'][0][0], address - dict4['114528458'][0][1]
                        response1['endpoints'][self.y]["account_number"] = self.accountnumber # mius is key now in dict2, a/c - dict4['114528458'][0][0], address - dict4['114528458'][0][1]
                        response1['endpoints'][self.y]["address"] = self.address1 # get address in dict2 with miu in response object as key and create new address key in response object
                        print('account_number,address',self.accountnumber,self.address1)
                        self.y+=1
                    except:
                        self.y+=1
                        pass
                self.x+=1
                self.y=0
                time.sleep(0.25)
                # append the new edited response object (response1) to a new list of object
                #self.edited_reponse.append(response1) #post_waterconsump_instance.edited_reponse[0]['endpoints'][0]['account_number'] how to access the account number and address from the list
                #self.edited_reponse.append(json.loads(json.dumps(response1))) #j_string = json.dumps(self.response.json()) self.edited_reponse = []
                edited_reponse.append(json.loads(json.dumps(response1))) 


        # defining a method to keep track of the water consumption reads per day where dates are used as keys and number of reads in respect to the date/miu are used as values.
        def dict_test(self):
            global count_date
            self.date2 = str(self.date.split('T')[0])
            if dict3.get(self.date2):
                if dict3.get(self.date2,0)[0] <= 1:
                    count_date = dict3.get(self.date2,0)[0]+1
                #else:
            else:
                count_date = dict3.get(self.date2,0)+1 
            dict3[self.date2] = [count_date]
            #return dict3.get(self.date2,0)[0]
            

        # revised method used to extract the data from the re-structed response object and export the data into a text file
        def export_data(self,file_path,object_data):
            global key1
            global dict3
            self.file_path = file_path 
            self.my_neptune = open(self.file_path,'w')
            #self.my_neptune.write("%-15s%-40s%-35s%-45s%-37s%-37s\n" %('AccountNumber','Address','Meter','MIU','ReadingDate', 'Consumption'))
            self.my_neptune.write("%-15s%-48s%-30s%-30s%-38s%-35s\n" %('AccountNumber','Address','Meter','MIU','ReadingDate', 'Consumption'))
            self.x =0
            self.y=0
            self.object_data = object_data
            if len(self.object_data)>0:
                for i in self.object_data:
                    initial_response = self.object_data[self.x]
                    for j in initial_response['endpoints']:
                        try:
                            dict3 = {} #re-initialize the dictionary for every meter etc.
                            self.account_number1 = str(initial_response['endpoints'][self.y]["account_number"])
                            self.address1 = str(initial_response['endpoints'][self.y]["address"])
                            self.miu_id1 = str(initial_response['endpoints'][self.y]["miu_id"])
                            self.meter_number1 = str(initial_response['endpoints'][self.y]["meter_number"])
                            #y+=1
                        except:
                            #y+=1
                            pass
                        self.z=0
                        self.d=0
                        while self.z < len(initial_response['endpoints'][self.y]["consumption_history"]):
                            self.date = initial_response['endpoints'][self.y]["consumption_history"][self.d]["reading_date"] 
                            self.reading_date1 = dateutil.parser.parse(self.date).strftime('%Y-%m-%d %H:%M:%S') # prints date in  a format like this '2014-05-18 12:19:24' etc . if process is slow, then break it into different variables
                            self.consumption1 = initial_response['endpoints'][self.y]["consumption_history"][self.d]["consumption"]
                            if self.consumption1 != 0:
                                self.dict_test()
                                # Filtering out the code to obtain 1 reading 
                                try:
                                    if dict3[self.date2][0] <= 1:
                                        #self.my_neptune.write("%-15s%-40s%-35s%-45s%-37s%-37s\n" %(self.account_number1,self.address1,self.meter_number1,self.miu_id1,self.reading_date1,self.consumption1))
                                        self.my_neptune.write("%-15s%-48s%-30s%-30s%-38s%-35s\n" %(self.account_number1,self.address1,self.meter_number1,self.miu_id1,self.reading_date1,self.consumption1))
                                        print('date',self.reading_date1)
                                        #elif dict_test(self,self.date) == 3:
                                        #break
                                except:
                                    pass
                            self.z+=1
                            self.d+=1
                        self.y+=1
                    self.x+=1
                    self.y=0
            self.my_neptune.close()
            return
                 
        # defining a recursive method/function to take small bites/chuncks of the mius in tens of thousand and update it in the list after a resquest is sent to the neptune server
        def function_tuple(self,post_waterconsump_inst):
            global tuple_input1
            self.total_pages+=1 # increase property by 1 to account for the rest of the records in the tuple
            if (len(self.objectidstuple) > 1) and (len(self.objectidstuple) > self.yy): #check whether the objectidstuple property/length of tuple is greater than 1 and greater than 10000
                tuple_input1 = self.objectidstuple[self.xx:self.xx+self.yy]
                tuple_input1_list = list(tuple_input1) # convert to a list
                if (len(tuple_input1) == 1):
                    tuple_input1 = "(" + str(tuple_input1[0])+")"
                    #post_waterconsump_instance.sending_request({'limit':100},list_mius_post,post_waterconsump_instance)
                    post_waterconsump_inst.sending_request({'limit':100,"miu_ids":tuple_input1_list,"begin_date": begin_date,"end_date": end_date,"actual_consumption": 'true'},self.mius_post,post_waterconsump_instance) 
                    #self.mius_post
                else:
                    post_waterconsump_inst.sending_request({'limit':100,"miu_ids":tuple_input1_list,"begin_date": begin_date,"end_date": end_date,"actual_consumption": 'true'},self.mius_post,post_waterconsump_instance)
                    index = self.xx+self.yy
                    print "x,index,tuple_input1", self.xx,index,tuple_input1
                    if index < len(self.objectidstuple):
                        self.xx = index
                        self.function_tuple(post_waterconsump_inst) # call the function_tuple method to continue the process

            #check whether the objectidstuple property/length of tuple is greater than 1 and less than 10000
            elif (len(self.objectidstuple) > 1) and (len(self.objectidstuple) < self.y):
                tuple_input1_list2 = list(self.objectidstuple) # convert to a list
                #post_waterconsump_instance.sending_request({'limit':100},list_mius_post,post_waterconsump_instance)
                post_waterconsump_inst.sending_request({'limit':100,"miu_ids":tuple_input1_list2,"begin_date": begin_date,"end_date": end_date,"actual_consumption": 'true'},self.mius_post,post_waterconsump_instance) 

            elif (len(self.objectidstuple) == 1):
                self.objectidstuple = "(" + str(self.objectidstuple[0])+")"
                tuple_input1_list2 = list(self.objectidstuple) # convert to a list
                #post_waterconsump_instance.sending_request({'limit':100},list_mius_post,post_waterconsump_instance)
                post_waterconsump_inst.sending_request({'limit':100,"miu_ids":tuple_input1_list2,"begin_date": begin_date,"end_date": end_date,"actual_consumption": 'true'},self.mius_post,post_waterconsump_instance) 

    # defining a class to initialize xx and yy objects and also use them in obtain the token from the get_responses class through inheritance.     
    class post_responses(get_responses):
        def __init__(self,headers,endpoint):
           get_responses.__init__(self,headers,endpoint)
           self.xx = 0
           self.yy =100
           pass

    # defining a class to get the endpoints from the api server   
    class post_endpoints(get_responses,get_chunks_data):
        def __init__(self,headers,endpoint):
           get_responses.__init__(self,headers,endpoint)
           get_chunks_data.__init__(self,headers,endpoint)
           self.t0= time.clock()
           pass

    # defining a class to get the water consumption from the api server   
    class post_water_comsumption(get_responses,get_chunks_data):
        def __init__(self,headers,endpoint):
           get_responses.__init__(self,headers,endpoint)
           get_chunks_data.__init__(self,headers,endpoint)
           self.xx = 0
           self.yy =100
           self.objectidstuple = tuple(list_mius)
           self.mius_post = []
           self.t0= time.clock()
           pass
        
        # Defining a method to send a request to the neptune api server to obtain the water consumption 
        def response_server(self,json1):
            #self.data = params
            self.json = json1
            #print('test_Response_method,self.requesturl,json1,self.headers',self.requesturl,self.json,self.headers)
            response = requests.post(self.requesturl,json = self.json,headers = self.headers)
            return response

    # Defining a class for json conversion to other object formats         
    class json_convertion:
       def __init__(self,response):
           self.response = response
           pass
       #method to convert the json object to a string
       def jsonobject_string(self):
           #create a formatted string of the object
           #j_string = json.dumps(self.response,sort_keys=True,indent=4)
           j_string = json.dumps(self.response.json())
           #print(j_string)
           return j_string

       # method to convert the json string to an object
       def jsonstring_object(self):
           #create a formatted string of the object
           #j_object = json.loads(self.response,sort_keys=True,indent=4)
           j_object = json.loads(self.jsonobject_string())
           #print(j_object)
           return j_object

    #create an instance of the Check_file class
    conn1 = Check_file("saint_cloud_temp")
    conn1.check_file_existence("saint_cloud_temp",1)

    #case 1 - create an instance of the filter class
    instance1 = filter_saintcloud_records() # create an instance of the filter_saintcloud_records
    instance2 = instance1.openfile(file1,file2) # call the openfile method
    #getClip(queryFeatureClass,clipFeatureClass,output)
    instance1.getClip(saint_cloud_original,Neptune,saint_cloud) # clip against the polygon feature.

    #filtering the saint cloud records - case2
    filter_instance = filter_records()
    #narcoossee(self,my_file)
    filter_instance.narcoossee(my_file) # filtering to get the right accounts
    filter_instance.filter(saint_cloud) # calling the filter method to filter the accounts

    # Creating an instance of the get_responses class to obtain the token
    init_response = get_responses({},'v1/token')
    second_response = init_response.response_server({}) # calling the response_server method to get the token authentication.
    json_response = json_convertion(second_response) # creating an instance of the json_convertion object class
    json_file_object = json_response.jsonstring_object() # calling the jsonstring_object method to convert the json object to a json string.

    # creating instances of the post_endpoints object.
    # sending a request to the api server to get the endpoints
    post_endpoints_instance = post_endpoints({'Authorization':'Bearer {}'.format(json_file_object['AccessToken'])},'v1/endpoints')
    post_endpoints_instance.sending_request({'limit':5000},responses,post_endpoints_instance) # sending limit information and passing and instance of the endpoints object in the request.
    post_endpoints_instance.recreate_dict1(responses)

    # FINAL SCRIPT TO USE FOR THE DATES
    x = 0
    today1 = DT.date.today()
    date_reformat = today1.strftime('%Y-%m-%d %H:%M:%S').split(' ')[0]
    x = 0
    begin_date =""
    end_date = ""
    today = DT.date.today()
    date_month_ago = datetime.today()-relativedelta(months=1) # refine based on the number of months you would like to run
    date = datetime.today() - date_month_ago 
    days_between = int(date.days)
    begin_date_1 = today-DT.timedelta(days=days_between)
    num_of_weeks = int(days_between/7) # rememeber there will be extra days left which will account for the last week
    initial_number_days = num_of_weeks*7
    final_begin_date_initial_number_of_days = today-DT.timedelta(days=initial_number_days)
    number_of_days_left = days_between-initial_number_days
    #limit = num_of_weeks +1
    try:
        #case1
        while x < num_of_weeks:
            end_date = today.strftime('%Y-%m-%d %H:%M:%S').split(' ')[0]
            begin_date1  = today-DT.timedelta(days=6)
            begin_date = begin_date1.strftime('%Y-%m-%d %H:%M:%S').split(' ')[0]
            #print("stuff, carry out operations")
            print("begin_date,end_date",begin_date,end_date)
            #clear cache
            requests_cache.clear()
            # second case of requesting token and start keeping track of the time
            init_response = get_responses({},'v1/token')
            second_response = init_response.response_server({})
            json_response = json_convertion(second_response)
            json_file_object = json_response.jsonstring_object()
            # sending a request to the api server to get the water consumption in bits
            post_waterconsump_instance = post_water_comsumption({'Authorization':'Bearer {}'.format(json_file_object['AccessToken'])},'v1/consumption')
            #post_waterconsump_instance.sending_request({'limit':100,"begin_date": end_date,"end_date": "2022-06-28","actual_consumption": 'true'},list_mius_post,post_waterconsump_instance) # sending limit information and passing and instance of the water consumption object in the request.
            post_waterconsump_instance.function_tuple(post_waterconsump_instance) #self.mius_post = []
            #del post_endpoints_instance # delete post_endpoints_instance # re-initialize post_endpoints_instance = {}
            post_waterconsump_instance.restructure_json_file(post_waterconsump_instance.mius_post) # calling method to restructure the response object for the water consumption
            time.sleep(5)
            del init_response
            del second_response
            del json_response
            del json_file_object
            del post_waterconsump_instance
            today = begin_date1-DT.timedelta(days=1) # subtract one day
            x+=1
            
        #new lines included
        begin_date1_format = begin_date1.strftime('%Y-%m-%d %H:%M:%S').split(' ')[0]
        print("begin_date1_format",begin_date1_format)
        
        #get the first day of the month using the replace method after the first session has ended
        first_date = begin_date1.replace(day=1)
        #print("first_date",first_date)
        first_date_format = first_date.strftime('%Y-%m-%d %H:%M:%S').split(' ')[0]
        print('first_date_format:', first_date_format)
        
        if first_date_format != begin_date1_format: # checks whether the first date of the month coincides with the last date calculated
            #case 2
            x=0
            while x < 1:
                #end_date = begin_date.strftime('%Y-%m-%d %H:%M:%S').split(' ')[0]
                #begin_date_1  = begin_date_1+DT.timedelta(days=1) # instead of begin_date_1  = begin_date_1 - DT.timedelta(days=0) *** subject to review
                #begin_date = begin_date_1.strftime('%Y-%m-%d %H:%M:%S').split(' ')[0]
                begin_date = first_date_format # added gets the first date for the month in question
                end_date = begin_date1-DT.timedelta(days=1) # subtract one day for last session in respect to case 1 after first loop has finished running
                end_date = end_date.strftime('%Y-%m-%d %H:%M:%S').split(' ')[0]
                #print("stuff, carry out operations")
                print("begin_date,end_date",begin_date,end_date)
                #clear cache
                requests_cache.clear()
                # second case of requesting token and start keeping track of the time
                init_response = get_responses({},'v1/token')
                second_response = init_response.response_server({})
                json_response = json_convertion(second_response)
                json_file_object = json_response.jsonstring_object()
                # sending a request to the api server to get the water consumption in bits
                post_waterconsump_instance = post_water_comsumption({'Authorization':'Bearer {}'.format(json_file_object['AccessToken'])},'v1/consumption')
                #post_waterconsump_instance.sending_request({'limit':100,"begin_date": end_date,"end_date": "2022-06-28","actual_consumption": 'true'},list_mius_post,post_waterconsump_instance) # sending limit information and passing and instance of the water consumption object in the request.
                post_waterconsump_instance.function_tuple(post_waterconsump_instance) #self.mius_post = []
                #del post_endpoints_instance # delete post_endpoints_instance # re-initialize post_endpoints_instance = {}
                post_waterconsump_instance.restructure_json_file(post_waterconsump_instance.mius_post) # calling method to restructure the response object for the water consumption
                time.sleep(5)
                del init_response
                del second_response
                del json_response
                del json_file_object
                del post_waterconsump_instance
                #today = begin_date1-DT.timedelta(days=1) # subtract one day
                x+=1
    except:
        pass
        
    #sending a request to the api server to get the water consumption in bits
    #post_waterconsump_instance = post_water_comsumption({'Authorization':'Bearer {}'.format(json_file_object['AccessToken'])},'v1/consumption')
    #post_waterconsump_instance.sending_request({'limit':100,"begin_date": end_date,"end_date": "2022-06-28","actual_consumption": 'true'},list_mius_post,post_waterconsump_instance) # sending limit information and passing and instance of the water consumption object in the request.
    #post_waterconsump_instance.function_tuple(post_waterconsump_instance) #self.mius_post = []
    del responses # delete responses reinialize responses = [] 
    del dict1 # delete responses # re-initialize dict1 = {}
    del post_endpoints_instance # delete post_endpoints_instance # re-initialize post_endpoints_instance = {}

    init_response = get_responses({},'v1/token')
    second_response = init_response.response_server({})
    json_response = json_convertion(second_response)
    json_file_object = json_response.jsonstring_object()
    # sending a request to the api server to get the water consumption in bits
    post_waterconsump_instance = post_water_comsumption({'Authorization':'Bearer {}'.format(json_file_object['AccessToken'])},'v1/consumption')

	#C:\Users\arcgisuser.TOHO_MAIN_HQ\Documents\ArcGIS\saint_cloud
    #file_path = r"C:\Users\mnkum\Desktop\Neptune_Projects\Neptune_Projects.txt"
    #file_path = "O:\\Users\\Nkum\\saint_cloud_scripts" + "\\" + "Water_Consumption_Report" + "_" + date_reformat + ".txt"
    file_path = "C:\\Users\\GISSRV\\Documents\ArcGIS\\saint_cloud" + "\\" + "Water_Consumption_Report" + "_" + date_reformat + ".txt"
    post_waterconsump_instance.export_data(file_path,edited_reponse)

    # deleting object file
    print("Deleting temporary feature class file")
    conn1.check_file_existence("saint_cloud_temp",1)

except:
    import traceback
    scriptSuccess = False
    failmessage = '\n**SCRIPT FAILURE**\n'
    failmessage += 'Most recent GP messages below.\n'
    failmessage += arcpy.GetMessages() +'\n'
    failmessage += '\nTraceback messages below.\n'
    failmessage += traceback.format_exc().splitlines()[-1]
    # Allow connections again.
    pass
    #pass

if scriptSuccess == True: # sending emails for conflict in ownership between Toho owned and private
        send_email(subject, message, from_email, to_email=[''], attachment=[file_path]) 
        print("Done.")
else:
    #message += failmessage
    send_email(subject, failmessage, from_email, to_email=[''])

# remove the file stored on the drive
try:
    time.sleep(30)
    #os.remove(file_path)
    print("file removed")
except:
    pass
    
