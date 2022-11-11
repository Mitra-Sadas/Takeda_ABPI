import streamlit as st
st.set_page_config(layout="wide")
from __future__ import print_function, unicode_literals
from facepplib import FacePP, exceptions
import pandas as pd
import io
from pathlib import Path
import recordlinkage
import numpy as np
from datetime import datetime
import base64
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from time import sleep
from bs4 import BeautifulSoup
import re
import preprocessor as p
from nameparser import HumanName
from io import BytesIO
from pyxlsb import open_workbook as open_xlsb
import warnings
warnings.filterwarnings("ignore")
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import locationtagger
@st.cache(allow_output_mutation=True)
def upload1(data, data2):
	col1, col2 = st.columns(2)
	with st.spinner("Uploading file"):
		with col1:
			if data is not None:
				df = pd.read_excel(data)
				df = df.astype(str)
		with col2:
			df2 = pd.DataFrame()			
			if data2 is not None:
				df2 = pd.read_excel(data2)
				df2 = df2.astype(str)
						
	return df, df2
		
def dataframe_head(df):
	st.dataframe(df.head())
	with st.expander("Show Statistics"):
		buffer = io.StringIO() 
		df.info(buf=buffer) 
		s = buffer.getvalue() 
		st.text(s)

def name_cleaning(df):
    df1 = df.select_dtypes(exclude=[np.number])
    df2 = df.select_dtypes(include=[np.number])
    df1 = df1.astype('str')
    df1 = df1.replace(r'[^a-zA-Z ]', '', regex=True).replace("'", '')
    df1 = df1.apply(lambda x: x.astype(str).str.lower())
    df1 = df1.replace(['miss ','mr ','ms', 'dr', 'shri', 'shree', 'smt', 'ms'],'', regex=True)
    df1 = df1.replace(['bhai', 'bhau', 'bhoi', 'bai', 'kumar', 'kumr', 'kmr','ben', 'dei', 'devi', 'debi', 'kumaar', 'saheb'],
                    '', regex=True)
    df1 = df1.replace(['nan','None'], '')
    df1.append(df2, ignore_index=True)
    return df1

def header_1(url):
     st.markdown(f'<p style="color:#00008B;font-size:36px;border-radius:2%;text-align:center;">{url}</p>', unsafe_allow_html=True)
def header_2(url):
     st.markdown(f'<p style="color:#000000;font-size:18px;border-radius:2%;text-align:center;">{url}</p>', unsafe_allow_html=True)
def header_3(url):
     st.markdown(f'<p style="color:#000000;font-size:36px;border-radius:2%;text-align:center;">{url}</p>', unsafe_allow_html=True)


def calcscore(hcp_first, hcp_middle, hcp_last, hcp_title, hcp_gender, hcp_city, hcp_state, hcp_specialty, sm_first, sm_middle, sm_last, sm_title, sm_gender, sm_city, sm_state, sm_specialty):
	score_list_g1 = {'First':28, 'Middle':4, 'Last':33}
	score_list_g2 = {'Gender':10, 'Title':5, 'City':5, 'State':5, 'Specialty':10}
	final_score_list_g1 = {'First':0, 'Middle':0, 'Last':0}
	final_score_list_g2 = {'Gender':0, 'Title':0, 'City':0, 'State':0, 'Specialty':0}

	if ((hcp_first=="") or (sm_first=="")):
		final_score_list_g1['First'] = 0
	else:
		final_score_list_g1['First'] = score_list_g1['First']

	if ((hcp_middle=="") or (sm_middle=="")):
		final_score_list_g1['Middle'] = 0
	else:
		final_score_list_g1['Middle'] = score_list_g1['Middle']

	if ((hcp_last=="") or (sm_last=="")):
		final_score_list_g1['Last'] = 0
	else:
		final_score_list_g1['Last'] = score_list_g1['Last']

	weight_divided_g1 = sum(score_list_g1.values()) - sum(final_score_list_g1.values())
	num_non_null_g1 = 0
	for value in final_score_list_g1.values():
		if value != 0:
			num_non_null_g1 = num_non_null_g1+1
	for key, value in final_score_list_g1.items():
		if value != 0:
			final_score_list_g1[key] = final_score_list_g1[key]+(weight_divided_g1/num_non_null_g1)
	

	if ((hcp_title=="") or (sm_title=="")):
		final_score_list_g2['Title'] = 0
	else:
		final_score_list_g2['Title'] = score_list_g2['Title']

	if ((hcp_gender=="") or (sm_gender=="")):
		final_score_list_g2['Gender'] = 0
	else:
		final_score_list_g2['Gender'] = score_list_g2['Gender']

	if ((hcp_city=="") or (sm_city=="")):
		final_score_list_g2['City'] = 0
	else:
		final_score_list_g2['City'] = score_list_g2['City']
	    
	if ((hcp_state=="") or (sm_state=="")):
		final_score_list_g2['State'] = 0
	else:
		final_score_list_g2['State'] = score_list_g2['State']

	if ((hcp_specialty=="") or (sm_specialty=="")):
		final_score_list_g2['Specialty'] = 0
	else:
		final_score_list_g2['Specialty'] = score_list_g2['Specialty']
		
	weight_divided_g2 = sum(score_list_g2.values()) - sum(final_score_list_g2.values())
	num_non_null_g2 = 0
	for value in final_score_list_g2.values():
	    if value != 0:
	        num_non_null_g2 = num_non_null_g2+1
	for key, value in final_score_list_g2.items():
	    if value != 0:
	        final_score_list_g2[key] = final_score_list_g2[key]+(weight_divided_g2/num_non_null_g2)
	final_score_list_g1.update(final_score_list_g2)
	
	return final_score_list_g1
	
# def face_comparing(image1,image2):
# 	#x=x.split()
# 	#image1=x[0]
# 	#image2=x[-1]
# 	#st.write('hcp',image1)
# 	#st.write('twitter',image2)
# 	if image1!='' and image2!='':
# 		#st.write('hcp image',image1)
# 		#st.write('twitter image',image2)
# 		face_detection = ""
# 		face_comparing_localphoto=""
# 		face_comparing_websitephoto=""
# 		faceset_initialize = ""
# 		face_search = ""
# 		face_landmarks = ""
# 		dense_facial_landmarks = ""
# 		face_attributes = ""
# 		beauty_score_and_emotion_recognition = ""
# 		api_key ='xQLsTmMyqp1L2MIt7M3l0h-cQiy0Dwhl'
# 		api_secret ='TyBSGw8NBEP9Tbhv_JbQM18mIlorY6-D'
# 		app_ = FacePP(api_key = api_key,api_secret = api_secret)
# 		funcs = [
# 		    face_detection,
# 		    face_comparing_localphoto,
# 		    face_comparing_websitephoto,
# 		    faceset_initialize,
# 		    face_search,
# 		    face_landmarks,
# 		    dense_facial_landmarks,
# 		    face_attributes,
# 		    beauty_score_and_emotion_recognition
# 		]
# 		try:
# 			cmp_ = app_.compare.get(image_url2 = image1,image_url1 = image2)
# 			return cmp_.confidence
# 		except:
# 			return 0
# 	else:
# 		return -1

@st.cache(persist=True,allow_output_mutation=True)
#@st.cache(allow_output_mutation=True)
def getoutput(df, df2, threshold1, threshold2):
	with st.spinner(text="Matching the social profiles, Please wait..."):
		df[['First Name','Last Name','Title']] = df[['First Name','Last Name','Title']].apply(lambda x: x.astype(str).str.lower())
		df2[['first','last','title']] = df2[['first','last','title']].apply(lambda x: x.astype(str).str.lower())
		df = df.replace(['nan','None'], '')
		df2 = df2.replace(['nan','None'], '')
		df.insert(len(df.columns), 'SrNum1', range(0, 0 + len(df)))
		df.set_index('SrNum1')
		df2.insert(len(df2.columns), 'SrNum2', range(0, 0 + len(df2)))
		df2.set_index('SrNum2')
		Oncology_keywords = ['oncology', 'oncologist', 'onco ', 'onc ', 'hematology', 'haematology', 'hematologist', 'haematologist','hem/onc',
		'cancer', 'lymphoma', 'chemo', 'chemotherapy', 'haem', 'leukaemia', 'leukemia', 'tumor', 'tumour', 'sarcoma', 'myeloma', 'hemato', 'cell therapy']
		df2['Desc'] = df2['Desc'].str.replace('#',' ')
		df2['Desc'] = df2['Desc'].astype(str)
		#df2['latest_tweets'] = df2['latest_tweets'].str.replace('#','')
		#df2['latest_tweets'] = df2['latest_tweets'].astype(str)
		def search_tag(s, tags):
			result = []
			s = s.lower()
			for each in tags:
			    if each.lower() in s:
			        result.append(each)
			if len(result)>0:
			    x = 'Oncology'
			else:
			    x = ''
			return x
		# df2['specialty_extracted'] = df2['Desc'].apply(lambda x: search_tag(x, Oncology_keywords))
		#st.dataframe(df2.head(10))
		#df2['Hashtags'] = df2['latest_tweets'].apply(lambda x: search_tag(x, Oncology_keywords))

		#df['Specialty'] = df['PrimarySpecialtyName'].replace(['Hematology/Oncology','Medical Oncology','Pediatric Hematology/Oncology','Surgical Oncology','Gynecological Oncology','Musculoskeletal Oncology','Advanced Surgical Oncology-ASO'],
		#	['Oncology','Oncology','Oncology','Oncology','Oncology','Oncology','Oncology',])

		# df['Specialty'] = df['PrimarySpecialtyName'].apply(lambda x:'Oncology' if 'oncology' in x.lower() else x) 
		# df['Specialty'] = df['Specialty'].apply(lambda x:'Oncology' if 'hematology' in x.lower() else x) 
		# df['Specialty'] = df['Specialty'].apply(lambda x:'Oncology' if 'haematology' in x.lower() else x) 

		# df['Specialty'] = 'Oncology'

		# df2.loc[(df2['specialty_extracted'] == 'Oncology') 
		#| (df2['Hashtags'] == 'Oncology')
		# , 'Specialty'] = 'Oncology'
		# df2['Specialty'] = df2['Specialty'].replace(['nan','None',np.nan], '')

		# df2['City'] = df2['City'].replace(['LA','NY'],['LOS ANGELES','NEW YORK'])

		# #st.write(len(df2[df2['Specialty']=='Oncology']))
		# us_state_to_abbrev = {
		#     "Alabama": "AL",
		#     "Alaska": "AK",
		#     "Arizona": "AZ",
		#     "Arkansas": "AR",
		#     "California": "CA",
		#     "Colorado": "CO",
		#     "Connecticut": "CT",
		#     "Delaware": "DE",
		#     "Florida": "FL",
		#     "Georgia": "GA",
		#     "Hawaii": "HI",
		#     "Idaho": "ID",
		#     "Illinois": "IL",
		#     "Indiana": "IN",
		#     "Iowa": "IA",
		#     "Kansas": "KS",
		#     "Kentucky": "KY",
		#     "Louisiana": "LA",
		#     "Maine": "ME",
		#     "Maryland": "MD",
		#     "Massachusetts": "MA",
		#     "Michigan": "MI",
		#     "Minnesota": "MN",
		#     "Mississippi": "MS",
		#     "Missouri": "MO",
		#     "Montana": "MT",
		#     "Nebraska": "NE",
		#     "Nevada": "NV",
		#     "New Hampshire": "NH",
		#     "New Jersey": "NJ",
		#     "New Mexico": "NM",
		#     "New York": "NY",
		#     "North Carolina": "NC",
		#     "North Dakota": "ND",
		#     "Ohio": "OH",
		#     "Oklahoma": "OK",
		#     "Oregon": "OR",
		#     "Pennsylvania": "PA",
		#     "Rhode Island": "RI",
		#     "South Carolina": "SC",
		#     "South Dakota": "SD",
		#     "Tennessee": "TN",
		#     "Texas": "TX",
		#     "Utah": "UT",
		#     "Vermont": "VT",
		#     "Virginia": "VA",
		#     "Washington": "WA",
		#     "West Virginia": "WV",
		#     "Wisconsin": "WI",
		#     "Wyoming": "WY",
		#     "District of Columbia": "DC",
		#     "American Samoa": "AS",
		#     "Guam": "GU",
		#     "Northern Mariana Islands": "MP",
		#     "Puerto Rico": "PR",
		#     "United States Minor Outlying Islands": "UM",
		#     "U.S. Virgin Islands": "VI",
		# }

		#df2 = df2.replace({'State code':us_state_to_abbrev})
		#df2 = df2.replace({"United Kingdom": "UK","England":"UK"})
		
		#st.dataframe(df2)
		#df2 = df2.loc[(df2['State code'].str.len() == 2) | (df2['State code'] == "")]
		#st.write(len(df2))

		indexer = recordlinkage.Index()
		indexer.sortedneighbourhood(left_on='First Name', right_on='first', window=25)
		candidates1 = indexer.index(df, df2)
		candidates1 = candidates1.to_frame(index=True)

		indexer.sortedneighbourhood(left_on='Last Name', right_on='last', window=25)
		candidates2 = indexer.index(df, df2)
		candidates2 = candidates2.to_frame(index=True)


		candidates = pd.concat([candidates1,candidates2])
		candidates = candidates.drop_duplicates([0,1])
		candidates = pd.MultiIndex.from_frame(candidates)
		

		#select features for string matching
		selectedfeatures1 = ['First Name','Last Name','Title','Gender','City','State']
		selectedfeatures = ['first','last','title','Gender','City','State code']
		lengh= len(selectedfeatures)
		#save orginal data for final display
		df1 = df.copy()
		df3 = df2.copy()
		#clean textual data

		df[selectedfeatures1] = name_cleaning(df[selectedfeatures1])
		df2[selectedfeatures] = name_cleaning(df2[selectedfeatures])

		compare = recordlinkage.Compare()
		for i in range(len(selectedfeatures)):
			compare.string(selectedfeatures1[i],
				               selectedfeatures[i],
				               #threshold=0.95,
				               label=selectedfeatures1[i],
				                method='levenshtein'
				              )
		features = compare.compute(candidates, df, df2)
		features.loc[features['State']<1, 'State'] = 0
		features.loc[features['City']<1, 'City'] = 0

		potential_matches = features.reset_index()
		potential_matches = potential_matches.add_suffix('_score')
		potential_matches.rename(columns={'0_score':'SrNum1', '1_score':'SrNum2'}, inplace=True)

		#potential_matches = potential_matches[(potential_matches['First Name_score']>=0.4) & (potential_matches['Last Name_score']>=0.4)]

		df1['SrNum1']=df1['SrNum1'].astype(int)
		df3['SrNum2']=df3['SrNum2'].astype(int)
		selectedfeatures1.append("SrNum1")
		#selectedfeatures1.append("URL")
		#selectedfeatures1.append('images')
		selectedfeatures.append("SrNum2")
		selectedfeatures.append('handle')
		#selectedfeatures.append('image')
		df1 = df1.filter(selectedfeatures1)
		df3 = df3.filter(selectedfeatures)

		potential_matches = pd.merge(potential_matches, df1.add_suffix('_hcp'), left_on='SrNum1',right_on='SrNum1_hcp', how='left')
		potential_matches = pd.merge(potential_matches, df3.add_suffix('_sm'), left_on='SrNum2', right_on='SrNum2_sm', how='left')
		#st.write(potential_matches.columns)
		potential_matches['Title_score'] = ''
		#potential_matches.loc[potential_matches['title_sm'].str.contains('MD') & potential_matches['Title_hcp'].str.contains('MD'), 'Title_score'] = 1
		#potential_matches.loc[potential_matches['title_sm'].str.contains('DO') & potential_matches['Title_hcp'].str.contains('DO'), 'Title_score'] = 1
		#potential_matches.loc[potential_matches['Title_score']!=1, 'Title_score'] = 0
		potential_matches['Title_hcp'] = potential_matches['Title_hcp'].apply(lambda x: x.split())
		potential_matches['title_sm'] = potential_matches['title_sm'].apply(lambda x: x.split())
		for i in range(len(potential_matches)):
			set1 = set(potential_matches['Title_hcp'][i])
			set2 = set(potential_matches['title_sm'][i])
			intsctn = set1.intersection(set2)
			if len(intsctn)>0:
				potential_matches['Title_score'][i]=1
			else:
				potential_matches['Title_score'][i]=0

			if potential_matches['City_hcp'][i] in potential_matches['City_sm'][i]:
				potential_matches['City_score'][i] = 1
			else:
				potential_matches['City_score'][i] = 0

			if potential_matches['State_hcp'][i] in potential_matches['State code_sm'][i]:
				potential_matches['State_score'][i] = 1
			else:
				potential_matches['State_score'][i] = 0

		potential_matches['Score'] = 0

		for index, row in potential_matches.iterrows():
			score_list_static= {'First':30, 'Last':35, 'Gender':10, 'Title':8, 'City':9, 'State':8}
			#score_list = calcscore(row['First Name_hcp'],row['Middle Name_hcp'],row['Last Name_hcp'],row['Title_hcp'],row['Gender_hcp'],row['City_hcp'],row['State_hcp'],row['Specialty_hcp'],row['first_sm'],row['middle_sm'],row['last_sm'],row['title_sm'],row['Gender_sm'],row['City_sm'],row['State code_sm'],row['Specialty_sm'])
			#potential_matches.at[index, 'Score_dynamic'] = row['First Name_score']*score_list.get('First')+row['Middle Name_score']*score_list.get('Middle')+row['Last Name_score']*score_list.get('Last')+row['Gender_score']*score_list.get('Gender')+row['Title_score']*score_list.get('Title')+row['City_score']*score_list.get('City')+row['State_score']*score_list.get('State')+row['Specialty_score']*score_list.get('Specialty')
			potential_matches.at[index, 'Score'] = row['First Name_score']*score_list_static.get('First')+row['Last Name_score']*score_list_static.get('Last')+row['Gender_score']*score_list_static.get('Gender')+row['Title_score']*score_list_static.get('Title')+row['City_score']*score_list_static.get('City')+row['State_score']*score_list_static.get('State')#+row['Specialty_score']*score_list_static.get('Specialty')
		#st.dataframe(potential_matches.head())
		#value=[]
		#L = [face_comparing(i,j) if i!='' and j!='' for i,j else -1 in zip(potential_matches['images_hcp'],potential_matches['image_sm'])]
		#for i,j in zip(potential_matches['images_hcp'],potential_matches['image_sm']):
		    #if i!='' and j!='':
		    #	value.append(face_comparing(i,j))
		    #else:
		    	#value.append(-1)
		#potential_matches.loc[((potential_matches['images_hcp']!='') & (potential_matches['image_sm']!='')),'image score']=face_comparing(potential_matches['images_hcp'],potential_matches['image_sm'])
		#potential_matches.loc[((potential_matches['images_hcp']=='') | (potential_matches['image_sm']=='')),'image score']=-1
		#potential_matches['image score']=value
		
		#st.dataframe(potential_matches)
		#potential_matches['image score']=(potential_matches['images_hcp']+" "+potential_matches['image_sm']).apply(face_comparing)
		#potential_matches['image score']=potential_matches[['images_hcp','image_sm']].apply(lambda x, y:face_comparing(x,y),axis=1 )
		#potential_matches['Score'] = (potential_matches['Score_static']+potential_matches['Score_dynamic'])/2
		#st.dataframe(potential_matches)
		potential_matches = potential_matches.sort_values(['SrNum1','Score'], ascending=[True,False])

		final_merge = potential_matches

		test = final_merge.groupby('SrNum1')['Score'].agg(max)
		test= test.reset_index()
		test.rename(columns={'Score':'Max HCP Score'}, inplace=True)
		final_merge = pd.merge(final_merge, test, on='SrNum1', how='left')
		final_merge.loc[final_merge['Max HCP Score']==final_merge['Score'], 'Highest'] = 1
		final_merge.loc[((final_merge['Max HCP Score']-final_merge['Score']>0) & (final_merge['Max HCP Score']-final_merge['Score']<=threshold2)), 'NearBy'] = 1
		final_merge[['Max HCP Score','Highest', 'NearBy']].fillna(0, inplace=True)
		test2 = final_merge.groupby('SrNum1')['NearBy'].agg(max)
		test2= test2.reset_index()
		test2.rename(columns={'NearBy':'HasNearBy'}, inplace=True)
		final_merge = pd.merge(final_merge, test2, on='SrNum1', how='left')
		final_merge.loc[((final_merge['Max HCP Score']>=threshold1) & (final_merge['HasNearBy']!=1) & (final_merge['Highest']==1)), 'Category'] = 'Match'
		final_merge.loc[((final_merge['Max HCP Score']>=threshold1) & (final_merge['HasNearBy']==1) & ((final_merge['Highest']==1) | (final_merge['NearBy']==1))), 'Category'] = 'Manual'
		final_merge.loc[((final_merge['Max HCP Score']<threshold1) & (final_merge['Max HCP Score']>=threshold1-10) & ((final_merge['Highest']==1) | (final_merge['NearBy']==1))), 'Category'] = 'Manual'
		final_merge.loc[((final_merge['Max HCP Score']<threshold1-10) & ((final_merge['Highest']==1) | (final_merge['NearBy']==1))), 'Category'] = 'Non Match'
		#st.dataframe(final_merge)
		#st.download_button(label="Final Merge Data",data=final_merge.to_csv(index=False).encode('utf-8'),file_name="Final_Merge.csv",mime='text/csv')

		#final_merge.to_csv('final_merge.csv',index=False,encoding='utf-8')
		#final_merge["Probabilty"]=(final_merge["Score"]/lengh)*100
		#final_merge["Probabilty"]=final_merge["Score"]
		#final_merge.drop(['Score'], inplace=True, axis=1)
		final_merge['handle'] = '@' + final_merge['handle_sm'].astype(str)
		final_merge['Source'] = 'twitter'
		#st.write(len(final_merge))
		#final_merge=final_merge[final_merge.Category.notnull()]
		final_merge=final_merge[final_merge['Category'].isin(['Match','Manual','Non Match'])]
		#st.write(len(final_merge))
		#with st.spinner("Comparing images"):
		#	final_merge['image score']=final_merge[['images_hcp','image_sm']].apply(lambda x:face_comparing(*x),axis=1)
		#st.dataframe(final_merge.head())
		#if final_merge['Category']=='Non Match' & final_merge['image score']>=85:
		#final_merge.loc[((final_merge['Category']=='Manual') & (final_merge['image score']>=85)),'Category']='Match1'
		#match_npi=list(final_merge[final_merge['Category']=='Match1']['URL_hcp'].unique())
		#final_merge.loc[(final_merge['Category']=='Manual') & (final_merge['URL_hcp'].isin(match_npi)),'Category']=''

		#final_merge.loc[((final_merge['Category']=='Non Match') & (final_merge['image score']>=85)),'Category']='Manual1'
		#manual_npi=list(final_merge[final_merge['Category']=='Manual1']['URL_hcp'].unique())
		#final_merge.loc[(final_merge['Category']=='Non Match') & (final_merge['URL_hcp'].isin(manual_npi)),'Category']=''
		
		#final_merge['Category']=final_merge['Category'].replace({'Match1':'Match','Manual1':'Manual'})
		
		#st.dataframe(final_merge)


		final_merge_match = final_merge[final_merge['Category'] == 'Match']
		final_merge_manual = final_merge[final_merge['Category'] == 'Manual']
		final_merge_non_match = final_merge[final_merge['Category'] == 'Non Match']
		
		lenofcandidates=len(final_merge_match)+len(final_merge_non_match)
		
	return final_merge, final_merge_match,final_merge_manual,final_merge_non_match,potential_matches, candidates, df, df2


def view_data(df, df2, threshold1,threshold2,final_merge, final_merge_match,final_merge_manual,final_merge_non_match,potential_matches, candidates):
	totalrecords=len(df)
	st1 = st.container()
	st2 = st.container()
	st3 = st.container()
	with st1:
		header_3('Results:')
		col1, col2, col3= st.columns(3)
		with col1:
			header_2("Number of HCP Records")
		with col2:
			header_2("Number of Social Profiles")
		#with col3:
			#header_2("Threshold")
		with col3:
			header_2("Number of Candidate Pairs")
		with col1:
			header_1(str(len(df)))
		with col2:
			header_1(str(len(df2)))
		#with col3:
		#	header_1(str(threshold1))
		with col3:
			header_1(str(len(candidates)))

		col1, col2, col3 = st.columns(3)
		with col1:
			header_2("Number of Matching Profiles")
			st.text("\n")
			st.text("\n")
		with col2:
			header_2("Number of Manual Review Profiles")
		with col3:
			header_2("Number of Non Matching Profiles")
		with col1:
			header_1(str(len(final_merge_match['SrNum1_hcp'].unique())))
		with col2:
			header_1(str(len(final_merge_manual['SrNum1_hcp'].unique())))
		with col3:
			header_1(str(len(final_merge_non_match['SrNum1_hcp'].unique())))

		st.cache()
	hide_dataframe_row_index = """
	            <style>
	            .row_heading.level0 {display:none}
	            .blank {display:none}
	            </style>
	            """
	st.write('<style>div.row-widget.stRadio > div{flex-direction:row;justify-content: center;padding-left:20px;} </style>', unsafe_allow_html=True)
	header_3("View Data")
	viewradio = st.radio("",('Match','Manual','Non Match'))
	if viewradio == "Match":
		st.caption("All the HCPs mapped with score greater than {}% having no other candidate within -{}% window".format(threshold1,threshold2))
		st.markdown(hide_dataframe_row_index, unsafe_allow_html=True)
		st.dataframe(final_merge_match[['SrNum1_hcp','First Name_hcp','Last Name_hcp','Title_hcp','Gender_hcp','City_hcp','State_hcp','first_sm','last_sm','title_sm','Gender_sm','City_sm','State code_sm','handle','Score']])
	if viewradio == "Manual":
		st.caption("All the HCPs mapped with score greater than {}% and having candidates within -{}% window".format(threshold1,threshold2))
		st.caption("All the HCPs mapped with score between {}% and {}%".format(threshold1,threshold1-20))
		st.markdown(hide_dataframe_row_index, unsafe_allow_html=True)
		st.dataframe(final_merge_manual[['SrNum1_hcp','First Name_hcp','Last Name_hcp','Title_hcp','Gender_hcp','City_hcp','State_hcp','first_sm','last_sm','title_sm','Gender_sm','City_sm','State code_sm','handle','Score']])
	if viewradio == "Non Match":
		st.caption("All the HCPs mapped with score less than {}%".format(threshold1-20))
		st.markdown(hide_dataframe_row_index, unsafe_allow_html=True)
		st.dataframe(final_merge_non_match[['SrNum1_hcp','First Name_hcp','Last Name_hcp','Title_hcp','Gender_hcp','City_hcp','State_hcp','first_sm','last_sm','title_sm','Gender_sm','City_sm','State code_sm','handle','Score']])
	
	col5,col6,col7,col8 = st.columns(4)
	final_merge_match.replace({"nan":np.nan},inplace=True)
	final_merge_match = final_merge_match[['SrNum1_hcp','First Name_hcp','Last Name_hcp','Title_hcp','Gender_hcp','City_hcp','State_hcp','first_sm','last_sm','title_sm','Gender_sm','City_sm','State code_sm','handle','Score','Source']]
	final_merge_manual.replace({"nan":np.nan},inplace=True)
	final_merge_manual = final_merge_manual[['SrNum1_hcp','First Name_hcp','Last Name_hcp','Title_hcp','Gender_hcp','City_hcp','State_hcp','first_sm','last_sm','title_sm','Gender_sm','City_sm','State code_sm','handle','Score','Source']]
	final_merge_manual1 = final_merge_manual
	final_merge_manual1['Valid (Enter Y where valid)'] = ''
	final_merge_non_match.replace({"nan":np.nan},inplace=True)
	final_merge_non_match = final_merge_non_match[['SrNum1_hcp','First Name_hcp','Last Name_hcp','Title_hcp','Gender_hcp','City_hcp','State_hcp','first_sm','last_sm','title_sm','Gender_sm','City_sm','State code_sm','handle','Score','Source']]
	potential_matches.replace({"nan":np.nan},inplace=True)
	final_merge1 = final_merge[['SrNum1_hcp','First Name_hcp','Last Name_hcp','Title_hcp','Gender_hcp','City_hcp','State_hcp','first_sm','last_sm','title_sm','Gender_sm','City_sm','State code_sm','handle','Score','Category','Source']]
	with col5:
		st.download_button(label="Download Match data",data=final_merge_match.to_csv(index=False).encode('utf-8'),file_name="Matching HCPs Twitter API.csv",mime='text/csv')
		
	with col6:
		st.download_button(label="Download Manual Review data",data=final_merge_manual1.to_csv(index=False).encode('utf-8'),file_name="Manual Review HCPs Twitter API.csv",mime='text/csv')
	
	with col7:	
		st.download_button(label="Download non Match data",data=final_merge_non_match.to_csv(index=False).encode('utf-8'),file_name="Non Matching HCPs Twitter API.csv",mime='text/csv')
	
	with col8:
		st.download_button(label="Download All HCPs data",data=final_merge1.to_csv(index=False).encode('utf-8'),file_name="All HCPs Twitter API.csv",mime='text/csv')


	#st.download_button(label="Download candidate data",data=potential_matches.to_csv(index=False).encode('utf-8'),file_name="Candidate.csv",mime='text/csv')

	
	return final_merge_match,final_merge_manual,final_merge_non_match

def view_data2(df, final_merge_match, final_merge_non_match, threshold1,threshold2):
	totalrecords=len(df)
	header_3('After Manual Review:')
	col1, col2, col3= st.columns(3)
	with col1:
		header_2("Total Number of HCPs")
		st.text("\n")
		st.text("\n")
	with col2:
		header_2("Number of Matching Profiles")
		st.text("\n")
		st.text("\n")
	with col3:
		header_2("Number of Non Matching Profiles")
	with col1:
		header_1(str(len(df)))
	with col2:
		header_1(str(len(final_merge_match['SrNum1_hcp'].unique())))
	with col3:
		header_1(str(len(final_merge_non_match['SrNum1_hcp'].unique())))

	hide_dataframe_row_index = """
	            <style>
	            .row_heading.level0 {display:none}
	            .blank {display:none}
	            </style>
	            """
	st.write('<style>div.row-widget.stRadio > div{flex-direction:row;justify-content: center;padding-left:20px;} </style>', unsafe_allow_html=True)
	viewradio = st.radio("",('Match','Non Match'), key='2')
	if viewradio == "Match":
		st.dataframe(final_merge_match[['SrNum1_hcp','First Name_hcp','Last Name_hcp','Title_hcp','Gender_hcp','City_hcp','State_hcp','first_sm','last_sm','title_sm','Gender_sm','City_sm','State code_sm','handle','Score']])
	if viewradio == "Non Match":
		st.dataframe(final_merge_non_match[['SrNum1_hcp','First Name_hcp','Last Name_hcp','Title_hcp','Gender_hcp','City_hcp','State_hcp','first_sm','last_sm','title_sm','Gender_sm','City_sm','State code_sm','handle','Score']])
	final_merge_match1 = final_merge_match
	final_merge_match1['Category'] = 'Match'
	final_merge_non_match1 = final_merge_non_match
	final_merge_non_match1['Category'] = 'Non Match'
	finalfile1 = final_merge_match1.append(final_merge_non_match1).drop_duplicates(['SrNum1_hcp'])
	col5,col6,col7 = st.columns(3)
	with col5:
		st.download_button(label="Download Match data",data=final_merge_match.to_csv(index=False).encode('utf-8'),file_name="Matching HCPs After Review.csv",mime='text/csv')
		
	with col6:	
		st.download_button(label="Download Non Match data",data=final_merge_non_match.to_csv(index=False).encode('utf-8'),file_name="Non Matching HCPs After Review.csv",mime='text/csv')
	
	with col7:
		st.download_button(label="Download All HCP data",data=finalfile1.to_csv(index=False).encode('utf-8'),file_name="All HCPs After Review.csv",mime='text/csv')
	
#@st.cache(persist=True)
def manual_file_upload(manualfile):
	
	manualfile['Valid'] = manualfile['Valid (Enter Y where valid)'].replace({'Y':1,'N':0})
	manualfile[['Valid']].fillna(0, inplace=True)
	test4 = manualfile.groupby('SrNum1_hcp')['Valid'].agg(sum)
	test4= test4.reset_index()
	test4.rename(columns={'Valid':'ValidCount'}, inplace=True)
	manualfile = pd.merge(manualfile,test4,on='SrNum1_hcp', how='left')
	if (manualfile['ValidCount'].unique() > 1).any():
		errordf = manualfile[manualfile['ValidCount']>1]
		st.error("Please select only 1 valid candidate for below HCPs in the CSV file")
		st.dataframe(errordf[['SrNum1_hcp','First Name_hcp','Last Name_hcp']].drop_duplicates())
		st.stop()
	test3 = manualfile.groupby('SrNum1_hcp')['Valid'].agg(max)
	test3= test3.reset_index()
	test3.rename(columns={'Valid':'HasValid'}, inplace=True)
	manualfile = pd.merge(manualfile,test3,on='SrNum1_hcp', how='left')
	manualfile.loc[(manualfile['HasValid']==1) & (manualfile['Valid']==1),'File'] = 'Match'
	manualfile.loc[(manualfile['HasValid']==1) & (manualfile['Valid']!=1),'File'] = 'Discard'
	manualfile.loc[(manualfile['HasValid']!=1),'File'] = 'Non Match'
	st.write()
	return manualfile


def search_specialization(site,speciality,result):

	
	#chrome_options = Options()
	#chrome_options.add_argument("user-data-dir=selenium") 
	#driver = webdriver.Chrome(chrome_options=chrome_options)
	with st.spinner(text="Fetching the LinkedIn user handles, Please wait..."):

		chrome_path = (r"C:\Users\sadasivuni.mitra\Downloads\chromedriver_win32\chromedriver.exe")
		#driver = webdriver.Chrome(chrome_options=chrome_options,executable_path=chrome_path)
		driver = webdriver.Chrome(executable_path=chrome_path)
		driver.minimize_window()
		driver.get('https://www.google.com')

		search_query = driver.find_element_by_name('q')

		# send_keys() to simulate the search text key strokes
		search_query.send_keys('site:{} AND "{}"'.format(site,speciality))
		sleep(20)
		# .send_keys() to simulate the return key 
		search_query.send_keys(Keys.RETURN)
		sleep(20)

		global df_spec 
		df_spec=pd.DataFrame()
		df_spec['Speciality']=[]
		df_spec['linkedin_url']=[]
		while len(df_spec)<2:
		    soup = BeautifulSoup(driver.page_source, "lxml")
		    #print(soup.prettify())

		    for div in soup.find_all("div",class_="g tF2Cxc"):
		        try:
		            df_spec=df_spec.append({'Speciality':speciality,'linkedin_url':div.a['href']},ignore_index=True)
		        except:
		            df_spec=df_spec.append({'Speciality':speciality,'linkedin_url':None},ignore_index=True)

		    try:
		        next_button = driver.find_element_by_xpath('//*[@id="pnnext"]') 
		        next_button.click()
		        sleep(20)
		    except:
		        break
	#st.success("Hurray! Data has been collected")
	#st.dataframe(df_spec.head())
	linkedin_url_list = list(df_spec.linkedin_url)
	result = search_linkedin(df_spec.linkedin_url,driver,result)
	return result

def search_linkedin(linkedin_url_list,driver,result):
	#userid = str(input("Enter email address or number with country code: "))
	#password = getpass.getpass('Enter your password:')
	with st.spinner(text="Fetching user details, Please wait..."):

		#userid="mitrasadas310896@gmail.com"
		#password="Zxc@123"
		#chrome_path = (r'C:\Users\sadasivuni.mitra\Downloads\chromedriver_win32\chromedriver.exe') # './chromedriver'
		#driver = webdriver.Chrome(executable_path= chrome_path)   #(chrome_path)

		driver.get("https://www.linkedin.com")
		sleep(10)

		actions.login(driver, userid, password)
		sleep(10)

		def firstname(x):
			if x:
				return x.split()[0]

		def lastname(x):
		    if x:
		    	return x.split()[-1]

		def middlename(x):
		    if x:
		    	return x.split()[1:-1]

		city=[]
		region=[]
		country=[]

		def loca(x):
		    
		    x=x.split(",")
		    
		    if len(x)==1:
		        country.append(x[0])
		        region.append(None)
		        city.append(None)
		    elif len(x)==2:
		        region.append(x[0])
		        country.append(x[1])
		        city.append(None)
		    elif len(x)==3:
		        city.append(x[0])
		        region.append(x[1])
		        country.append(x[2])
		    else:
		        city.append(x[-3])
		        region.append(x[-2])
		        country.append(x[-1])


		for link in linkedin_url_list:
		    result = linkedin_userDetails_extract(link,driver,result)


		result["First_Name"]=result.title.apply(firstname)
		result["Last_Name"]=result.title.apply(lastname)
		result["Middle_Name"]=result.title.apply(middlename)

		result.location.apply(loca)

		result['city']=city
		result['region']=region
		result['country']=country


	st.write("Number of records found:",str(len(result)))

	gastro_tags = ['Gastroenterology', 'Gastro-entérologie', 'Gastro-enterologie', 'Gastroenterologie', 'Gastroenterologist', 
               'Gastro-entérologue', 'gastro-enteroloog', 'Gastroenterologe', 'General gastroenterology', 
               'Gastro-entérologie générale', 'Algemene gastro-enterologie', 'Allgemeine Gastroenterologie', 'Colonoscopy', 
               'Coloscopie', 'colonoscopie', 'Darmspiegelung', 'Gastroscopy', 'Gastroscopie', 'Gastroscopie', 'Gastroskopie',
               'gastroscopies', 'gastroscopies', 'gastroscopieën', 'Gastroskopien', 'Gastro surgeon', 
               'Gastroenterological surgery', 'SURGICAL GASTROENTEROLOGY', 'gastro-entérologie chirurgicale', 
               'chirurgische gastro-enterologie', 'chirurgische Gastroenterologie', 'gastrointestinal surgery',
               'chirurgie gastro-intestinale', 'gastro-intestinale chirurgie', 'Magen-Darm-Chirurgie', 'Fibroscan', 'IBS',
               'Hepatology', 'Hépatologie', 'Hepatologie', 'Hepatologie', 'proctology', 'Proctologie', 'Proctologie',
               'Proktologie', 'proctologist', 'proctologue', 'proctoloog', 'Proktologe', 'Inﬂammaty bowel disease', 
               'Maladie intestinale inflammatoire', 'Inflammatoire darmziekte', 'Entzündliche Darmerkrankung',
               ' Gastro intestinal', 'GI diseases', 'Abdominal discomfort', 'Gêne abdominale', 'Abdominaal ongemak', 
               'Bauchbeschwerden', 'Unintentional weight loss', 'Perte de poids involontaire', 'Onbedoeld gewichtsverlies',
               'Unbeabsichtigter Gewichtsverlust', 'Acid reflux', 'Reflux acide', 'Zure reflux', 'Saurer Reflux', 
               'Fecal incontinence', 'Incontinence fécale', 'Fecale incontinentie', 'Stuhlinkontinenz', 'Fatigue', 'Fatigue',
               'Vermoeidheid', 'Ermüdung', 'Loss of appetite', 'Perte d\'appétit', 'Verlies van eetlust', 'Appetitverlust',
               'Difficulty swallowing', 'Difficulté à avaler', 'Moeite met slikken', 'Schluckbeschwerden', 'colonoscopies',
               'colonoscopies', 'colonoscopieën', 'Koloskopie', 'treatment of inflammatory bowel disease', 
               'traitement des maladies inflammatoires chroniques intestinales', 'behandeling van inflammatoire darmziekten',
               'Behandlung von entzündlichen Darmerkrankungen', 'hepatology', 'hépatologie', 'hepatologie', 'Hepatologie',
               'manometry', 'manométrie', 'manometrie', 'Manometrie', 'hepaticencephalopathy', 'encéphalopathie hépatique',
               'hepatische encefalopathie', 'hepatische Enzephalopathie', 'Gastric reflux', 'Reflux gastrique', 'Maagreflux',
               'Magen-Reflux', 'Gastrointestinal Endoscopy', 'Endoscopie gastro-intestinale', 'Gastro-intestinale endoscopie',
               'Magen-Darm-Endoskopie', 'Endoscopic']          

	def search_tag(s, tags):
	    result = []
	    s = s.lower()
	    for each in tags:
	        if each.lower() in s:
	            result.append(each)
	    result = set(result)
	    return ';'.join(result)
	
	if speciality == "Gastroenterology":
		tags = gastro_tags

	def get_speciality(df):
	    cols = ['summary','about','designation','posts']
	    #df['concat_terms'] = df[cols].apply(lambda row: '_'.join(row.values.astype(str)), axis=1)
	    df['concat_terms'] = df.apply(lambda x:'%s %s %s %s' % (x['summary'],x['about'],x['designation'],x['posts']),axis=1)
	    df['final_tags'] = df['concat_terms'].apply(lambda x: search_tag(x, tags))
	    df['Speciality_Name'] = speciality
	    return df

	result = get_speciality(result)

	st.dataframe(result.head())

	return result

def linkedin_userDetails_extract(link,driver,result):

    driver.get("{}".format(link))
    sleep(10)
    
    driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")

    soup = BeautifulSoup(driver.page_source, 'lxml')

    title = soup.find("h1",class_="text-heading-xlarge inline t-24 v-align-middle break-words")
    if title:
        title = title.text.strip()
    else:
        title = None

    summary = soup.find("div",class_="text-body-medium break-words")
    if summary:
        summary = summary.text.strip()
    else:
        summary = None

    location = soup.find("span",class_="text-body-small inline t-black--light break-words")
    if location:
        location = location.text.strip()
    else:
        location = None
        
    connections = soup.find("span",class_="t-bold")
    if connections:
        connections = connections.text.strip()
    else:
        connections = None
        
    followers = soup.find("p",class_="pvs-header__subtitle text-body-small")
    if followers:
        followers = followers.text.split()[0]
    else:
        followers = None
        
    about = soup.find("div",class_="pv-shared-text-with-see-more t-14 t-normal t-black display-flex align-items-center")
    if about:
        about = about.text.strip()
    else:
        about = None
        
    current_company = soup.find("span",class_="t-14 t-normal")
    if current_company:
        current_company = current_company.find("span",{"aria-hidden":"true"})
        current_company = current_company.text.split("·")[0]
    else:
        current_company = None
        
    designation = soup.find("span",class_="mr1 t-bold")
    if designation:
        designation = designation.find("span",{"aria-hidden":"true"})
        designation = designation.text
    else:
        designation = None
        
    highest_education = soup.find("span",class_="mr1 hoverable-link-text t-bold")
    if highest_education:
        highest_education = highest_education.find("span",{"aria-hidden":"true"})
        highest_education = highest_education.text
    else:
        highest_education = None
        
    driver.get("{}/recent-activity/shares/".format(link))
    sleep(10)
    driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")
    
    soup = BeautifulSoup(driver.page_source, 'lxml')

    recent_posted = soup.find("span",class_="feed-shared-actor__sub-description t-12 t-normal t-black--light")
    if recent_posted:
        recent_posted = recent_posted.text.split("•")[-1].strip()
    else: 
        recent_posted = None
        
    posts=[]
    for post in soup.find_all("span",class_="break-words"):
        if post:
            posts.append(post.text.strip())
        else:
            posts.append(None)

    #global result
    
    result=result.append({"title":title,
                         "summary":summary,
                         "location":location,
                         "connections":connections,
                         "followers":followers,
                         "about":about,
                         "current_company":current_company,
                         "designation":designation,
                         "recent_posted":recent_posted,
                         "posts":posts,
                         "linkedIn_url":link},ignore_index=True)
    return result	

def search_twitter(result):

	df=pd.read_excel("sam_23.xlsx")
	df.dropna(inplace=True)

	Name=[]
	Handle=[]
	Desc=[]
	Location=[]

	chrome_path = (r'C:\Users\sadasivuni.mitra\Downloads\chromedriver_win32\chromedriver.exe')
	driver = webdriver.Chrome(executable_path=chrome_path)
	driver.minimize_window()

	l1=[]
	for i in df["twitterurls"]:
	    l1.append(i)
	    
	for urls in l1:
	    driver.get(urls)
	    sleep(5)
	    driver.execute_script(f"window.scrollTo(0,document.body.scrollHeight);")
	    last_height = driver.execute_script("return document.body.scrollHeight")
	    soup=BeautifulSoup(driver.page_source, 'lxml')
	    try:
	        Name.append(driver.find_element_by_xpath('//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div[2]/div/div/div/div/div[2]/div/div/div[1]/div/div/span[1]/span').text.replace("\n", ""))
	    except:
	        Name.append('NA')
	    try:
	        Handle.append(driver.find_element_by_xpath('//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div[2]/div/div/div/div/div[2]/div/div/div[2]/div/div/div/span').text.replace("\n", ""))
	    except:
	        Handle.append('NA')

	    try:
	        Desc.append(driver.find_element_by_xpath('//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div[2]/div/div/div/div/div[3] /div/div').text.replace("\n", ""))
	    except:
	        Desc.append('NA')
	    try:
	        Location.append(driver.find_element_by_xpath('//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div[2]/div/div/div/div/div[4]/div/span[1]/span/span').text.replace("\n", ""))
	    except:
	        Location.append('NA')

	dt = pd.DataFrame()
	dt['Name'] = Name
	dt['Handle']=Handle
	dt['Desc']=Desc
	dt['Location']=Location

	return dt

def Data_col(result):
	
	#st.markdown("[Please click here to Navigate to Brand Watch](https://www.brandwatch.com/)", unsafe_allow_html=True)
	
	column1,column2 = st.columns(2)

	with column1:

	#st.write('Click here to Navigate to Brand Watch:', Brand_Watch)
		specializations=["",'Acupuncture', 'Allergology', 'Anesthesiology', 'Arts in specialization', 'Cardiology', 'Clinical biology', 
		'Dermatology', 'Diabetology', 'emergency doctor', 'Endocrinology', 'Gastroenterology', 'General medicine', 'General Surgery', 
		'Geriatrics', 'Hematology', 'Hepatology', 'Homeopathy', 'Hospital pharmacist', 'Hospital pharmacy', 'Hygienist medicine', 
		'Infectiology', 'Intensive care', 'Internal Medicine', 'Nephrology', 'Neurology', 'Neuropsychiatry', 'Non-Physician', 
		'Nuclear Medicine', 'Nurse', 'O.R.L.', 'Occupational Medicine', 'Oncology', 'Pathological anatomy', 'Pediatrics', 'Pharmacist', 
		'Physician Hygienist', 'Physician Specialist', 'Procto-angiology', 'Psychiatry', 'Pulmonology', 'Radiotherapy', 'Reumatology', 
		'Sports medicine', 'Thorax surgery']

		specialization = st.selectbox('Please enter the Keywords to search:',specializations,key='sel1')

	with column2:
		Social_handles=["",'Twitter',"LinkedIn"]

		Social_handle = st.selectbox("Please select a social handle:",Social_handles,key='sel1' )

	search = st.button("Search")

	if search:

		if Social_handle == "LinkedIn":
			site = "linkedin.com/in/"
			result = search_specialization(site,specialization,result)
			st.download_button(label="Download LinkedIn user Data as CSV",data=result.to_csv(index=False).encode('utf-8'),file_name="LinkedIn_UserData.csv",mime='text/csv')
			st.stop()

		if Social_handle == "Twitter":
			#site = "twitter.com/"
			#result = search_specialization(site,specialization)
			with st.spinner(text="Fetching user details, Please wait..."):
				result = search_twitter(result)
			
			st.download_button(label="Download Twitter user Data as CSV",data=result.to_csv(index=False).encode('utf-8'),file_name="Twitter_UserData.csv",mime='text/csv')
			st.write("File Name: Twitter_UserData")
			st.write("Number of Records: ",str(len(result)))
			st.dataframe(result.head())
			#st.stop()

	return result

@st.cache(persist=True,allow_output_mutation=True)
def profilesearch(df):

	first = df['First Name'][:2]
	last = df['Last Name'][:2]
	f_name = first+" "+last

	chrom_opt = Options()
	chrom_opt.add_argument("--disable-extensions")
	chrom_opt.add_argument("--disable-gpu")
	chrom_opt.headless = True
	driver = webdriver.Chrome(chrome_options=chrom_opt)
	handle_list = []
	name = []

	with st.spinner(text="Fetching relevant profiles using combination of \nHCP FirstName and Last Name, Please wait...."):	
		for i in f_name:
		    url = "https://twitter.com/search?q=({})%20&src=typed_query&f=user".format(i)
		    #print(url)
		    driver.get(url)
		    sleep(2)
		    last_height = 0
		    for p in range(10):
		        soup = BeautifulSoup(driver.page_source,"lxml")
		        for div in soup.find_all("div",class_="css-901oao css-1hf3ou5 r-14j79pv r-18u37iz r-37j5jr r-a023e6 r-16dba41 r-rjixqe r-bcqeeo r-qvutc0"):
		            handle = div.text
		            handle = div.text.strip()
		            #print(handle)
		            handle_list.append(handle)
		            name.append(i)
		        driver.execute_script(f"window.scrollTo(0,document.body.scrollHeight);")
		        sleep(2)
		        current_height = driver.execute_script("return document.body.scrollHeight")
		        if current_height == last_height:
		            break
		        last_height = current_height

		for j,k in zip(first,last):
		    url = "https://twitter.com/search?q={}%20OR%20{}%20&src=typed_query&f=user".format(j,k)
		    #print(url)
		    driver.get(url)
		    sleep(2)
		    last_height = 0
		    for p in range(10):
		        soup = BeautifulSoup(driver.page_source,"lxml")
		        for div in soup.find_all("div",class_="css-901oao css-1hf3ou5 r-14j79pv r-18u37iz r-37j5jr r-a023e6 r-16dba41 r-rjixqe r-bcqeeo r-qvutc0"):
		            handle = div.text
		            handle = div.text.strip()
		            #print(handle)
		            handle_list.append(handle)
		            name.append(j+' '+k)
		        driver.execute_script(f"window.scrollTo(0,document.body.scrollHeight);")
		        sleep(2)
		        current_height = driver.execute_script("return document.body.scrollHeight")
		        if current_height == last_height:
		            break
		        last_height = current_height

	d = pd.DataFrame()
	d['name'] = name
	d["handle_list"] = handle_list
	d.drop_duplicates(subset=['handle_list'],inplace=True)

	return d

def datacleaning(df):
	st.dataframe(df.head())
	# st.caption("Features considered for preprocessing:")
	# st.caption("Full Name, City Code, Professions, Hastags")
	# st.caption("preprocessing involves:")
	# st.caption("1.Removal of duplicacy")
	# st.caption("2.Cleaning and Categoring Full Name to First, Middle and Last Name")
	# st.caption("3.Separation of titles from Full Name")
	# st.caption("4.Converstion of city code to state")
	with st.spinner("Data cleaning in progress, please wait...."):
		d=pd.DataFrame()
		d_author = []
		d_hastag = []

		with st.spinner("Identifying duplicate profiles and cleaning..."):
			
			for i in df['Author'].unique():
				d_author.append(i)
				d_hastag.append(", ".join(list(df[df.Author == i]['Hashtags'].dropna())))
			    
			d['Author']=d_author
			d['All_hastags'] = d_hastag

			df1 = pd.merge(df,d,how='inner',on=['Author'])
			df = df1.drop_duplicates(subset=['Author'])
			df.reset_index(drop=True,inplace=True)

		def namecleaning(x):
			x= x.split(maxsplit=1)[1]
			x= re.sub('[^\w\s,-]', '', x)
			x= p.clean(x)
			return x

		def citycode(x):
			try:
				x = x.split(".")[1]
				return x
			except:
				return None
		with st.spinner("Cleaning the profile names"):    
			df['Full Name cleaned'] = df['Full Name'].apply(namecleaning)
		lst = ["AACC","AAHIVP","AAS","ABAAHP","ABD","ABLM","ABOM","ABPP","ACCNSP","ACHPN","ACS","AFAASLD","AGCNSBC","AGNPC","AGPCNP","AIBVRC","ANPBC","AOCNP","AOCNS","APRN","APSW","ASCP","ATC","ATSF","BCACP","BCCCP","BCCP","BCIDP","BCOP","BCPA","BCPPS","BCPS","BSc","BSN","CACP","CAQSM","CBM","CCAP","CCCSLP","CCDS","CCHP","CCRC","CCRN","CCRNCSC","CCRP","CCSP","CCTP","CDCES","CDE","CDN","CEHP","CFLE","CFPS","CGC","CHFN","CIC","CIH","CKNS","CLS","CLT","CMD","CMN","CMPC","CNE","CNM","CNS","CPA","CPC","CPCS","CPE","CPH","CPhT","CPI","CPN","CPNPAC","CPNPPC","CPT","CRNA","CRNP","CRS","CRT","CSAT","CSCN","CSCS","CSM","CSR","CSSD","CST","CV","DABAT","DABCC","DABOM","DABR","DABS","DC","DD","DDS","DFAPA","Dipl","DMD","DMedSc","DNP","DO","DPM","DPT","Dr","DS","DVM","EdD","EEG","ELS","EMT","EMTP","es","Esq","FAAD","FAAFP","FAAHKS","FAAHPM","FAAN","FAANA","FAANS","FAAOS","FAAP","FABNO","FACC","FACE","FACEP","FACG","FACHE","FACOG","FACOP","FACOS","FACP","FACPM","FACR","FACS","FAEMS","FAHA","FAIUM","FAMIA","FAND","FAOA","FASA","FASCO","FASCP","FASCRS","FASE","FASN","FAST","FCAP","FCCM","FCCP","FESC","FHFSA","FHRS","FIDSA","FNKF","FNLA","FNLDI","FNP","FNPBC","FNPC","FNPS","FPC","FPMRS","FRCP","FRCPC","FRCSC","FRCSEd","FSCAI","FSCCT","FSCMR","FSIR","FSVM","FSVS","GC","GCDF","GED","HMDC","IBCLC","IFMCP","IHC","INHC","ISE","IV","JD","AFCON","Jr","LAc","law","LCAC","LCGC","LCPC","LCSW","LD","LDN","LE","LICSW","LLC","LMSW","LMT","LP","LPC","LPCC","LPN","LRCPI","LRCSI","MA","MACC","MACP","MAM","MAN","MAS","MBA","MBBS","MBI","MBMS","MBS","MCh","md","MD","MDiv","Mecca","MEd","MEHP","MFA","MHA","MHPE","MHR","MHS","MHSc","MIAC","MLA","MLS","MLSASCP","MM","MMM","MMSc","MOT","MPA","MPE","mph","MPhil","MPHTM","MPP","MRC","MRCSI","MS","MSc","MSCE","MSCI","MSCN","MSCR","MSCS","MSHS","MSME","MSN","MSPH","MSW","myself","NBCT","NCC","NCSN","NCSP","NCTTP","ND","NJWO","NP","NPC","NRP","Nurse","NVRN","OCDT","OCN","OCS","OD","ONC","OT","PAC","PCS","PE","Pharm","PharmD","PhD","PhDoubleDs","PHN","PNPBC","Professor","Psychologist","PsyD","PT","QIAASCP","Quichocho","RBT","RD","RDH","RDN","RhMSUS","RKmd","RN","RNBC","RNCOB","RPh","RPVI","RRT","RVT","Science","SCRN","Sr","ThM","VP","VTILVOT","WCC","WHNPBC","do"]

		fullname=[]
		main_title=[]
		with st.spinner("Seperating out the titles from profile Names"):
			for j in range(len(df)):
				name=[]
				title=[]
				for i in df['Full Name cleaned'][j].split():
					i = re.sub('[^\w\s]', '', i)
					if i in lst:
						title.append(i)
					else:
						name.append(i)
				fullname.append(" ".join(name))
				main_title.append(" ".join(title))

		with st.spinner("Categories Full Name to First,Middle and Last Name"):    
			df['newfullname'] = fullname
			df['title'] = main_title

			df["First Name"] = df["newfullname"].apply(lambda x: HumanName(x).first)
			df["Middle Name"] = df["newfullname"].apply(lambda x: HumanName(x).middle)
			df["Last Name"] = df["newfullname"].apply(lambda x: HumanName(x).last)

			df.Gender.replace({'male':'M','female':'F','unknown':np.nan},inplace=True)
			df['State code'] = df['City Code'].apply(citycode)
		
		with st.spinner("Separating out the Job titles"):
			profession_1 = []
			profession_2= []
			profession_3= []
			Job_title_1= []
			Job_title_2= []
			Job_title_3= []

			for i in df.Professions:
			    
			    try:
			        l = i.split("},")
			        if len(l)==1:
			            prof1 = l[0].split(',')[0].split("=")[1].strip("}")
			            job1 = l[0].split(',')[1].split("=")[1].strip("}")
			            prof2 = None
			            job2 = None
			            prof3 = None
			            job3 = None

			        elif len(l)==2:
			            prof1 = l[0].split(',')[0].split("=")[1].strip("}")
			            job1 = l[0].split(',')[1].split("=")[1].strip("}")
			            prof2 = l[1].split(',')[0].split("=")[1].strip("}")
			            job2 = l[1].split(',')[1].split("=")[1].strip("}")
			            prof3 = None
			            job3 = None
			            

			        elif len(l)==3:
			            prof1 = l[0].split(',')[0].split("=")[1].strip("}")
			            job1 = l[0].split(',')[1].split("=")[1].strip("}")
			            prof2 = l[1].split(',')[0].split("=")[1].strip("}")
			            job2 = l[1].split(',')[1].split("=")[1].strip("}")
			            prof3 = l[2].split(',')[0].split("=")[1].strip("}")
			            job3 = l[2].split(',')[1].split("=")[1].strip("}")


			        else:
			            prof1 = l[0].split(',')[0].split("=")[1].strip("}")
			            job1 = l[0].split(',')[1].split("=")[1].strip("}")
			            prof2 = None
			            job2 = None
			            prof3 = None
			            job3 = None
			        
			        profession_1.append(prof1)
			        profession_2.append(prof2)
			        profession_3.append(prof3)
			        Job_title_1.append(job1)
			        Job_title_2.append(job2)
			        Job_title_3.append(job3)
			    
			    except:
			        profession_1.append(None)
			        profession_2.append(None)
			        profession_3.append(None)
			        Job_title_1.append(None)
			        Job_title_2.append(None)
			        Job_title_3.append(None)
			        

			df['Profession_1'] = profession_1
			df['Job_title_1'] = Job_title_1
			df['Profession_2'] = profession_2
			df['Job_title_2'] = Job_title_2
			df['Profession_3'] = profession_3
			df['Job_title_3'] = Job_title_3
	st.success("Data Cleaning is successful")
	# st.dataframe(df.head())	
	return df

def fetch_desc(cleaned_sm):
	twitterurls = "https://twitter.com/"+cleaned_sm['Author']
	chrom_opt = Options()
	chrom_opt.add_argument("--disable-extensions")
	chrom_opt.add_argument("--disable-gpu")
	chrom_opt.headless = True
	driver = webdriver.Chrome(chrome_options=chrom_opt)

	Handle=[]
	Desc=[]
	Location = []
	with st.spinner("Parsing through SM profiles to fetch Bio/Description, Please wait..."):
		for url in twitterurls:
		    driver.get(url)
		    sleep(1)
		    soup=BeautifulSoup(driver.page_source, 'lxml')
		    try:
		        Handle.append(driver.find_element_by_xpath('//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div[2]/div/div/div/div/div[2]/div/div/div[2]/div/div/div/span').text.replace("\n", ""))
		    except:
		        Handle.append(np.nan)

		    try:
		        Desc.append(driver.find_element_by_xpath('//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div[2]/div/div/div/div/div[3]/div/div').text.replace("\n", ""))
		    except:
		        Desc.append(np.nan)
		    try:
		        Location.append(driver.find_element_by_xpath('//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div[2]/div/div/div/div/div[4]/div/span[1]/span/span').text.replace("\n", ""))
		    except:
		        Location.append(np.nan)

	driver.delete_all_cookies()
	driver.close()

	result =pd.DataFrame()
	result["Author"] = Handle
	result["Desc"] = Desc
	result["Location"] = Location
	result['Author'] = result['Author'].str.replace('@','')
	#st.dataframe(result)
	st.success('Bio/Description details for SM profiles are Successfully parsed')

	df_sm = pd.merge(cleaned_sm,result,how='left',on='Author')
	st.caption('Sample data after cleaning:')
	st.dataframe(df_sm.head())

	return df_sm


image = Image.open('Indegene_Logo.png')
st.sidebar.image(image, width=200, clamp=False, channels="RGB", output_format="auto")


activities = ["Data Collection", "Social Media Handle Mapping", "Affinity Calculation", "Sentiment Analysis"]
choice = st.sidebar.selectbox("Select Activity", activities, key='sel1')

@st.cache
def calc_affinity(df, df2):
	df2 = df2[['Date','Author','Full Text','Twitter Followers','Twitter Following','Twitter Tweets']]
	df2 = df2.sort_values(by=['Author','Date'], ascending=[True,False])
	d=pd.DataFrame()
	d_author = []
	d_tweets = []
	for i in df2['Author'].unique():
		d_author.append(i)
		d_tweets.append(";; ".join(list(df2[df2.Author == i]['Full Text'].dropna())))
	    
	d['Author']=d_author
	d['All_Tweets'] = d_tweets

	df2 = pd.merge(df2,d,how='inner',on=['Author'])
	df2 = df2.drop_duplicates(subset=['Author'])
	df2.reset_index(drop=True,inplace=True)
	

	tags = ['cancer','cdk inhibitor','trilaciclib','cmv','cytomegalovirus','cpx','ctn','hif','belzutifan','jak','Janus kinase inhibitors','pde','vegf','abdominal','abiraterone','enzalutamide','acral','acral rash','adipose','agglutinin','alcohol septal','allopurinol','AML','alveolar','annexin','anthracycline','anticancer','antiglobulin','aspirin','atovaquone azithromycin','axillary','lymphoma','basement membrane','oncology','malignant','bevacizumab','bispecific antibody','bladder cancer','blister','blood cancer','blood cell','blood clot','blood saliva','blood vein','body disease','bone joint','bone marrow','Borrelia burgdorferi','bortezomib cyclophosphamide','biopsy','bowel','brafvmutant nonmelanoma cancer','brain cell','leptomeningeal','lung cancer','prostate cancer','breast cancer','endometrial','breast nipple dimpling','ovarian cancer','breast tissue','cabozantinib','cadaver','cancer cell','cancer genitourinary system','cancer memoriam','noncancerous','cancer plasma cell','cancer sacituzumab','capecitabine','caput','carboplatin','carcinoid','carcinoma','cardiac','cardiovascular','carfilzomib','MRCC','ceftriaxone','cell body','integrin','cancer center','cell prolification','cell surface','cellular cancer','cerebro','cerebrospinal fluid','cerebrum','cervical','cervical cancer','cervix cancer','cetuximab','chemo','cancer patient','chemotreated','chest tightness','chromatin','chromosome','cisplatin','colchicine','colon cancer','colorectal','colorectal tumor','coma','cordova','coregulators','cheek info cancer','coronary artery','cubam amultiligand receptor','cxcl','cyclophosphamide','cytarabine','cytoxan','dalteparin','daratumumab','decoy molecule','dendritic','derm','dexamethasone','dimenhydrinate','dna','docetaxel','dorsal','doxycycline','ecmo','eculizumab','ediatricians','egfr','colorectal cancer','eltrombopag','emicizumab pups','endocrine','endometrial cancer','endothelium','eosinophil','ependymoma','epidermal growth factor','erdafitinib','eribulin','erythroblast','esophageal cancer','estrogen receptor','etoposide','everolimus','factor v leiden','gallbladder cancer','gamma secretase','gastric cancer','gastroesophageal','gastroesophageal cancer','gastrointestinal','gemfibrozil','genitourinary','genitourinary cancer','genmab','genome','gliblastoma','glioma','glomerular capillary','glutamate','glycine','graft','gyn cancer','grfs ','gut','gynecological cancer','haem','stem cell','head neck cancer patient','hct','hdac','head neck cancer','malignancy','heart','hematology','hematocrit rbc','hematologic','hematologic cancer','hematopoietic','heme','heme solid','hemophilia','hep c','hepatitis b cancer','hepatocytes','hepcidin','hodgkin','oropharyngeal cancer','hras','hsv','human brain','human telomerase','hydroxychloroquine','ibrutinib','igg','imatinib','immune','immune colitis','immunoglobulin','infliximab','inotuzumab','insulin','intestinal cell','intracranial','iodine','ipilimumab','ipilumumab','iron dextran','ivermectin','joint synovium','karyopharm','kidney','kidney cancer','kidney renal','kras','lamivudine','lateral pelvic','latino cancer','leiomyosarcoma','lenalidomide','lenvatinib','leucocyte','leukaemia','levofloxacin','lipid','liver','liver cancer','loperamide','lung cancer','melanoma','leukemia','sarcoma','myeloma','tumor','basal squamous subtypehigh osteopontin']
	df2['Relevancy'] = df2.apply(lambda row : search_tag(row['All_Tweets'], tags), axis = 1)
	df2 = df2.drop(['Full Text','All_Tweets'], axis=1)
	df2['Last Tweeted Date'] = df2['Date'].str.split(" ").str[0]
	df2['Current Date'] = pd.to_datetime('today').date()
	df2['Current Date'] = df2['Current Date'].astype(str)
	df2[['Last Tweeted Date','Current Date']] = df2[['Last Tweeted Date','Current Date']].apply(pd.to_datetime)
	df2['Days Since Last Tweet'] = (df2['Current Date'] - df2['Last Tweeted Date']) / np.timedelta64(1, 'D')
	
	df2['Scores - presence_twitter'] = 1
	df2['Score - no. of Tweets_twitter'] = calcscore(df2['Twitter Tweets'], 0.7, 0.4)
	df2['Scores - no. of Followers_twitter'] = calcscore(df2['Twitter Followers'], 0.7, 0.4)
	df2['Scores - no. of Following_twitter'] = calcscore(df2['Twitter Following'], 0.7, 0.4)
	df2.loc[df2['Relevancy']=='1', 'Scores - Relevancy_twitter'] = 0.5
	df2.loc[df2['Relevancy']=='1', 'Scores - Relevancy_twitter'] = 0.3
	df2.loc[df2['Days Since Last Tweet']>60,  'Scores - Recency of post_twitter'] = 0.2
	df2.loc[(df2['Days Since Last Tweet']<=60) & (df2['Days Since Last Tweet']>30),  'Scores - Recency of post_twitter'] = 0.3
	df2.loc[(df2['Days Since Last Tweet']<=30),  'Scores - Recency of post_twitter'] = 0.5

	df2['Total Score_twitter'] = df2.apply(lambda row: row['Scores - presence_twitter']*0.5 + row['Score - no. of Tweets_twitter']*0.2 + row['Scores - no. of Followers_twitter']*0.2 + row['Scores - no. of Following_twitter']*0.2 + row['Scores - Recency of post_twitter']*0.2 + row['Scores - Relevancy_twitter']*0.2, axis=1)
	df2['Total Score_twitter'] = df2['Total Score_twitter'].round(4)
	return df2

@st.cache
def search_tag(s, tags):

    s = s.lower()
    s = re.sub(r'[^a-zA-Z ]', '', s)
    flg = '0'
    for each in tags:
        if each.lower() in s:
            flg = '1'
            break
    return flg

@st.cache
def calcscore(df, q1, q2):
	df = pd.DataFrame(df)
	df.columns = ['Value']
	df = df.astype(float)
	cut1 = df.quantile(q1).round(decimals=0).values[0]
	cut2 = df.quantile(q2).round(decimals=0).values[0]
	#st.write(cut1, cut2)
	df.loc[df['Value']>=cut1, 'Score'] = 0.5
	df.loc[(df['Value']<cut1) & (df['Value']>=cut2), 'Score'] = 0.3
	df.loc[df['Value']<cut2, 'Score'] = 0.2
	df.loc[df['Value'].isin([0,'']), 'Score'] = 0
	return df['Score']

@st.cache
def calcscore_noroundoff(df, q1, q2):
	df = pd.DataFrame(df)
	df.columns = ['Value']
	df = df.astype(float)
	cut1 = df.quantile(q1).values[0]
	cut2 = df.quantile(q2).values[0]
	#st.write(cut1,cut2)
	df.loc[df['Value']>=cut1, 'Score'] = 0.5
	df.loc[(df['Value']<cut1) & (df['Value']>=cut2), 'Score'] = 0.3
	df.loc[df['Value']<cut2, 'Score'] = 0.2
	df.loc[df['Value'].isin([0,'']), 'Score'] = 0
	return df['Score']
    
def viewpie(finaldf):
	finaldf['Total Score_twitter'] = finaldf['Total Score_twitter'].replace('nan', '0')
	finaldf['Total Score_twitter'] = finaldf['Total Score_twitter'].astype(float)
	finaldf.loc[(finaldf['Total Score_twitter']>=0) & (finaldf['Total Score_twitter']<=0.70), 'Affinity'] = 'Below 70%'
	finaldf.loc[(finaldf['Total Score_twitter']>0.7) & (finaldf['Total Score_twitter']<=0.8), 'Affinity'] = 'Between 70% to 80%'
	finaldf.loc[(finaldf['Total Score_twitter']>0.8) & (finaldf['Total Score_twitter']<=0.9), 'Affinity'] = 'Between 80% to 90%'
	finaldf.loc[(finaldf['Total Score_twitter']>0.9), 'Affinity'] = 'Above 90%'

	import plotly.express as px
	fig = px.histogram(
		finaldf,
    x = 'Affinity')
	st.plotly_chart(fig)

def sentiment_scores2(sentence):
	sentiment = ""
	sid_obj = SentimentIntensityAnalyzer()
	sentiment_dict = sid_obj.polarity_scores(sentence)

	if sentiment_dict['compound'] >= 0.05 :
		sentiment = "Positive"
	elif sentiment_dict['compound'] <= - 0.05 :
		sentiment = "Negative"
	else :
		sentiment = "Neutral"

	return sentiment_dict['compound'],sentiment


def func(choice):

	# if choice == "Data Preparation":
	# 	st.subheader('Data Preparation')
	# 	data = st.file_uploader("Upload brandwatch file for preprocessing",type=["xlsx"])
		
	# 	if data is not None:
	# 		flg = 'N'
	# 		with st.spinner("Uploading and Reading the file..."):
	# 			df = pd.read_excel(data)
	# 			#df = df.astype(str)
	# 		df =df.head()
	# 		cleaned_sm = datacleaning(df)

	# 		#st.caption('Using open parser to fetch the Bio/Description for SM handles')
	# 		df_sm = fetch_desc(cleaned_sm)
	# 		st.caption("Final SM profiles are ready for Name Matching model")
	# 		#st.download_button(label="Download Social Media Profile information",data=df_sm.to_excel("Social Media profile information.xlsx",index=False).encode('utf-8'),file_name="Social Media profile information.xlsx",mime='xlsx')
	# 		#st.download_button(label='Download Social Media Profile information', data=df_sm , file_name= "Social Media profile information.xlsx", mime="application/vnd.ms-excel")
	# 		def to_excel(df):
	# 		    output = BytesIO()
	# 		    writer = pd.ExcelWriter(output, engine='xlsxwriter')
	# 		    df.to_excel(writer, index=False, sheet_name='Sheet1')
	# 		    workbook = writer.book
	# 		    worksheet = writer.sheets['Sheet1']
	# 		    format1 = workbook.add_format({'num_format': '0.00'}) 
	# 		    worksheet.set_column('A:A', None, format1)  
	# 		    writer.save()
	# 		    processed_data = output.getvalue()
	# 		    return processed_data
	# 		df_sm = to_excel(df_sm)
	# 		st.download_button(label='Download Social Media Profile information',
	# 		                                data=df_sm ,
	# 		                                file_name= 'Download Social Media Profile information.xlsx')
	# 		st.stop()

	if choice == "Data Collection":
		st.subheader('Data Collection')
		result = pd.DataFrame(columns=['title', 'First_Name', 'Last_Name', 'Middle_Name', 'summary',
	       'location', 'city', 'region', 'country', 'connections', 'followers',
	       'about', 'current_company', 'designation', 'recent_posted', 'posts',
	       'linkedIn_url'])

		df = pd.DataFrame()	
		data = st.file_uploader("Upload HCP Dataset",type=["xlsx"])
		with st.spinner("Uploading and Reading the Data...."):
			if data is not None:
				flg = 'N'
				df = pd.read_excel(data)
				df = df.astype(str)
				df = df[["URL","First Name","Middle Name",'Last Name','Title','Gender','City','State']]
				st.dataframe(df.head())	
		if len(df)>0:
			sm_handles = profilesearch(df)
			col3, col4 = st.columns(2)
			col3.metric("",sm_handles.name.nunique(),"Number of HCPs searched for")
			col4.metric("",len(sm_handles),"Number of Handles Fetched")
			sm_handles['Platform'] = 'twitter'
			if len(sm_handles)>0:
				sm_handles = sm_handles[['handle_list','Platform']]
				st.download_button(label="Download Social Media Handles as CSV",data=sm_handles.to_csv(index=False).encode('utf-8'),file_name="Social Media Handles.csv",mime='text/csv')
				# st.caption("The Handles fetched needs to be uploaded to brandwatch by creating a social panel.")
				# st.caption("The Social panel needs to tagged to a query editor using medicalKeywords for search.")
				# st.caption("The brandwatch would give the complete profile information of these handles.")
				# st.caption("Please upload the file that received from brandwatch for further preprocessing.")
		
			st.subheader('Data Preparation')
			data = st.file_uploader("Upload brandwatch file for preprocessing",type=["xlsx"])
			
			if data is not None:
				flg = 'N'
				with st.spinner("Uploading and Reading the file..."):
					df = pd.read_excel(data)
					#df = df.astype(str)
				df =df.head()
				cleaned_sm = datacleaning(df)
				st.caption('Using open parser to fetch the Bio/Description for SM handles')
				df_sm = fetch_desc(cleaned_sm)
				st.caption("Final SM profiles are ready for Name Matching model")
				#st.download_button(label="Download Social Media Profile information",data=df_sm.to_excel("Social Media profile information.xlsx",index=False).encode('utf-8'),file_name="Social Media profile information.xlsx",mime='xlsx')
				#st.download_button(label='Download Social Media Profile information', data=df_sm , file_name= "Social Media profile information.xlsx", mime="application/vnd.ms-excel")
				def to_excel(df):
				    output = BytesIO()
				    writer = pd.ExcelWriter(output, engine='xlsxwriter')
				    df.to_excel(writer, index=False, sheet_name='Sheet1')
				    workbook = writer.book
				    worksheet = writer.sheets['Sheet1']
				    format1 = workbook.add_format({'num_format': '0.00'}) 
				    worksheet.set_column('A:A', None, format1)  
				    writer.save()
				    processed_data = output.getvalue()
				    return processed_data
				df_sm = to_excel(df_sm)
				st.download_button(label='Download Social Media Profile information',
				                                data=df_sm ,
				                                file_name= 'Download Social Media Profile information.xlsx')
				st.stop()
	

	if choice =='Social Media Handle Mapping':
		st.subheader('Social Media Handle Identification')	
		threshold1 = st.sidebar.slider('Select Threshold (Minimum score for candidate to be considered as a match)',50, 100,value=85, step=1)
		threshold2 = st.sidebar.slider('Select Window Size (Window size for candidate to be considered for manual review)',1, 10,value=5, step=1)
		df=pd.DataFrame()
		df2=pd.DataFrame()
		data=pd.DataFrame()
		data2=pd.DataFrame()
		col1, col2 = st.columns(2)
		with col1:
			data = st.file_uploader("Upload HCP Dataset",type=["xlsx"])
		with col2:
			data2 = st.file_uploader("Upload Social Media Dataset",type=["xlsx"])
		if (data is not None) & (data2 is not None):
			df, df2 = upload1(data, data2)
			
			if (len(df)>0) & (len(df2)>0):
				with col1:
					dataframe_head(df)
					all_columns = df.columns.to_list()
				with col2:	
					dataframe_head(df2)
					all_columns1 = df2.columns.to_list()
				final_merge, final_merge_match,final_merge_manual,final_merge_non_match,potential_matches, candidates, df, df2 = getoutput(df, df2, threshold1, threshold2)
				final_merge_match,final_merge_manual,final_merge_non_match = view_data(df, df2, threshold1,threshold2,final_merge, final_merge_match,final_merge_manual,final_merge_non_match,potential_matches, candidates)

				if len(final_merge_manual)>0:
					manualfile = st.file_uploader("Upload Manually Reviewed Dataset",type=["csv"])
					if manualfile is not None:
						manualfile = pd.read_csv(manualfile)
						manualfile = manual_file_upload(manualfile)
						if manualfile is not None:
							manual_match = manualfile[manualfile['File']=='Match']
							manual_non_match = manualfile[manualfile['File']=='Non Match']
							manual_match = manual_match[['SrNum1_hcp','First Name_hcp','Last Name_hcp','Title_hcp','Gender_hcp','City_hcp','State_hcp','first_sm','last_sm','title_sm','Gender_sm','City_sm','State code_sm','handle','Score']]
							manual_non_match = manual_non_match[['SrNum1_hcp','First Name_hcp','Last Name_hcp','Title_hcp','Gender_hcp','City_hcp','State_hcp','first_sm','last_sm','title_sm','Gender_sm','City_sm','State code_sm','handle','Score']]
							final_merge_match = final_merge_match.append(manual_match)
							final_merge_non_match = final_merge_non_match.append(manual_non_match)
							view_data2(df, final_merge_match, final_merge_non_match, threshold1,threshold2)

				st.caption("Description:")
				st.caption("The model creates candidate pairs from Full Name in the HCP data and Socia Media data based on sortedneighbourhood indexing.")
				st.caption("All the features selected for name matching are then compared for each candidate pair. Each feature is compared with the corresponding feature using the exact match, bag of words or Levenstein method of string similarity. Based on the matching features, a probability score (%) is assigned to each candidate pair.")
				st.caption("All the candidate pairs with probability over a specified threshold is considered as a match and the rest are considered as non-matches. The threshold is 80% by default, however, the user has an option of modifying it on the UI.")
				
				#st.write(len(manual_match))
				#st.write(len(manual_non_match['SrNum1_hcp'].unique()))
				#st.write(final_merge_match.columns)
				#st.write(manual_match.columns)
		st.stop()

	if choice == 'Affinity Calculation':
		st.subheader('Affinity Calculation')
		st.write('<style>div.row-widget.stRadio > div{flex-direction:row} </style>', unsafe_allow_html=True)
		source = st.radio("Select Source for Affinity Check", ('Twitter','LinkedIn','Instagram'))
		if source == 'Twitter':
			col1, col2 = st.columns(2)
			with col1:
				data = st.file_uploader("Upload Matching Data for Affinity Calculation",type=["csv"])
				
			with col2:
				data2 = st.file_uploader("Upload Brandwatch Data",type=["csv"])

			if (data is not None) & (data2 is not None):
				df = pd.read_csv(data)
				df = df.astype(str)
				df['Author'] = df['handle'].str.replace("@","")
				df2 = pd.read_csv(data2, skiprows=6)
				df2 = df2.astype(str)
				with col1:
					dataframe_head(df)
				with col2:
					dataframe_head(df2)
				df2 = calc_affinity(df, df2)
				finaldf = pd.merge(df,df2,on='Author', how='left')
				finaldf = finaldf.astype(str)
				#finaldf['Full Text'] = finaldf['Full Text'].str.replace(",","")
				#finaldf['All_Tweets'] = finaldf['All_Tweets'].str.replace(",","")
				st.subheader("Results")
				
				viewpie(finaldf)
				st.dataframe(finaldf)
				st.download_button(label="Download Affinity data",data=finaldf.to_csv(index=False).encode('utf-8'),file_name="Affinity Data.csv",mime='text/csv')
		if source == 'LinkedIn':
			st.write(""" <style> .font {color: #4C9900;} </style> """, unsafe_allow_html=True)
			st.write('<p class="font"><b>Work In Progress</b></p>', unsafe_allow_html=True)
		if source == 'Instagram':
			st.write(""" <style> .font {color: #4C9900;} </style> """, unsafe_allow_html=True)
			st.write('<p class="font"><b>Work In Progress</b></p>', unsafe_allow_html=True)


	if choice == 'Sentiment Analysis':
		st.subheader('Sentiment Analysis')
		col1, col2 = st.columns(2)
		with col1:
			data = st.file_uploader("Upload Matching Data for Sentiment Analysis",type=["csv"])
			
		with col2:
			data2 = st.file_uploader("Upload Tweets Data",type=["csv"])
		if (data is not None) & (data2 is not None):
			df = pd.read_csv(data)
			df = df.astype(str)
			df['Author'] = df['handle'].str.replace("@","")
			df2 = pd.read_csv(data2, skiprows=6)
			df2 = df2.astype(str)
			with col1:
				dataframe_head(df)
			with col2:
				dataframe_head(df2)
			finaldf = pd.merge(df,df2,on='Author', how='left')
			finaldf = finaldf.astype(str)
			finaldf = finaldf[['First Name_hcp','Last Name_hcp','Title_hcp','Gender_hcp','City_hcp','State_hcp','Author','Score','Full Text','Sentiment']]
			#for i,row in finaldf.iterrows():
			#	sentence = str(row["Full Text"])
			#	score, sentiment = sentiment_scores2(sentence)
			#	finaldf.loc[i,"Sentiment_calc"] = sentiment
			#	finaldf.loc[i,"Sentiment_Score"] = score
			#finaldf = finaldf.dropna(how='all')
			
			finaldf = finaldf[finaldf['Full Text']!='nan']
			finaldf = finaldf[finaldf['Full Text']!=np.nan]
			st.dataframe(finaldf)
			import matplotlib.pyplot as plt
			fig, ax_pie1 = plt.subplots(figsize=(2,2))	
			#fig, (ax_pie1, ax_pie2) = plt.subplots(1,2,figsize=(3,3))				
			#finaldf.Sentiment_calc.value_counts().plot(kind="pie",autopct="%.1f%%",ax=ax_pie1,fontsize=3)
			#plt.legend(loc="best",bbox_to_anchor=(0.5, 0, 1, 1),fontsize=5)
			#centre_circle = plt.Circle((0, 0), 0.4, fc='white')
			#fig_ = plt.gcf()
			#fig_.gca().add_artist(centre_circle)
			#st.pyplot(fig)

			#fig,ax_pie = plt.subplots(figsize=(3,3))
			finaldf.Sentiment.value_counts().plot(kind="pie",autopct="%.1f%%",ax=ax_pie1,fontsize=5)
			plt.legend(loc="best",bbox_to_anchor=(0.5, 0, 1, 1),fontsize=5)
			centre_circle = plt.Circle((0, 0), 0.4, fc='white')
			fig_ = plt.gcf()
			fig_.gca().add_artist(centre_circle)
			st.pyplot(fig)	
			st.download_button(label="Download Sentiment Analysis data",data=finaldf.to_csv(index=False).encode('utf-8'),file_name="Sentiment Analysis Data.csv",mime='text/csv')
func(choice)

			

