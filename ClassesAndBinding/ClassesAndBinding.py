### DATA AUDIT WORK
## Paste following into anaconda prompt
# cd /d S:\Users\mikael.miller
# python PCTAudit.py


import pandas as pd
import pandas.io.sql as psql
import pyodbc
import os
from datetime import datetime
from tkinter import *
from tkinter.ttk import *
from math import sqrt


class Dataverse:
	def __init__(self):
		self.user = os.getlogin()
		print("Logged in as: "+self.user)
		self.current_index = 0
		self.current_id = 1
		self.jobexec=1
		self.jobname = "Chief Executive Officer"
		self.pyocnxn = pyodbc.connect("DRIVER={SQL Server};SERVER=SNADSSQ3;DATABASE=assessorwork;trusted_connection=yes;")
		self.inititalizedataframe()
		self.initializerawdataframe()
		self.initializesocdataframe()
		self.pyocnxn.close()
		self.set_vars(input="index")
		pd.options.display.float_format = '{:20,.4f}'.format 
		
	def initializesocdataframe(self):
		self.soc_sql = """ SELECT [SocCode],[SocTitle] FROM [AssessorWork].[dbo].[SocDescription] """
		self.socdf = pd.DataFrame(psql.read_sql(self.soc_sql, self.pyocnxn))
		self.socdf.set_index('SocCode', inplace=True)
		#print(self.socdf)
	
	def initializerawdataframe(self):
		self.sql = """
			SELECT surveycan.[EriJobId]
					, cast(REPLACE([S_Comp],'TARGET ->','TAR_CAN') as varchar(15)) S_Comp

					, cast([S_Year] AS VARCHAR(4))+'_'+right('000'+cast([S_Month] AS VARCHAR(2)),2) YEARMO
					, isnull([Rev], Wgt) Wgt
					, isnull([No_Emp],0) No_Emp
					, isnull([AveBase],0) AveBase
					, isnull(cast([Y_Base] as int),0) Y_Base
					, case when S_Comp like 'TARGET%' then 1 else 0 end as S_Order
					, 1 as Can_Order
					, S_Title
			FROM [AssessorWork].[sa].[SurveyCan] surveycan
	
			UNION
	
			SELECT surveyexec.[EriJobId]
					, REPLACE([S_Comp],'TARGET ->','TAR_EXEC') S_Comp
					, cast([S_Year] AS VARCHAR(4))+'_'+right('000'+cast([S_Month] AS VARCHAR(2)),2) YEARMO
					, [Rev] Wgt
					, isnull([No_Emp],0) No_Emp
					, isnull([AveBase],0) AveBase
					, isnull(cast([Y_Base] as int),0) Y_Base
					, case when S_Comp like 'TARGET%' then 1 else 0 end as S_Order
					, 0 as Can_Order
					, S_Title
			FROM [AssessorWork].[sa].[SurveyExec] surveyexec
	
			UNION
	
			SELECT surveynonexec.[EriJobId]
					, REPLACE([S_Comp],'TARGET ->','TAR_NONEX') S_Comp
					, cast([S_Year] AS VARCHAR(4))+'_'+right('000'+cast([S_Month] AS VARCHAR(2)),2) YEARMO
					, [Wgt] Wgt
					, isnull([No_Emp],0) No_Emp
					, isnull([AveBase],0) AveBase
					, isnull(cast([Y_Base] as int),0) Y_Base
					, case when S_Comp like 'TARGET%' then 1 else 0 end as S_Order
					, 0 as Can_Order
					, S_Title
			FROM [AssessorWork].[sa].[SurveyNonExec] surveynonexec

			ORDER BY erijobid, Can_Order, S_Order, YEARMO, S_Title
		"""
		self.rawdatadf = pd.DataFrame(psql.read_sql(self.sql, self.pyocnxn))
		self.rawdatadf.set_index('EriJobId', inplace=True)
		self.getrawdata()

	def inititalizedataframe(self):
		self.sql = """SELECT pct.erijobid
			, pct.jobdot
			, pct.jobdottitle
			, pct.CAN_AVE
			, isnull(pct.Sal1Mil,0) Sal1Mil
			, pct.LOWSAL
			, pct.MEDSAL
			, pct.HIGHSAL
			, isnull(pct.Sal10Bil,0) Sal10Bil
			, isnull(pct.Sal100Bil,0) Sal100Bil
			, isnull(pct.Yr3Sal,0) Yr3Sal
			, pct.CAN_PCT
			, pct.Pct_1Mil
			, pct.LOW_F
			, pct.US_PCT
			, pct.HIGH_F
			, pct.Pct_10Bil
			, pct.Pct_100Bil
			, pct.CANPK_C
			, pct.USPK_C
			, pct.USPK_C1
			, pct.CanBonusPct
			, pct.BonusPct1Mil
			, pct.LowBonusPct
			, pct.MedBonusPct
			, pct.HighBonusPct
			, pct.BonusPct10Bil
			, pct.BonusPct100Bil
			, pct.StdErr
			, isnull(pct.Q11Mil,0) Q11Mil
			, pct.Q1Low
			, pct.Q1Med
			, pct.Q1High
			, isnull(pct.Q1100Bil,0) Q1100Bil
			, isnull(pct.Q110Bil,0) Q110Bil
			, pct.Repto
			, pct.ReptoTitle
			, pct.ReptoSal
			, pct.ReptoYr3
			, pct.JobXRef
			, pct.XRefTitle
			, pct.XRefMed
			, pct.XRefCan
			, pct.Medyrs
			, pct.OldMyrs
			, pct.N_Medyrs
			, pct.AverageYears
			, pct.EstimatedYears
			, isnull(pct.SurveySampleSize,0) SurveySampleSize
			, isnull(pct.Y_Base,0) Y_Base
			, pct.Y_Bpct
			, pct.LowPred
			, pct.MedPred
			, pct.HighPred
			, isnull(pct.CanQ1,0) CanQ1
			, pct.CanPred
			, pct.CanPoly1
			, pct.CanPoly2
			, pct.CanPoly3
			, pct.AvgCanPoly
			, pct.AvgCanModels
			, pct.AvgCan3Qtr
			, pct.Low3QTR_1Mil
			, pct.Low3Qtr
			, pct.Med3Qtr
			, pct.High3Qtr
			, pct.High3Qtr_100Bil
			, pct.Low10thPercentile_1Mil
			, pct.Low10thPercentile
			, pct.Med10thPercentile
			, pct.High10thPercentile
			, pct.High10thPercentile_10Bil
			, pct.High10thPercentile_100Bil
			, pct.Low90thPercentile_1Mil
			, pct.Low90thPercentile
			, pct.Med90thPercentile
			, pct.High90thPercentile
			, pct.High90thPercentile_10bil
			, pct.High90thPercentile_100bil
			, pct.TotalComp1Mil
			, pct.LowTotalComp
			, pct.MedTotalComp
			, pct.HighTotalComp
			, pct.TotalComp10Bil
			, pct.TotalComp100Bil
			, pct.CPCNO
			, pct.CPCSalary
			, pct.CPCSampleSize
			, pct.DegreeType
			, pct.CPCYearlyIncrease
			, pct.Adder
			, pct.DegreeName
			, pct.SOC
			, pct.OccAve
			, pct.USPop
			, pct.JobPopPct
			, pct.Funno
			, pct.SOC16pct
			, pct.SOC66pct
			, pct.LowSOCGrowthPct
			, pct.HighSOCGrothPct
			, pct.GrowthRate
			, pct.LowGrowthRate
			, pct.HighGrowthRate
			, pct.Indusdiffcode
			, pct.eriSurveyCode
			, pct.Profile
			, pct.DOTMatch
			, pct.Math
			, pct.Verb
			, pct.Reas
			, pct.SVP
			, pct.ReleaseId
			, socdesc.soctitle as SocTitle
			, cast(LowPred as float)/MedPred as LowPredCalc
			, cast(HighPred as float)/MedPred as HighPredCalc
			, case when (pct.medyrs>40) then 1 else 0 end as execjob
			, jobdesc.ShortDesc
			
			FROM assessorwork.sa.pct pct
			join (select soccode, soctitle from [AssessorWork].[dbo].[SocDescription]) socdesc on pct.SOC = socdesc.SocCode
			join (select eDOT, replace(replace(ShortDesc,'/duty','duty'),'<duty>','') as ShortDesc from [AssessorWork].[sa].[Sadescriptions]) jobdesc on jobdesc.eDOT = pct.jobdot
			where releaseid like ?
			order by execjob desc, pct.erijobid asc"""
		self.releaseid = str(input ("Enter year & quarter desired (i.e. 2018Q2): "))
		self.jobsdf = pd.DataFrame(psql.read_sql(self.sql, self.pyocnxn, params=(self.releaseid,)))
		self.jobsdf['indexmaster'] = self.jobsdf.index
		self.jobsdf['index1'] = self.jobsdf['indexmaster']
		self.jobsdf['indexsearch'] = self.jobsdf['erijobid']
		self.last_index = self.jobsdf.last_valid_index()
		self.outputdf = pd.DataFrame(columns=self.jobsdf.columns)
		self.jobsdf[['Sal1Mil','LOWSAL','MEDSAL','HIGHSAL','Sal10Bil','Sal100Bil']] = self.jobsdf[['Sal1Mil','LOWSAL','MEDSAL','HIGHSAL','Sal10Bil','Sal100Bil']].astype(int)
		self.outputdf[['Sal1Mil','LOWSAL','MEDSAL','HIGHSAL','Sal10Bil','Sal100Bil']] = self.outputdf[['Sal1Mil','LOWSAL','MEDSAL','HIGHSAL','Sal10Bil','Sal100Bil']].astype(int)
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
			self.getrawdata()
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
		self.getrawdata()

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
		self.getrawdata()

	def getrawdata(self):
		self.rawstring = "S_Comp          S_Title                        YEARMO  Wgt/Rev  No_Emp AveBase Y_Base\n---------------------------------------------------------------------------------------\n" #self.rawdatadf.loc[self.current_id].to_string(index=FALSE, header=FALSE, columns=['S_Comp', 'YEARMO', 'Wgt', 'No_Emp', 'AveBase', 'Y_Base'])
		try:
			self.temprawdf = self.rawdatadf.loc[self.current_id]
			#print(self.temprawdf)
			for index, row in self.temprawdf.iterrows():
				#self.rawstring = self.rawstring+(row[0][:15]).ljust(15)+' '+str(row[1])[:7].ljust(7)+' '+str(row[2])[:8].ljust(8)+' '+str(row[3])[:6].ljust(6)+' '+str(row[4])[:7].ljust(7)+' '+str(int(row[5]))[:10].ljust(10)+'\n'
				self.rawstring = self.rawstring+(row[0][:15]).ljust(15)+' '+str(row[8])[:30].ljust(30)+' '+str(row[1])[:7].ljust(7)+' '+str(row[2])[:8].ljust(8)+' '+str(row[3])[:6].ljust(6)+' '+str(row[4])[:7].ljust(7)+' '+str(int(row[5]))[:8].ljust(8)+'\n'
				if ((row[0][:5]=="TAR_E" and str(row[2])[:5]=="10000") or row[0][:5]=="TAR_N"): self.rawstring = self.rawstring+"---------------------------------------------------------------------------------------\n"
		except: self.rawstring = self.rawstring+""

	def set_vars(self, input="index"):
		if(input=="index"):
			current_selector = self.current_index
		else:
			current_selector = self.current_id
		## Labels
		self.Yr3Data = self.jobsdf.loc[current_selector,'Yr3Sal']
		self.JobTitleData = self.jobsdf.loc[current_selector,'jobdottitle']
		self.ERIJobIdData = self.jobsdf.loc[current_selector,'erijobid']
		self.JobDotData = self.jobsdf.loc[current_selector,'jobdot']
		self.JobSocData = self.jobsdf.loc[current_selector,'SOC']
		self.HighPredPctData = self.jobsdf.loc[current_selector,'HighPredCalc']
		self.LowPredPctData = self.jobsdf.loc[current_selector,'LowPredCalc']
		self.B100TotalCompData = self.jobsdf.loc[current_selector,'TotalComp100Bil']
		self.B10TotalCompData = self.jobsdf.loc[current_selector,'TotalComp10Bil']
		self.HighTotalCompData = self.jobsdf.loc[current_selector,'HighTotalComp']
		self.MedTotalCompData = self.jobsdf.loc[current_selector,'MedTotalComp']
		self.LowTotalCompData = self.jobsdf.loc[current_selector,'LowTotalComp']
		self.Mil1TotalCompData = self.jobsdf.loc[current_selector,'TotalComp1Mil']
		if pd.isnull(self.jobsdf.loc[current_selector,'EstimatedYears']) : self.EstimatedYears = 0
		else: self.EstimatedYears = int(self.jobsdf.loc[current_selector,'EstimatedYears'])
		if pd.isnull(self.jobsdf.loc[current_selector,'Q1100Bil']) : self.B100Q1Data=""
		else: self.B100Q1Data = int(self.jobsdf.loc[current_selector,'Q1100Bil'])
		if pd.isnull(self.jobsdf.loc[current_selector,'Q110Bil']) : self.B10Q1Data=""
		else: self.B10Q1Data = int(self.jobsdf.loc[current_selector,'Q110Bil'])
		self.HighQ1Data = self.jobsdf.loc[current_selector,'Q1High']
		self.MedQ1Data = self.jobsdf.loc[current_selector,'Q1Med']
		self.LowQ1Data = self.jobsdf.loc[current_selector,'Q1Low']
		if pd.isnull(self.jobsdf.loc[current_selector,'Q11Mil']) : self.Mil1Q1Data=""
		else: self.Mil1Q1Data = int(self.jobsdf.loc[current_selector,'Q11Mil'])
		#self.Mil1Q1Data = self.jobsdf.loc[current_selector,'Q11Mil']
		try: self.QCCheckData = int(self.jobsdf.loc[current_selector,'MedPred'])
		except: self.QCCheckData = self.jobsdf.loc[current_selector,'MedPred']
		self.SocPredData = self.jobsdf.loc[current_selector,'OccAve']
		try: self.SurveyMeanData = int(self.jobsdf.loc[current_selector,'Y_Base'])
		except: self.SurveyMeanData = self.jobsdf.loc[current_selector,'Y_Base']
		try: self.SurveyIncumbentsData = int(self.jobsdf.loc[current_selector,'SurveySampleSize'])
		except: self.SurveyIncumbentsData = self.jobsdf.loc[current_selector,'SurveySampleSize']
		try: self.QCCheckCanData = int(self.jobsdf.loc[current_selector,'CanPred'])
		except: self.QCCheckCanData = self.jobsdf.loc[current_selector,'CanPred']
		self.CanQ1Data = self.jobsdf.loc[current_selector,'CanQ1']
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
		if pd.isnull(self.jobsdf.loc[current_selector,'CPCSalary']): self.CPCSalData=0
		else: self.CPCSalData = self.jobsdf.loc[current_selector,'CPCSalary']
		self.AdderData = self.jobsdf.loc[current_selector,'Adder']
		self.SocTitleData = self.jobsdf.loc[current_selector,'SocTitle']
		## Entries
		if pd.isnull(self.jobsdf.loc[current_selector,'Pct_100Bil']): self.B100PctData = 0 #1.95
		else: self.B100PctData = self.jobsdf.loc[current_selector,'Pct_100Bil']
		if pd.isnull(self.jobsdf.loc[current_selector,'Pct_10Bil']): self.B10PctData = 0
		else: self.B10PctData = self.jobsdf.loc[current_selector,'Pct_10Bil']
		self.HighPctData = self.jobsdf.loc[current_selector,'HIGH_F']
		self.MedPctData = self.jobsdf.loc[current_selector,'US_PCT']
		self.LowPctData = self.jobsdf.loc[current_selector,'LOW_F']
		if pd.isnull(self.jobsdf.loc[current_selector,'Pct_1Mil']): self.Mil1PctData = 0 #0.1
		else: self.Mil1PctData = self.jobsdf.loc[current_selector,'Pct_1Mil']
		if pd.isnull(self.jobsdf.loc[current_selector,'BonusPct100Bil']): self.B100BonusPctData = 0
		else: self.B100BonusPctData = self.jobsdf.loc[current_selector,'BonusPct100Bil']
		if pd.isnull(self.jobsdf.loc[current_selector,'BonusPct10Bil']): self.B10BonusPctData = 0
		else: self.B10BonusPctData = self.jobsdf.loc[current_selector,'BonusPct10Bil']
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
		if pd.isnull(self.jobsdf.loc[current_selector,'CANPK_C']): self.CANOverrideData = 0
		else: self.CANOverrideData = float(self.jobsdf.loc[current_selector,'CANPK_C'])
		## Init
		if pd.isnull(self.jobsdf.loc[current_selector,'Pct_100Bil']): self.B100PctDataInit = 0 #1.95
		else: self.B100PctDataInit = self.jobsdf.loc[current_selector,'Pct_100Bil']
		if pd.isnull(self.jobsdf.loc[current_selector,'Pct_10Bil']): self.B10PctDataInit = 0
		else: self.B10PctDataInit = self.jobsdf.loc[current_selector,'Pct_10Bil']
		self.HighPctDataInit = self.jobsdf.loc[current_selector,'HIGH_F']
		self.MedPctDataInit = self.jobsdf.loc[current_selector,'US_PCT']
		self.LowPctDataInit = self.jobsdf.loc[current_selector,'LOW_F']
		if pd.isnull(self.jobsdf.loc[current_selector,'Pct_1Mil']): self.Mil1PctDataInit = 0 #0.1
		else: self.Mil1PctDataInit = self.jobsdf.loc[current_selector,'Pct_1Mil']
		if pd.isnull(self.jobsdf.loc[current_selector,'BonusPct10Bil']): self.B10BonusPctDataInit = 0
		else: self.B10BonusPctDataInit = self.jobsdf.loc[current_selector,'BonusPct10Bil']
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
		self.JobSocDataInit = self.jobsdf.loc[current_selector,'SOC']
		if pd.isnull(self.jobsdf.loc[current_selector,'Repto']): self.ReptoDataInit = int(self.current_id)
		else: self.ReptoDataInit = int(self.jobsdf.loc[current_selector,'Repto'])
		self.XRefDataInit = self.jobsdf.loc[current_selector,'JobXRef']
		self.CPCDataInit = self.jobsdf.loc[current_selector,'CPCNO']
		if pd.isnull(self.jobsdf.loc[current_selector,'USPK_C']): self.USOverrideDataInit = 0
		else: self.USOverrideDataInit = float(self.jobsdf.loc[current_selector,'USPK_C'])
		if pd.isnull(self.jobsdf.loc[current_selector,'CANPK_C']): self.CANOverrideDataInit = 0
		else: self.CANOverrideDataInit = float(self.jobsdf.loc[current_selector,'CANPK_C'])
		self.B100TotalCompDataInit = self.jobsdf.loc[current_selector,'TotalComp100Bil']
		self.B10TotalCompDataInit = self.jobsdf.loc[current_selector,'TotalComp10Bil']
		self.HighTotalCompDataInit = self.jobsdf.loc[current_selector,'HighTotalComp']
		self.MedTotalCompDataInit = self.jobsdf.loc[current_selector,'MedTotalComp']
		self.LowTotalCompDataInit = self.jobsdf.loc[current_selector,'LowTotalComp']
		self.Mil1TotalCompDataInit = self.jobsdf.loc[current_selector,'TotalComp1Mil']
		## Other
		self.jobexec = self.jobsdf.loc[current_selector,'execjob']
		self.JobDescriptionData = self.jobsdf.loc[current_selector,'ShortDesc']
		## Check Output before calculating
		self.check_output()
		## Calculations
		self.CanAveData = self.CanPercentData * self.XRefCanData
		# fix below
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
		self.Sal10BilData = self.MedSalData * self.B10PctData
		self.Sal100BilData = self.MedSalData * self.B100PctData
		self.HighSalData = self.MedSalData * self.HighPctData
		self.LowSalData = self.MedSalData * self.LowPctData
		self.Sal1MilData = self.MedSalData * self.Mil1PctData
		self.High90thPercentile_100BilData = ((self.StdErrData/100*1.6)+1) * self.Sal100BilData
		self.High90thPercentile_10BilData = ((self.StdErrData/100*1.6)+1) * self.Sal10BilData
		self.High90thPercentileData = ((self.StdErrData/100*1.6)+1) * self.HighSalData
		self.Med90thPercentileData = ((self.StdErrData/100*1.6)+1) * self.MedSalData
		self.Low90thPercentileData = ((self.StdErrData/100*1.6)+1) * self.LowSalData
		self.Low90thPercentile_1MilData = ((self.StdErrData/100*1.6)+1) * self.Sal1MilData
		self.High10thPercentile_100BilData = ((1 - self.StdErrData/100) * self.Sal100BilData)
		self.High10thPercentile_10BilData = ((1 - self.StdErrData/100) * self.Sal10BilData)
		self.High10thPercentileData = ((1 - self.StdErrData/100) * self.HighSalData)
		self.Med10thPercentileData = ((1 - self.StdErrData/100) * self.MedSalData)
		self.Low10thPercentileData = ((1 - self.StdErrData/100) * self.LowSalData)
		self.Low10thPercentile_1MilData = ((1 - self.StdErrData/100) * self.Sal1MilData)
		self.B100TotalCompData = int(self.Sal100BilData + self.Sal100BilData * self.B100BonusPctData)
		self.B10TotalCompData = int(self.Sal10BilData + self.Sal10BilData * self.B10BonusPctData)
		self.HighTotalCompData = int(self.HighSalData + self.HighSalData * self.HighBonusPctData)
		self.MedTotalCompData = int(self.MedSalData + self.MedSalData * self.MedBonusPctData)
		self.LowTotalCompData = int(self.LowSalData + self.LowSalData * self.LowBonusPctData)
		self.Mil1TotalCompData = int(self.Sal1MilData + self.Sal1MilData * self.Mil1BonusPctData)

	def check_output(self, *event):
		try:
			self.jobsdf.set_index('indexsearch', inplace=True)
			self.jobsdf['indexsearch'] = self.jobsdf['erijobid']
		except: pass
		## Check for current erijobid in output df, add or update as necessary
		if (self.outputdf['erijobid']==self.current_id).any():
			current_selector = self.current_id
			self.Yr3Data = self.outputdf.loc[current_selector,'Yr3Sal']
			self.JobTitleData = self.outputdf.loc[current_selector,'jobdottitle']
			self.ERIJobIdData = self.outputdf.loc[current_selector,'erijobid']
			self.JobDotData = self.outputdf.loc[current_selector,'jobdot']
			self.JobSocData = self.outputdf.loc[current_selector,'SOC']
			self.HighPredPctData = self.outputdf.loc[current_selector,'HighPredCalc']
			self.LowPredPctData = self.outputdf.loc[current_selector,'LowPredCalc']
			self.B100TotalCompData = self.outputdf.loc[current_selector,'TotalComp100Bil']
			self.B10TotalCompData = self.outputdf.loc[current_selector,'TotalComp10Bil']
			self.HighTotalCompData = self.outputdf.loc[current_selector,'HighTotalComp']
			self.MedTotalCompData = self.outputdf.loc[current_selector,'MedTotalComp']
			self.LowTotalCompData = self.outputdf.loc[current_selector,'LowTotalComp']
			self.Mil1TotalCompData = self.outputdf.loc[current_selector,'TotalComp1Mil']
			if pd.isnull(self.outputdf.loc[current_selector,'EstimatedYears']) : self.EstimatedYears = 0
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
			if pd.isnull(self.outputdf.loc[current_selector,'Pct_100Bil']): self.B100PctData = 0
			else: self.B100PctData = self.outputdf.loc[current_selector,'Pct_100Bil']
			if pd.isnull(self.outputdf.loc[current_selector,'Pct_10Bil']): self.B10PctData = 0 #1.95
			else: self.B10PctData = self.outputdf.loc[current_selector,'Pct_10Bil']
			self.HighPctData = self.outputdf.loc[current_selector,'HIGH_F']
			self.MedPctData = self.outputdf.loc[current_selector,'US_PCT']
			self.LowPctData = self.outputdf.loc[current_selector,'LOW_F']
			if pd.isnull(self.outputdf.loc[current_selector,'Pct_1Mil']): self.Mil1PctData = 0 #0.1
			else: self.Mil1PctData = self.outputdf.loc[current_selector,'Pct_1Mil']
			self.B100BonusPctData = self.outputdf.loc[current_selector,'BonusPct100Bil']
			self.B10BonusPctData = self.outputdf.loc[current_selector,'BonusPct10Bil']
			self.HighBonusPctData = self.outputdf.loc[current_selector,'HighBonusPct']
			self.MedBonusPctData = self.outputdf.loc[current_selector,'MedBonusPct']
			self.LowBonusPctData = self.outputdf.loc[current_selector,'LowBonusPct']
			self.Mil1BonusPctData = self.outputdf.loc[current_selector,'BonusPct1Mil']
			self.StdErrData = self.outputdf.loc[current_selector,'StdErr']
			self.MedYrsData = self.outputdf.loc[current_selector,'Medyrs']
			self.CanPercentData = self.outputdf.loc[current_selector,'CAN_PCT']
			self.CanBonusPctData = self.outputdf.loc[current_selector,'CanBonusPct']
			self.JobSocData = self.outputdf.loc[current_selector,'SOC']
			if pd.isnull(self.outputdf.loc[current_selector,'Repto']): self.ReptoData = int(self.current_id)
			else: self.ReptoData = int(self.outputdf.loc[current_selector,'Repto'])
			self.XRefData = self.outputdf.loc[current_selector,'JobXRef']
			self.CPCData = self.outputdf.loc[current_selector,'CPCNO']
			self.jobexec = self.outputdf.loc[current_selector,'execjob']
			self.USOverrideData = self.outputdf.loc[current_selector,'USPK_C']
			self.CANOverrideData = self.outputdf.loc[current_selector, 'CANPK_C']

	def write_to_outputdf(self, *event):
		try:
			self.jobsdf.set_index('indexsearch', inplace=True)
			self.jobsdf['indexsearch'] = self.jobsdf['erijobid']
		except: pass
		## Check for current erijobid in output df, add or update as necessary
		if (self.outputdf['erijobid']==self.current_id).any():
			self.outputdf.update(self.jobsdf.loc[self.current_id,:])
		else: self.outputdf = self.outputdf.append(self.jobsdf.loc[self.current_id,:])
		## Update output rows after creating
		self.outputdf.update(self.jobsdf.loc[self.current_id,:])
		self.outputdf.set_value(self.current_id,'erijobid', self.current_id) #[erijobid]
		self.outputdf.set_value(self.current_id,'jobdot', self.JobDotData) #[jobdot]
		self.outputdf.set_value(self.current_id,'jobdottitle', self.JobTitleData) #[jobdottitle]
		self.outputdf.set_value(self.current_id,'CAN_AVE', self.CanAveData) #[CAN_AVE]
		self.outputdf.set_value(self.current_id,'Sal1Mil', self.Sal1MilData) #[Sal1Mil]
		self.outputdf.set_value(self.current_id,'LOWSAL', self.LowSalData) #[LOWSAL]
		self.outputdf.set_value(self.current_id,'MEDSAL', self.MedSalData) #[MEDSAL]
		self.outputdf.set_value(self.current_id,'HIGHSAL', self.HighSalData) #[HIGHSAL]
		self.outputdf.set_value(self.current_id,'Sal10Bil', self.Sal10BilData) #[Sal10Bil]
		self.outputdf.set_value(self.current_id,'Sal100Bil', self.Sal100BilData) #[Sal100Bil]
		self.outputdf.set_value(self.current_id,'Yr3Sal', int(self.Yr3Data)) #[Yr3Sal]
		self.outputdf.set_value(self.current_id,'CAN_PCT', self.CanPercentData) #[CAN_PCT]
		self.outputdf.set_value(self.current_id,'Pct_1Mil', self.Mil1PctData) #[Pct_1Mil]
		self.outputdf.set_value(self.current_id,'LOW_F', self.LowPctData) #[LOW_F]
		self.outputdf.set_value(self.current_id,'US_PCT', self.MedPctData) #[US_PCT]
		self.outputdf.set_value(self.current_id,'HIGH_F', self.HighPctData) #[HIGH_F]
		self.outputdf.set_value(self.current_id,'Pct_10Bil', self.B10PctData) #[Pct_10Bil]
		self.outputdf.set_value(self.current_id,'Pct_100Bil', self.B100PctData) #[Pct_100Bil]
		self.outputdf.set_value(self.current_id,'CANPK_C', self.CANOverrideData) #[CANPK_C]
		self.outputdf.set_value(self.current_id,'USPK_C', self.USOverrideData) #[USPK_C]
		 #[USPK_C1]
		self.outputdf.set_value(self.current_id,'CanBonusPct', self.CanBonusPctData) #[CanBonusPct]
		self.outputdf.set_value(self.current_id,'BonusPct1Mil', self.Mil1BonusPctData) #[BonusPct1Mil]
		self.outputdf.set_value(self.current_id,'LowBonusPct', self.LowBonusPctData) #[LowBonusPct]
		self.outputdf.set_value(self.current_id,'MedBonusPct', self.MedBonusPctData) #[MedBonusPct]
		self.outputdf.set_value(self.current_id,'HighBonusPct', self.HighBonusPctData) #[HighBonusPct]
		self.outputdf.set_value(self.current_id,'BonusPct10Bil', self.B10BonusPctData) #[BonusPct10Bil]
		self.outputdf.set_value(self.current_id,'BonusPct100Bil', self.B100BonusPctData) #[BonusPct100Bil]
		self.outputdf.set_value(self.current_id,'StdErr', self.StdErrData) #[StdErr]
		self.outputdf.set_value(self.current_id,'Q11Mil', self.Mil1Q1Data) #[Q11Mil]
		self.outputdf.set_value(self.current_id,'Q1Low', int(self.LowQ1Data)) #[Q1Low]
		self.outputdf.set_value(self.current_id,'Q1Med', int(self.MedQ1Data)) #[Q1Med]
		self.outputdf.set_value(self.current_id,'Q1High', int(self.HighQ1Data)) #[Q1High]
		self.outputdf.set_value(self.current_id,'Q1100Bil', int(self.B100Q1Data)) #[Q1100Bil]
		self.outputdf.set_value(self.current_id,'Repto', int(self.ReptoData)) #[Repto]
		self.outputdf.set_value(self.current_id,'ReptoTitle', self.ReptoTitleData) #[ReptoTitle]
		self.outputdf.set_value(self.current_id,'ReptoSal', int(self.ReptoSalData)) #[ReptoSal]
		self.outputdf.set_value(self.current_id,'ReptoYr3', int(self.ReptoYr3Data)) #[ReptoYr3]
		self.outputdf.set_value(self.current_id,'JobXRef', int(self.XRefData)) #[JobXRef]
		self.outputdf.set_value(self.current_id,'XRefTitle', self.XRefTitleData) #[XRefTitle]
		self.outputdf.set_value(self.current_id,'XRefMed', int(self.XRefUSData)) #[XRefMed]
		self.outputdf.set_value(self.current_id,'XRefCan', int(self.XRefCanData)) #[XRefCan]
		self.outputdf.set_value(self.current_id,'Medyrs', int(self.MedYrsData)) #[Medyrs]
		##[OldMyrs]
		##[N_Medyrs]
		##[AverageYears]
		##[EstimatedYears]
		self.outputdf.set_value(self.current_id,'SurveySampleSize', int(self.SurveyIncumbentsData)) #[SurveySampleSize]
		self.outputdf.set_value(self.current_id,'Y_Base', int(self.SurveyMeanData)) #[Y_Base]
		##[Y_Bpct]
		##[LowPred]
		self.outputdf.set_value(self.current_id,'MedPred', int(self.QCCheckData)) #[MedPred]
		##[HighPred]
		self.outputdf.set_value(self.current_id,'CanPred', int(self.QCCheckCanData)) #[CanPred]
		self.outputdf.set_value(self.current_id,'CanPoly1', int(self.CanPoly1Data)) #[CanPoly1]
		self.outputdf.set_value(self.current_id,'CanPoly2', int(self.CanPoly2Data)) #[CanPoly2]
		self.outputdf.set_value(self.current_id,'CanPoly3', int(self.CanPoly3Data)) #[CanPoly3]
		self.outputdf.set_value(self.current_id,'AvgCanPoly', int(self.CanPolyMeanData)) #[AvgCanPoly]
		self.outputdf.set_value(self.current_id,'AvgCanModels', int(self.CanPolyMeanQCData)) #[AvgCanModels]
		##[AvgCan3Qtr]
		##[Low3QTR_1Mil]
		##[Low3Qtr]
		##[Med3Qtr]
		##[High3Qtr]
		##[High3Qtr_100Bil]
		self.outputdf.set_value(self.current_id,'Low10thPercentile_1Mil', int(self.Low10thPercentile_1MilData)) #[Low10thPercentile_1Mil]
		self.outputdf.set_value(self.current_id,'Low10thPercentile', int(self.Low10thPercentileData)) #[Low10thPercentile]
		self.outputdf.set_value(self.current_id,'Med10thPercentile', int(self.Med10thPercentileData)) #[Med10thPercentile]
		self.outputdf.set_value(self.current_id,'High10thPercentile', int(self.High10thPercentileData)) #[High10thPercentile]
		self.outputdf.set_value(self.current_id,'High10thPercentile_100Bil', int(self.High10thPercentile_100BilData)) #[High10thPercentile_100Bil]
		self.outputdf.set_value(self.current_id,'High10thPercentile_10Bil', int(self.High10thPercentile_10BilData)) #[High10thPercentile_10Bil]
		self.outputdf.set_value(self.current_id,'Low90thPercentile_1Mil', int(self.Low90thPercentile_1MilData)) #[Low90thPercentile_1Mil]
		self.outputdf.set_value(self.current_id,'Low90thPercentile', int(self.Low90thPercentileData)) #[Low90thPercentile]
		self.outputdf.set_value(self.current_id,'Med90thPercentile', int(self.Med90thPercentileData)) #[Med90thPercentile]
		self.outputdf.set_value(self.current_id,'High90thPercentile', int(self.High90thPercentileData)) #[High90thPercentile]
		self.outputdf.set_value(self.current_id,'High90thPercentile_10bil', int(self.High90thPercentile_10BilData)) #[High90thPercentile_10bil]
		self.outputdf.set_value(self.current_id,'High90thPercentile_100bil', int(self.High90thPercentile_100BilData)) #[High90thPercentile_100bil]
		self.outputdf.set_value(self.current_id,'TotalComp1Mil', int(self.Mil1TotalCompData)) #[TotalComp1Mil]
		self.outputdf.set_value(self.current_id,'LowTotalComp', int(self.LowTotalCompData)) #[LowTotalComp]
		self.outputdf.set_value(self.current_id,'MedTotalComp', int(self.MedTotalCompData)) #[MedTotalComp]
		self.outputdf.set_value(self.current_id,'HighTotalComp', int(self.HighTotalCompData)) #[HighTotalComp]
		self.outputdf.set_value(self.current_id,'TotalComp10Bil', int(self.B10TotalCompData)) #[TotalComp100Bil]
		self.outputdf.set_value(self.current_id,'TotalComp100Bil', int(self.B100TotalCompData)) #[TotalComp100Bil]
		self.outputdf.set_value(self.current_id,'CPCNO', int(self.CPCData)) #[CPCNO]
		self.outputdf.set_value(self.current_id,'CPCSalary', int(self.CPCSalData)) #[CPCSalary]
		##[CPCSampleSize]
		##[DegreeType]
		##[CPCYearlyIncrease]
		self.outputdf.set_value(self.current_id,'Adder', int(self.AdderData)) #[Adder]
		self.outputdf.set_value(self.current_id,'DegreeName', self.DegreeNameData) #[DegreeName]
		self.outputdf.set_value(self.current_id,'SOC', self.JobSocData) #[SOC]
		self.outputdf.set_value(self.current_id,'OccAve', int(self.SocPredData)) #[OccAve]
		##[USPop]
		##[JobPopPct]
		##[Funno]
		##[SOC16pct]
		##[SOC66pct]
		##[LowSOCGrowthPct]
		##[HighSOCGrothPct]
		##[GrowthRate]
		##[LowGrowthRate]
		##[HighGrowthRate]
		##[Indusdiffcode]
		##[eriSurveyCode]
		##[Profile]
		##[DOTMatch]
		##[Math]
		##[Verb]
		##[Reas]
		##[SVP]
		##[ReleaseId]
		self.outputdf.set_value(self.current_id,'SocTitle', self.SocTitleData) #[SocTitle]
		self.outputdf.set_value(self.current_id,'LowPredCalc', float(self.LowPredPctData)) #[LowPredCalc]
		self.outputdf.set_value(self.current_id,'HighPredCalc', float(self.HighPredPctData)) #[HighPredCalc]
		##[USBenchMed]
		##[CanBenchMed]
		##[ShortDesc]
		#print("Output DF")
		#with pd.option_context('display.max_rows', None, 'display.max_columns', None):
		#	print(self.outputdf)

		print(str(self.current_id)+" - Data written to OutputDF")

	def write_to_sql(self, *event):
		# Copy output DataFrame to SQL DataFrame before printing
		self.sqldf = self.outputdf.copy()
		#print("SQL DF")
		#with pd.option_context('display.max_rows', None, 'display.max_columns', None):
		#	print(self.sqldf)
		# Drop specific columns from SQL DataFrame before writing to SQL database
		self.sqldf = self.sqldf.drop(['execjob','indexmaster','index1','indexsearch'],axis=1)
		self.pyocnxn = pyodbc.connect("DRIVER={SQL Server};SERVER=SNADSSQ3;DATABASE=assessorwork;trusted_connection=yes;")
		cursor = self.pyocnxn.cursor()
		for index, row in self.sqldf.iterrows():
			self.outputsql = """
				update assessorwork.sa.PCT
				set CAN_AVE = ?
				, Sal1Mil = ?
				, LOWSAL = ?
				, MEDSAL = ?
				, HIGHSAL = ?
				, Sal10Bil = ?
				, Sal100Bil = ?
				, CAN_PCT = ?
				, Pct_1Mil = ?
				, LOW_F = ?
				, US_PCT = ?
				, HIGH_F = ?
				, PCT_10Bil = ?
				, PCT_100Bil = ?
				, CANPK_C = ?
				, USPK_C = ?
				, CanBonusPct = ?
				, BonusPct1Mil = ?
				, LowBonusPct = ?
				, MedBonusPct = ?
				, HighBonusPct = ?
				, BonusPct10Bil = ?
				, BonusPct100Bil = ?
				, StdErr = ?
				, Repto = ?
				, ReptoTitle = ?
				, ReptoSal = ?
				, ReptoYr3 = ?
				, JobXRef = ?
				, XRefTitle = ?
				, XRefMed = ?
				, XRefCan = ?
				, Medyrs = ?
				, Low10thPercentile_1Mil = ?
				, Low10thPercentile = ?
				, Med10thPercentile = ?
				, High10thPercentile = ?
				, High10thPercentile_100Bil = ?
				, High10thPercentile_10Bil = ?
				, Low90thPercentile_1Mil = ?
				, Low90thPercentile = ?
				, Med90thPercentile = ?
				, High90thPercentile = ?
				, High90thPercentile_10bil = ?
				, High90thPercentile_100bil = ?
				, TotalComp1Mil = ?
				, LowTotalComp = ?
				, MedTotalComp = ?
				, HighTotalComp = ?
				, TotalComp10Bil = ?
				, TotalComp100Bil = ?
				, LastUpdateDate = ?
				, SOC = ?
				, Yr3Sal = ?
				, CanPoly1 = ?
				, CanPoly2 = ?
				, CanPoly3 = ?
				, AvgCanPoly = ?
				, AvgCanModels = ?
				
				where erijobid = ? and releaseid = ?"""
			
			## Inserting Nulls to SQL DB for consistency
			if row['Sal1Mil']<=0: Sal1Mil_out = None
			else: Sal1Mil_out = row['Sal1Mil']
			if row['Sal100Bil']<=0: Sal100Bil_out = None
			else: Sal100Bil_out = row['Sal100Bil']
			if row['Sal10Bil']<=0: Sal10Bil_out = None
			else: Sal10Bil_out = row['Sal10Bil']
			if row['BonusPct1Mil']==0: BonusPct1Mil_out = None
			else: BonusPct1Mil_out = row['BonusPct1Mil']
			if row['BonusPct10Bil']==0: BonusPct10Bil_out = None
			else: BonusPct10Bil_out = row['BonusPct10Bil']
			if row['BonusPct100Bil']==0: BonusPct100Bil_out = None
			else: BonusPct100Bil_out = row['BonusPct100Bil']
			if row['CANPK_C']==0: CanOverride_out = None
			else: CanOverride_out = row['CANPK_C']
			if row['USPK_C']==0: USOverride_out = None
			else: USOverride_out = row['USPK_C']
			if row['Low10thPercentile_1Mil']==0: Low10thPercentile_1Mil_out = None
			else: Low10thPercentile_1Mil_out = row['Low10thPercentile_1Mil']
			if row['High10thPercentile_100Bil']==0: High10thPercentile_100Bil_out = None
			else: High10thPercentile_100Bil_out = row['High10thPercentile_100Bil']
			if row['High10thPercentile_10Bil']==0: High10thPercentile_10Bil_out = None
			else: High10thPercentile_10Bil_out = row['High10thPercentile_10Bil']
			if row['Low90thPercentile_1Mil']==0: Low90thPercentile_1Mil_out = None
			else: Low90thPercentile_1Mil_out = row['Low90thPercentile_1Mil']
			if row['High90thPercentile_10bil']==0: High90thPercentile_10bil_out = None
			else: High90thPercentile_10bil_out = row['High90thPercentile_10bil']
			if row['High90thPercentile_100bil']==0: High90thPercentile_100bil_out = None
			else: High90thPercentile_100bil_out = row['High90thPercentile_100bil']
			if row['TotalComp1Mil']==0: TotalComp1Mil_out = None
			else: TotalComp1Mil_out = row['TotalComp1Mil']
			if row['TotalComp10Bil']==0: TotalComp10Bil_out = None
			else: TotalComp10Bil_out = row['TotalComp10Bil']
			if row['TotalComp100Bil']==0: TotalComp100Bil_out = None
			else: TotalComp100Bil_out = row['TotalComp100Bil']
			
			args = (int(row['CAN_AVE']), Sal1Mil_out, int(row['LOWSAL']), int(row['MEDSAL']), int(row['HIGHSAL']), Sal10Bil_out, Sal100Bil_out, row['CAN_PCT'], row['Pct_1Mil'], row['LOW_F'], row['US_PCT'], row['HIGH_F'],row['Pct_10Bil'], row['Pct_100Bil'], CanOverride_out, USOverride_out, row['CanBonusPct'], BonusPct1Mil_out, row['LowBonusPct'], row['MedBonusPct'], row['HighBonusPct'], BonusPct10Bil_out, BonusPct100Bil_out, row['StdErr'], row['Repto'], row['ReptoTitle'], row['ReptoSal'], row['ReptoYr3'], row['JobXRef'], row['XRefTitle'], row['XRefMed'], row['XRefCan'], row['Medyrs'], Low10thPercentile_1Mil_out, row['Low10thPercentile'], row['Med10thPercentile'], row['High10thPercentile'],High10thPercentile_100Bil_out, High10thPercentile_10Bil_out, Low90thPercentile_1Mil_out, row['Low90thPercentile'], row['Med90thPercentile'], row['High90thPercentile'], High90thPercentile_10bil_out, High90thPercentile_100bil_out, TotalComp1Mil_out, row['LowTotalComp'], row['MedTotalComp'], row['HighTotalComp'], TotalComp10Bil_out, TotalComp100Bil_out, datetime.now(), row['SOC'], row['Yr3Sal'], row['CanPoly1'], row['CanPoly2'], row['CanPoly3'], row['AvgCanPoly'], row['AvgCanModels'],int(row['erijobid']), self.releaseid)
			#for item in args: print(item)
			cursor.execute(self.outputsql,args)
			self.pyocnxn.commit()
			
			#logsql = """ insert into assessorwork.dbo.pctauditlog values (?,?,?) """
			#logargs = (int(row['erijobid']),self.user,datetime.now())
			#cursor.execute(logsql, logargs)
			#self.pyocnxn.commit()
			
		self.pyocnxn.close()
		#engine = sqlalchemy.create_engine('mssql+pyodbc://SNADSSQ3/AssessorWork?driver=SQL+Server+Native+Client+11.0')
		#self.sqldf.to_sql('AuditTest_',engine,schema='dbo',if_exists='append',index=False)
		print("Dataframe written to SQL")
		#self.outputdf.drop(self.outputdf.index, inplace=True)
		self.sqldf.drop(self.sqldf.index, inplace=True)


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
		self.bind_all('<Control-s>', self.write_output)
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
		self.TitleFrame = Frame(self)
		self.TitleFrame.grid(row=0, column=0, columnspan=4, sticky=NW)
		self.TitleFrame.config(pad=(5,0))
		self.TitleEri = Label(self.TitleFrame,text="Title")
		self.TitleEri.pack(side=LEFT)
		self.JobTitleLabel = Label(self.TitleFrame, text="[Initial Text]", relief="groove", width=45, anchor=W)
		self.JobTitleLabel.pack(side=LEFT, padx=10)
		self.ERISearch = Label(self.TitleFrame,text="ERI # Search")
		self.ERISearch.pack(side=LEFT, padx=10)
		self.JobIdSearchEntry = Entry(self.TitleFrame, width=10)
		self.JobIdSearchEntry.pack(side=LEFT, padx=10)
		self.obsnum = Label(self.TitleFrame, text="Obs #:")
		self.obsnum.pack(side=LEFT)
		self.obsnumlabel = Label(self.TitleFrame, text="1")
		self.obsnumlabel.pack(side=LEFT)
		self.SOCFrame = Frame(self)
		self.SOCFrame.grid(row=2, column=0, columnspan=8, sticky=NW)
		self.eDOT = Label(self.SOCFrame,text="eDOT")
		self.eDOT.pack(side=LEFT, padx=10)
		self.JobDotLabel = Label(self.SOCFrame, text="[Initial Text]", relief="groove", width=10)
		self.JobDotLabel.pack(side=LEFT, padx=10)
		self.SOC = Label(self.SOCFrame,text="SOC")
		self.SOC.pack(side=LEFT, padx=10)
		self.SOCEntry = Entry(self.SOCFrame, width=10)
		self.SOCEntry.pack(side=LEFT, padx=10)
		self.SocOutputLabel = Label(self.SOCFrame, text="[Initial Text]", relief="groove", width=100)
		self.SocOutputLabel.pack(side=LEFT)
		self.ReloadBtn = Button(self, text="Reload Data", command=self.label_entry_reload)
		self.ReloadBtn.grid(row=0, column=4)
		self.CommitBtn = Button(self, text="Commit", command=self.write_output, width=9)
		self.CommitBtn.grid(row=0, column=5)
		self.WriteSQLBtn = Button(self, text="Write to SQL", command=self.write_sql)
		self.WriteSQLBtn.grid(row=0, column=6, sticky=W)
		self.B100PctEntry = Entry(self, width=10)
		self.B100PctEntry.grid(row=11, column=3)
		self.B10PctEntry = Entry(self, width=10)
		self.B10PctEntry.grid(row=12, column=3)
		self.HighPctEntry = Entry(self, width=10)
		self.HighPctEntry.grid(row=13, column=3)
		self.MedPctEntry = Entry(self, width=10)
		self.MedPctEntry.grid(row=14, column=3)
		self.LowPctEntry = Entry(self, width=10)
		self.LowPctEntry.grid(row=15, column=3)
		self.Mil1PctEntry = Entry(self, width=10)
		self.Mil1PctEntry.grid(row=16, column=3)
		self.B100BonusPctEntry = Entry(self, width=10)
		self.B100BonusPctEntry.grid(row=17, column=3)
		self.B10BonusPctEntry = Entry(self, width=10)
		self.B10BonusPctEntry.grid(row=18, column=3)
		self.HighBonusPctEntry = Entry(self, width=10)
		self.HighBonusPctEntry.grid(row=19, column=3)
		self.MedBonusPctEntry = Entry(self, width=10)
		self.MedBonusPctEntry.grid(row=20, column=3)
		self.LowBonusPctEntry = Entry(self, width=10)
		self.LowBonusPctEntry.grid(row=21, column=3)
		self.Mil1BonusPctEntry = Entry(self, width=10)
		self.Mil1BonusPctEntry.grid(row=22, column=3)
		self.StdErrEntry = Entry(self, width=10)
		self.StdErrEntry.grid(row=23, column=3)
		self.MedYrsEntry = Entry(self, width=10)
		self.MedYrsEntry.grid(row=24, column=3)
		self.USOverrideEntry = Entry(self, width=10)
		self.USOverrideEntry.grid(row=26, column=2)
		self.CanOverrideEntry = Entry(self, width=10)
		self.CanOverrideEntry.grid(row=27, column=2)
		self.CanPercentEntry = Entry(self, width=10)
		self.CanPercentEntry.grid(row=28, column=4, sticky=W)
		self.CanBonusPctEntry = Entry(self, width=10)
		self.CanBonusPctEntry.grid(row=29, column=4, sticky=W)
		self.ReptoEntry = Entry(self, width=10)
		self.ReptoEntry.grid(row=32, column=2)
		self.XRefEntry = Entry(self, width=10)
		self.XRefEntry.grid(row=33, column=2)
		self.Pct10 = Label(self,text="10th Pct")
		self.Pct10.grid(row=3, column=2)
		self.Mean = Label(self,text="Mean")
		self.Mean.grid(row=3, column=3)
		self.Pct90 = Label(self,text="90th Pct")
		self.Pct90.grid(row=3, column=4)
		self.LastQ = Label(self,text="Last Qtr")
		self.LastQ.grid(row=3, column=5)
		self.RawData = Label(self,text="Raw Data")
		self.RawData.grid(row=4, column=0, sticky=W)
		self.B100 = Label(self,text="Exec/100 Bil")
		self.B100.grid(row=4, column=1, sticky=E)
		self.B100 = Label(self,text="Exec/10 Bil")
		self.B100.grid(row=5, column=1, sticky=E)
		self.B100Q1 = Label(self,text="Q1 100 Bil/Exec")
		self.B100Q1.grid(row=4, column=6, sticky=W)
		self.B10Q1 = Label(self,text="Q1 10 Bil/Exec")
		self.B10Q1.grid(row=5, column=6, sticky=W)
		self.High = Label(self,text="High Year/1 Bil")
		self.High.grid(row=6, column=1, sticky=E)
		self.HighQ1 = Label(self,text="Q1 Highsal")
		self.HighQ1.grid(row=6, column=6, sticky=W)
		self.Med = Label(self,text="Med Year/100 Mil")
		self.Med.grid(row=7, column=1, sticky=E)
		self.MedQ1 = Label(self,text="Q1 Medsal")
		self.MedQ1.grid(row=7, column=6, sticky=W)
		self.Low = Label(self,text="Low Year/10 Mil")
		self.Low.grid(row=8, column=1, sticky=E)
		self.LowQ1 = Label(self,text="Q1 Lowsal")
		self.LowQ1.grid(row=8, column=6, sticky=W)
		self.Mil1 = Label(self,text="Exec/1 Mil")
		self.Mil1.grid(row=9, column=1, sticky=E)
		self.Mil1Q1 = Label(self,text="Q1 1 Mil/Exec")
		self.Mil1Q1.grid(row=9, column=6, sticky=W)
		self.B100Pct = Label(self,text="100B Percent")
		self.B100Pct.grid(row=11, column=4, sticky=W)
		self.B10Pct = Label(self,text="10B Percent")
		self.B10Pct.grid(row=12, column=4, sticky=W)
		self.PredUS = Label(self,text="Pred US")
		self.PredUS.grid(row=11, column=5)
		self.HighPredPct = Label(self,text="High Pred %")
		self.HighPredPct.grid(row=13, column=1, sticky=E)
		self.HighPct = Label(self,text="High Percent")
		self.HighPct.grid(row=13, column=4, sticky=W)
		self.QCCheck = Label(self,text="QC Check")
		self.QCCheck.grid(row=12, column=6, sticky=W)
		self.MedPct = Label(self,text="Med Percent")
		self.MedPct.grid(row=14, column=4, sticky=W)
		self.SOCPred = Label(self,text="SOC Pred")
		self.SOCPred.grid(row=13, column=6, sticky=W)
		self.LowPredPct = Label(self,text="Low Pred %")
		self.LowPredPct.grid(row=15, column=1, sticky=E)
		self.LowPct = Label(self,text="Low Percent")
		self.LowPct.grid(row=15, column=4, sticky=W)
		self.SurveyMean = Label(self,text="Survey Mean")
		self.SurveyMean.grid(row=14, column=6, sticky=W)
		self.Mil1Pct = Label(self,text="1 Mil Percent")
		self.Mil1Pct.grid(row=16, column=4, sticky=W)
		self.SurveyIncumbents = Label(self,text="Survey Incumbents")
		self.SurveyIncumbents.grid(row=15, column=6, sticky=W)
		self.B100Total = Label(self,text="Exec/100B Total")
		self.B100Total.grid(row=17, column=1, sticky=E)
		self.B10Total = Label(self,text="Exec/10B Total")
		self.B10Total.grid(row=18, column=1, sticky=E)
		self.B100Bonus = Label(self,text="100B Bonus")
		self.B100Bonus.grid(row=17, column=4, sticky=W)
		self.B10Bonus = Label(self,text="10B Bonus")
		self.B10Bonus.grid(row=18, column=4, sticky=W)
		self.MeanPred = Label(self,text="Mean Predicted")
		self.MeanPred.grid(row=16, column=6, sticky=W)
		self.Yr3Sal = Label(self, text="Year 3 Sal")
		self.Yr3Sal.grid(row=17, column=6, sticky=W)
		self.HighTotal = Label(self,text="High Total Comp")
		self.HighTotal.grid(row=19, column=1, sticky=E)
		self.HighBonus = Label(self,text="High Bonus")
		self.HighBonus.grid(row=19, column=4, sticky=W)
		self.MedTotal = Label(self,text="Med Total Comp")
		self.MedTotal.grid(row=20, column=1, sticky=E)
		self.MedBonus = Label(self,text="Med Bonus")
		self.MedBonus.grid(row=20, column=4, sticky=W)
		self.LowTotal = Label(self,text="Low Total Comp")
		self.LowTotal.grid(row=21, column=1, sticky=E)
		self.LowBonus = Label(self,text="Low Bonus")
		self.LowBonus.grid(row=21, column=4, sticky=W)
		self.Mil1Total = Label(self,text="Exec/1 Mil Total")
		self.Mil1Total.grid(row=22, column=1, sticky=E)
		self.Mil1Bonus = Label(self,text="1 Mil Bonus")
		self.Mil1Bonus.grid(row=22, column=4, sticky=W)
		self.StdErr = Label(self,text="Std Error")
		self.StdErr.grid(row=23, column=4, sticky=W)
		self.MedyrsPred = Label(self,text="Medyrs Pred")
		self.MedyrsPred.grid(row=24, column=1, sticky=E)
		self.Medyears = Label(self,text="Medyears")
		self.Medyears.grid(row=24, column=4, sticky=W)
		self.CanPred = Label(self,text="Pred Can")
		self.CanPred.grid(row=24, column=5)
		self.QCCheckCan = Label(self,text="QC Check Can")
		self.QCCheckCan.grid(row=25, column=6, sticky=W)
		self.USOverride = Label(self,text="US Override")
		self.USOverride.grid(row=26, column=1, sticky=E)
		self.CanMean = Label(self,text="Can Mean")
		self.CanMean.grid(row=26, column=3, sticky=E)
		self.CanPoly1 = Label(self,text="Can Poly 1")
		self.CanPoly1.grid(row=26, column=6, sticky=W)
		self.CanOverride = Label(self,text="Can Override")
		self.CanOverride.grid(row=27, column=1, sticky=E)
		self.CanQ1 = Label(self,text="Can Q1")
		self.CanQ1.grid(row=27, column=3, sticky=E)
		self.CanPoly2 = Label(self,text="Can Poly 2")
		self.CanPoly2.grid(row=27, column=6, sticky=W)
		self.CanPct = Label(self,text="Can Percent")
		self.CanPct.grid(row=28, column=3, sticky=E)
		self.CanPoly3 = Label(self,text="Can Poly 3")
		self.CanPoly3.grid(row=28, column=6, sticky=W)
		self.CanBonusPct = Label(self,text="Can Bonus %")
		self.CanBonusPct.grid(row=29, column=3, sticky=E)
		self.CanPolyMean = Label(self,text="Can Poly Mean")
		self.CanPolyMean.grid(row=29, column=6, sticky=W)
		self.CanTotal = Label(self,text="Can Total")
		self.CanTotal.grid(row=30, column=3, sticky=E)
		self.CanQCPoly = Label(self,text="Can QC/Poly Mean")
		self.CanQCPoly.grid(row=30, column=6, sticky=W)
		self.Repto = Label(self,text="Title    Repto    ERI")
		self.Repto.grid(row=32, column=1)
		self.ReptoSal = Label(self,text="Repto Salary")
		self.ReptoSal.grid(row=32, column=3, sticky=E)
		self.ReptoYr3 = Label(self,text="Repto Yr 3")
		self.ReptoYr3.grid(row=32, column=6, sticky=W)
		self.XRef = Label(self,text="Title    XRef     ERI")
		self.XRef.grid(row=33, column=1)
		self.XRefUSSal = Label(self,text="XRef US Sal")
		self.XRefUSSal.grid(row=33, column=3, sticky=E)
		self.XRefCanSal = Label(self,text="XRef Can Salary")
		self.XRefCanSal.grid(row=33, column=6, sticky=W)
		self.CPC = Label(self,text="Deg     CPC    CPC")
		self.CPC.grid(row=34, column=1)
		self.CPCSal = Label(self,text="CPC Salary")
		self.CPCSal.grid(row=34, column=3, sticky=E)
		self.Adder = Label(self,text="Adder")
		self.Adder.grid(row=34, column=6, sticky=W)
		self.Description = Label(self,text="Job Description")
		self.Description.grid(row=37, column=0, sticky=W)
		self.High10thPercentile_100BilLabel = Label(self, text="Initial Text", relief="groove", width=10)
		self.High10thPercentile_100BilLabel.grid(row=4, column=2)
		self.Sal100BilLabel = Label(self, text="Initial Text", relief="groove", width=10)
		self.Sal100BilLabel.grid(row=4, column=3)
		self.High90thPercentile_100BilLabel = Label(self, text="Initial Text", relief="groove", width=10)
		self.High90thPercentile_100BilLabel.grid(row=4, column=4)
		self.High90thPercentile_10BilLabel = Label(self, text="Initial Text", relief="groove", width=10)
		self.High90thPercentile_10BilLabel.grid(row=5, column=4)
		self.High10thPercentile_10BilLabel = Label(self, text="Initial Text", relief="groove", width=10)
		self.High10thPercentile_10BilLabel.grid(row=5, column=2)
		self.Sal10BilLabel = Label(self, text="Initial Text", relief="groove", width=10)
		self.Sal10BilLabel.grid(row=5, column=3)
		self.B100Q1Label = Label(self, text="[Initial Text]", relief="groove", width=10)
		self.B100Q1Label.grid(row=4, column=5)
		self.B10Q1Label = Label(self, text="[Initial Text]", relief="groove", width=10)
		self.B10Q1Label.grid(row=5, column=5)
		self.FrameR5C0 = Frame(self) #, height=5)
		self.FrameR5C0.grid(row=5, column=0, columnspan=1, rowspan=29, sticky=NW)
		self.RawDataTextbox = Text(self.FrameR5C0, height=29, width=90)
		self.RawDataTextbox.pack(side='left', fill='both', expand=True)
		self.RawDataScrollbar = Scrollbar(self.FrameR5C0)
		self.RawDataScrollbar.pack(side='right', fill='both', expand=True)
		self.RawDataTextbox.delete('1.0', END)
		self.RawDataTextbox.insert(END,self.data.rawstring)
		self.RawDataTextbox.config(state=DISABLED, yscrollcommand=self.RawDataScrollbar.set)
		self.RawDataScrollbar.config(command=self.RawDataTextbox.yview)
		self.High10thPercentileLabel = Label(self, text="Initial Text", relief="groove", width=10)
		self.High10thPercentileLabel.grid(row=6, column=2)
		self.HighSalLabel = Label(self, text="Initial Text", relief="groove", width=10)
		self.HighSalLabel.grid(row=6, column=3)
		self.High90thPercentileLabel = Label(self, text="Initial Text", relief="groove", width=10)
		self.High90thPercentileLabel.grid(row=6, column=4)
		self.HighQ1Label = Label(self, text="[Initial Text]", relief="groove", width=10)
		self.HighQ1Label.grid(row=6, column=5)
		self.Med10thPercentileLabel = Label(self, text="Initial Text", relief="groove", width=10)
		self.Med10thPercentileLabel.grid(row=7, column=2)
		self.MedSalLabel = Label(self, text="Initial Text", relief="groove", width=10)
		self.MedSalLabel.grid(row=7, column=3)
		self.Med90thPercentileLabel = Label(self, text="Initial Text", relief="groove", width=10)
		self.Med90thPercentileLabel.grid(row=7, column=4)
		self.MedQ1Label = Label(self, text="[Initial Text]", relief="groove", width=10)
		self.MedQ1Label.grid(row=7, column=5)
		self.Low10thPercentileLabel = Label(self, text="Initial Text", relief="groove", width=10)
		self.Low10thPercentileLabel.grid(row=8, column=2)
		self.LowSalLabel = Label(self, text="Initial Text", relief="groove", width=10)
		self.LowSalLabel.grid(row=8, column=3)
		self.Low90thPercentileLabel = Label(self, text="Initial Text", relief="groove", width=10)
		self.Low90thPercentileLabel.grid(row=8, column=4)
		self.LowQ1Label = Label(self, text="[Initial Text]", relief="groove", width=10)
		self.LowQ1Label.grid(row=8, column=5)
		self.Low10thPercentile_1MilLabel = Label(self, text="Initial Text", relief="groove", width=10)
		self.Low10thPercentile_1MilLabel.grid(row=9, column=2)
		self.Sal1MilLabel = Label(self, text="Initial Text", relief="groove", width=10)
		self.Sal1MilLabel.grid(row=9, column=3)
		self.Low90thPercentile_1MilLabel = Label(self, text="Initial Text", relief="groove", width=10)
		self.Low90thPercentile_1MilLabel.grid(row=9, column=4)
		self.Mil1Q1Label = Label(self, text="[Initial Text]", relief="groove", width=10)
		self.Mil1Q1Label.grid(row=9, column=5)
		self.HighPredPctLabel = Label(self, text="[Initial Text]", relief="groove", width=10)
		self.HighPredPctLabel.grid(row=13, column=2)
		self.QCCheckLabel = Label(self, text="[Initial Text]", relief="groove", width=10)
		self.QCCheckLabel.grid(row=12, column=5)
		self.SocPredLabel = Label(self, text="[Initial Text]", relief="groove", width=10)
		self.SocPredLabel.grid(row=13, column=5)
		self.LowPredPctLabel = Label(self, text="[Initial Text]", relief="groove", width=10)
		self.LowPredPctLabel.grid(row=15, column=2)
		self.SurveyMeanLabel = Label(self, text="[Initial Text]", relief="groove", width=10)
		self.SurveyMeanLabel.grid(row=14, column=5)
		self.SurveyIncumbentsLabel = Label(self, text="[Initial Text]", relief="groove", width=10)
		self.SurveyIncumbentsLabel.grid(row=15, column=5)
		self.B100TotalCompLabel = Label(self, text="[Initial Text]", relief="groove", width=10)
		self.B100TotalCompLabel.grid(row=17, column=2)
		self.B10TotalCompLabel = Label(self, text="[Initial Text]", relief="groove", width=10)
		self.B10TotalCompLabel.grid(row=18, column=2)
		self.MeanPredLabel = Label(self, text="[Initial Text]", relief="groove", width=10)
		self.MeanPredLabel.grid(row=16, column=5)
		self.Yr3SalLabel = Label(self, text="[Initial Text]", relief="groove", width=10)
		self.Yr3SalLabel.grid(row=17, column=5)
		self.HighTotalCompLabel = Label(self, text="[Initial Text]", relief="groove", width=10)
		self.HighTotalCompLabel.grid(row=19, column=2)
		self.MedTotalCompLabel = Label(self, text="[Initial Text]", relief="groove", width=10)
		self.MedTotalCompLabel.grid(row=20, column=2)
		self.LowTotalCompLabel = Label(self, text="[Initial Text]", relief="groove", width=10)
		self.LowTotalCompLabel.grid(row=21, column=2)
		self.Mil1TotalCompLabel = Label(self, text="[Initial Text]", relief="groove", width=10)
		self.Mil1TotalCompLabel.grid(row=22, column=2)
		self.EstimatedYearsLabel = Label(self, text="[Initial Text]", relief="groove", width=10)
		self.EstimatedYearsLabel.grid(row=24, column=2)
		self.QCCheckCanLabel = Label(self, text="[Initial Text]", relief="groove", width=10)
		self.QCCheckCanLabel.grid(row=25, column=5)
		self.CanMeanLabel = Label(self, text="[Initial Text]", relief="groove", width=10)
		self.CanMeanLabel.grid(row=26, column=4, sticky=W)
		self.CanPoly1Label = Label(self, text="[Initial Text]", relief="groove", width=10)
		self.CanPoly1Label.grid(row=26, column=5)
		self.CanQ1Label = Label(self, text="[Initial Text]", relief="groove", width=10)
		self.CanQ1Label.grid(row=27, column=4, sticky=W)
		self.CanPoly2Label = Label(self, text="[Initial Text]", relief="groove", width=10)
		self.CanPoly2Label.grid(row=27, column=5)
		self.CanPoly3Label = Label(self, text="[Initial Text]", relief="groove", width=10)
		self.CanPoly3Label.grid(row=28, column=5)
		self.CanPolyMeanLabel = Label(self, text="[Initial Text]", relief="groove", width=10)
		self.CanPolyMeanLabel.grid(row=29, column=5)
		self.CanTotalLabel = Label(self, text="[Initial Text]", relief="groove", width=10)
		self.CanTotalLabel.grid(row=30, column=4, sticky=W)
		self.CanPolyMeanQCLabel = Label(self, text="[Initial Text]", relief="groove", width=10)
		self.CanPolyMeanQCLabel.grid(row=30, column=5)
		self.ReptoTitleLabel = Label(self, text="[Initial Text]", relief="groove", width=45, anchor=E)
		self.ReptoTitleLabel.grid(row=32, column=0, sticky=E)
		self.ReptoSalLabel = Label(self, text="[Initial Text]", relief="groove", width=10)
		self.ReptoSalLabel.grid(row=32, column=4, sticky=W)
		self.ReptoYr3Label = Label(self, text="[Initial Text]", relief="groove", width=10)
		self.ReptoYr3Label.grid(row=32, column=5)
		self.XRefTitleLabel = Label(self, text="[Initial Text]", relief="groove", width=45, anchor=E)
		self.XRefTitleLabel.grid(row=33, column=0, sticky=E)
		self.XRefUSLabel = Label(self, text="[Initial Text]", relief="groove", width=10)
		self.XRefUSLabel.grid(row=33, column=4, sticky=W)
		self.XRefCanLabel = Label(self, text="[Initial Text]", relief="groove", width=10)
		self.XRefCanLabel.grid(row=33, column=5)
		self.DegreeNameLabel = Label(self, text="[Initial Text]", relief="groove", width=45, anchor=E)
		self.DegreeNameLabel.grid(row=34, column=0, sticky=E)
		self.CPCLabel = Label(self, text="[Initial Text]", relief="groove", width=10)
		self.CPCLabel.grid(row=34, column=2)
		self.CPCSalLabel = Label(self, text="[Initial Text]", relief="groove", width=10)
		self.CPCSalLabel.grid(row=34, column=4, sticky=W)
		self.AdderLabel = Label(self, text="[Initial Text]", relief="groove", width=10)
		self.AdderLabel.grid(row=34, column=5)
		self.JobDescriptionLabel = Label(self, text="[Initial Text]", relief="groove", wraplength=1000, width=169)
		self.JobDescriptionLabel.grid(row=38, column=0, columnspan=8, sticky=NW)
		## Real-time updates
		self.SOCEntry.bind('<Return>',self.update_Soc)
		self.JobIdSearchEntry.bind('<Return>',self.jobidsearch)
		self.JobIdSearchEntry.insert(0, "1")
		self.USOverrideEntry.bind('<Return>', self.update_MedSal)
		self.CanOverrideEntry.bind('<Return>', self.update_CanLabels)
		self.CanBonusPctEntry.bind('<Return>', self.update_CanValues)
		self.CanPercentEntry.bind('<Return>', self.update_CanValues)
		self.B100PctEntry.bind('<Return>', self.set_SalPercents)
		self.B10PctEntry.bind('<Return>', self.set_SalPercents)
		self.Mil1PctEntry.bind('<Return>', self.set_SalPercents)
		self.HighPctEntry.bind('<Return>', self.set_SalPercents)
		self.MedPctEntry.bind('<Return>', self.set_SalPercents)
		self.LowPctEntry.bind('<Return>', self.set_SalPercents)
		self.StdErrEntry.bind('<Return>', self.set_SalPercents)
		self.B100BonusPctEntry.bind('<Return>', self.set_SalPercents)
		self.B10BonusPctEntry.bind('<Return>', self.set_SalPercents)
		self.HighBonusPctEntry.bind('<Return>', self.set_SalPercents)
		self.MedBonusPctEntry.bind('<Return>', self.set_SalPercents)
		self.LowBonusPctEntry.bind('<Return>', self.set_SalPercents)
		self.Mil1BonusPctEntry.bind('<Return>', self.set_SalPercents)
		self.ReptoEntry.bind('<Return>', self.update_Repto)
		self.XRefEntry.bind('<Return>', self.update_XRef)
		self.MedYrsEntry.bind('<Return>', self.update_MedSal)
		self.BlankSpace = Label(self, text="    ")
		self.BlankSpace.grid(row=31, column=2)
		self.BlankSpace2 = Label(self, text="    ")
		self.BlankSpace2.grid(row=10, column=2)

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
		self.obsnumlabel.config(text=" ")
		self.JobDotLabel.config(text="    ")
		#self.ExecJobLabel.config(text="    ")
		#self.JobSocLabel.config(text="    ")
		self.HighPredPctLabel.config(text="    ")
		self.LowPredPctLabel.config(text="    ")
		self.B100TotalCompLabel.config(text="    ")
		self.B10TotalCompLabel.config(text="    ")
		self.HighTotalCompLabel.config(text="    ")
		self.MedTotalCompLabel.config(text="    ")
		self.LowTotalCompLabel.config(text="    ")
		self.Mil1TotalCompLabel.config(text="    ")
		self.EstimatedYearsLabel.config(text="    ")
		self.B100Q1Label.config(text="    ")
		self.B10Q1Label.config(text="    ")
		self.HighQ1Label.config(text="    ")
		self.MedQ1Label.config(text="    ")
		self.LowQ1Label.config(text="    ")
		self.Mil1Q1Label.config(text="    ")
		self.QCCheckLabel.config(text= "    ")
		self.SocPredLabel.config(text= "    ")
		self.SurveyMeanLabel.config(text= "    ")
		self.SurveyIncumbentsLabel.config(text= "    ")
		self.QCCheckCanLabel.config(text="    ")
		self.CanQ1Label.config(text="    ")
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
		self.CPCLabel.config(text="    ")
		self.CPCSalLabel.config(text="    ")
		self.AdderLabel.config(text="    ")
		#self.RawDataLabel.config(text="    ")
		self.JobDescriptionLabel.config(text="    ")
		#self.StdErrPredLabel.config(text="    ")
		self.SocOutputLabel.config(text="    ")
		## Entries
		self.RawDataTextbox.config(state=NORMAL)
		self.RawDataTextbox.delete('1.0', END)
		self.B100PctEntry.delete(0, END)
		self.B10PctEntry.delete(0, END)
		self.HighPctEntry.delete(0, END)
		self.MedPctEntry.delete(0, END)
		self.LowPctEntry.delete(0, END)
		self.Mil1PctEntry.delete(0, END)
		self.B100BonusPctEntry.delete(0, END)
		self.B10BonusPctEntry.delete(0, END)
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
		self.SOCEntry.delete(0,END)
		self.ReptoEntry.delete(0, END)
		self.XRefEntry.delete(0, END)
		## Calc Labels
		self.Sal100BilLabel.config(text="    ")
		self.Sal10BilLabel.config(text="    ")
		self.MedSalLabel.config(text="    ")
		self.HighSalLabel.config(text="    ")
		self.LowSalLabel.config(text="    ")
		self.Sal1MilLabel.config(text="    ")
		self.High90thPercentile_100BilLabel.config(text="    ")
		self.High90thPercentile_10BilLabel.config(text="    ")
		self.High90thPercentileLabel.config(text="    ")
		self.Med90thPercentileLabel.config(text="    ")
		self.Low90thPercentileLabel.config(text="    ")
		self.Low90thPercentile_1MilLabel.config(text="    ")
		self.High10thPercentile_100BilLabel.config(text="    ")
		self.High10thPercentile_10BilLabel.config(text="    ")
		self.High10thPercentileLabel.config(text="    ")
		self.Med10thPercentileLabel.config(text="    ")
		self.Low10thPercentileLabel.config(text="    ")
		self.Low10thPercentile_1MilLabel.config(text="    ")
		self.MeanPredLabel.config(text="    ")
		self.Yr3SalLabel.config(text="    ")

	def label_entry_reload(self, *event):
		self.obsnumlabel.config(text=str(self.data.current_index+1))
		self.B100PctEntry.delete(0, END)
		self.B10PctEntry.delete(0, END)
		self.HighPctEntry.delete(0, END)
		self.MedPctEntry.delete(0, END)
		self.LowPctEntry.delete(0, END)
		self.Mil1PctEntry.delete(0, END)
		self.B100BonusPctEntry.delete(0, END)
		self.B10BonusPctEntry.delete(0, END)
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
		self.SOCEntry.delete(0, END)
		self.ReptoEntry.delete(0, END)
		self.XRefEntry.delete(0, END)
		self.RawDataTextbox.delete('1.0', END)
		self.B100PctEntry.insert(0, str(self.data.B100PctDataInit))
		self.B10PctEntry.insert(0, str(self.data.B10PctDataInit))
		self.HighPctEntry.insert(0, str(self.data.HighPctDataInit))
		self.MedPctEntry.insert(0, str(self.data.MedPctDataInit))
		self.LowPctEntry.insert(0, str(self.data.LowPctDataInit))
		self.Mil1PctEntry.insert(0, str(self.data.Mil1PctDataInit))
		self.B100BonusPctEntry.insert(0, str(self.data.B100BonusPctDataInit))
		self.B10BonusPctEntry.insert(0, str(self.data.B10BonusPctDataInit))
		self.HighBonusPctEntry.insert(0, str(self.data.HighBonusPctDataInit))
		self.MedBonusPctEntry.insert(0, str(self.data.MedBonusPctDataInit))
		self.LowBonusPctEntry.insert(0, str(self.data.LowBonusPctDataInit))
		self.Mil1BonusPctEntry.insert(0, str(self.data.Mil1BonusPctDataInit))
		self.B100TotalCompLabel.config(text= self.data.B100TotalCompDataInit)
		self.B10TotalCompLabel.config(text= self.data.B10TotalCompDataInit)
		self.HighTotalCompLabel.config(text= self.data.HighTotalCompDataInit)
		self.MedTotalCompLabel.config(text= self.data.MedTotalCompDataInit)
		self.LowTotalCompLabel.config(text= self.data.LowTotalCompDataInit)
		self.Mil1TotalCompLabel.config(text= self.data.Mil1TotalCompDataInit)
		self.StdErrEntry.insert(0, str(self.data.StdErrDataInit))
		self.MedYrsEntry.insert(0, str(self.data.MedYrsDataInit))
		self.CanPercentEntry.insert(0, str(self.data.CanPercentDataInit))
		self.CanBonusPctEntry.insert(0, str(self.data.CanBonusPctDataInit))
		self.SOCEntry.insert(0, str(self.data.JobSocDataInit))
		self.ReptoEntry.insert(0, str(self.data.ReptoDataInit))
		self.XRefEntry.insert(0, str(self.data.XRefDataInit))
		self.USOverrideEntry.insert(0, str(self.data.USOverrideDataInit))
		self.CanOverrideEntry.insert(0, str(self.data.CANOverrideDataInit))
		self.RawDataTextbox.insert(END, self.data.rawstring)
		self.RawDataTextbox.config(state=DISABLED)
		self.MeanPredLabel.config(text=int(self.data.MeanPredData))
		self.Yr3SalLabel.config(text=int(self.data.Yr3Data))
		self.set_SalPercents()
		self.update_MedSal()
		self.update_CanLabels()
		self.update_Repto()
		self.update_XRef()
		self.update_Soc()

	def label_entry_initload(self, *event):
		self.label_entry_clear()
		self.jobentryreplace()
		## Labels
		self.obsnumlabel.config(text=str(self.data.current_index+1))
		self.JobTitleLabel.config(text= self.data.jobname)
		self.JobDotLabel.config(text= self.data.JobDotData)
		self.HighPredPctLabel.config(text= str(round(self.data.HighPredPctData, 2)))
		self.LowPredPctLabel.config(text= str(round(self.data.LowPredPctData, 2)))
		self.B100TotalCompLabel.config(text= self.data.B100TotalCompData)
		self.B10TotalCompLabel.config(text= self.data.B10TotalCompData)
		self.HighTotalCompLabel.config(text= self.data.HighTotalCompData)
		self.MedTotalCompLabel.config(text= self.data.MedTotalCompData)
		self.LowTotalCompLabel.config(text= self.data.LowTotalCompData)
		self.Mil1TotalCompLabel.config(text= self.data.Mil1TotalCompData)
		self.EstimatedYearsLabel.config(text= self.data.EstimatedYears)
		if self.data.jobexec==0: self.B100Q1Label.config(text="    ")
		else: self.B100Q1Label.config(text= int(self.data.B100Q1Data))
		if self.data.jobexec==0: self.B10Q1Label.config(text="    ")
		else: self.B10Q1Label.config(text= int(self.data.B10Q1Data))
		self.HighQ1Label.config(text= self.data.HighQ1Data)
		self.MedQ1Label.config(text= self.data.MedQ1Data)
		self.LowQ1Label.config(text= self.data.LowQ1Data)
		self.Mil1Q1Label.config(text= self.data.Mil1Q1Data)
		if self.data.jobexec==0: self.Mil1Q1Label.config(text="    ")
		else: self.Mil1Q1Label.config(text= int(self.data.Mil1Q1Data))
		self.QCCheckLabel.config(text= self.data.QCCheckData)
		self.SocPredLabel.config(text= self.data.SocPredData)
		self.SurveyMeanLabel.config(text= self.data.SurveyMeanData)
		self.SurveyIncumbentsLabel.config(text= self.data.SurveyIncumbentsData)
		self.QCCheckCanLabel.config(text= self.data.QCCheckCanData)
		self.CanQ1Label.config(text= int(self.data.CanQ1Data))
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
		self.CPCLabel.config(text=self.data.CPCData)
		self.CPCSalLabel.config(text= self.data.CPCSalData)
		self.AdderLabel.config(text= self.data.AdderData)
		self.JobDescriptionLabel.config(text= self.data.JobDescriptionData)
		self.SocOutputLabel.config(text=self.data.SocTitleData)
		## Entries
		self.RawDataTextbox.insert(END,self.data.rawstring)
		self.RawDataTextbox.config(state=DISABLED)
		self.B100PctEntry.insert(0, str(self.data.B100PctData))
		self.B10PctEntry.insert(0, str(self.data.B10PctData))
		self.HighPctEntry.insert(0, str(self.data.HighPctData))
		self.MedPctEntry.insert(0, str(self.data.MedPctData))
		self.LowPctEntry.insert(0, str(self.data.LowPctData))
		self.Mil1PctEntry.insert(0, str(self.data.Mil1PctData))
		self.B100BonusPctEntry.insert(0, str(self.data.B100BonusPctData))
		self.B10BonusPctEntry.insert(0, str(self.data.B10BonusPctData))
		self.HighBonusPctEntry.insert(0, str(self.data.HighBonusPctData))
		self.MedBonusPctEntry.insert(0, str(self.data.MedBonusPctData))
		self.LowBonusPctEntry.insert(0, str(self.data.LowBonusPctData))
		self.Mil1BonusPctEntry.insert(0, str(self.data.Mil1BonusPctData))
		self.StdErrEntry.insert(0, str(self.data.StdErrData))
		self.MedYrsEntry.insert(0, str(self.data.MedYrsData))
		self.CanPercentEntry.insert(0, str(self.data.CanPercentData))
		self.CanBonusPctEntry.insert(0, str(self.data.CanBonusPctData))
		self.SOCEntry.insert(0, str(self.data.JobSocData))
		self.ReptoEntry.insert(0, str(self.data.ReptoData))
		self.XRefEntry.insert(0, str(self.data.XRefData))
		self.USOverrideEntry.insert(0, str(self.data.USOverrideData))
		self.CanOverrideEntry.insert(0, str(self.data.CANOverrideData))
		## Calc Labels
		self.MeanPredLabel.config(text=int(self.data.MeanPredData))
		self.Yr3SalLabel.config(text=int(self.data.Yr3Data))
		self.set_SalPercents()
		self.update_MedSal()
		self.update_CanLabels()
		self.update_Repto()
		self.update_XRef()
		self.update_Soc()

	def update_Soc(self, *event):
		current_selector = int(self.SOCEntry.get())
		self.data.JobSocData = int(self.SOCEntry.get())
		try:
			self.data.SocTitleData = self.data.socdf.loc[current_selector,'SocTitle']
		except KeyError:
			self.data.SocTitleData = 'NA'
		self.SocOutputLabel.config(text=self.data.SocTitleData)

	def send_entry(self):
		self.data.B100PctData = float(self.B100PctEntry.get())
		self.data.B10PctData = float(self.B10PctEntry.get())
		self.data.HighPctData = float(self.HighPctEntry.get())
		self.data.MedPctData = float(self.MedPctEntry.get())
		self.data.LowPctData = float(self.LowPctEntry.get())
		self.data.Mil1PctData = float(self.Mil1PctEntry.get())
		self.data.B100BonusPctData = float(self.B100BonusPctEntry.get())
		self.data.B10BonusPctData = float(self.B10BonusPctEntry.get())
		self.data.HighBonusPctData = float(self.HighBonusPctEntry.get())
		self.data.MedBonusPctData = float(self.MedBonusPctEntry.get())
		self.data.LowBonusPctData = float(self.LowBonusPctEntry.get())
		self.data.Mil1BonusPctData = float(self.Mil1BonusPctEntry.get())

	#def update_MedYrs(self, *event):
	#	self.data.MedYrsData = int(self.MedYrsEntry.get())

	def update_Repto(self, *event):
		current_selector = int(self.ReptoEntry.get())
		self.data.ReptoData = int(self.ReptoEntry.get())
		try:
			self.data.jobsdf.set_index('indexsearch', inplace=True)
			self.data.jobsdf['indexsearch'] = self.data.jobsdf['erijobid']
		except: pass
		try:
			self.data.ReptoTitleData = self.data.jobsdf.loc[current_selector,'jobdottitle']
			self.data.ReptoSalData = self.data.jobsdf.loc[current_selector,'MEDSAL']
			self.data.ReptoYr3Data = self.data.jobsdf.loc[current_selector,'Yr3Sal']
		except KeyError:
			self.data.ReptoTitleData = 0
			self.data.ReptoSalData = 0
			self.data.ReptoYr3Data = 0
		self.ReptoTitleLabel.config(text= self.data.ReptoTitleData)
		self.ReptoSalLabel.config(text= self.data.ReptoSalData)
		self.ReptoYr3Label.config(text= self.data.ReptoYr3Data)

	def update_XRef(self, *event):
		current_selector = int(self.XRefEntry.get())
		self.data.XRefData = int(self.XRefEntry.get())
		try:
			self.data.jobsdf.set_index('indexsearch', inplace=True)
			self.data.jobsdf['indexsearch'] = self.data.jobsdf['erijobid']
		except: pass
		try:
			self.data.XRefTitleData = self.data.jobsdf.loc[current_selector,'jobdottitle']
			self.data.XRefUSData = self.data.jobsdf.loc[current_selector,'MEDSAL']
			self.data.XRefCanData = self.data.jobsdf.loc[current_selector,'CAN_AVE']
		except KeyError:
			self.data.XRefTitleData = 0
			self.data.XRefData = 0
			self.data.XRefCanData = 0
		self.XRefTitleLabel.config(text= self.data.XRefTitleData)
		self.XRefUSLabel.config(text= self.data.XRefUSData)
		self.XRefCanLabel.config(text= self.data.XRefCanData)
		self.update_MedSal()
	
	def set_SalPercents(self, *event):
		self.send_entry()
		try: self.data.B100PctData = float(self.B100PctEntry.get())
		except ValueError: print("B100err")
		try: self.data.B10PctData = float(self.B10PctEntry.get())
		except ValueError: print("B10err")
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
		self.data.B100BonusPctData = float(self.B100BonusPctEntry.get())
		self.data.B10BonusPctData = float(self.B10BonusPctEntry.get())
		self.data.HighBonusPctData = float(self.HighBonusPctEntry.get())
		self.data.MedBonusPctData = float(self.MedBonusPctEntry.get())
		self.data.LowBonusPctData = float(self.LowBonusPctEntry.get())
		self.data.Mil1BonusPctData = float(self.Mil1BonusPctEntry.get())
		self.update_MedSal()
	
	def update_MedSal(self, *event):
		try:
			if float(self.USOverrideEntry.get())!=0:
				self.data.update_MedSalCalcData(float(self.USOverrideEntry.get()))
				self.data.MedPctData = round(float(self.data.MedSalData)/float(self.data.XRefUSData),2)
			else:
				self.data.MedSalData = int(self.data.MedPctData*self.data.XRefUSData)
				#self.data.MedSalData = 1
				#self.data.MedPctData = self.data.MedPctDataInit
		except ValueError: print("MedSal Value error")
		self.data.USOverrideData = float(self.USOverrideEntry.get())
		self.data.MedYrsData = int(self.MedYrsEntry.get())
		self.MedPctEntry.delete(0,END)
		self.MedPctEntry.insert(0, str(self.data.MedPctData))
		self.data.set_CalcData()
		self.update_CalcLabels()
	
	def update_CanLabels(self, *event):
		try: 
			if float(self.CanOverrideEntry.get())==0: 
				self.data.CanAveData = self.data.CanPercentData * self.data.XRefCanData
			else: 
				self.data.update_canavedata(float(self.CanOverrideEntry.get()))
				self.data.CanPercentData = round(float(self.data.CanAveData)/float(self.data.XRefCanData),2)
				self.CanPercentEntry.delete(0,END)
				self.CanPercentEntry.insert(0,str(self.data.CanPercentData))
		except ValueError: print("CanSal Value error")
		self.data.CANOverrideData = float(self.CanOverrideEntry.get())
		self.CanMeanLabel.config(text= int(self.data.CanAveData))
		self.CanTotalLabel.config(text= int(self.data.CanAveData+(self.data.CanAveData * self.data.CanBonusPctData)))

	def update_CalcLabels(self, *event):
		## 10th Percentile
		if self.data.jobexec==0: self.High10thPercentile_100BilLabel.config(text="    ")
		else: self.High10thPercentile_100BilLabel.config(text= int(self.data.High10thPercentile_100BilData))
		if self.data.jobexec==0: self.High10thPercentile_10BilLabel.config(text="    ")
		else: self.High10thPercentile_10BilLabel.config(text= int(self.data.High10thPercentile_10BilData))
		self.High10thPercentileLabel.config(text= int(self.data.High10thPercentileData))
		self.Med10thPercentileLabel.config(text= int(self.data.Med10thPercentileData))
		self.Low10thPercentileLabel.config(text= int(self.data.Low10thPercentileData))
		if self.data.jobexec==0: self.Low10thPercentile_1MilLabel.config(text="    ")
		else: self.Low10thPercentile_1MilLabel.config(text= int(self.data.Low10thPercentile_1MilData))
		## Mean
		if self.data.jobexec==0: self.Sal100BilLabel.config(text="    ")
		else: self.Sal100BilLabel.config(text= int(self.data.Sal100BilData))
		if self.data.jobexec==0: self.Sal10BilLabel.config(text="    ")
		else: self.Sal10BilLabel.config(text= int(self.data.Sal10BilData))
		self.HighSalLabel.config(text= int(self.data.HighSalData))
		self.MedSalLabel.config(text= int(self.data.MedSalData))
		self.LowSalLabel.config(text= int(self.data.LowSalData))
		if self.data.jobexec==0: self.Sal1MilLabel.config(text="    ")
		else: self.Sal1MilLabel.config(text= int(self.data.Sal1MilData))
		## 90th Percentile
		if self.data.jobexec==0: self.High90thPercentile_100BilLabel.config(text="    ")
		else: self.High90thPercentile_100BilLabel.config(text= int(self.data.High90thPercentile_100BilData))
		if self.data.jobexec==0: self.High90thPercentile_10BilLabel.config(text="    ")
		else: self.High90thPercentile_10BilLabel.config(text= int(self.data.High90thPercentile_10BilData))
		self.High90thPercentileLabel.config(text= int(self.data.High90thPercentileData))
		self.Med90thPercentileLabel.config(text= int(self.data.Med90thPercentileData))
		self.Low90thPercentileLabel.config(text= int(self.data.Low90thPercentileData))
		if self.data.jobexec==0: self.Low90thPercentile_1MilLabel.config(text="    ")
		else: self.Low90thPercentile_1MilLabel.config(text= int(self.data.Low90thPercentile_1MilData))
		## Total Comp
		self.B100TotalCompLabel.config(text= self.data.B100TotalCompData)
		self.B10TotalCompLabel.config(text= self.data.B10TotalCompData)
		self.HighTotalCompLabel.config(text= self.data.HighTotalCompData)
		self.MedTotalCompLabel.config(text= self.data.MedTotalCompData)
		self.LowTotalCompLabel.config(text= self.data.LowTotalCompData)
		self.Mil1TotalCompLabel.config(text= self.data.Mil1TotalCompData)
		## Yr3
		self.data.Yr3Data = (self.data.LowSalData + (2*((self.data.MedSalData - self.data.LowSalData)/(self.data.MedYrsData - 1))))
		self.Yr3SalLabel.config(text= int(self.data.Yr3Data))
		##CanPoly1
		x = self.data.MedSalData / 1000 #used over all canpolys
		c_mean1 = (1.428197939) + (sqrt(x) * (0.026290736)) + (x * 1.211187086) + (x * x * ( -0.002949176 )) + (x * x * x * ( 0.000005412 ))
		self.data.CanPoly1Data = int(c_mean1*1000)
		self.CanPoly1Label.config(text= int(self.data.CanPoly1Data))
		##CanPoly2
		c_mean2 = (-23.05331731) + (sqrt(x) * (12.52969784)) + (x * (-0.53745324)) + (x * x * (0.00564765)) + (x * x * x * (-0.00001242))
		self.data.CanPoly2Data = int(c_mean2*1000)
		self.CanPoly2Label.config(text= int(self.data.CanPoly2Data))
		##CanPoly3
		c_mean3 = (-14.97877804) + (sqrt(x) * (7.28561872)) + (x * (0.17477767)) + (x * x * (0.00247309)) + (x * x * x * (-0.00000328))
		self.data.CanPoly3Data = int(c_mean3*1000)
		self.CanPoly3Label.config(text= int(self.data.CanPoly3Data))
		##CanPolyMean
		self.data.CanPolyMeanData = int((self.data.CanPoly1Data+self.data.CanPoly2Data+self.data.CanPoly3Data)/3)
		self.CanPolyMeanLabel.config(text= int(self.data.CanPolyMeanData))
		##CanPolyQCMean
		self.data.CanPolyMeanQCData = int((self.data.CanPoly1Data+self.data.CanPoly2Data+self.data.CanPoly3Data+self.data.QCCheckCanData)/4)
		self.CanPolyMeanQCLabel.config(text= int(self.data.CanPolyMeanQCData))
		
		

	def update_CanValues(self, *event):
		try: self.data.CanPercentData = float(self.CanPercentEntry.get())
		except ValueError: self.data.CanPercentData = self.data.CanPercentData
		try: self.data.CanBonusPctData = float(self.CanBonusPctEntry.get())
		except ValueError: self.data.CanBonusPctData = self.data.CanBonusPctData
		self.update_CanLabels()

	def write_output(self, *event):
		self.send_entry()
		self.data.write_to_outputdf()

	def write_sql(self, *event):
		self.data.write_to_sql()


root = Tk()
root.geometry("1255x865")
Application(root)
root.mainloop()





