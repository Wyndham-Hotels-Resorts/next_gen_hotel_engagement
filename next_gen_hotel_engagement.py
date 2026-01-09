# -*- coding: utf-8 -*-
"""
Created on Mon Oct 27 11:26:30 2025

@author: 540965
"""

import pandas as pd
import numpy as np
import tableauserverclient as TSC
import datetime

from Birst_Includes import AWS_Utils
from Birst_Includes import Birst_Utils

from Birst_Includes import sf_connector, AWS_Utils
s3 = AWS_Utils.GetAWSClient()

s3 = AWS_Utils.GetAWSClient()
#file_path = os.path.dirname(os.path.abspath(__file__)) + '/'
file_path_sources = './SourceFiles/'
file_path_outputs = 'E:/Business Intelligence/Tableau/Next_Gen_QA_Pip/'  #'E:/Users/699508/qa_pip/'  #'E:/Business Intelligence/Tableau/Next_Gen_QA_Pip/' 

logFileName = 'next_gen_hotel_engagement_data_automation_output.txt'
logFilePath = 'D:/Business Intelligence/PythonScripts/next_gen_hotel_engagement/' + logFileName

errorEmailTo = ['businessintelligence@wyndham.com']
errorEmailSubject = 'Next Gen Hotel Engagement Data Automation - Error'
successEmailTo = ['businessintelligence@wyndham.com']
successEmailSubject = 'Next Gen Hotel Engagement Data Automation - Success'

fileName_Hotel_Engagement = 'Hotel Engagement'
fileName_Waiver = 'Waiver'
fileName_contract = 'Contract'

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
    
    dist_col_count = df_he_item['Hotel Engagement ID'].nunique()
    print(f"Distinct count in 'col1': {dist_col_count}")
    
    df_he_item['ID Count'] = df_he_item.groupby(['Brand Standard Number', 'Hotel Engagement ID'])['Id'].transform('count')
    df_he_item['Status Count'] = df_he_item.groupby(['Hotel Engagement ID', 'GSC Catalog Item Category1', 'Subcategory'])['Hotel Engagement Status'].transform('count')
    df_he_item['Cleanliness Count'] = df_he_item.groupby(['Hotel Engagement ID', 'GSC Catalog Item Category1', 'Subcategory', 'Hotel Engagement Status'])['Cleanliness'].transform(sum)
    df_he_item['Compliance Count'] = df_he_item.groupby(['Hotel Engagement ID', 'GSC Catalog Item Category1', 'Subcategory', 'Hotel Engagement Status'])['Compliance'].transform(sum)
    df_he_item['Condition Count'] = df_he_item.groupby(['Hotel Engagement ID', 'GSC Catalog Item Category1', 'Subcategory', 'Hotel Engagement Status'])['Condition'].transform(sum)
    df_he_item['Failed PIP Item Count'] = df_he_item.groupby(['Hotel Engagement ID', 'GSC Catalog Item Category1', 'Subcategory', 'Hotel Engagement Status'])['Failed PIP Item'].transform(sum)

    # Rename specific records in the 'Category' column
    df_he_item['GSC Catalog Item Category1'] = df_he_item['GSC Catalog Item Category1'].replace({'Meeting and Business': 'Meeting & Business', 
                                                                                                 'Lobby and Front Desk': 'Lobby & Front Desk',
                                                                                                 'Food and Beverage': 'Food & Beverage'})
    
    df_he_item = df_he_item[['ID Count', 'Brand Standard Number', 'Hotel Engagement ID', 
                              'GSC Catalog Item Category1', 'GSC Catalog Item Category2',	
                              'Subcategory', 'Hotel Engagement Status', 'Cleanliness', 
                              'Compliance', 'Condition', 'Failed PIP Item', 'Status Count',
                              'Cleanliness Count', 'Compliance Count', 'Condition Count',
                              'Failed PIP Item Count']]
    
    df_he_item.to_csv(file_path_outputs + 'df_he_item_new' + '.csv', index=False, sep=',', header=True,
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

def sf_contract(_sf, _sf_queries_dir) -> pd.DataFrame:
    
    with open(rf'{_sf_queries_dir}contract_query.txt') as q:
        contract_query = q.read()
    
    print(contract_query)
    contract_dict = _sf.query_all(contract_query)
    
    df_contract = pd.DataFrame(contract_dict['records'])[['Id', 'Name']]
    df_contract.columns = ['Contract ID', 'Contract Name']
    
    print('df_contract info:')
    print(df_contract.info())
    print(f'df_contract shape: {df_contract.shape}')
    
    df_contract['Contract ID'] = df_contract['Contract ID'].astype(str)
    
    df_contract = df_contract[['Contract ID', 'Contract Name']]
    
    print(df_contract)

    # df_contract.to_csv(file_path_outputs + fileName_contract + '.csv', index=False, sep=',', header=True,
    #             date_format='%Y-%m-%d')
       
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


if __name__=='__main__':
    
    client = Birst_Utils.GetBirstClient()
    login = client.service.Login(Birst_Utils.GetBirstUser(), Birst_Utils.GetBirstPassword())
 
    sf_queries_dir = 'D:/Business Intelligence/PythonScripts/next_gen_hotel_engagement/' #'E:/Users/699508/qa_pip/'
    sf = sf_connector.sf_connect()
    
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
                              'Failed PIP Item Count']]
    
    merged_df.to_csv(file_path_outputs + fileName_Hotel_Engagement + '.csv', index=False, sep=',', header=True,
                  date_format='%Y-%m-%d')
    
    sf_contract = sf_contract(sf, sf_queries_dir)
    
    sf_waiver = sf_waiver(sf, sf_queries_dir)
    
    sf_brand_std_desc = sf_brand_std_desc(sf, sf_queries_dir)
    
    sf_waiver = sf_waiver.merge(sf_brand_std_desc, how = 'left', left_on='Brand Standards Description', right_on='ID' )
    
    merged_df1 = sf_contract.merge(sf_waiver, how='inner', left_on='Contract ID', right_on='Contract')
    merged_df1 = siteAttributes.merge(merged_df1, how = 'left', left_on = 'Franchise Agreement Account Number', right_on = 'Contract Name')
    
    merged_df1 = merged_df1[['Id', 'Owner Id', 'Name', 'Created Date', 'Last Modified Date', 'System Modstamp', 'Last Activity Date', 
                            'Account', 'Brand Standards Description', 'Comments to Waiver Requestor', 'Contract Status', 'Contract', 
                            'Date of Request', 'Date of approval', 'Hotel Engagement Item', 'Inspection Category', 'Internal Comments', 
                            'Internal Description', 'site_id' , 'Waiver Approver', 'Waiver Description', 'Waiver Expiration Date', 
                            'Waiver Rationale', 'Waiver Requested Extension Date', 'Waiver Status', 'Waiver Type', 'Property Brand Standards', 
                            'BSD Category', 'BSD Subcategory', 'Brand Standard Number', 'Expired', 'Waiver Classification', 'Account DFO', 
                            'Expected Ship Date', 'Waiver Additional Details', 'Waiver Conditional Details', 'Waiver Sub', 
                            'Brand Description Name']]
    
    merged_df1 = merged_df1.replace({r'\r\n|\r|\n': ' '}, regex=True)
    
    merged_df1.to_csv(file_path_outputs + fileName_Waiver + '.csv', index=False, sep=',', header=True,
                date_format='%Y-%m-%d')