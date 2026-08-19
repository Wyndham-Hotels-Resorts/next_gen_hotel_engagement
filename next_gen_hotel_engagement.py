# -*- coding: utf-8 -*-
"""
Created on Mon Oct 27 11:26:30 2025

@author: 540965
"""

import pandas as pd
import numpy as np
import tableauserverclient as TSC
import datetime
import traceback

from Birst_Includes import AWS_Utils
from Birst_Includes import Birst_Utils

from Birst_Includes import sf_connector, AWS_Utils
s3 = AWS_Utils.GetAWSClient()

s3 = AWS_Utils.GetAWSClient()
#file_path = os.path.dirname(os.path.abspath(__file__)) + '/'
file_path_sources = './SourceFiles/'
file_path_outputs =  'D:/Business Intelligence/Tableau/next_gen_hotel_engagement/' #''E:/Business Intelligence/Tableau/Next_Gen_QA_Pip/''  

logFileName = 'next_gen_hotel_engagement_data_automation_output.txt'
logFilePath = 'D:/Business Intelligence/PythonScripts/next_gen_hotel_engagement/' + logFileName #D:/Business Intelligence/PythonScripts/next_gen_hotel_engagement/

errorEmailTo = ['anshul.maathur1@wyndham.com','eric.kwok@wyndham.com', 'daniel.dai@wyndham.com','brian.mohr@wyndham.com','businessintelligence@wyndham.com']
errorEmailSubject = 'Next Gen Hotel Engagement Data Automation - Error'
successEmailTo = ['anshul.maathur1@wyndham.com','eric.kwok@wyndham.com', 'daniel.dai@wyndham.com','brian.mohr@wyndham.com','businessintelligence@wyndham.com']
successEmailSubject = 'Next Gen Hotel Engagement Data Automation - Success'

fileName_Hotel_Engagement = 'Hotel Engagement'
fileName_Waiver = 'Waiver'
fileName_contract = 'Contract'
fileName_user = 'User'
fileName_action_plans = 'action_plans'
action_plans_ota = 'action_plans_ota'
fileName_photo = 'photo'
fileName_account = 'FEMA Account'
fileName_owner = 'opportunity owner'
fileName_funding = 'funding'
fileName_funding_date ='Funding_date'

spaceID = '0f8fd184-9964-4ecb-a8a0-dad517e12dab'  # WHR Business Intelligence - Production

def Getsitedata(in_client):
    try:
        
        # Get data from birst
        #login = in_client.service.Login(Birst_Utils.GetBirstUser(), Birst_Utils.GetBirstPassword())
        #spaceID = 'a503244e-dfbc-44f0-93ce-1e8bea95dcef' #NT-STR - Production
        query = "SELECT USING OUTER JOIN [Site_Mapping.CHAIN_CODE_CURR] 'COL1' , [Site_Mapping.DFO] 'COL2' ,[Site_Mapping.RDFO] 'COL3' ,\
                 [Site_Mapping.SAME_STORE_CURR] 'COL4' , [Site_Mapping.SDFO] 'COL5' , [Site_Mapping.site_id] 'COL6',\
                 [Site_Mapping.country_name] 'COL7' , [Site_Mapping.Chain Scale Curr] 'COL8',[Site_Mapping.STR_STATE_CD] 'COL9',\
                 [Site_Mapping.STR Region] 'COL10' , [Site_Mapping.brand_nm_cur] 'COL11',[Site_Mapping.CDRM/RM] 'COL12',\
                 [Site_Mapping.Site Name Curr Fix] 'COL13', [Site_Mapping.Highgate_Flag] 'COL14',[Site_Mapping.fran_agr_acct_num] 'COL15',\
                 [Site_Mapping.same_store_upscale] 'COL16', [Site_Mapping.Time Period] 'COL17',[Site_Mapping.FAC Member Flag]'COL18',\
                 [Site_Mapping.mgmnt_cmpny]'COL19',[Site_Mapping.sf_portfolio]'COL20'\
                 FROM [ALL] WHERE ( ( [Site_Mapping.cur_site_flg]='Y' ))"
                 
        data = Birst_Utils.QueryData(in_client, login, spaceID, query, 25000)
        
        # Set column headers
        data.columns = ['Chaincode',  'DFO',  'RDFO',  'Same Store',  'SDFO',  'site_id',  'Country',  'Chain Scale',  'State',  'STR Region', 
                        'Brand Name',  'Revenue Manager',  'Site Name',  'Highgate Flag', 'Franchise Agreement Account Number',  'Same Store Upscale', 
                        'Time Period', 'FAC Flag',  'Management Company',  'SF Portfolio']
        
        data['site_id'] = data['site_id'].astype(str)
        data['DFO'] = data['DFO'].str.lower()
        data['Franchise Agreement Account Number'] = data['Franchise Agreement Account Number'].astype(str)
    
        print('data DF:')
        print(data)
        
        return data

    except Exception as e:
        print(e)
        raise e

def sf_he_item(_sf, _sf_queries_dir) -> pd.DataFrame:
    
    with open(rf'{_sf_queries_dir}he_item_query.txt') as q:
        he_item_query = q.read()
    
    print(he_item_query)
    he_item_dict = _sf.query_all(he_item_query)
    
    # The 'attributes' column contains stuff like object name and the REST API endpoint accessed.
    df_he_item = pd.DataFrame(he_item_dict['records']).drop(columns=['attributes'])
    df_he_item.columns = ['Id', 'IsDeleted', 'Name', 'RecordTypeId', 'CreatedDate', 'LastModifiedDate', 
                          'SystemModstamp', 'LastActivityDate', 'LastViewedDate', 'LastReferencedDate', 
                          'ConnectionReceivedId', 'ConnectionSentId', 'Hotel Engagement ID', 'Assignee', 
                          'Description', 'Due Date', 'GSC Catalog Item Category1', 'GSC Catalog Item Category2', 
                          'GSC Catalog Item Created Date', 'GSC Catalog Item Disabled Date', 'GSC Catalog Item ID', 
                          'GSC Catalog Item Name', 'GSC Catalog Item Updated Date', 'GSC Custom ID', 'GSC PIP Active', 
                          'Hotel Engagement Status', 'Title', 'Completed Date', 'ContractId GSC Catalog Item ID', 
                          'GSC Catalog Item Category3', 'GSC Item', 'Legacy Id', 'Time Frame', 'Internal Files', 
                          'Brand Standards Description', 'Calculated Due Date', 'Cleanliness', 'Compliance', 'Condition', 
                          'Contract', 'Failed PIP Item', 'Safety Time Sensitive Item', 'Brand Standard Number', 'Subcategory']
    
    print('df_he_item info:')
    print(df_he_item.info())
    print(f'df_he_item shape: {df_he_item.shape}')
    
    print(df_he_item)
    
    # df_he_item.to_csv(file_path_outputs + 'df_he_item' + '.csv', index=False, sep=',', header=True,
    #             date_format='%Y-%m-%d')
    
    dist_col_count = df_he_item['Hotel Engagement ID'].nunique()
    print(f"Distinct count in 'col1': {dist_col_count}")
    
    df_he_item['ID Count'] = df_he_item.groupby(['Brand Standard Number', 'Hotel Engagement ID'])['Id'].transform('count')
    df_he_item['Status Count'] = 1
    df_he_item['Cleanliness Count'] = df_he_item['Cleanliness'].astype(int)
    df_he_item['Compliance Count'] = df_he_item['Compliance'].astype(int)
    df_he_item['Condition Count'] = df_he_item['Condition'].astype(int)
    df_he_item['Failed PIP Item Count'] = df_he_item['Failed PIP Item'].astype(int)
    df_he_item['Safety Time Sensitive Item Count'] = df_he_item['Safety Time Sensitive Item'].astype(int)

    # df_he_item['Cleanliness Count'] = df_he_item.groupby(['Hotel Engagement ID', 'GSC Catalog Item Category1', 'Subcategory', 'Hotel Engagement Status'])['Cleanliness'].transform(sum)
    # df_he_item['Compliance Count'] = df_he_item.groupby(['Hotel Engagement ID', 'GSC Catalog Item Category1', 'Subcategory', 'Hotel Engagement Status'])['Compliance'].transform(sum)
    # df_he_item['Condition Count'] = df_he_item.groupby(['Hotel Engagement ID', 'GSC Catalog Item Category1', 'Subcategory', 'Hotel Engagement Status'])['Condition'].transform(sum)
    # df_he_item['Failed PIP Item Count'] = df_he_item.groupby(['Hotel Engagement ID', 'GSC Catalog Item Category1', 'Subcategory', 'Hotel Engagement Status'])['Failed PIP Item'].transform(sum)
    # df_he_item['Safety Time Sensitive Item Count'] = df_he_item.groupby(['Hotel Engagement ID', 'GSC Catalog Item Category1', 'Subcategory', 'Hotel Engagement Status'])['Safety Time Sensitive Item'].transform(sum)

    # Rename specific records in the 'Category' column
    df_he_item['GSC Catalog Item Category1'] = df_he_item['GSC Catalog Item Category1'].replace({'Meeting and Business': 'Meeting & Business', 
                                                                                                 'Lobby and Front Desk': 'Lobby & Front Desk',
                                                                                                 'Food and Beverage': 'Food & Beverage'})
    
    df_he_item = df_he_item[['ID Count', 'Brand Standard Number', 'Hotel Engagement ID', 
                              'GSC Catalog Item Category1', 'GSC Catalog Item Category2',	
                              'Subcategory', 'Hotel Engagement Status', 'Cleanliness', 
                              'Compliance', 'Condition', 'Failed PIP Item', 'Status Count',
                              'Cleanliness Count', 'Compliance Count', 'Condition Count',
                              'Failed PIP Item Count', 'Safety Time Sensitive Item',
                              'Safety Time Sensitive Item Count', 'Time Frame']]
    
    df_he_item.to_csv(file_path_outputs + 'df_he_item' + '.csv', index=False, sep=',', header=True,
                date_format='%Y-%m-%d')
       
    return df_he_item

def sf_he_qa(_sf, _sf_queries_dir) -> pd.DataFrame:
    
    with open(rf'{_sf_queries_dir}he_qa_query.txt') as q:
        he_qa_query = q.read()
    
    print(he_qa_query)
    he_qa_dict = _sf.query_all(he_qa_query)
    
    # The 'attributes' column contains stuff like object name and the REST API endpoint accessed.
    df_he_qa = pd.DataFrame(he_qa_dict['records']).drop(columns=['attributes'])
    
    df_he_qa.columns = ['ID','Name', 'RecordTypeId', 'Contract', 'Status','Type',	'Contract Name',
                        'QA Last Inspection Date', 'QA Last Inspection Grade',	'QA Last Inspection Score',	
                        'QA Last Inspection Type',	'Action Plan Status',	'Administrative Policies Score',
                        'Anticipated Inspection Date',	'Failed Reason',	'Food Beverage Score',
                        'General Manager','Guestroom Score', 'Hazard Items',	'Hotel Arrival and Exterior Score',
                        'Hotel Facilities Score',	'Inspection Performed By',	'Lobby Front Desk Score',
                        'Meeting Business Score',	'Overall Result History',	'Overall Score History',
                        'PIP Failures',	'Property Commencement Date',	'Property Open Date',
                        'Reinspection Number',	'Rescored',	'Safety',	'Scheduled Inspection Date',	
                        'Total Passed Questions Administrative',	'Total Passed Questions Food Beverage',
                        'Total Passed Questions Guestroom',	'Total Passed Questions Hotel Arrival',
                        'Total Passed Questions Hotel Facilities',	'Total Passed Questions Lobby Front Desk',
                        'Total Passed Questions Meeting Business',	'Total Questions Administrative Policies',
                        'Total Questions Food Beverage',	'Total Questions Guestroom',	'Total Questions Hotel Arrival Exterior',	
                        'Total Questions Hotel Facilities', 'Total Questions Lobby Front Desk',	'Total Questions Meeting Business',	
                        'Administrative Policies Results',	'Failed Reason Formula',	'Food Beverage Results',	'Guestroom Results',	
                        'Hotel Arrival and Exterior Results',	'Hotel Facilities Results',	'Inspector Is Current Running User',
                        'Lobby Front Desk Results',	'Location',	'Meeting Business Results',	'Overall Grade', 'Overall Score',
                        'QA Inspection Date',	'Total Passed Questions', 'Total Questions',	'Special Request Type',
                        'Latest Inspection Indicator',	'Cure Date',	'Special Request',	'Special Request Date',
                        'Special Request Comments',	'Inspection Start Time',	'Inspection End Time', 'Count of Waivers',
                        'Cleanliness Blitzes', 'Quality Matters Workshop',	'Quality Matters Workshop 2', 'Remedial Training',
                        'Remedial Training Charge Date', 'Required For Capital Funding', 'Account', 'PIP Type',
                        'PIP Inspection Date']
    
    df_he_qa['Contract Name'] = df_he_qa['Contract Name'].astype(str)
    df_he_qa['RecordTypeDesc'] = df_he_qa['RecordTypeId'].apply(lambda row: 'QA' if row == '0124u000000YX32AAG' or row == '0124u000000YX3dAAG'  else 'PIP')
    
    print(df_he_qa['Contract Name'].unique())
    
    print('df_he_qa info:')
    print(df_he_qa.info())
    print(f'df_he_qa shape: {df_he_qa.shape}')
    
    print(df_he_qa)

    # df_he_qa.to_csv(file_path_outputs + 'df_he_qa' + '.csv', index=False, sep=',', header=True,
    #             date_format='%Y-%m-%d')
       
    return df_he_qa

def sf_user(_sf, _sf_queries_dir) -> pd.DataFrame:
    
    with open(rf'{_sf_queries_dir}user_query.txt') as q:
        user_query = q.read()
    
    print(user_query)
    user_dict = _sf.query_all(user_query)
    
    df_user = pd.DataFrame(user_dict['records']).drop(columns=['attributes'])
    df_user.columns = ['Id', 'Name']
    
    print('df_user info:')
    print(df_user.info())
    print(f'df_user shape: {df_user.shape}')
    
    df_user['Id'] = df_user['Id'].astype(str)
    
    df_user = df_user[['Id', 'Name']]
    
    # print(df_user)

    df_user.to_csv(file_path_outputs + fileName_user + '.csv', index=False, sep=',', header=True,
                date_format='%Y-%m-%d')
       
    return df_user


def sf_contract(_sf, _sf_queries_dir) -> pd.DataFrame:
    
    with open(rf'{_sf_queries_dir}contract_query.txt') as q:
        contract_query = q.read()
    
    print(contract_query)
    contract_dict = _sf.query_all(contract_query)
    
    df_contract = pd.DataFrame(contract_dict['records']).drop(columns=['attributes'])
    df_contract.columns = ['Contract ID', 'Contract Name', 'Openings_Manager', 'Previously_Affiliated_Brand', 'Distribution_Launch_Manager', 'Opportunity__c', 'Program_Participation__c', 'Application_Type__c']
    
    print('df_contract info:')
    print(df_contract.info())
    print(f'df_contract shape: {df_contract.shape}')
    
    df_contract['Contract ID'] = df_contract['Contract ID'].astype(str)
    
    # df_contract = pd.read_csv(file_path_outputs + fileName_contract + '.csv')
    df_user = pd.read_csv(file_path_outputs + fileName_user + '.csv')
    
    df_merged = df_contract.merge(
    df_user[['Id', 'Name']], 
    left_on='Openings_Manager', 
    right_on='Id', 
    how='left'
    )
    df_merged = df_merged.drop(columns=['Id', 'Openings_Manager'])
    # Rename the newly added 'name' column to be specific
    df_merged = df_merged.rename(columns={'Name': 'Openings_Manager'})

    # 2. Second merge: Get the name for Distribution_Launch_Manager_id
    df_merged = df_merged.merge(
        df_user[['Id', 'Name']], 
        left_on='Distribution_Launch_Manager', 
        right_on='Id', 
        how='left'
        )
    df_merged = df_merged.drop(columns=['Id', 'Distribution_Launch_Manager'])
    
    # Rename the second 'name' column
    df_contract = df_merged.rename(columns={'Name': 'Distribution_Launch_Manager'})
    
    df_contract.info()
    
    df_contract = df_contract[['Contract ID', 'Contract Name', 'Openings_Manager', 'Previously_Affiliated_Brand', 'Distribution_Launch_Manager', 'Opportunity__c', 'Program_Participation__c', 'Application_Type__c']]
    

    df_contract.to_csv(file_path_outputs + fileName_contract + '.csv', index=False, sep=',', header=True,
                date_format='%Y-%m-%d')
       
    return df_contract


def sf_waiver(_sf, _sf_queries_dir) -> pd.DataFrame:
    
    with open(rf'{_sf_queries_dir}waiver_query.txt') as q:
        waiver_query = q.read()
    
    print(waiver_query)
    waiver_dict = _sf.query_all(waiver_query)
    
    # The 'attributes' column contains stuff like object name and the REST API endpoint accessed.
    df_waiver = pd.DataFrame(waiver_dict['records']).drop(columns=['attributes'])
    df_waiver.columns = ['Id', 'Owner Id', 'Name', 'Created Date', 'Last Modified Date', 'System Modstamp', 'Last Activity Date', 
                          'Account', 'Brand Standards Description', 'Comments to Waiver Requestor', 'Contract Status', 'Contract', 
                          'Date of Request', 'Date of approval', 'Hotel Engagement Item', 'Inspection Category', 'Internal Comments', 
                          'Internal Description', 'Site ID', 'Waiver Approver', 'Waiver Description', 'Waiver Expiration Date', 
                          'Waiver Rationale', 'Waiver Requested Extension Date', 'Waiver Status', 'Waiver Type', 'Property Brand Standards', 
                          'BSD Category', 'BSD Subcategory', 'Brand Standard Number', 'Expired', 'Waiver Classification', 'Account DFO', 
                          'Expected Ship Date', 'Waiver Additional Details', 'Waiver Conditional Details', 'Waiver Sub']
    
    df_waiver['Contract'] = df_waiver['Contract'].astype(str)
    
    print('df_waiver info:')
    print(df_waiver.info())
    print(f'df_waiver shape: {df_waiver.shape}')
    
    print(df_waiver)
    
    # df_waiver.to_csv(file_path_outputs + 'df_waiver' + '.csv', index=False, sep=',', header=True,
    #             date_format='%Y-%m-%d')
       
    return df_waiver

def sf_brand_std_desc(_sf, _sf_queries_dir) -> pd.DataFrame:
    
    with open(rf'{_sf_queries_dir}brand_std_desc_query.txt') as q:
        brand_std_desc_query = q.read()
    
    print(brand_std_desc_query)
    brand_std_desc_dict = _sf.query_all(brand_std_desc_query)
    
    df_brand_std_desc = pd.DataFrame(brand_std_desc_dict['records'])[['Id', 'Description__c']]
    df_brand_std_desc.columns = ['ID', 'Brand Description Name']
    
    print('df_brand_std_desc info:')
    print(df_brand_std_desc.info())
    print(f'df_brand_std_desc shape: {df_brand_std_desc.shape}')
    
    print(df_brand_std_desc)
    
    # df_brand_std_desc.to_csv(file_path_outputs + 'df_brand_std_desc' + '.csv', index=False, sep=',', header=True,
    #             date_format='%Y-%m-%d')
       
    return df_brand_std_desc

def sf_action_plans(_sf, _sf_queries_dir) -> pd.DataFrame:
    
    with open(rf'{_sf_queries_dir}action_plans_query.txt') as q:
        action_plans_query = q.read()
    
    print(action_plans_query)
    action_plans_dict = _sf.query_all(action_plans_query)
    
    df_action_plans = pd.DataFrame(action_plans_dict['records']).drop(columns=['attributes'])
    
    
    # The 'attributes' column contains stuff like object name and the REST API endpoint accessed.
    df_action_plans.columns = ['Id',
                               'Name',
                               'OwnerId',
                               'Action_Plan__c',
                               'Status__c',
                               'contract__c',
                               'Description__c',
                               'TaskRecordTypeID__c',
                               'Completed__c',
                               'Completed_Tasks_Count__c',
                               'Franchise_Task_Total_Role__c',
                               'Franchisee_Task_Completion__c',
                               'Franchisee_Task_Completion_Category__c',
                               'Franchisee_Task_Completion_Role__c',
                               'Franchisee_Task_Opened_Category__c',
                               'Franchisee_Task_Opened_Role__c',
                               'Franchisee_Task_Pending_Category__c',
                               'Franchisee_Task_Pending_Percentage__c',
                               'Franchisee_Task_Pending_Role__c',
                               'Franchisee_Task_Reopened_Category__c',
                               'Franchisee_Task_Reopened_Role__c',
                               'Franchisee_Task_Total_Category__c',
                               'Open_Tasks__c',
                               'Outstanding_Tasks_Count__c',
                               'Overdue_Task__c',
                               'Overdue_Tasks__c',
                               'Task_Completion__c',
                               'Task_Status_Formula__c',
                               'Total_Tasks__c',
                               'Total_Tasks_Count__c']
    
    
    print('df_action_plans info:')
    print(df_action_plans.info())
    # print(f'df_action_plans shape: {action_plans_query.shape}')
    # print(df_action_plans)
    
    df_action_plans = df_action_plans[['contract__c', 'Completed_Tasks_Count__c', 'Total_Tasks_Count__c']]
    
    df_action_plans = df_action_plans.groupby('contract__c')[['Completed_Tasks_Count__c', 'Total_Tasks_Count__c']].sum().reset_index()
    
    df_action_plans.to_csv(file_path_outputs + fileName_action_plans + '.csv', index=False, sep=',', header=True,
                date_format='%Y-%m-%d')
    
def sf_action_plans_ota(_sf, _sf_queries_dir) -> pd.DataFrame:
    
    with open(rf'{_sf_queries_dir}action_plans_ota_query.txt') as q:
        action_plans_ota_query = q.read()
    
    print(action_plans_ota_query)
    action_plans_ota_dict = _sf.query_all(action_plans_ota_query)
    
    df_action_plans_ota = pd.DataFrame(action_plans_ota_dict['records']).drop(columns=['attributes'])
    
    
    # The 'attributes' column contains stuff like object name and the REST API endpoint accessed.
    df_action_plans_ota.columns = [
        'id',
        'recordtypeid',
        'whoid',
        'whatid',
        'whocount',
        'whatcount',
        'subject',
        'activitydate',
        'status',
        'priority',
        'ishighpriority',
        'ownerid',
        'description',
        'type',
        'isdeleted',
        'accountid',
        'tasksubtype',
        'completeddatetime',
        'task_type__c',
        'comments__c',
        'gsofollowupdate__c',
        'results__c',
        'gsoactivity_reason__c',
        'original_task_id__c',
        'next_steps__c',
        'cr_case__c',
        'tag__c',
        'site_visit_metric__c',
        'item__c',
        'journal_subject__c',
        'task_origin__c',
        'action_plan_name__c',
        'action_plan__c',
        'actvty_id__c',
        'approval_status__c',
        'category_name__c',
        'completion_date__c',
        'contract_name__c',
        'marked_complete_date__c',
        'task_subcategory__c',
        'state__c',
        'whr_initiative_type__c' ]
            
    
    print('df_action_plans_ota info:')
    print(df_action_plans_ota.info())
    
    
    df_action_plans_ota = df_action_plans_ota[['subject', 'completion_date__c', 'contract_name__c']]
    
    df_action_plans_ota = df_action_plans_ota.pivot_table(
    index='contract_name__c', 
    columns='subject', 
    values='completion_date__c',
    aggfunc='max' # Keeps the latest completion date if duplicates exist
    ).reset_index()
    
    df_action_plans_ota.to_csv(file_path_outputs + action_plans_ota + '.csv', index=False, sep=',', header=True,
                date_format='%Y-%m-%d')
    
def sf_photo(_sf, _sf_queries_dir) -> pd.DataFrame:
    
    with open(rf'{_sf_queries_dir}photo_query.txt') as q:
        photo_query = q.read()
    
    print(photo_query)
    photo_dict = _sf.query_all(photo_query)
    
    df_photo = pd.DataFrame(photo_dict['records']).drop(columns=['attributes'])
    
    
    # The 'attributes' column contains stuff like photo name and the REST API endpoint accessed.
    df_photo.columns = ['Photo_Shoot_Actual_Date__c', 'Contract_Name__c', 'Name']
    
    df_photo['Photo_Shoot_Actual_Date__c'] = pd.to_datetime(df_photo['Photo_Shoot_Actual_Date__c'])

    # 2. Group by Contract and find the Max (Latest) date
    df_photo = df_photo.groupby('Contract_Name__c')['Photo_Shoot_Actual_Date__c'].max().reset_index()

    # 3. Rename the column for clarity
    df_photo.columns = ['Contract_Name__c', 'Latest_Photo_Shoot_Date']

    print(df_photo)
    
    
    print('df_photo info:')
    print(df_photo.info())
    # print(f'df_photo shape: {photo_query.shape}')
    # print(df_photo)
    
    df_photo.to_csv(file_path_outputs + fileName_photo + '.csv', index=False, sep=',', header=True,
                date_format='%Y-%m-%d')
    
    
def sf_account(_sf, _sf_queries_dir) -> pd.DataFrame:
        
    with open(rf'{_sf_queries_dir}account_query.txt') as q:
            account_query = q.read()
        
    print(account_query)
    account_dict = _sf.query_all(account_query)
        
    df_account = pd.DataFrame(account_dict['records']).drop(columns=['attributes'])
        
        
    # The 'attributes' column contains stuff like account name and the REST API endpoint accessed.
    df_account.columns = ['FEMA_ID__c', 'Contract_Name__c' , 'FEMA_ID_Expiration_Date__c']
        
        
    print('df_account info:')
    print(df_account.info())
    columns_to_check = ['FEMA_ID__c', 'Contract_Name__c', 'FEMA_ID_Expiration_Date__c']

    # Drop rows where ALL of the specified columns are NaN
    df_account = df_account.dropna(subset=columns_to_check, how='all')

        
    df_account.to_csv(file_path_outputs + fileName_account + '.csv', index=False, sep=',', header=True,
                    date_format='%Y-%m-%d')
    
def sf_owner(_sf, _sf_queries_dir) -> pd.DataFrame:
        
    with open(rf'{_sf_queries_dir}owner_query.txt') as q:
            owner_query = q.read()
        
    print(owner_query)
    owner_dict = _sf.query_all(owner_query)
        
    df_owner = pd.DataFrame(owner_dict['records']).drop(columns=['attributes'])
        
        
    # The 'attributes' column contains stuff like owner name and the REST API endpoint accessed.
    df_owner.columns = ['OwnerId', 'Contract_Name__c', 'Opportunity Name', 'Opportunity Id']        
        
    print('df_owner info:')
    print(df_owner.info())
    
    df_user = pd.read_csv(file_path_outputs + fileName_user + '.csv')
    
    df_merged = df_owner.merge(
    df_user[['Id', 'Name']], 
    left_on='OwnerId', 
    right_on='Id', 
    how='left'
    )
    df_merged = df_merged.drop(columns=['Id', 'OwnerId'])
    # Rename the newly added 'name' column to be specific
    df_merged = df_merged.rename(columns={'Name': 'Opportunity Owner'})

        
    df_merged.to_csv(file_path_outputs + fileName_owner + '.csv', index=False, sep=',', header=True,
                    date_format='%Y-%m-%d')
    
def sf_funding(_sf, _sf_queries_dir) -> pd.DataFrame:
    
    with open(rf'{_sf_queries_dir}funding_query.txt') as q:
        funding_query = q.read()
    
    print(funding_query)
    funding_dict = _sf.query_all(funding_query)
    
    funding_query = pd.DataFrame(funding_dict['records']).drop(columns=['attributes'])
    funding_query.columns = ['Id', 'Name', 'Contract Id']
    
    print('funding_query info:')
    print(funding_query.info())
    print(f'funding_query shape: {funding_query.shape}')
    
    funding_query['Id'] = funding_query['Id'].astype(str)
    
    funding_query = funding_query[['Id', 'Name', 'Contract Id']]
    
    print(funding_query)

    funding_query.to_csv(file_path_outputs + fileName_funding + '.csv', index=False, sep=',', header=True,
                date_format='%Y-%m-%d')
       
    return funding_query

def sf_funding_date(_sf, _sf_queries_dir) -> pd.DataFrame:
    
    with open(rf'{_sf_queries_dir}funding_date_query.txt') as q:
        funding_query = q.read()
    
    print(funding_query)
    funding_dict = _sf.query_all(funding_query)
    
    funding_query = pd.DataFrame(funding_dict['records']).drop(columns=['attributes'])
    funding_query.columns = ['Id',  'Funded_Amount_Date__c']
    
    print('funding_query info:')
    print(funding_query.info())
    print(f'funding_query shape: {funding_query.shape}')
    
    funding_query['Id'] = funding_query['Id'].astype(str)
    
    funding_query = funding_query[['Id', 'Funded_Amount_Date__c']]
    
    print(funding_query)

    funding_query.to_csv(file_path_outputs + fileName_funding_date + '.csv', index=False, sep=',', header=True,
                date_format='%Y-%m-%d')
       
    return funding_query
    
try:
    # if __name__=='__main__':
    
    client = Birst_Utils.GetBirstClient()
    login = client.service.Login(Birst_Utils.GetBirstUser(), Birst_Utils.GetBirstPassword())
 
    sf_queries_dir = 'D:/Business Intelligence/PythonScripts/next_gen_hotel_engagement/' #'E:/Users/699052/PythonScripts/next_gen_hotel_engagement/' 
    sf = sf_connector.sf_connect()
    
    startTime = datetime.datetime.now(tz=None).strftime('%Y-%m-%d %H:%M:%S')
    
   
    print(datetime.datetime.now(tz=None).strftime('%Y-%m-%d %H:%M:%S'))
    print('Downloading siteAttributes...')
    siteAttributes = Getsitedata(client)
    
    sf_he_item = sf_he_item(sf, sf_queries_dir)
    
    sf_he_qa = sf_he_qa(sf, sf_queries_dir)
    
    merged_df = sf_he_qa.merge(sf_he_item, how='left', left_on='ID', right_on='Hotel Engagement ID')
    
    # Categories list you want to compare with
    required_categories = ['Administrative Policies','Food & Beverage',
                            'Guestroom','Hotel Arrival and Exterior',
                            'Hotel Facilities','Lobby & Front Desk',
                            'Meeting & Business']
    
    # Columns that must become NULL in the new rows
    null_cols = ['ID Count', 'Brand Standard Number', 'GSC Catalog Item Category2', 
                  'Subcategory', 'Hotel Engagement Status', 'Cleanliness', 
                  'Compliance', 'Condition', 'Failed PIP Item', 'Status Count',
                  'Cleanliness Count', 'Compliance Count', 'Condition Count',
                  'Failed PIP Item Count']
            
    merged_category_col = 'GSC Catalog Item Category1'
    
    new_rows = []
    
    # Filter only QA rows first
    qa_df = merged_df[merged_df['RecordTypeDesc'] == 'QA']
    
    # Group by ID, but only using QA rows
    for id_value, group in qa_df.groupby('ID'):
    
        # Categories already present for this ID (only QA rows)
        existing_categories = group[merged_category_col].dropna().unique()
    
        # Find missing categories
        missing = [cat for cat in required_categories if cat not in existing_categories]
    
        # Create one new row per missing category
        for cat in missing:
            new_row = group.iloc[0].copy()  # take first QA row as template
    
            # Set the category name
            new_row[merged_category_col] = cat
    
            # Set selected fields to NULL
            new_row[null_cols] = np.nan
    
            # Keep RecordType = 'QA'
            new_row['RecordTypeDesc'] = 'QA'
    
            new_rows.append(new_row)
    
    # Build new rows df
    new_rows_df = pd.DataFrame(new_rows)
    
    # Combine with original df
    merged_df = pd.concat([merged_df, new_rows_df], ignore_index=True)

    merged_df = siteAttributes.merge(merged_df, how = 'inner', left_on = 'Franchise Agreement Account Number', right_on = 'Contract Name')
    
    merged_df['Last Updated'] = startTime
    
    merged_df = merged_df[['site_id', 'ID', 'ID Count', 'Brand Standard Number',
                              'GSC Catalog Item Category1', 'GSC Catalog Item Category2',
                              'Subcategory', 'Name','RecordTypeId', 'Contract', 'Status', 'Type', 'Contract Name',
                              'QA Last Inspection Date', 'QA Last Inspection Grade',	'QA Last Inspection Score',	
                              'QA Last Inspection Type',	'Action Plan Status',	'Administrative Policies Score',
                              'Anticipated Inspection Date',	'Failed Reason',	'Food Beverage Score',
                              'General Manager','Guestroom Score', 'Hazard Items', 'Hotel Arrival and Exterior Score',
                              'Hotel Facilities Score',	'Inspection Performed By',	'Lobby Front Desk Score',
                              'Meeting Business Score',	'Overall Result History',	'Overall Score History',
                              'PIP Failures',	'Property Commencement Date',	'Property Open Date',
                              'Reinspection Number',	'Rescored',	'Safety',	'Scheduled Inspection Date',	
                              'Total Passed Questions Administrative',	'Total Passed Questions Food Beverage',
                              'Total Passed Questions Guestroom',	'Total Passed Questions Hotel Arrival',
                              'Total Passed Questions Hotel Facilities',	'Total Passed Questions Lobby Front Desk',
                              'Total Passed Questions Meeting Business',	'Total Questions Administrative Policies',
                              'Total Questions Food Beverage',	'Total Questions Guestroom',	'Total Questions Hotel Arrival Exterior',	
                              'Total Questions Hotel Facilities', 'Total Questions Lobby Front Desk',	'Total Questions Meeting Business',	
                              'Administrative Policies Results',	'Failed Reason Formula',	'Food Beverage Results',	'Guestroom Results',	
                              'Hotel Arrival and Exterior Results',	'Hotel Facilities Results',	'Inspector Is Current Running User',
                              'Lobby Front Desk Results',	'Location',	'Meeting Business Results',	'Overall Grade',	'Overall Score',
                              'QA Inspection Date',	'Total Passed Questions', 'Total Questions',	'Special Request Type',
                              'Latest Inspection Indicator',	'Cure Date',	'Special Request',	'Special Request Date',
                              'Special Request Comments',	'Inspection Start Time',	'Inspection End Time', 'Count of Waivers',
                              'Cleanliness Blitzes', 'Quality Matters Workshop',	'Quality Matters Workshop 2', 'Remedial Training',
                              'Remedial Training Charge Date', 'Required For Capital Funding', 'Account', 'PIP Type',
                              'PIP Inspection Date', 'Chaincode',  'DFO',  'RDFO',  'Same Store',  'SDFO',  
                              'Country',  'Chain Scale',  'State',  'STR Region', 'Brand Name',  'Revenue Manager',  'Site Name',  
                              'Highgate Flag', 'Same Store Upscale', 
                              'Time Period', 'FAC Flag',  'Management Company',  'SF Portfolio', 'RecordTypeDesc',
                              'Hotel Engagement Status', 'Cleanliness', 'Compliance', 'Condition', 'Failed PIP Item', 
                              'Status Count','Cleanliness Count', 'Compliance Count', 'Condition Count',
                              'Failed PIP Item Count', 'Safety Time Sensitive Item', 'Safety Time Sensitive Item Count', 'Last Updated', 'Time Frame']]
    
    merged_df.to_csv(file_path_outputs + fileName_Hotel_Engagement + '.csv', index=False, sep=',', header=True,
                  date_format='%Y-%m-%d')
    
    sf_user = sf_user(sf, sf_queries_dir)
    
    sf_contract = sf_contract(sf, sf_queries_dir)
    
    
    
    sf_waiver = sf_waiver(sf, sf_queries_dir)
    
    sf_brand_std_desc = sf_brand_std_desc(sf, sf_queries_dir)
    
    sf_waiver = sf_waiver.merge(sf_brand_std_desc, how = 'left', left_on='Brand Standards Description', right_on='ID' )
    
    merged_df1 = sf_contract.merge(sf_waiver, how='inner', left_on='Contract ID', right_on='Contract')
    merged_df1 = siteAttributes.merge(merged_df1, how = 'left', left_on = 'Franchise Agreement Account Number', right_on = 'Contract Name')
    
    merged_df1['Last Updated'] = startTime
    
    merged_df1 = merged_df1[['Id', 'Owner Id', 'Name', 'Created Date', 'Last Modified Date', 'System Modstamp', 'Last Activity Date', 
                            'Account', 'Brand Standards Description', 'Comments to Waiver Requestor', 'Contract Status', 'Contract', 
                            'Date of Request', 'Date of approval', 'Hotel Engagement Item', 'Inspection Category', 'Internal Comments', 
                            'Internal Description', 'site_id' , 'Waiver Approver', 'Waiver Description', 'Waiver Expiration Date', 
                            'Waiver Rationale', 'Waiver Requested Extension Date', 'Waiver Status', 'Waiver Type', 'Property Brand Standards', 
                            'BSD Category', 'BSD Subcategory', 'Brand Standard Number', 'Expired', 'Waiver Classification', 'Account DFO', 
                            'Expected Ship Date', 'Waiver Additional Details', 'Waiver Conditional Details', 'Waiver Sub', 
                            'Brand Description Name', 'Last Updated']]
    
    merged_df1 = merged_df1.replace({r'\r\n|\r|\n': ' '}, regex=True)
    
    merged_df1.to_csv(file_path_outputs + fileName_Waiver + '.csv', index=False, sep=',', header=True,
                date_format='%Y-%m-%d')
    
    
    # ########################## Brand Champion Dashboard ###########################################
    
    # ################Get OTA Status Go-Live Dates, AP Task Completion, Opening Manager, Previous Affiliated, Distribution Launch Manager, opportunity owner  #########
  
    
    sf_act_pln = sf_action_plans(sf, sf_queries_dir)
    
    sf_act_pln_ota = sf_action_plans_ota(sf, sf_queries_dir)
    
    sf_owner = sf_owner(sf, sf_queries_dir)
    
    sf_funding = sf_funding(sf, sf_queries_dir)
    
    sf_funding_date = sf_funding_date(sf, sf_queries_dir)
    
    sf_act_pln = pd.read_csv(file_path_outputs + fileName_action_plans + '.csv')
    sf_contract = pd.read_csv(file_path_outputs + fileName_contract + '.csv')
    sf_act_pln_ota = pd.read_csv(file_path_outputs + action_plans_ota  + '.csv')
    sf_owner = pd.read_csv(file_path_outputs + fileName_owner + '.csv')
    sf_funding = pd.read_csv(file_path_outputs + fileName_funding + '.csv')
    sf_funding_date = pd.read_csv(file_path_outputs + fileName_funding_date + '.csv')
    
    sf_act_pln_ota = sf_act_pln_ota.rename(columns={'Verify Google is Live': 'Google Active date'}) 
    
    # Convert date field
    sf_funding_date["Funded_Amount_Date__c"] = pd.to_datetime(
        sf_funding_date["Funded_Amount_Date__c"],
        errors="coerce"
        )
    
    # Aggregate Fund_date
    fund_summary = (
        sf_funding_date
        .groupby("Id", as_index=False)
        .agg(
            Number_of_Installments=("Id", "size"),  # counts all rows, including blank dates
            Funded_Amount_Date__c=("Funded_Amount_Date__c", "max")
            )
        )
    
    # Join Funding -> Contract
    df = sf_funding.merge(
        sf_contract,
        left_on="Contract Id",
        right_on="Contract ID",
        how="left"
        )
    
    # Join to Fund summary
    df = df.merge(
        fund_summary,
        on="Id",
        how="left"
        )
    # Collapse to one row per Contract
    
    df = (
        df.sort_values(
            by=["Openings_Manager",
                "Previously_Affiliated_Brand",
                "Distribution_Launch_Manager",
                "Opportunity__c",
                "Program_Participation__c",
                "Application_Type__c"
                ],
            na_position="last"
            )
        .groupby("Contract ID", as_index=False)
        .first()
        )
    
    # Select final columns
    merged_df = df[
        [
            "Contract ID",
            "Contract Name",
            "Number_of_Installments",
            "Funded_Amount_Date__c",
            "Openings_Manager",
            "Previously_Affiliated_Brand",
            "Distribution_Launch_Manager",
            "Opportunity__c",
            "Program_Participation__c",
            "Application_Type__c"
            ]
        ]
   
    # duplicate_rows = merged_df[merged_df.duplicated(subset=['Contract ID'], keep=False)]
    # # Sort by Contract Name so the duplicates are grouped together for easy viewing
    # duplicate_rows_sorted = duplicate_rows.sort_values(by='Contract ID')
    # print(duplicate_rows_sorted)  

    
    merged_df = merged_df.merge(sf_owner, how='left', left_on='Opportunity__c', right_on='Opportunity Id')
    
    # merged_df.to_csv(file_path_outputs + 'owner_contract' + '.csv', index=False, sep=',', header=True,
    #             date_format='%Y-%m-%d')
    
    merged_df1 = merged_df.merge(sf_act_pln, how='left', left_on='Contract ID', right_on='contract__c')
    
    merge_df2 = sf_act_pln_ota.merge(merged_df1, how='right', left_on='contract_name__c', right_on='Contract Name')
    
    # Don't use # #################### Add PIP Completion, active waiver count #####################
    
    # df = pd.read_csv(file_path_outputs + 'Hotel Engagement' + '.csv')
    # df = df[df['PIP Type'] == 'Standard']
    # df['Contract Name'].info()
    # # 2. Pivot to get status counts per Contract and Time Frame
    # df_pivot = df.pivot_table(
    #     index=['Contract Name', 'Time Frame'], 
    #     columns='Hotel Engagement Status', 
    #     values='Status Count', 
    #     aggfunc='sum',
    #     fill_value=0
    #     )
    
    # # 3. Ensure 'Submitted' and 'Approved' columns exist 
    # # (This prevents errors if a certain status doesn't appear in your raw data)
    # for col in ['Submitted', 'Approved']:
    #     if col not in df_pivot.columns:
    #         df_pivot[col] = 0
            
    # # 4. Calculate the %: (Submitted + Approved) / Total of all statuses
    # # We sum across the row to get the denominator
    # total_counts = df_pivot.sum(axis=1)
    # df_pivot['Submitted %'] = ((df_pivot['Submitted'] + df_pivot['Approved']) / total_counts) 
            
    # # 5. Second Pivot: Move 'Time Frame' to Column headers
    # df_rates = df_pivot[['Submitted %']].reset_index()
    # final_df = df_rates.pivot(
    #             index='Contract Name', 
    #             columns='Time Frame', 
    #             values='Submitted %'
    #             )
            
    # # 6. Final Formatting
    # # Rename columns to include "submitted %" suffix
    # final_df.columns = [f"{col} submitted %" for col in final_df.columns]
    # # Fill missing combinations with 0 and move Contract Number back to a column
    # final_df = final_df.reset_index().fillna(0)
            
    # # Optional: Round to 2 decimal places
    # final_df = final_df.round(2)

    # final_df = final_df[['Contract Name', '6 Months submitted %', '12 Months submitted %', 'Within Noted Timeframe submitted %', 'PTO submitted %']]
    
    # final_df = final_df[['Contract Name', '6 Months submitted %', '12 Months submitted %', 'Within Noted Timeframe submitted %', 'PTO submitted %']]
    # final_df.columns = [col if col == 'Contract Name' else f'PIP {col}' for col in final_df.columns]
    
    ################################################################################################
    
    df = pd.read_csv(file_path_outputs + 'Hotel Engagement' + '.csv')
    df = df[df['PIP Type'] == 'Standard']
    df['Contract Name'].info()
    
    # 2. Pivot to get status counts per Contract and Time Frame
    df_pivot = df.pivot_table(
        index=['Contract Name', 'Time Frame'], 
        columns='Hotel Engagement Status', 
        values='Status Count', 
        aggfunc='sum',
        fill_value=0
    )
    
    # 3. Ensure necessary columns exist to prevent KeyError
    for col in ['Submitted', 'Approved']:
        if col not in df_pivot.columns:
            df_pivot[col] = 0
            
    # 4. Calculate raw counts for your groups
    # Total count is the sum of all statuses combined (sum across the row)
    df_pivot['total count'] = df_pivot.sum(axis=1)
    # Combined count for Submitted + Approved
    df_pivot['submitted/approved count'] = df_pivot['Submitted'] + df_pivot['Approved']
            
    # 5. Second Pivot: Move 'Time Frame' to Column headers 
    df_counts = df_pivot[['submitted/approved count', 'total count']].reset_index()
    final_df = df_counts.pivot(
        index='Contract Name', 
        columns='Time Frame', 
        values=['submitted/approved count', 'total count']
    )
            
    # 6. Final Formatting and Flattening Columns
    # Flattens multi-level columns to: "6 Months submitted/approved count", "6 Months total count", etc.
    final_df.columns = [f"{time_frame} {metric}" for metric, time_frame in final_df.columns]
    final_df = final_df.reset_index().fillna(0)

    # 7. Select and reorder exactly the columns you want
    final_df = final_df[[
        'Contract Name', 
        '6 Months submitted/approved count', '6 Months total count', 
        '12 Months submitted/approved count', '12 Months total count',
        'Within Noted Timeframe submitted/approved count', 'Within Noted Timeframe total count',
        'PTO submitted/approved count', 'PTO total count'
    ]]
    
    # 8. Add the PIP prefix to everything except 'Contract Name'
    final_df.columns = [col if col == 'Contract Name' else f'PIP {col}' for col in final_df.columns]
    
    merge_df2 = merge_df2.merge(final_df, how='left', left_on='Contract Name', right_on='Contract Name')
    
    df = pd.read_csv(file_path_outputs + 'Waiver' + '.csv')
    
    df = df[df['Expired'].astype(str).str.upper() == 'FALSE']
    
    df = df[[ 'Waiver Status', 'Contract']]
    
    pivot_df = df.pivot_table(
    index='Contract', 
    columns='Waiver Status', 
    aggfunc='size',
    fill_value=0
    ).reset_index()
    
    pivot_df.columns = [
    f'Waiver {col}' if col != 'Contract' else col 
    for col in pivot_df.columns
    ]
    # pivot_df.info()
    merge_df2 = merge_df2.merge(pivot_df, how='left', left_on='Contract ID', right_on='Contract')
    
    ####### Get photo date ##############
    
    # df_photo = sf_photo(sf, sf_queries_dir)
    
    df_photo = pd.read_csv(file_path_outputs + fileName_photo  + '.csv')
    
    merge_df3 = merge_df2.merge(df_photo, how='left', left_on='Contract Name', right_on='Contract_Name__c')
    
    ###### FEMA #################
    
    # df_account = sf_account(sf, sf_queries_dir)
    
    df_account = pd.read_csv(file_path_outputs + fileName_account + '.csv')
    
    
    merge_df4 = merge_df3.merge(df_account, how='left', left_on='Contract Name', right_on='Contract_Name__c')
    merge_df4.info()
    merge_df4 = merge_df4.drop(columns=['contract_name__c', 'Contract_Name__c_x', 'Contract_Name__c_y', 'Contract_Name__c_x', 'Contract_Name__c_y'])
    merge_df4 = merge_df4.drop_duplicates()
    merge_df4.to_csv(file_path_outputs + 'brand_champion_att' + '.csv', index=False, sep=',', header=True,
                date_format='%Y-%m-%d')
    
    
    
    print('Script completed successfully')
    print(datetime.datetime.now(tz=None).strftime('%Y-%m-%d %H:%M:%S'))
    print('Sending success email...')
    successEmailMessage = 'hotel engagement script has finished successfully'
    for i in successEmailTo:
        Birst_Utils.SendEmail(i, successEmailSubject, successEmailMessage, logFileName, logFilePath)
    
except Exception as e:

    print('Sending error email...')
    errorEmailMessage = str(e) + "\n"
    errorEmailMessage += str(traceback.format_exc()) + "\n"
    for i in errorEmailTo:
        Birst_Utils.SendEmail(i, errorEmailSubject, errorEmailMessage, logFileName, logFilePath)
        
    print(e)
    raise e    

    
    # df = pd.read_csv(file_path_outputs + 'brand_champion_att' + '.csv')
    # duplicate_rows = df[df.duplicated(subset=['Contract Name'], keep=False)]
    # # Sort by Contract Name so the duplicates are grouped together for easy viewing
    # duplicate_rows_sorted = duplicate_rows.sort_values(by='Contract Name')
    # print(duplicate_rows_sorted)    
    # duplicate_rows_sorted.to_csv(file_path_outputs + 'duplicates' + '.csv', index=False, sep=',', header=True,
    #             date_format='%Y-%m-%d')