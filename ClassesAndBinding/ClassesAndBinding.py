### DATA AUDIT WORK

import pandas as pd
import numpy as np
import pandas.io.sql as psql
import pyodbc
import sqlalchemy
import datetime
from tkinter import *
from tkinter.ttk import *


class Dataverse:
	def __init__(self):
		self.inititalizedataframe()
		self.current_index = 0
		self.current_id = 1
		self.jobexec=1
		self.jobname = "Chief Executive Officer"
		self.set_vars(input="index")
		print("DF Initialized")

	def inititalizedataframe(self):
		self.pyocnxn = pyodbc.connect("DRIVER={SQL Server};SERVER=SNADSSQ3;DATABASE=assessorwork;trusted_connection=yes;")
		self.sql = """SELECT pct.*
			, left(socdesc.soctitle, 60) as SocTitle
			, cast(LowPred as float)/MedPred as LowPredCalc
			, cast(HighPred as float)/MedPred as HighPredCalc
			, bench.USBenchMed
			, bench.CanBenchMed
			, case when (pct.medyrs>40 and pct.medyrs<99) then 1 else 0 end as execjob
			, jobdesc.ShortDesc
			
			FROM assessorwork.sa.pct pct 
			left join assessorwork.sa.bench bench on bench.erijobid=pct.erijobid and bench.releaseid=pct.releaseid
			join (select soccode, soctitle from [AssessorWork].[dbo].[SocDescription]) socdesc on pct.SOC = socdesc.SocCode
			join (select eDOT, replace(replace(ShortDesc,'/duty','duty'),'<duty>','') as ShortDesc from [AssessorWork].[sa].[Sadescriptions]) jobdesc on jobdesc.eDOT = pct.jobdot
			order by execjob desc, pct.erijobid"""
		self.jobsdf = pd.DataFrame(psql.read_sql(self.sql, self.pyocnxn))
		self.jobsdf['indexmaster'] = self.jobsdf.index
		self.jobsdf['index1'] = self.jobsdf['indexmaster']
		self.jobsdf['indexsearch'] = self.jobsdf['erijobid']
		self.last_index = self.jobsdf.last_valid_index()
		self.outputdf = pd.DataFrame(columns=self.jobsdf.columns)
		self.outputdf['timestamp']=""
		#print(self.jobsdf[['indexmaster','indexsearch']])
		#print(sorted(list(self.jobsdf.columns.values)))
		#print(self.jobsdf)
		#print(self.outputdf)
		print("Dataframe loaded from SQL")

	def find_by_erijobid(self, entry):
		idsearch = int(entry)
		try:
			try:
				self.jobsdf.set_index('indexsearch', inplace=True)
				self.jobsdf['indexsearch'] = self.jobsdf['erijobid']
			except: pass
			self.jobname = self.jobsdf.loc[idsearch,'jobdottitle']
			self.current_id = idsearch
			self.current_index = self.jobsdf.loc[self.current_id,'index1']
			self.set_vars(input="id")
			##Need to check if exists in outputdf, if so: pull from output df instead of jobsdf
		except KeyError:
			self.jobname = "No job found"

	def index_next(self ,*event):
		try:
			self.jobsdf.set_index('index1', inplace=True)
			self.jobsdf['index1'] = self.jobsdf['indexmaster']
		except: pass
		if self.current_index < self.last_index: self.current_index = self.current_index + 1
		else: self.current_index = 0
		self.current_id = self.jobsdf.loc[self.current_index,'erijobid']
		self.jobname = self.jobsdf.loc[self.current_index,'jobdottitle']
		self.set_vars(input="index")

	def index_prior(self, *event):
		try:
			self.jobsdf.set_index('index1', inplace=True)
			self.jobsdf['index1'] = self.jobsdf['indexmaster']
		except: pass
		if self.current_index > 0: self.current_index = self.current_index - 1
		else: self.current_index = self.last_index
		self.jobname = self.jobsdf.loc[self.current_index,'jobdottitle']
		self.current_id = self.jobsdf.loc[self.current_index,'erijobid']
		self.set_vars(input="index")

	def set_vars(self, input="index"):
		if(input=="index"):
			current_selector = self.current_index
		else:
			current_selector = self.current_id
		## Labels
		self.JobTitleData = self.jobsdf.loc[current_selector,'jobdottitle']
		self.ERIJobIdData = self.jobsdf.loc[current_selector,'erijobid']
		self.JobDotData = self.jobsdf.loc[current_selector,'jobdot']
		self.JobSocData = self.jobsdf.loc[current_selector,'SOC']
		self.HighPredPctData = self.jobsdf.loc[current_selector,'HighPredCalc']
		self.LowPredPctData = self.jobsdf.loc[current_selector,'LowPredCalc']
		self.B100TotalCompData = self.jobsdf.loc[current_selector,'TotalComp100Bil']
		self.HighTotalCompData = self.jobsdf.loc[current_selector,'HighTotalComp']
		self.MedTotalCompData = self.jobsdf.loc[current_selector,'MedTotalComp']
		self.LowTotalCompData = self.jobsdf.loc[current_selector,'LowTotalComp']
		self.Mil1TotalCompData = self.jobsdf.loc[current_selector,'TotalComp1Mil']
		if pd.isnull(self.jobsdf.loc[current_selector,'EstimatedYears']) : self.EstimatedYears = "NA"
		else: self.EstimatedYears = int(self.jobsdf.loc[current_selector,'EstimatedYears'])
		self.B100Q1Data = self.jobsdf.loc[current_selector,'Q1100Bil']
		self.HighQ1Data = self.jobsdf.loc[current_selector,'Q1High']
		self.MedQ1Data = self.jobsdf.loc[current_selector,'Q1Med']
		self.LowQ1Data = self.jobsdf.loc[current_selector,'Q1Low']
		self.Mil1Q1Data = self.jobsdf.loc[current_selector,'Q11Mil']
		self.QCCheckData = self.jobsdf.loc[current_selector,'MedPred']
		self.SocPredData = self.jobsdf.loc[current_selector,'OccAve']
		self.SurveyMeanData = self.jobsdf.loc[current_selector,'Y_Base']
		self.SurveyIncumbentsData = self.jobsdf.loc[current_selector,'SurveySampleSize']
		self.QCCheckCanData = self.jobsdf.loc[current_selector,'CanPred']
		self.CanPoly1Data = self.jobsdf.loc[current_selector,'CanPoly1']
		self.CanPoly2Data = self.jobsdf.loc[current_selector,'CanPoly2']
		self.CanPoly3Data = self.jobsdf.loc[current_selector,'CanPoly3']
		self.CanPolyMeanData = self.jobsdf.loc[current_selector,'AvgCanPoly']
		self.CanPolyMeanQCData = self.jobsdf.loc[current_selector,'AvgCanModels']
		self.ReptoTitleData = self.jobsdf.loc[current_selector,'ReptoTitle']
		self.ReptoSalData = self.jobsdf.loc[current_selector,'ReptoSal']
		self.ReptoYr3Data = self.jobsdf.loc[current_selector,'ReptoYr3']
		self.XRefTitleData = self.jobsdf.loc[current_selector,'XRefTitle']
		self.XRefUSData = self.jobsdf.loc[current_selector,'XRefMed']
		self.XRefCanData = self.jobsdf.loc[current_selector,'XRefCan']
		self.DegreeNameData = self.jobsdf.loc[current_selector,'DegreeName']
		self.CPCSalData = self.jobsdf.loc[current_selector,'CPCSalary']
		self.AdderData = self.jobsdf.loc[current_selector,'Adder']
		self.SocTitleData = self.jobsdf.loc[current_selector,'SocTitle']
		## Entries
		if pd.isnull(self.jobsdf.loc[current_selector,'Pct_100Bil']): self.B100PctData = 1.95
		else: self.B100PctData = self.jobsdf.loc[current_selector,'Pct_100Bil']
		self.HighPctData = self.jobsdf.loc[current_selector,'HIGH_F']
		self.MedPctData = self.jobsdf.loc[current_selector,'US_PCT']
		self.LowPctData = self.jobsdf.loc[current_selector,'LOW_F']
		if pd.isnull(self.jobsdf.loc[current_selector,'Pct_1Mil']): self.Mil1PctData = 0.1
		else: self.Mil1PctData = self.jobsdf.loc[current_selector,'Pct_1Mil']
		if pd.isnull(self.jobsdf.loc[current_selector,'BonusPct100Bil']): self.B100BonusPctData = 0
		else: self.B100BonusPctData = self.jobsdf.loc[current_selector,'BonusPct100Bil']
		self.HighBonusPctData = self.jobsdf.loc[current_selector,'HighBonusPct']
		self.MedBonusPctData = self.jobsdf.loc[current_selector,'MedBonusPct']
		self.LowBonusPctData = self.jobsdf.loc[current_selector,'LowBonusPct']
		if pd.isnull(self.jobsdf.loc[current_selector,'BonusPct1Mil']): self.Mil1BonusPctData = 0
		else: self.Mil1BonusPctData = self.jobsdf.loc[current_selector,'BonusPct1Mil']
		self.StdErrData = self.jobsdf.loc[current_selector,'StdErr']
		self.MedYrsData = self.jobsdf.loc[current_selector,'Medyrs']
		self.CanPercentData = self.jobsdf.loc[current_selector,'CAN_PCT']
		self.CanBonusPctData = self.jobsdf.loc[current_selector,'CanBonusPct']
		if pd.isnull(self.jobsdf.loc[current_selector,'Repto']): self.ReptoData = int(self.current_id)
		else: self.ReptoData = int(self.jobsdf.loc[current_selector,'Repto'])
		self.XRefData = self.jobsdf.loc[current_selector,'JobXRef']
		self.CPCData = self.jobsdf.loc[current_selector,'CPCNO']
		if pd.isnull(self.jobsdf.loc[current_selector,'USPK_C']): self.USOverrideData = 0
		else: self.USOverrideData = float(self.jobsdf.loc[current_selector,'USPK_C'])
		## Entries Init
		if pd.isnull(self.jobsdf.loc[current_selector,'Pct_100Bil']): self.B100PctDataInit = 1.95
		else: self.B100PctDataInit = self.jobsdf.loc[current_selector,'Pct_100Bil']
		self.HighPctDataInit = self.jobsdf.loc[current_selector,'HIGH_F']
		self.MedPctDataInit = self.jobsdf.loc[current_selector,'US_PCT']
		self.LowPctDataInit = self.jobsdf.loc[current_selector,'LOW_F']
		if pd.isnull(self.jobsdf.loc[current_selector,'Pct_1Mil']): self.Mil1PctDataInit = 0.1
		else: self.Mil1PctDataInit = self.jobsdf.loc[current_selector,'Pct_1Mil']
		if pd.isnull(self.jobsdf.loc[current_selector,'BonusPct100Bil']): self.B100BonusPctDataInit = 0
		else: self.B100BonusPctDataInit = self.jobsdf.loc[current_selector,'BonusPct100Bil']
		self.HighBonusPctDataInit = self.jobsdf.loc[current_selector,'HighBonusPct']
		self.MedBonusPctDataInit = self.jobsdf.loc[current_selector,'MedBonusPct']
		self.LowBonusPctDataInit = self.jobsdf.loc[current_selector,'LowBonusPct']
		if pd.isnull(self.jobsdf.loc[current_selector,'BonusPct1Mil']): self.Mil1BonusPctDataInit = 0
		else: self.Mil1BonusPctDataInit = self.jobsdf.loc[current_selector,'BonusPct1Mil']
		self.StdErrDataInit = self.jobsdf.loc[current_selector,'StdErr']
		self.MedYrsDataInit = self.jobsdf.loc[current_selector,'Medyrs']
		self.CanPercentDataInit = self.jobsdf.loc[current_selector,'CAN_PCT']
		self.CanBonusPctDataInit = self.jobsdf.loc[current_selector,'CanBonusPct']
		if pd.isnull(self.jobsdf.loc[current_selector,'Repto']): self.ReptoDataInit = int(self.current_id)
		else: self.ReptoDataInit = int(self.jobsdf.loc[current_selector,'Repto'])
		self.XRefDataInit = self.jobsdf.loc[current_selector,'JobXRef']
		self.CPCDataInit = self.jobsdf.loc[current_selector,'CPCNO']
		if pd.isnull(self.jobsdf.loc[current_selector,'USPK_C']): self.USOverrideDataInit = 0
		else: self.USOverrideDataInit = float(self.jobsdf.loc[current_selector,'USPK_C'])
		
		## Other
		self.jobexec = self.jobsdf.loc[current_selector,'execjob']
		self.JobDescriptionData = self.jobsdf.loc[current_selector,'ShortDesc']
		## Check Output before calculating
		self.check_output()
		## Calculations
		self.CanAveData = self.CanPercentData * self.XRefCanData
		if pd.isnull(self.SurveyMeanData) and pd.isnull(self.QCCheckData): self.MeanPredData = self.SocPredData
		elif pd.isnull(self.SurveyMeanData): self.MeanPredData = float((self.QCCheckData+self.SocPredData)/2)
		elif pd.isnull(self.QCCheckData): self.MeanPredData = float((self.SocPredData+self.SurveyMeanData)/2)
		else: self.MeanPredData = (self.QCCheckData+self.SocPredData+self.SurveyMeanData)/3
		self.MedSalData = self.MedPctData*self.XRefUSData
		self.set_CalcData()

	def update_canavedata(self, entry):
		self.CanAveData = entry*(self.CPCSalData+self.AdderData)

	def update_MedSalCalcData(self, entry, *event):
		self.MedSalData = int(entry*(self.CPCSalData+self.AdderData))
		self.set_CalcData()

	def set_CalcData(self, *event):
		self.Sal100BilData = self.MedSalData * self.B100PctData
		self.HighSalData = self.MedSalData * self.HighPctData
		self.LowSalData = self.MedSalData * self.LowPctData
		self.Sal1MilData = self.MedSalData * self.Mil1PctData
		self.High90thPercentile_100BilData = ((self.StdErrData/100*1.6)+1) * self.Sal100BilData
		self.High90thPercentileData = ((self.StdErrData/100*1.6)+1) * self.HighSalData
		self.Med90thPercentileData = ((self.StdErrData/100*1.6)+1) * self.MedSalData
		self.Low90thPercentileData = ((self.StdErrData/100*1.6)+1) * self.LowSalData
		self.Low90thPercentile_1MilData = ((self.StdErrData/100*1.6)+1) * self.Sal1MilData
		self.High10thPercentile_100BilData = ((1 - self.StdErrData/100) * self.Sal100BilData)
		self.High10thPercentileData = ((1 - self.StdErrData/100) * self.HighSalData)
		self.Med10thPercentileData = ((1 - self.StdErrData/100) * self.MedSalData)
		self.Low10thPercentileData = ((1 - self.StdErrData/100) * self.LowSalData)
		self.Low10thPercentile_1MilData = ((1 - self.StdErrData/100) * self.Sal1MilData)

	def check_output(self, *event):
		try:
			self.jobsdf.set_index('indexsearch', inplace=True)
			self.jobsdf['indexsearch'] = self.jobsdf['erijobid']
		except: pass
		## Check for current erijobid in output df, add or update as necessary
		if (self.outputdf['erijobid']==self.current_id).any():
			current_selector = self.current_id
			self.JobTitleData = self.outputdf.loc[current_selector,'jobdottitle']
			self.ERIJobIdData = self.outputdf.loc[current_selector,'erijobid']
			self.JobDotData = self.outputdf.loc[current_selector,'jobdot']
			self.JobSocData = self.outputdf.loc[current_selector,'SOC']
			self.HighPredPctData = self.outputdf.loc[current_selector,'HighPredCalc']
			self.LowPredPctData = self.outputdf.loc[current_selector,'LowPredCalc']
			self.B100TotalCompData = self.outputdf.loc[current_selector,'TotalComp100Bil']
			self.HighTotalCompData = self.outputdf.loc[current_selector,'HighTotalComp']
			self.MedTotalCompData = self.outputdf.loc[current_selector,'MedTotalComp']
			self.LowTotalCompData = self.outputdf.loc[current_selector,'LowTotalComp']
			self.Mil1TotalCompData = self.outputdf.loc[current_selector,'TotalComp1Mil']
			if pd.isnull(self.outputdf.loc[current_selector,'EstimatedYears']) : self.EstimatedYears = "NA"
			else: self.EstimatedYears = int(self.outputdf.loc[current_selector,'EstimatedYears'])
			self.B100Q1Data = self.outputdf.loc[current_selector,'Q1100Bil']
			self.HighQ1Data = self.outputdf.loc[current_selector,'Q1High']
			self.MedQ1Data = self.outputdf.loc[current_selector,'Q1Med']
			self.LowQ1Data = self.outputdf.loc[current_selector,'Q1Low']
			self.Mil1Q1Data = self.outputdf.loc[current_selector,'Q11Mil']
			self.QCCheckData = self.outputdf.loc[current_selector,'MedPred']
			self.SocPredData = self.outputdf.loc[current_selector,'OccAve']
			self.SurveyMeanData = self.outputdf.loc[current_selector,'Y_Base']
			self.SurveyIncumbentsData = self.outputdf.loc[current_selector,'SurveySampleSize']
			self.QCCheckCanData = self.outputdf.loc[current_selector,'CanPred']
			self.CanPoly1Data = self.outputdf.loc[current_selector,'CanPoly1']
			self.CanPoly2Data = self.outputdf.loc[current_selector,'CanPoly2']
			self.CanPoly3Data = self.outputdf.loc[current_selector,'CanPoly3']
			self.CanPolyMeanData = self.outputdf.loc[current_selector,'AvgCanPoly']
			self.CanPolyMeanQCData = self.outputdf.loc[current_selector,'AvgCanModels']
			self.ReptoTitleData = self.outputdf.loc[current_selector,'ReptoTitle']
			self.ReptoSalData = self.outputdf.loc[current_selector,'ReptoSal']
			self.ReptoYr3Data = self.outputdf.loc[current_selector,'ReptoYr3']
			self.XRefTitleData = self.outputdf.loc[current_selector,'XRefTitle']
			self.XRefUSData = self.outputdf.loc[current_selector,'XRefMed']
			self.XRefCanData = self.outputdf.loc[current_selector,'XRefCan']
			self.DegreeNameData = self.outputdf.loc[current_selector,'DegreeName']
			self.CPCSalData = self.outputdf.loc[current_selector,'CPCSalary']
			self.AdderData = self.outputdf.loc[current_selector,'Adder']
			## Entries
			if pd.isnull(self.outputdf.loc[current_selector,'Pct_100Bil']): self.B100PctData = 1.95
			else: self.B100PctData = self.outputdf.loc[current_selector,'Pct_100Bil']
			self.HighPctData = self.outputdf.loc[current_selector,'HIGH_F']
			self.MedPctData = self.outputdf.loc[current_selector,'US_PCT']
			self.LowPctData = self.outputdf.loc[current_selector,'LOW_F']
			if pd.isnull(self.outputdf.loc[current_selector,'Pct_1Mil']): self.Mil1PctData = 0.1
			else: self.Mil1PctData = self.outputdf.loc[current_selector,'Pct_1Mil']
			self.B100BonusPctData = self.outputdf.loc[current_selector,'BonusPct100Bil']
			self.HighBonusPctData = self.outputdf.loc[current_selector,'HighBonusPct']
			self.MedBonusPctData = self.outputdf.loc[current_selector,'MedBonusPct']
			self.LowBonusPctData = self.outputdf.loc[current_selector,'LowBonusPct']
			self.Mil1BonusPctData = self.outputdf.loc[current_selector,'BonusPct1Mil']
			self.StdErrData = self.outputdf.loc[current_selector,'StdErr']
			self.MedYrsData = self.outputdf.loc[current_selector,'Medyrs']
			self.CanPercentData = self.outputdf.loc[current_selector,'CAN_PCT']
			self.CanBonusPctData = self.outputdf.loc[current_selector,'CanBonusPct']
			if pd.isnull(self.outputdf.loc[current_selector,'Repto']): self.ReptoData = int(self.current_id)
			else: self.ReptoData = int(self.outputdf.loc[current_selector,'Repto'])
			self.XRefData = self.outputdf.loc[current_selector,'JobXRef']
			self.CPCData = self.outputdf.loc[current_selector,'CPCNO']
			## Entries Init
			#if pd.isnull(self.outputdf.loc[current_selector,'Pct_100Bil']): self.B100PctDataInit = 1.95
			#else: self.B100PctDataInit = self.outputdf.loc[current_selector,'Pct_100Bil']
			#self.HighPctDataInit = self.outputdf.loc[current_selector,'HIGH_F']
			#self.MedPctDataInit = self.outputdf.loc[current_selector,'US_PCT']
			#self.LowPctDataInit = self.outputdf.loc[current_selector,'LOW_F']
			#if pd.isnull(self.outputdf.loc[current_selector,'Pct_1Mil']): self.Mil1PctDataInit = 0.1
			#else: self.Mil1PctDataInit = self.outputdf.loc[current_selector,'Pct_1Mil']
			#self.B100BonusPctDataInit = self.outputdf.loc[current_selector,'BonusPct100Bil']
			#self.HighBonusPctDataInit = self.outputdf.loc[current_selector,'HighBonusPct']
			#self.MedBonusPctDataInit = self.outputdf.loc[current_selector,'MedBonusPct']
			#self.LowBonusPctDataInit = self.outputdf.loc[current_selector,'LowBonusPct']
			#self.Mil1BonusPctDataInit = self.outputdf.loc[current_selector,'BonusPct1Mil']
			#self.StdErrDataInit = self.outputdf.loc[current_selector,'StdErr']
			#self.MedYrsDataInit = self.outputdf.loc[current_selector,'Medyrs']
			#self.CanPercentDataInit = self.outputdf.loc[current_selector,'CAN_PCT']
			#self.CanBonusPctDataInit = self.outputdf.loc[current_selector,'CanBonusPct']
			#if pd.isnull(self.outputdf.loc[current_selector,'Repto']): self.ReptoDataInit = int(self.current_id)
			#else: self.ReptoDataInit = int(self.outputdf.loc[current_selector,'Repto'])
			#self.XRefDataInit = self.outputdf.loc[current_selector,'JobXRef']
			#self.CPCDataInit = self.outputdf.loc[current_selector,'CPCNO']
			self.jobexec = self.outputdf.loc[current_selector,'execjob']

	def write_to_outputdf(self, *event):
		try:
			self.jobsdf.set_index('indexsearch', inplace=True)
			self.jobsdf['indexsearch'] = self.jobsdf['erijobid']
		except: pass
		## Check for current erijobid in output df, add or update as necessary
		if (self.outputdf['erijobid']==self.current_id).any():
			#print("Overwriting "+str(self.current_id))
			self.outputdf.update(self.jobsdf.loc[self.current_id,:])
		else: self.outputdf = self.outputdf.append(self.jobsdf.loc[self.current_id,:])
		## Update output rows after creating
		self.outputdf.update(self.jobsdf.loc[self.current_id,:])
		self.outputdf.set_value(self.current_id,'timestamp',datetime.datetime.now())
		self.outputdf.set_value(self.current_id,'Pct_100Bil', self.B100PctData)
		self.outputdf.set_value(self.current_id,'HIGH_F', self.HighPctData)
		self.outputdf.set_value(self.current_id,'US_PCT', self.MedPctData)
		self.outputdf.set_value(self.current_id,'LOW_F', self.LowPctData)
		self.outputdf.set_value(self.current_id,'Pct_1Mil', self.Mil1PctData)
		self.outputdf.set_value(self.current_id,'BonusPct100Bil', self.B100BonusPctData)
		self.outputdf.set_value(self.current_id,'HighBonusPct', self.HighBonusPctData)
		self.outputdf.set_value(self.current_id,'MedBonusPct', self.MedBonusPctData)
		self.outputdf.set_value(self.current_id,'LowBonusPct', self.LowBonusPctData)
		self.outputdf.set_value(self.current_id,'BonusPct1Mil', self.Mil1BonusPctData)
		#print(self.outputdf.loc[self.current_id,['erijobid', 'jobdottitle', 'Pct_100Bil', 'HIGH_F', 'US_PCT', 'LOW_F', 'Pct_1Mil', 'timestamp']])
		print("Data written to OutputDF")

	def write_to_sql(self, *event):
		# Copy output DataFrame to SQL DataFrame before printing
		self.sqldf = self.outputdf.copy()
		# Drop specific columns from SQL DataFrame before writing to SQL database
		self.sqldf = self.sqldf.drop(['execjob','indexmaster','index1','indexsearch'],axis=1)
		engine = sqlalchemy.create_engine('mssql+pyodbc://SNADSSQ3/AssessorWork?driver=SQL+Server+Native+Client+11.0')
		self.sqldf.to_sql('AuditTest_',engine,schema='dbo',if_exists='append',index=False)
		print("Dataframe written to SQL")


class Application(Frame):
	def __init__(self, master):
		"""Initialize the Frame"""
		Frame.__init__(self, master)
		self.master = master
		self.data = Dataverse()
		self.master.title("Data Audit Window")
		self.pack(fill=BOTH, expand=0)
		self.create_widgets()
		self.label_entry_initload()
		self.bind_all('<Next>', self.nextpage)
		self.bind_all('<Prior>', self.priorpage)
		self.bind_all('<Insert>', self.write_output)
		self.bind_all('<Control-p>', self.write_sql)

	def create_widgets(self):
		# Widget templates :
		# Entry box (user types in entry box) [editable]: self.[EntryName] = Entry(self, width=[15])
		# Button (activates functions when pressed): self.[BtnName] = Button(self, text="[BtnText]", command=[python function])
		# # # Binding button to entry key when highlighted: self.[BtnName].bind('<Return>',[same python function referenced in command= in button definition])
		# Universal Label (does not update, static) [noedit]: self.[LabelName] = Label(self, text="[Label Text]")
		# Update Label (updates with user entry) [noedit]: self.[LabelName] = Label(self, text="[initial text]", relief="groove")
		# # # Overwriting an update label:
		# # #		self.[LabelVarName].delete(0, END)
		# # #		self.[LabelVarName].insert(0, [value to pull])
		# /End widget formats
		
###########################
#### Created from Google Sheet 
		self.ReloadBtn = Button(self, text="Reload Data", command=self.label_entry_reload)
		self.ReloadBtn.grid(row=0, column=5)
		self.CommitBtn = Button(self, text="Commit Changes", command=self.write_output)
		self.CommitBtn.grid(row=0, column=6)
		self.WriteSQLBtn = Button(self, text="Write to SQL")
		self.WriteSQLBtn.grid(row=0, column=7)
		self.JobIdSearchEntry = Entry(self, width=15)
		self.JobIdSearchEntry.grid(row=0, column=2)
		self.B100PctEntry = Entry(self, width=15)
		self.B100PctEntry.grid(row=10, column=3)
		self.HighPctEntry = Entry(self, width=15)
		self.HighPctEntry.grid(row=11, column=3)
		self.MedPctEntry = Entry(self, width=15)
		self.MedPctEntry.grid(row=12, column=3)
		self.LowPctEntry = Entry(self, width=15)
		self.LowPctEntry.grid(row=13, column=3)
		self.Mil1PctEntry = Entry(self, width=15)
		self.Mil1PctEntry.grid(row=14, column=3)
		self.B100BonusPctEntry = Entry(self, width=15)
		self.B100BonusPctEntry.grid(row=15, column=3)
		self.HighBonusPctEntry = Entry(self, width=15)
		self.HighBonusPctEntry.grid(row=16, column=3)
		self.MedBonusPctEntry = Entry(self, width=15)
		self.MedBonusPctEntry.grid(row=17, column=3)
		self.LowBonusPctEntry = Entry(self, width=15)
		self.LowBonusPctEntry.grid(row=18, column=3)
		self.Mil1BonusPctEntry = Entry(self, width=15)
		self.Mil1BonusPctEntry.grid(row=19, column=3)
		self.StdErrEntry = Entry(self, width=15)
		self.StdErrEntry.grid(row=20, column=3)
		self.MedYrsEntry = Entry(self, width=15)
		self.MedYrsEntry.grid(row=21, column=3)
		self.USOverrideEntry = Entry(self, width=15)
		self.USOverrideEntry.grid(row=23, column=2)
		self.CanOverrideEntry = Entry(self, width=15)
		self.CanOverrideEntry.grid(row=24, column=2)
		self.CanPercentEntry = Entry(self, width=15)
		self.CanPercentEntry.grid(row=25, column=4)
		self.CanBonusPctEntry = Entry(self, width=15)
		self.CanBonusPctEntry.grid(row=26, column=4)
		self.ReptoEntry = Entry(self, width=15)
		self.ReptoEntry.grid(row=29, column=2)
		self.XRefEntry = Entry(self, width=15)
		self.XRefEntry.grid(row=30, column=2)
		self.CPCEntry = Entry(self, width=15)
		self.CPCEntry.grid(row=31, column=2)
		self.ERISearch = Label(self,text="ERI # Search")
		self.ERISearch.grid(row=0, column=1)
		self.TitleEri = Label(self,text="Title")
		self.TitleEri.grid(row=2, column=1, sticky=W)
		self.eDOT = Label(self,text="eDOT")
		self.eDOT.grid(row=2, column=3)
		self.SOC = Label(self,text="SOC")
		self.SOC.grid(row=2, column=5)
		self.Pct10 = Label(self,text="10th Percentile")
		self.Pct10.grid(row=3, column=2)
		self.Mean = Label(self,text="Mean")
		self.Mean.grid(row=3, column=3)
		self.Pct90 = Label(self,text="90th Percentile")
		self.Pct90.grid(row=3, column=4)
		self.LastQ = Label(self,text="Last Quarter")
		self.LastQ.grid(row=3, column=6)
		self.RawData = Label(self,text="Raw Data")
		self.RawData.grid(row=4, column=0)
		self.B100 = Label(self,text="Exec/100 Bil")
		self.B100.grid(row=4, column=1, sticky=E)
		self.B100Q1 = Label(self,text="Q1 100 bil/Exec")
		self.B100Q1.grid(row=4, column=7)
		self.High = Label(self,text="High Year/1 Bil")
		self.High.grid(row=5, column=1, sticky=E)
		self.HighQ1 = Label(self,text="Q1 Highsal")
		self.HighQ1.grid(row=5, column=7)
		self.Med = Label(self,text="Med Year/100 Mil")
		self.Med.grid(row=6, column=1, sticky=E)
		self.MedQ1 = Label(self,text="Q1 Medsal")
		self.MedQ1.grid(row=6, column=7)
		self.Low = Label(self,text="Low Year/10 Mil")
		self.Low.grid(row=7, column=1, sticky=E)
		self.LowQ1 = Label(self,text="Q1 Lowsal")
		self.LowQ1.grid(row=7, column=7)
		self.Mil1 = Label(self,text="Exec/1 Mil")
		self.Mil1.grid(row=8, column=1, sticky=E)
		self.Mil1Q1 = Label(self,text="Q1 1 Mil/Exec")
		self.Mil1Q1.grid(row=8, column=7)
		self.B100Pct = Label(self,text="Exec/100 Bil Percent")
		self.B100Pct.grid(row=10, column=4)
		self.PredUS = Label(self,text="Predicted US Values")
		self.PredUS.grid(row=10, column=6)
		self.HighPredPct = Label(self,text="High Pred %")
		self.HighPredPct.grid(row=11, column=1, sticky=E)
		self.HighPct = Label(self,text="High Percent")
		self.HighPct.grid(row=11, column=4)
		self.QCCheck = Label(self,text="QC Check")
		self.QCCheck.grid(row=11, column=7)
		self.MedPct = Label(self,text="Med Percent")
		self.MedPct.grid(row=12, column=4)
		self.SOCPred = Label(self,text="SOC Pred")
		self.SOCPred.grid(row=12, column=7)
		self.LowPredPct = Label(self,text="Low Pred %")
		self.LowPredPct.grid(row=13, column=1, sticky=E)
		self.LowPct = Label(self,text="Low Percent")
		self.LowPct.grid(row=13, column=4)
		self.SurveyMean = Label(self,text="Survey Mean")
		self.SurveyMean.grid(row=13, column=7)
		self.Mil1Pct = Label(self,text="Exec/1 Mil Percent")
		self.Mil1Pct.grid(row=14, column=4)
		self.SurveyIncumbents = Label(self,text="Survey Incumbents")
		self.SurveyIncumbents.grid(row=14, column=7)
		self.B100Total = Label(self,text="Exec/100 Bil Total")
		self.B100Total.grid(row=15, column=1, sticky=E)
		self.B100Bonus = Label(self,text="Exec/100 Bil Bonus")
		self.B100Bonus.grid(row=15, column=4)
		self.MeanPred = Label(self,text="Mean Predicted")
		self.MeanPred.grid(row=15, column=7)
		self.HighTotal = Label(self,text="High Total Comp")
		self.HighTotal.grid(row=16, column=1, sticky=E)
		self.HighBonus = Label(self,text="High Bonus")
		self.HighBonus.grid(row=16, column=4)
		self.MedTotal = Label(self,text="Med Total Comp")
		self.MedTotal.grid(row=17, column=1, sticky=E)
		self.MedBonus = Label(self,text="Med Bonus")
		self.MedBonus.grid(row=17, column=4)
		self.LowTotal = Label(self,text="Low Total Comp")
		self.LowTotal.grid(row=18, column=1, sticky=E)
		self.LowBonus = Label(self,text="Low Bonus")
		self.LowBonus.grid(row=18, column=4)
		self.Mil1Total = Label(self,text="Exec/1 Mil Total")
		self.Mil1Total.grid(row=19, column=1, sticky=E)
		self.Mil1Bonus = Label(self,text="Exec/1 Mil Bonus")
		self.Mil1Bonus.grid(row=19, column=4)
		self.StdErrPred = Label(self,text="Std Error Pred")
		self.StdErrPred.grid(row=20, column=1, sticky=E)
		self.StdErr = Label(self,text="Standard Error")
		self.StdErr.grid(row=20, column=4)
		self.MedyrsPred = Label(self,text="Medyrs Pred")
		self.MedyrsPred.grid(row=21, column=1, sticky=E)
		self.Medyears = Label(self,text="Medyears")
		self.Medyears.grid(row=21, column=4)
		self.CanPred = Label(self,text="Predicted Canada Values")
		self.CanPred.grid(row=21, column=6)
		self.QCCheckCan = Label(self,text="QC Check Can")
		self.QCCheckCan.grid(row=22, column=7)
		self.USOverride = Label(self,text="US Override")
		self.USOverride.grid(row=23, column=1, sticky=E)
		self.CanMean = Label(self,text="Can Mean")
		self.CanMean.grid(row=23, column=3, sticky=E)
		self.CanPoly1 = Label(self,text="Can Poly 1")
		self.CanPoly1.grid(row=23, column=7)
		self.CanOverride = Label(self,text="Can Override")
		self.CanOverride.grid(row=24, column=1, sticky=E)
		self.CanQ1 = Label(self,text="Can Q1")
		self.CanQ1.grid(row=24, column=3, sticky=E)
		self.CanPoly2 = Label(self,text="Can Poly 2")
		self.CanPoly2.grid(row=24, column=7)
		self.CanPct = Label(self,text="Can Percent")
		self.CanPct.grid(row=25, column=3, sticky=E)
		self.CanPoly3 = Label(self,text="Can Poly 3")
		self.CanPoly3.grid(row=25, column=7)
		self.CanBonusPct = Label(self,text="Can Bonus %")
		self.CanBonusPct.grid(row=26, column=3, sticky=E)
		self.CanPolyMean = Label(self,text="Can Poly Mean")
		self.CanPolyMean.grid(row=26, column=7)
		self.CanTotal = Label(self,text="Can Total")
		self.CanTotal.grid(row=27, column=3, sticky=E)
		self.CanQCPoly = Label(self,text="Can QC/Poly Mean")
		self.CanQCPoly.grid(row=27, column=7)
		self.Repto = Label(self,text="Title    Repto   ERI")
		self.Repto.grid(row=29, column=1)
		self.ReptoSal = Label(self,text="Repto Salary")
		self.ReptoSal.grid(row=29, column=3, sticky=E)
		self.ReptoYr3 = Label(self,text="Repto Yr 3")
		self.ReptoYr3.grid(row=29, column=7)
		self.XRef = Label(self,text="Title    XRef    ERI")
		self.XRef.grid(row=30, column=1)
		self.XRefUSSal = Label(self,text="XRef US Salary")
		self.XRefUSSal.grid(row=30, column=3, sticky=E)
		self.XRefCanSal = Label(self,text="XRef Can Salary")
		self.XRefCanSal.grid(row=30, column=7)
		self.CPC = Label(self,text="Deg    CPC     CPC")
		self.CPC.grid(row=31, column=1)
		self.CPCSal = Label(self,text="CPC Salary")
		self.CPCSal.grid(row=31, column=3, sticky=E)
		self.Adder = Label(self,text="Adder")
		self.Adder.grid(row=31, column=7)
		self.Description = Label(self,text="Job Description")
		self.Description.grid(row=32, column=0)
		self.JobTitleLabel = Label(self, text="[Initial Text]", relief="groove", width=45, anchor=E)
		self.JobTitleLabel.grid(row=2, column=0)
		self.ExecJobLabel = Label(self, text="Row2Col2", relief="groove")
		self.ExecJobLabel.grid(row=2, column=2)
		self.JobDotLabel = Label(self, text="[Initial Text]", relief="groove")
		self.JobDotLabel.grid(row=2, column=4)
		self.JobSocLabel = Label(self, text="[Initial Text]", relief="groove")
		self.JobSocLabel.grid(row=2, column=6)
		self.SocOutputLabel = Label(self, text="[Initial Text]", relief="groove", wraplength=200)
		self.SocOutputLabel.grid(row=2, column=7)
		self.High10thPercentile_100BilLabel = Label(self, text="Initial Text", relief="groove")
		self.High10thPercentile_100BilLabel.grid(row=4, column=2)
		self.Sal100BilLabel = Label(self, text="Initial Text", relief="groove")
		self.Sal100BilLabel.grid(row=4, column=3)
		self.High90thPercentile_100BilLabel = Label(self, text="Initial Text", relief="groove")
		self.High90thPercentile_100BilLabel.grid(row=4, column=4)
		self.B100Q1Label = Label(self, text="[Initial Text]", relief="groove")
		self.B100Q1Label.grid(row=4, column=6)
		self.RawDataLabel = Label(self, text="""[Initial 



					Text]""", relief="groove", width=45)
		self.RawDataLabel.grid(row=5, column=0)
		self.High10thPercentileLabel = Label(self, text="Initial Text", relief="groove")
		self.High10thPercentileLabel.grid(row=5, column=2)
		self.HighSalLabel = Label(self, text="Initial Text", relief="groove")
		self.HighSalLabel.grid(row=5, column=3)
		self.High90thPercentileLabel = Label(self, text="Initial Text", relief="groove")
		self.High90thPercentileLabel.grid(row=5, column=4)
		self.HighQ1Label = Label(self, text="[Initial Text]", relief="groove")
		self.HighQ1Label.grid(row=5, column=6)
		self.Med10thPercentileLabel = Label(self, text="Initial Text", relief="groove")
		self.Med10thPercentileLabel.grid(row=6, column=2)
		self.MedSalLabel = Label(self, text="Initial Text", relief="groove")
		self.MedSalLabel.grid(row=6, column=3)
		self.Med90thPercentileLabel = Label(self, text="Initial Text", relief="groove")
		self.Med90thPercentileLabel.grid(row=6, column=4)
		self.MedQ1Label = Label(self, text="[Initial Text]", relief="groove")
		self.MedQ1Label.grid(row=6, column=6)
		self.Low10thPercentileLabel = Label(self, text="Initial Text", relief="groove")
		self.Low10thPercentileLabel.grid(row=7, column=2)
		self.LowSalLabel = Label(self, text="Initial Text", relief="groove")
		self.LowSalLabel.grid(row=7, column=3)
		self.Low90thPercentileLabel = Label(self, text="Initial Text", relief="groove")
		self.Low90thPercentileLabel.grid(row=7, column=4)
		self.LowQ1Label = Label(self, text="[Initial Text]", relief="groove")
		self.LowQ1Label.grid(row=7, column=6)
		self.Low10thPercentile_1MilLabel = Label(self, text="Initial Text", relief="groove")
		self.Low10thPercentile_1MilLabel.grid(row=8, column=2)
		self.Sal1MilLabel = Label(self, text="Initial Text", relief="groove")
		self.Sal1MilLabel.grid(row=8, column=3)
		self.Low90thPercentile_1MilLabel = Label(self, text="Initial Text", relief="groove")
		self.Low90thPercentile_1MilLabel.grid(row=8, column=4)
		self.Mil1Q1Label = Label(self, text="[Initial Text]", relief="groove")
		self.Mil1Q1Label.grid(row=8, column=6)
		self.HighPredPctLabel = Label(self, text="[Initial Text]", relief="groove")
		self.HighPredPctLabel.grid(row=11, column=2)
		self.QCCheckLabel = Label(self, text="[Initial Text]", relief="groove")
		self.QCCheckLabel.grid(row=11, column=6)
		self.SocPredLabel = Label(self, text="[Initial Text]", relief="groove")
		self.SocPredLabel.grid(row=12, column=6)
		self.LowPredPctLabel = Label(self, text="[Initial Text]", relief="groove")
		self.LowPredPctLabel.grid(row=13, column=2)
		self.SurveyMeanLabel = Label(self, text="[Initial Text]", relief="groove")
		self.SurveyMeanLabel.grid(row=13, column=6)
		self.SurveyIncumbentsLabel = Label(self, text="[Initial Text]", relief="groove")
		self.SurveyIncumbentsLabel.grid(row=14, column=6)
		self.B100TotalCompLabel = Label(self, text="[Initial Text]", relief="groove")
		self.B100TotalCompLabel.grid(row=15, column=2)
		self.MeanPredLabel = Label(self, text="[Initial Text]", relief="groove")
		self.MeanPredLabel.grid(row=15, column=6)
		self.HighTotalCompLabel = Label(self, text="[Initial Text]", relief="groove")
		self.HighTotalCompLabel.grid(row=16, column=2)
		self.MedTotalCompLabel = Label(self, text="[Initial Text]", relief="groove")
		self.MedTotalCompLabel.grid(row=17, column=2)
		self.LowTotalCompLabel = Label(self, text="[Initial Text]", relief="groove")
		self.LowTotalCompLabel.grid(row=18, column=2)
		self.Mil1TotalCompLabel = Label(self, text="[Initial Text]", relief="groove")
		self.Mil1TotalCompLabel.grid(row=19, column=2)
		self.StdErrPredLabel = Label(self, text="[Initial Text]", relief="groove")
		self.StdErrPredLabel.grid(row=20, column=2)
		self.EstimatedYearsLabel = Label(self, text="[Initial Text]", relief="groove")
		self.EstimatedYearsLabel.grid(row=21, column=2)
		self.QCCheckCanLabel = Label(self, text="[Initial Text]", relief="groove")
		self.QCCheckCanLabel.grid(row=22, column=6)
		self.CanMeanLabel = Label(self, text="[Initial Text]", relief="groove")
		self.CanMeanLabel.grid(row=23, column=4)
		self.CanPoly1Label = Label(self, text="[Initial Text]", relief="groove")
		self.CanPoly1Label.grid(row=23, column=6)
		self.CanQ1Label = Label(self, text="[Initial Text]", relief="groove")
		self.CanQ1Label.grid(row=24, column=4)
		self.CanPoly2Label = Label(self, text="[Initial Text]", relief="groove")
		self.CanPoly2Label.grid(row=24, column=6)
		self.CanPoly3Label = Label(self, text="[Initial Text]", relief="groove")
		self.CanPoly3Label.grid(row=25, column=6)
		self.CanPolyMeanLabel = Label(self, text="[Initial Text]", relief="groove")
		self.CanPolyMeanLabel.grid(row=26, column=6)
		self.CanTotalLabel = Label(self, text="[Initial Text]", relief="groove")
		self.CanTotalLabel.grid(row=27, column=4)
		self.CanPolyMeanQCLabel = Label(self, text="[Initial Text]", relief="groove")
		self.CanPolyMeanQCLabel.grid(row=27, column=6)
		self.ReptoTitleLabel = Label(self, text="[Initial Text]", relief="groove")
		self.ReptoTitleLabel.grid(row=29, column=0)
		self.ReptoSalLabel = Label(self, text="[Initial Text]", relief="groove")
		self.ReptoSalLabel.grid(row=29, column=4)
		self.ReptoYr3Label = Label(self, text="[Initial Text]", relief="groove")
		self.ReptoYr3Label.grid(row=29, column=6)
		self.XRefTitleLabel = Label(self, text="[Initial Text]", relief="groove")
		self.XRefTitleLabel.grid(row=30, column=0)
		self.XRefUSLabel = Label(self, text="[Initial Text]", relief="groove")
		self.XRefUSLabel.grid(row=30, column=4)
		self.XRefCanLabel = Label(self, text="[Initial Text]", relief="groove")
		self.XRefCanLabel.grid(row=30, column=6)
		self.DegreeNameLabel = Label(self, text="[Initial Text]", relief="groove")
		self.DegreeNameLabel.grid(row=31, column=0)
		self.CPCSalLabel = Label(self, text="[Initial Text]", relief="groove")
		self.CPCSalLabel.grid(row=31, column=4)
		self.AdderLabel = Label(self, text="[Initial Text]", relief="groove")
		self.AdderLabel.grid(row=31, column=6)
		self.JobDescriptionLabel = Label(self, text="[Initial Text]", relief="groove", wraplength=950, width=160)
		self.JobDescriptionLabel.grid(row=33, column=0)
		####
		## Special notes:
			#self.JobTitleLabel ... width=45
			#self.RawDataLabel ... width=45
		self.JobTitleLabel.grid_configure(sticky=E)
		self.JobIdSearchEntry.bind('<Return>',self.jobidsearch)
		self.JobIdSearchEntry.insert(0, "1")
		self.JobDescriptionLabel.grid_configure(columnspan=8, sticky=NW)
		self.RawDataLabel.grid_configure(rowspan=21, sticky=N)
		self.SocOutputLabel.grid_configure(rowspan=2, sticky=NW)
		self.WriteSQLBtn.grid_configure(sticky=W)
		self.B100Q1.grid_configure(sticky=W)
		self.HighQ1.grid_configure(sticky=W)
		self.MedQ1.grid_configure(sticky=W)
		self.LowQ1.grid_configure(sticky=W)
		self.Mil1Q1.grid_configure(sticky=W)
		self.QCCheck.grid_configure(sticky=W)
		self.SOCPred.grid_configure(sticky=W)
		self.SurveyMean.grid_configure(sticky=W)
		self.SurveyIncumbents.grid_configure(sticky=W)
		self.MeanPred.grid_configure(sticky=W)
		self.QCCheckCan.grid_configure(sticky=W)
		self.CanPoly1.grid_configure(sticky=W)
		self.CanPoly2.grid_configure(sticky=W)
		self.CanPoly3.grid_configure(sticky=W)
		self.CanPolyMean.grid_configure(sticky=W)
		self.CanQCPoly.grid_configure(sticky=W)
		self.ReptoYr3.grid_configure(sticky=W)
		self.XRefCanSal.grid_configure(sticky=W)
		self.Adder.grid_configure(sticky=W)
		self.ReptoTitleLabel.grid_configure(sticky=E)
		self.XRefTitleLabel.grid_configure(sticky=E)
		self.DegreeNameLabel.grid_configure(sticky=E)
		## Additional Labels
		## Real-time updates
		self.USOverrideEntry.bind('<Return>', self.update_MedSal)
		self.CanOverrideEntry.bind('<Return>', self.update_CanLabels)
		self.CanBonusPctEntry.bind('<Return>', self.update_CanValues)
		self.CanPercentEntry.bind('<Return>', self.update_CanValues)
		self.B100PctEntry.bind('<Return>', self.set_SalPercents)
		self.Mil1PctEntry.bind('<Return>', self.set_SalPercents)
		self.HighPctEntry.bind('<Return>', self.set_SalPercents)
		self.MedPctEntry.bind('<Return>', self.set_SalPercents)
		self.LowPctEntry.bind('<Return>', self.set_SalPercents)
		self.StdErrEntry.bind('<Return>', self.set_SalPercents)
		self.ReptoEntry.bind('<Return>', self.update_Repto)
		self.XRefEntry.bind('<Return>', self.update_XRef)
		self.BlankSpace = Label(self, text="    ")
		self.BlankSpace.grid(row=28, column=2)
		self.BlankSpace2 = Label(self, text="    ")
		self.BlankSpace2.grid(row=9, column=2)

## Navigation
	def nextpage(self, event):
		self.JobTitleLabel.config(foreground="Black")
		self.data.index_next()
		self.label_entry_initload()
		self.jobentryreplace()

	def priorpage(self, event):
		self.JobTitleLabel.config(foreground="Black")
		self.data.index_prior()
		self.label_entry_initload()
		self.jobentryreplace()

	def jobidsearch(self, event):
		self.label_entry_clear()
		try:
			self.intJobIdSearchEntry = int(self.JobIdSearchEntry.get())
			self.data.find_by_erijobid(self.intJobIdSearchEntry)
			self.label_entry_initload()
			if self.data.jobname=="No job found":
				self.JobTitleLabel.config(foreground="Red")
				self.label_entry_clear()
			else:
				self.JobTitleLabel.config(foreground="Black")
		except ValueError:
			self.JobTitleLabel.config(foreground="Red")
			self.JobTitleLabel.config(text="Not a valid search entry")
			self.label_entry_clear()

### Text Editing
	def jobentryreplace(self):
		self.JobIdSearchEntry.delete(0, END)
		self.JobIdSearchEntry.insert(0, str(self.data.current_id))

	def label_entry_clear(self, *event):
		## Labels
		self.JobDotLabel.config(text="    ")
		#self.ExecJobLabel.config(text="    ")
		self.JobSocLabel.config(text="    ")
		self.HighPredPctLabel.config(text="    ")
		self.LowPredPctLabel.config(text="    ")
		self.B100TotalCompLabel.config(text="    ")
		self.HighTotalCompLabel.config(text="    ")
		self.MedTotalCompLabel.config(text="    ")
		self.LowTotalCompLabel.config(text="    ")
		self.Mil1TotalCompLabel.config(text="    ")
		self.EstimatedYearsLabel.config(text="    ")
		self.B100Q1Label.config(text="    ")
		self.HighQ1Label.config(text="    ")
		self.MedQ1Label.config(text="    ")
		self.LowQ1Label.config(text="    ")
		self.Mil1Q1Label.config(text="    ")
		self.QCCheckLabel.config(text= "    ")
		self.SocPredLabel.config(text= "    ")
		self.SurveyMeanLabel.config(text= "    ")
		self.SurveyIncumbentsLabel.config(text= "    ")
		self.QCCheckCanLabel.config(text="    ")
		self.CanPoly1Label.config(text="    ")
		self.CanPoly2Label.config(text="    ")
		self.CanPoly3Label.config(text="    ")
		self.CanPolyMeanLabel.config(text="    ")
		self.CanPolyMeanQCLabel.config(text="    ")
		self.CanMeanLabel.config(text="    ")
		self.CanTotalLabel.config(text="    ")
		self.ReptoTitleLabel.config(text="    ")
		self.ReptoSalLabel.config(text="    ")
		self.ReptoYr3Label.config(text="    ")
		self.XRefTitleLabel.config(text="    ")
		self.XRefUSLabel.config(text="    ")
		self.XRefCanLabel.config(text="    ")
		self.DegreeNameLabel.config(text="    ")
		self.CPCSalLabel.config(text="    ")
		self.AdderLabel.config(text="    ")
		self.RawDataLabel.config(text="    ")
		self.JobDescriptionLabel.config(text="    ")
		self.StdErrPredLabel.config(text="    ")
		self.SocOutputLabel.config(text="    ")
		## Entries
		self.B100PctEntry.delete(0, END)
		self.HighPctEntry.delete(0, END)
		self.MedPctEntry.delete(0, END)
		self.LowPctEntry.delete(0, END)
		self.Mil1PctEntry.delete(0, END)
		self.B100BonusPctEntry.delete(0, END)
		self.HighBonusPctEntry.delete(0, END)
		self.MedBonusPctEntry.delete(0, END)
		self.LowBonusPctEntry.delete(0, END)
		self.Mil1BonusPctEntry.delete(0, END)
		self.StdErrEntry.delete(0, END)
		self.MedYrsEntry.delete(0, END)
		self.USOverrideEntry.delete(0, END)
		self.CanOverrideEntry.delete(0, END)
		self.CanPercentEntry.delete(0, END)
		self.CanBonusPctEntry.delete(0, END)
		self.ReptoEntry.delete(0, END)
		self.XRefEntry.delete(0, END)
		self.CPCEntry.delete(0, END)
		## Calc Labels
		self.Sal100BilLabel.config(text="    ")
		self.MedSalLabel.config(text="    ")
		self.HighSalLabel.config(text="    ")
		self.LowSalLabel.config(text="    ")
		self.Sal1MilLabel.config(text="    ")
		self.High90thPercentile_100BilLabel.config(text="    ")
		self.High90thPercentileLabel.config(text="    ")
		self.Med90thPercentileLabel.config(text="    ")
		self.Low90thPercentileLabel.config(text="    ")
		self.Low90thPercentile_1MilLabel.config(text="    ")
		self.High10thPercentile_100BilLabel.config(text="    ")
		self.High10thPercentileLabel.config(text="    ")
		self.Med10thPercentileLabel.config(text="    ")
		self.Low10thPercentileLabel.config(text="    ")
		self.Low10thPercentile_1MilLabel.config(text="    ")
		self.MeanPredLabel.config(text="    ")

	def label_entry_reload(self, *event):
		self.B100PctEntry.delete(0, END)
		self.HighPctEntry.delete(0, END)
		self.MedPctEntry.delete(0, END)
		self.LowPctEntry.delete(0, END)
		self.Mil1PctEntry.delete(0, END)
		self.B100BonusPctEntry.delete(0, END)
		self.HighBonusPctEntry.delete(0, END)
		self.MedBonusPctEntry.delete(0, END)
		self.LowBonusPctEntry.delete(0, END)
		self.Mil1BonusPctEntry.delete(0, END)
		self.StdErrEntry.delete(0, END)
		self.MedYrsEntry.delete(0, END)
		self.USOverrideEntry.delete(0, END)
		self.CanOverrideEntry.delete(0, END)
		self.CanPercentEntry.delete(0, END)
		self.CanBonusPctEntry.delete(0, END)
		self.ReptoEntry.delete(0, END)
		self.XRefEntry.delete(0, END)
		self.CPCEntry.delete(0, END)
		self.B100PctEntry.insert(0, str(self.data.B100PctDataInit))
		self.HighPctEntry.insert(0, str(self.data.HighPctDataInit))
		self.MedPctEntry.insert(0, str(self.data.MedPctDataInit))
		self.LowPctEntry.insert(0, str(self.data.LowPctDataInit))
		self.Mil1PctEntry.insert(0, str(self.data.Mil1PctDataInit))
		self.B100BonusPctEntry.insert(0, str(self.data.B100BonusPctDataInit))
		self.HighBonusPctEntry.insert(0, str(self.data.HighBonusPctDataInit))
		self.MedBonusPctEntry.insert(0, str(self.data.MedBonusPctDataInit))
		self.LowBonusPctEntry.insert(0, str(self.data.LowBonusPctDataInit))
		self.Mil1BonusPctEntry.insert(0, str(self.data.Mil1BonusPctDataInit))
		self.StdErrEntry.insert(0, str(self.data.StdErrDataInit))
		self.MedYrsEntry.insert(0, str(self.data.MedYrsDataInit))
		self.CanPercentEntry.insert(0, str(self.data.CanPercentDataInit))
		self.CanBonusPctEntry.insert(0, str(self.data.CanBonusPctDataInit))
		self.ReptoEntry.insert(0, str(self.data.ReptoDataInit))
		self.XRefEntry.insert(0, str(self.data.XRefDataInit))
		self.CPCEntry.insert(0, str(self.data.CPCDataInit))
		self.USOverrideEntry.insert(0, str(self.data.USOverrideDataInit))
		self.MeanPredLabel.config(text=int(self.data.MeanPredData))
		self.set_SalPercents()
		self.update_MedSal()
		self.update_CanLabels()
		self.update_Repto()
		self.update_XRef()

	def label_entry_initload(self, *event):
		self.label_entry_clear()
		self.jobentryreplace()
		## Labels
		#if self.data.jobexec==1 : self.ExecJobLabel.config(text="Exec")
		#else : self.ExecJobLabel.config(text="Non-Exec")
		self.JobTitleLabel.config(text= self.data.jobname)
		self.JobDotLabel.config(text= self.data.JobDotData)
		self.JobSocLabel.config(text= self.data.JobSocData)
		self.HighPredPctLabel.config(text= str(round(self.data.HighPredPctData, 2)))
		self.LowPredPctLabel.config(text= str(round(self.data.LowPredPctData, 2)))
		self.B100TotalCompLabel.config(text= self.data.B100TotalCompData)
		self.HighTotalCompLabel.config(text= self.data.HighTotalCompData)
		self.MedTotalCompLabel.config(text= self.data.MedTotalCompData)
		self.LowTotalCompLabel.config(text= self.data.LowTotalCompData)
		self.Mil1TotalCompLabel.config(text= self.data.Mil1TotalCompData)
		self.EstimatedYearsLabel.config(text= self.data.EstimatedYears)
		self.B100Q1Label.config(text= self.data.B100Q1Data)
		self.HighQ1Label.config(text= self.data.HighQ1Data)
		self.MedQ1Label.config(text= self.data.MedQ1Data)
		self.LowQ1Label.config(text= self.data.LowQ1Data)
		self.Mil1Q1Label.config(text= self.data.Mil1Q1Data)
		self.QCCheckLabel.config(text= self.data.QCCheckData)
		self.SocPredLabel.config(text= self.data.SocPredData)
		self.SurveyMeanLabel.config(text= self.data.SurveyMeanData)
		self.SurveyIncumbentsLabel.config(text= self.data.SurveyIncumbentsData)
		self.QCCheckCanLabel.config(text= self.data.QCCheckCanData)
		self.CanPoly1Label.config(text= self.data.CanPoly1Data)
		self.CanPoly2Label.config(text= self.data.CanPoly2Data)
		self.CanPoly3Label.config(text= self.data.CanPoly3Data)
		self.CanPolyMeanLabel.config(text= self.data.CanPolyMeanData)
		self.CanPolyMeanQCLabel.config(text= self.data.CanPolyMeanQCData)
		self.ReptoTitleLabel.config(text= self.data.ReptoTitleData)
		self.ReptoSalLabel.config(text= self.data.ReptoSalData)
		self.ReptoYr3Label.config(text= self.data.ReptoYr3Data)
		self.XRefTitleLabel.config(text= self.data.XRefTitleData)
		self.XRefUSLabel.config(text= self.data.XRefUSData)
		self.XRefCanLabel.config(text= self.data.XRefCanData)
		self.DegreeNameLabel.config(text= self.data.DegreeNameData)
		self.CPCSalLabel.config(text= self.data.CPCSalData)
		self.AdderLabel.config(text= self.data.AdderData)
		#self.RawDataLabel.config(text="Raw data text")
		self.JobDescriptionLabel.config(text= self.data.JobDescriptionData)
		self.SocOutputLabel.config(text=self.data.SocTitleData)
		## Entries
		self.B100PctEntry.insert(0, str(self.data.B100PctData))
		self.HighPctEntry.insert(0, str(self.data.HighPctData))
		self.MedPctEntry.insert(0, str(self.data.MedPctData))
		self.LowPctEntry.insert(0, str(self.data.LowPctData))
		self.Mil1PctEntry.insert(0, str(self.data.Mil1PctData))
		self.B100BonusPctEntry.insert(0, str(self.data.B100BonusPctData))
		self.HighBonusPctEntry.insert(0, str(self.data.HighBonusPctData))
		self.MedBonusPctEntry.insert(0, str(self.data.MedBonusPctData))
		self.LowBonusPctEntry.insert(0, str(self.data.LowBonusPctData))
		self.Mil1BonusPctEntry.insert(0, str(self.data.Mil1BonusPctData))
		self.StdErrEntry.insert(0, str(self.data.StdErrData))
		self.MedYrsEntry.insert(0, str(self.data.MedYrsData))
		self.CanPercentEntry.insert(0, str(self.data.CanPercentData))
		self.CanBonusPctEntry.insert(0, str(self.data.CanBonusPctData))
		self.ReptoEntry.insert(0, str(self.data.ReptoData))
		self.XRefEntry.insert(0, str(self.data.XRefData))
		self.CPCEntry.insert(0, str(self.data.CPCData))
		self.USOverrideEntry.insert(0, str(self.data.USOverrideData))
		## Calc Labels
		self.MeanPredLabel.config(text=int(self.data.MeanPredData))
		self.set_SalPercents()
		self.update_MedSal()
		self.update_CanLabels()
		self.update_Repto()
		self.update_XRef()

	def send_entry(self):
		self.data.B100PctData = float(self.B100PctEntry.get())
		self.data.HighPctData = float(self.HighPctEntry.get())
		self.data.MedPctData = float(self.MedPctEntry.get())
		self.data.LowPctData = float(self.LowPctEntry.get())
		self.data.Mil1PctData = float(self.Mil1PctEntry.get())
		self.data.B100BonusPctData = float(self.B100BonusPctEntry.get())
		self.data.HighBonusPctData = float(self.HighBonusPctEntry.get())
		self.data.MedBonusPctData = float(self.MedBonusPctEntry.get())
		self.data.LowBonusPctData = float(self.LowBonusPctEntry.get())
		self.data.Mil1BonusPctData = float(self.Mil1BonusPctEntry.get())

	def update_Repto(self, *event):
		current_selector = int(self.ReptoEntry.get())
		try:
			self.data.jobsdf.set_index('indexsearch', inplace=True)
			self.data.jobsdf['indexsearch'] = self.data.jobsdf['erijobid']
		except: pass
		try:
			self.data.ReptoTitleData = self.data.jobsdf.loc[current_selector,'jobdottitle']
			self.data.ReptoSalData = self.data.jobsdf.loc[current_selector,'MEDSAL']
			self.data.ReptoYr3Data = self.data.jobsdf.loc[current_selector,'Yr3Sal']
		except KeyError:
			self.data.ReptoTitleData = 'NA'
			self.data.ReptoSalData = 'NA'
			self.data.ReptoYr3Data = 'NA'
		self.ReptoTitleLabel.config(text= self.data.ReptoTitleData)
		self.ReptoSalLabel.config(text= self.data.ReptoSalData)
		self.ReptoYr3Label.config(text= self.data.ReptoYr3Data)

	def update_XRef(self, *event):
		current_selector = int(self.XRefEntry.get())
		try:
			self.data.jobsdf.set_index('indexsearch', inplace=True)
			self.data.jobsdf['indexsearch'] = self.data.jobsdf['erijobid']
		except: pass
		try:
			self.data.XRefTitleData = self.data.jobsdf.loc[current_selector,'jobdottitle']
			self.data.XRefUSData = self.data.jobsdf.loc[current_selector,'MEDSAL']
			self.data.XRefCanData = self.data.jobsdf.loc[current_selector,'CAN_AVE']
		except KeyError:
			self.data.XRefTitleData = 'NA'
			self.data.XRefData = 'NA'
			self.data.XRefCanData = 'NA'
		self.XRefTitleLabel.config(text= self.data.XRefTitleData)
		self.XRefUSLabel.config(text= self.data.XRefUSData)
		self.XRefCanLabel.config(text= self.data.XRefCanData)
		self.update_MedSal()

	def set_SalPercents(self, *event):
		try: self.data.B100PctData = float(self.B100PctEntry.get())
		except ValueError: print("B100err")
		try: self.data.HighPctData = float(self.HighPctEntry.get())
		except ValueError: print("HighPcterr")
		try: self.data.MedPctData = float(self.MedPctEntry.get())
		except ValueError: print("Med error")
		try: self.data.LowPctData = float(self.LowPctEntry.get())
		except ValueError: print("LowPcterr")
		try: self.data.Mil1PctData = float(self.Mil1PctEntry.get())
		except ValueError: print("Mil1err")
		try: self.data.StdErrData = float(self.StdErrEntry.get())
		except ValueError: print("Stderr Error")
		self.update_MedSal()
	
	def update_MedSal(self, *event):
		try:
			if float(self.USOverrideEntry.get())!=0: self.data.update_MedSalCalcData(float(self.USOverrideEntry.get()))
			else: self.data.MedSalData = int(self.data.MedPctData*self.data.XRefUSData)
		except ValueError: print("MedSal Value error")
		self.data.set_CalcData()
		self.update_CalcLabels()
	
	def update_CalcLabels(self, *event):
		## 10th Percentile
		if self.data.jobexec==0: self.High10thPercentile_100BilLabel.config(text="    ")
		else: self.High10thPercentile_100BilLabel.config(text= int(self.data.High10thPercentile_100BilData))
		self.High10thPercentileLabel.config(text= int(self.data.High10thPercentileData))
		self.Med10thPercentileLabel.config(text= int(self.data.Med10thPercentileData))
		self.Low10thPercentileLabel.config(text= int(self.data.Low10thPercentileData))
		if self.data.jobexec==0: self.Low10thPercentile_1MilLabel.config(text="    ")
		else: self.Low10thPercentile_1MilLabel.config(text= int(self.data.Low10thPercentile_1MilData))
		## Mean
		if self.data.jobexec==0: self.Sal100BilLabel.config(text="    ")
		else: self.Sal100BilLabel.config(text= int(self.data.Sal100BilData))
		self.HighSalLabel.config(text= int(self.data.HighSalData))
		self.MedSalLabel.config(text= int(self.data.MedSalData))
		self.LowSalLabel.config(text= int(self.data.LowSalData))
		if self.data.jobexec==0: self.Sal1MilLabel.config(text="    ")
		else: self.Sal1MilLabel.config(text= int(self.data.Sal1MilData))
		## 90th Percentile
		if self.data.jobexec==0: self.High90thPercentile_100BilLabel.config(text="    ")
		else: self.High90thPercentile_100BilLabel.config(text= int(self.data.High90thPercentile_100BilData))
		self.High90thPercentileLabel.config(text= int(self.data.High90thPercentileData))
		self.Med90thPercentileLabel.config(text= int(self.data.Med90thPercentileData))
		self.Low90thPercentileLabel.config(text= int(self.data.Low90thPercentileData))
		if self.data.jobexec==0: self.Low90thPercentile_1MilLabel.config(text="    ")
		else: self.Low90thPercentile_1MilLabel.config(text= int(self.data.Low90thPercentile_1MilData))

	def update_CanValues(self, *event):
		try: self.data.CanPercentData = float(self.CanPercentEntry.get())
		except ValueError: self.data.CanPercentData = self.data.CanPercentData
		try: self.data.CanBonusPctData = float(self.CanBonusPctEntry.get())
		except ValueError: self.data.CanBonusPctData = self.data.CanBonusPctData
		self.update_CanLabels()

	def update_CanLabels(self, *event):
		try: self.data.update_canavedata(float(self.CanOverrideEntry.get()))
		except ValueError: self.data.CanAveData = self.data.CanPercentData * self.data.XRefCanData
		self.CanMeanLabel.config(text= int(self.data.CanAveData))
		self.CanTotalLabel.config(text= int(self.data.CanAveData+(self.data.CanAveData * self.data.CanBonusPctData)))

	def write_output(self, *event):
		self.send_entry()
		#If any changes are made, these will update those; else, these will input what was there before
		self.data.write_to_outputdf()

	def write_sql(self, *event):
		self.data.write_to_sql()


root = Tk()
root.geometry("1150x800")
app = Application(root)
root.mainloop()





