from email.mime.text import MIMEText

import json    

import sys

import os

import requests

import time

from pprint import pprint

import pyad.adquery

import pandas as pd

import shutil

import csv

import smtplib

from email.mime.multipart import MIMEMultipart

from email.mime.base import MIMEBase

from email import encoders

import subprocess

import pandas as pd

import openpyxl

import zipfile

import datetime

print("################################################# GITHUB USER FETCH CODE ###############################################################")

 

try:

 

    url="https://gtihub.devops.com/api/v3/orgs/org_name/members"

 

    url_2="https://gtihub.devops.com/api/v3/orgs/org_name/repos"

   

    url_3="https://gtihub.devops.com/api/v3/orgs/org_name/teams"

   

   

    headers = {
        "Authorization": "Bearer {}".format(os.getenv("Token")),
        'Accept' :'application/vnd.github+json',
        "X-Github-Api-Version":"2022-11-28"

    }

 

    payload={"role":"member"}


    payload_3={'per_page':50}



    list_of_repo_names=[]

   

    print("############################################ Getting Repositories #############################################################################")

  

    def getting_repo_name(url_2_var,headers_var):

       

        response2=requests.get(url_2_var,headers=headers_var)

       

        if response2.status_code== 200:

       

        

            link_header=response2.headers.get('Link')

       

            last =None

       

            if link_header:

       

                links=link_header.split(',')

       

                for link in links:

       

                    if "last" in link:

       

                        last = link.split(";")[0].split("?")[1].split('=')[1].replace(">","")

       

            for page in range(1,int(last)+1):

       

                resp = requests.get(url_2_var+f"?page={page}",headers=headers_var)

       

                resp=resp.json()

       

                for json_res in resp:

       

                    list_of_repo_names.append(json_res['name'])

 

            return list_of_repo_names

        else:

            return []

       

        

    print("############################################ Getting Teams #####################################################################")

   

    def getting_teams(url_3_var,headers_var,payload_3_var):

        response3=requests.get(url_3_var,headers=headers_var,params=payload_3_var)

 

        if response3.status_code==200:

 

            response3=response3.json()

           

            list_of_team=[]

           

            list_of_team_slug=[]

           

            for teams_from_res in response3:

               

                list_of_team.append(teams_from_res['name'])

 

                list_of_team_slug.append(teams_from_res['slug'])

            return list_of_team_slug 

        else:

           

  

            print('######################### Error ##################################################',response3.status_code)

            return []

       

    print("########################################## Getting collaborators##################################################")

   

    list_team=[]

   

    for collaborators in getting_repo_name(url_2,headers):

   

        

        curl_cmd= f"""curl.exe -s -H "Accept: application/vnd.github+json" -H "Authorization: Bearer {os.getenv('Token')} -H "X-Github-Api-Version: 2022-11-28" -K https://github.devops.com/api/v3/repos/org/{collaborators}/teams """

      

        res_subprocess=subprocess.run(curl_cmd,capture_output=True)

 

        json_response=json.loads(res_subprocess.stdout.decode())

      

        for detail_of_team in json_response:

            try:

                list_team.append([collaborators,detail_of_team['name'],detail_of_team['permissions']])

 

            except:

                pass

      

       

    

    print("######################################################### REPOSITORIES ACCESS TO TEAMS ########################################################################")

 

    def get_team_members(headers_team_members,payload_team_members):

        list_name=[]

        page_number=1

        while True :

            url=f"https:github.com/api/v3/organization/318/members?pages={page_number}"

 

            response=requests.get(url,headers=headers_team_members)

 

            response=response.json()

           

            list_name+=response

           

            if len(response)==0:

               

                print('Break-')

 

                break   

            

            page_number=page_number+1

 

        return list_name

 

    git_user_detail=[]

 

 

    for users in get_team_members(headers,payload):

     

        git_user_detail.append(users['login'].replace('-',''))

 

    # pprint(git_user_detail)

   

    

 

    print("########################################################## ACTIVE DIRECTORY DATA FETCH ##############################################################")

 

    AD_query = pyad.adquery.ADQuery()

   

    AD_query.execute_query(

 

        attributes = ["distinguishedName", "displayName",'extensionAttribute11','mail','sAMAccountName'],

 

        where_clause = "objectClass = 'user' " ,

 

        base_dn="ad.cibc.com")

 

    AD_query_list=[]

 

    

    for ad_user in AD_query.get_results():

 

        if (ad_user['extensionAttribute11']) != None :

           

            str1=''

           

            str2=''

           

            var1=0

           

            var2=0

 

            for var in ad_user["displayName"]:

 

                if var=="," or var1==1:

 

                    var1=1

 

                    if var == "," or var==" ":

 

                        pass

                    else:

                        str2=str2+var     

                else:

                    str1=str1+var

                   

                    var2=var2+1

       

            AD_query_list.append({(str2+str1) :ad_user['extensionAttribute11'],'email':ad_user['mail'],'SAM_accountName':ad_user['sAMAccountName'],'DisplayName':ad_user['displayName']})

 

   

        else:

   

            pass

 

    

    print("################################################## ACTIVE DIRECTORY QUERY LIST ###################################################")
    final_list_user=[]

 

    for userAD_var in AD_query_list:

        check_var_unindentified=0

        for userAD_var2 in userAD_var.keys():

            for usergit in git_user_detail:

                if userAD_var2.casefold() == usergit.casefold():

                    check_var_unindentified=1

                    git_user_detail.remove(usergit)

                    final_list_user.append(userAD_var)

                    break

                else:

                    pass

          

            

 

  

   

    pprint(final_list_user)

    print("################################################# FINAL LIST OF USER COMMON IN GITHUB AND AD###########################################")

  

    compare_list=[]

 

    for user_team_names in getting_teams(url_3,headers,payload_3):

      

        url_4=f"https://github.com/api/v3/orgs/team/{user_team_names}/members"

      

        response4=requests.get(url_4,headers=headers)

      

        response4=response4.json()

      

        for getting_name in response4:

      

            compare_list.append({getting_name['login'].replace('-',''):user_team_names})

  

   

    for compare_list_var in compare_list:

      

        for key,val in compare_list_var.items():

         

            index=0

         

            for list_team_var in list_team:

         

                if list_team_var[1].casefold()==val.casefold():

                   

                    for var_for_email in final_list_user:

                        var_check_3=0

                        for key_2,value_2 in var_for_email.items():

                            if var_check_3==0:

                                if key.casefold()==key_2.casefold():

           

                                    list_team[index].append(var_for_email)

                                var_check_3+=1

                index+=1   

  

   

    list_of_manager=[]

   

    for x in final_list_user:

        var_check_2=0

        for key,val in x.items():

            if var_check_2==0:

                list_of_manager.append(val)

                var_check_2+=1

   

    list_of_manager=(set(list_of_manager))


    

    

    final_list=[]

   

    for x in list_of_manager:

   

        for y in list_team:

   

            dict=[]

   

            var=0

   

            check=0

   

            newvar=1

   

            for bb in y[3:]:

   

                a=len(y)-3

                var_check_4=0

                for key,value in bb.items():

                    if var_check_4==0:

                        if x.casefold() == value.casefold():

       

                            if (var > 0):

       

                                dict.append([bb])

       

                                if newvar==a:

       

                                    check=2

       

                                    final_list.append([x,dict])

       

                                else:

       

                                    pass

       

                            else :

       

                                check=1

       

                                dict.append([y[0],y[1],y[2]])

       

                                dict.append([bb])

       

                                var+=1      

                        if dict!=[] and newvar==a and check==1:

                   

                                final_list.append([x,dict])

                   

                        newvar+=1

                        var_check_4+=1

 

    print(final_list)

   

    try:

        print('################################################### Deleting Old Files ###############################################################################')

        cwd=os.getcwd()

 

        for filename in os.listdir(cwd):

            if filename.endswith('.zip'):

                print(os.remove(filename))

        csv_folder_path='csv_files_dir'

     

        shutil.rmtree(csv_folder_path)

    except:

        print('Folder doesnt exit')

        pass

   

    folder_name='csv_files_dir'

   

    os.mkdir(folder_name)

  

    for x_in_list_manager in list(list_of_manager):

   

        count=1

      

        listt=[]

      

        for y_in_final_list in final_list:

      

            if x_in_list_manager.casefold()==y_in_final_list[0].casefold():

          

                manager=y_in_final_list[0]

      

                listt.append(y_in_final_list[1:])

        

       

            if len(final_list)==count and listt != []:

   

                csv_data = []

       

                for i_listt in listt:

       

                    for j_i in i_listt:

      

                        for aa in range(1,len(j_i[1:])+1):

                            key_user=list(j_i[aa][0].keys())

                            key_email=list(j_i[aa][0].values())

                            key_sAMAccountName=list(j_i[aa][0].values())

                            csv_data.append([key_user[0],j_i[0][0], j_i[0][1], j_i[0][2]['admin'],j_i[0][2]['maintain'],j_i[0][2]['pull'],j_i[0][2]['push'],j_i[0][2]['triage'],key_email[1],key_sAMAccountName[2],key_sAMAccountName[3]])

       

                for i in range(len(csv_data)):

      

                    csv_data[i][0]=str(csv_data[i][0]).replace("'",'').replace('[','').replace(']','')

            

       

                merged_rows=[]

      

                a=0

      

                iter_var=0

      

                for outer_csv_data in csv_data:

      

                    iter_var2=0

      

                    for inner_csv_data in csv_data[1:]:

      

                        if outer_csv_data[2:] ==inner_csv_data[2:] and outer_csv_data[0] ==inner_csv_data[0]:

      

                            if outer_csv_data==inner_csv_data:

      

                                exit

      

                            else:

      

                                csv_data[iter_var][1]="\n"+inner_csv_data[1].upper()+"," +outer_csv_data[1].upper()

      

                                csv_data.remove(inner_csv_data)      

       

                        else:

      

                            pass

      

                        iter_var2+=1

      

                    iter_var+=1

      

                new_csv_data=[]

               

                for row in csv_data:

                    new_row=[row[10],row[9],row[8]]+row[:8]+row[11:]

                    new_csv_data.append(new_row)

                   

             

 

                headerss = ['DisplayName','AD-ID','Email','UserName (GitHub)','Repository','Teams (Github)','Admin','Maintain','Pull','Push','Triage','Attestation',"Comments"]

                

                with open(fr'csv_files_dir/{manager.split("@")[0]}.csv', 'w', newline='') as csvfile:

       

                    csv_writer = csv.writer(csvfile)

       

                    csv_writer.writerow(headerss)

       

                    csv_writer.writerows(new_csv_data)

               

              

            count+=1

           

 

    df =pd.DataFrame({'UserName(GitHub)':git_user_detail,'Comments':['']*len(git_user_detail)})

    df.to_excel('csv_files_dir/unidentified.xlsx',index=False)

 

    csv_folder_dir = 'csv_files_dir/'

    pprint('csv to xlsx conversion')

    for filename in os.listdir(csv_folder_dir):

        if filename.endswith('.csv'):

            csv_path=os.path.join(csv_folder_dir,filename)

            df = pd.read_csv(csv_path)

            xlsx_path=os.path.splitext(csv_path)[0]+ ".xlsx"

            df.to_excel(xlsx_path,index=False)

            os.remove(csv_path)

    timestamp= datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    pprint('zip file creation')

    folder_name="csv_files_dir"

    zip_files_name=f"attestation_files_{timestamp}.zip"

    folder_path=os.path.abspath(folder_name)

    files=os.listdir(folder_path)

    with zipfile.ZipFile(zip_files_name,'w') as zip_file:

        for file in files:

            file_path= os.path.join(folder_path, file)

            zip_file.write(file_path, file)

    pprint('zip folder created')

    pprint(list_of_manager)

 

except Exception as error:

   

    response ={

 

        'Exception':str(error)

    }

   

    pprint(response)

 