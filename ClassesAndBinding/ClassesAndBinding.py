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
		self.set_datavariables_index()
		print("DF Initialized")

	def inititalizedataframe(self):
		self.pyocnxn = pyodbc.connect("DRIVER={SQL Server};SERVER=SNADSSQ3;DATABASE=assessorwork;trusted_connection=yes;")
		self.sql = """SELECT pct.*, round((cast(LowPred as float)/MedPred), 2) as LowPredCalc, round(cast(HighPred as float)/MedPred, 2) as HighPredCalc
			, bench.USBenchMed
			, bench.CanBenchMed
			, case when (pct.medyrs>40 and pct.medyrs<99) then 1 else 0 end as execjob 
			FROM assessorwork.sa.pct pct 
			left join assessorwork.sa.bench bench on bench.erijobid=pct.erijobid and bench.releaseid=pct.releaseid
			order by execjob desc, pct.erijobid"""
		self.jobsdf = pd.DataFrame(psql.read_sql(self.sql, self.pyocnxn))
		self.jobsdf['indexmaster'] = self.jobsdf.index
		self.jobsdf['index1'] = self.jobsdf['indexmaster']
		self.jobsdf['indexsearch'] = self.jobsdf['erijobid']
		self.last_index = self.jobsdf.last_valid_index()
		self.outputdf = pd.DataFrame(columns=self.jobsdf.columns)
		self.outputdf['timestamp']=""
		print(self.jobsdf[['indexmaster','indexsearch']])
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
			except:
				pass
			self.jobname = self.jobsdf.loc[idsearch,'jobdottitle']
			self.jobexec = self.jobsdf.loc[idsearch,'execjob']
			self.current_id = idsearch
			self.current_index = self.jobsdf.loc[self.current_id,'index1'] #self.jobsdf.index.get_loc(idsearch)
			self.set_datavariables_id()
			#Need to check if exists in outputdf, if so: pull from output df instead of jobsdf
			#return self.jobname
		except KeyError:
			self.jobname = "No job found"

	def index_next(self ,*event):
		try:
			self.jobsdf.set_index('index1', inplace=True)
			self.jobsdf['index1'] = self.jobsdf['indexmaster']
		except:
			pass
		if self.current_index < self.last_index: self.current_index = self.current_index + 1
		else: self.current_index = 0
		self.current_id = self.jobsdf.loc[self.current_index,'erijobid']
		self.jobname = self.jobsdf.loc[self.current_index,'jobdottitle']
		self.jobexec = self.jobsdf.loc[self.current_index,'execjob']
		self.set_datavariables_index()
		#return jobname

	def index_prior(self, *event):
		try:
			self.jobsdf.set_index('index1', inplace=True)
			self.jobsdf['index1'] = self.jobsdf['indexmaster']
		except:
			pass
		if self.current_index > 0: self.current_index = self.current_index - 1
		else: self.current_index = self.last_index
		self.jobname = self.jobsdf.loc[self.current_index,'jobdottitle']
		self.current_id = self.jobsdf.loc[self.current_index,'erijobid']
		self.jobexec = self.jobsdf.loc[self.current_index,'execjob']
		self.set_datavariables_index()
		#return jobname

	def set_datavariables_index(self, *event):
		self.JobTitleData = self.jobsdf.loc[self.current_index,'jobdottitle']
		self.ERIJobIdData = self.jobsdf.loc[self.current_index,'erijobid']
		self.JobDotData = self.jobsdf.loc[self.current_index,'jobdot']
		self.HighPredPctData = self.jobsdf.loc[self.current_index,'HighPredCalc']
		self.LowPredPctData = self.jobsdf.loc[self.current_index,'LowPredCalc']
		print(  str(self.JobTitleData)+" | "+str(self.ERIJobIdData)+" | "+str(self.JobDotData)+" | "+str(self.HighPredPctData)  )

	def set_datavariables_id(self, *event):
		self.JobTitleData = self.jobsdf.loc[self.current_id,'jobdottitle']
		self.ERIJobIdData = self.jobsdf.loc[self.current_id,'erijobid']
		self.JobDotData = self.jobsdf.loc[self.current_id,'jobdot']
		self.HighPredPctData = self.jobsdf.loc[self.current_id,'HighPredCalc']
		self.LowPredPctData = self.jobsdf.loc[self.current_id,'LowPredCalc']
		print(  str(self.JobTitleData)+" | "+str(self.ERIJobIdData)+" | "+str(self.JobDotData)+" | "+str(self.HighPredPctData)  )

	def write_to_outputdf(self, *event):
		print("writing data to OutputDF")
		try:
			self.jobsdf.set_index('indexsearch', inplace=True)
			self.jobsdf['indexsearch'] = self.jobsdf['erijobid']
		except:
			pass
		if (self.outputdf['erijobid']==self.current_id).any():
			print("Overwriting "+str(self.current_id))
			self.outputdf.update(self.jobsdf.loc[self.current_id,:])
		else: self.outputdf = self.outputdf.append(self.jobsdf.loc[self.current_id,:])
		self.outputdf.set_value(self.current_id,'timestamp',datetime.datetime.now())
		print(self.outputdf)

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
		self.labels_reload()
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
		self.JobIdLabel = Label(self,text="JobId")
		#self.JobIdLabel.grid(row=0,column=0)
		#self.JobIdSearchEntry = Entry(self, width=15)
		#self.JobIdSearchEntry.grid(row=0, column=1)
		#self.JobIdSearchEntry.bind('<Return>',self.jobidsearch)
		self.JobTitleLabel = Label(self)
		#self.blank = Label(self,text=" ")
		#self.execjoblabel = Label(self)
		#self.execjoblabel.grid(row=2, column=1)
		self.invalidsearchwarning = Label(self,text="Invalid search",foreground="Red")
		
###########################
#### Created from Google Sheet 
		self.ReloadBtn = Button(self, text="Reload Data Btn")
		self.ReloadBtn.grid(row=0, column=5)
		self.CommitBtn = Button(self, text="Commit Changes Btn")
		self.CommitBtn.grid(row=0, column=6)
		self.WriteSQLBtn = Button(self, text="Write to SQL Btn")
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
		self.TitleEri = Label(self,text="Title           Exec")
		self.TitleEri.grid(row=2, column=1)
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
		self.B100.grid(row=4, column=1)
		self.B100Q1 = Label(self,text="Q1 100 bil/Exec")
		self.B100Q1.grid(row=4, column=7)
		self.High = Label(self,text="High Year/1 Bil")
		self.High.grid(row=5, column=1)
		self.HighQ1 = Label(self,text="Q1 Highsal")
		self.HighQ1.grid(row=5, column=7)
		self.Med = Label(self,text="Med Year/100 Mil")
		self.Med.grid(row=6, column=1)
		self.MedQ1 = Label(self,text="Q1 Medsal")
		self.MedQ1.grid(row=6, column=7)
		self.Low = Label(self,text="Low Year/10 Mil")
		self.Low.grid(row=7, column=1)
		self.LowQ1 = Label(self,text="Q1 Lowsal")
		self.LowQ1.grid(row=7, column=7)
		self.Mil1 = Label(self,text="Exec/1 Mil")
		self.Mil1.grid(row=8, column=1)
		self.Mil1Q1 = Label(self,text="Q1 1 Mil/Exec")
		self.Mil1Q1.grid(row=8, column=7)
		self.B100Pct = Label(self,text="Exec/100 Bil Percent")
		self.B100Pct.grid(row=10, column=4)
		self.PredUS = Label(self,text="Predicted US Values")
		self.PredUS.grid(row=10, column=6)
		self.HighPredPct = Label(self,text="High Pred %")
		self.HighPredPct.grid(row=11, column=1)
		self.HighPct = Label(self,text="High Percent")
		self.HighPct.grid(row=11, column=4)
		self.QCCheck = Label(self,text="QC Check")
		self.QCCheck.grid(row=11, column=7)
		self.MedPct = Label(self,text="Med Percent")
		self.MedPct.grid(row=12, column=4)
		self.SOCPred = Label(self,text="SOC Pred")
		self.SOCPred.grid(row=12, column=7)
		self.LowPredPct = Label(self,text="Low Pred %")
		self.LowPredPct.grid(row=13, column=1)
		self.LowPct = Label(self,text="Low Percent")
		self.LowPct.grid(row=13, column=4)
		self.SurveyMean = Label(self,text="Survey Mean")
		self.SurveyMean.grid(row=13, column=7)
		self.Mil1Pct = Label(self,text="Exec/1 Mil Percent")
		self.Mil1Pct.grid(row=14, column=4)
		self.SurveyIncumbents = Label(self,text="Survey Incumbents")
		self.SurveyIncumbents.grid(row=14, column=7)
		self.B100Total = Label(self,text="Exec/100 Bil Total")
		self.B100Total.grid(row=15, column=1)
		self.B100Bonus = Label(self,text="Exec/100 Bil Bonus")
		self.B100Bonus.grid(row=15, column=4)
		self.MeanPred = Label(self,text="Mean Predicted")
		self.MeanPred.grid(row=15, column=7)
		self.HighTotal = Label(self,text="High Total Comp")
		self.HighTotal.grid(row=16, column=1)
		self.HighBonus = Label(self,text="High Bonus")
		self.HighBonus.grid(row=16, column=4)
		self.MedTotal = Label(self,text="Med Total Comp")
		self.MedTotal.grid(row=17, column=1)
		self.MedBonus = Label(self,text="Med Bonus")
		self.MedBonus.grid(row=17, column=4)
		self.LowTotal = Label(self,text="Low Total Comp")
		self.LowTotal.grid(row=18, column=1)
		self.LowBonus = Label(self,text="Low Bonus")
		self.LowBonus.grid(row=18, column=4)
		self.Mil1Total = Label(self,text="Exec/1 Mil Total")
		self.Mil1Total.grid(row=19, column=1)
		self.Mil1Bonus = Label(self,text="Exec/1 Mil Bonus")
		self.Mil1Bonus.grid(row=19, column=4)
		self.StdErrPred = Label(self,text="Std Error Pred")
		self.StdErrPred.grid(row=20, column=1)
		self.StdErr = Label(self,text="Standard Error")
		self.StdErr.grid(row=20, column=4)
		self.MedyrsPred = Label(self,text="Medyrs Pred")
		self.MedyrsPred.grid(row=21, column=1)
		self.Medyears = Label(self,text="Medyears")
		self.Medyears.grid(row=21, column=4)
		self.CanPred = Label(self,text="Predicted Canada Values")
		self.CanPred.grid(row=21, column=6)
		self.QCCheckCan = Label(self,text="QC Check Can")
		self.QCCheckCan.grid(row=22, column=7)
		self.USOverride = Label(self,text="US Override")
		self.USOverride.grid(row=23, column=1)
		self.CanMean = Label(self,text="Can Mean")
		self.CanMean.grid(row=23, column=3)
		self.CanPoly1 = Label(self,text="Can Poly 1")
		self.CanPoly1.grid(row=23, column=7)
		self.CanOverride = Label(self,text="Can Override")
		self.CanOverride.grid(row=24, column=1)
		self.CanQ1 = Label(self,text="Can Q1")
		self.CanQ1.grid(row=24, column=3)
		self.CanPoly2 = Label(self,text="Can Poly 2")
		self.CanPoly2.grid(row=24, column=7)
		self.CanPct = Label(self,text="Can Percent")
		self.CanPct.grid(row=25, column=3)
		self.CanPoly3 = Label(self,text="Can Poly 3")
		self.CanPoly3.grid(row=25, column=7)
		self.CanBonusPct = Label(self,text="Can Bonus %")
		self.CanBonusPct.grid(row=26, column=3)
		self.CanPolyMean = Label(self,text="Can Poly Mean")
		self.CanPolyMean.grid(row=26, column=7)
		self.CanTotal = Label(self,text="Can Total")
		self.CanTotal.grid(row=27, column=3)
		self.CanQCPoly = Label(self,text="Can QC/Poly Mean")
		self.CanQCPoly.grid(row=27, column=7)
		self.Repto = Label(self,text="Title    Repto   ERI")
		self.Repto.grid(row=29, column=1)
		self.ReptoSal = Label(self,text="Repto Salary")
		self.ReptoSal.grid(row=29, column=3)
		self.ReptoYr3 = Label(self,text="Repto Yr 3")
		self.ReptoYr3.grid(row=29, column=7)
		self.Xref = Label(self,text="Title    XRef    ERI")
		self.Xref.grid(row=30, column=1)
		self.XrefUSSal = Label(self,text="Xref US Salary")
		self.XrefUSSal.grid(row=30, column=3)
		self.XrefCanSal = Label(self,text="Xref Can Salary")
		self.XrefCanSal.grid(row=30, column=7)
		self.CPC = Label(self,text="Deg    CPC     CPC")
		self.CPC.grid(row=31, column=1)
		self.CPCSal = Label(self,text="CPC Salary")
		self.CPCSal.grid(row=31, column=3)
		self.Adder = Label(self,text="Adder")
		self.Adder.grid(row=31, column=7)
		self.Description = Label(self,text="Job Description")
		self.Description.grid(row=32, column=0)
		self.JobTitleLabel = Label(self, text="[Initial Text]", relief="groove", width=45)
		self.JobTitleLabel.grid(row=2, column=0)
		self.ExecJobLabel = Label(self, text="[Initial Text]", relief="groove")
		self.ExecJobLabel.grid(row=2, column=2)
		self.JobDotLabel = Label(self, text="[Initial Text]", relief="groove")
		self.JobDotLabel.grid(row=2, column=4)
		self.JobSocLabel = Label(self, text="[Initial Text]", relief="groove")
		self.JobSocLabel.grid(row=2, column=6)
		self.SocOutputLabel = Label(self, text="[Initial Text]", relief="groove")
		self.SocOutputLabel.grid(row=2, column=7)
		self.Pct10B100Label = Label(self, text="[Initial Text]", relief="groove")
		self.Pct10B100Label.grid(row=4, column=2)
		self.MeanB100Label = Label(self, text="[Initial Text]", relief="groove")
		self.MeanB100Label.grid(row=4, column=3)
		self.Pct90B100Label = Label(self, text="[Initial Text]", relief="groove")
		self.Pct90B100Label.grid(row=4, column=4)
		self.B100Q1Label = Label(self, text="[Initial Text]", relief="groove")
		self.B100Q1Label.grid(row=4, column=6)
		self.RawDataLabel = Label(self, text="""[Initial 



					Text]""", relief="groove", width=50)
		self.RawDataLabel.grid(row=5, column=0, rowspan=21, sticky="N")
		self.Pct10HighB1Label = Label(self, text="[Initial Text]", relief="groove")
		self.Pct10HighB1Label.grid(row=5, column=2)
		self.MeanHigh1BLabel = Label(self, text="[Initial Text]", relief="groove")
		self.MeanHigh1BLabel.grid(row=5, column=3)
		self.Pct90High1BLabel = Label(self, text="[Initial Text]", relief="groove")
		self.Pct90High1BLabel.grid(row=5, column=4)
		self.HighQ1Label = Label(self, text="[Initial Text]", relief="groove")
		self.HighQ1Label.grid(row=5, column=6)
		self.PctMil10edMil100Label = Label(self, text="[Initial Text]", relief="groove")
		self.PctMil10edMil100Label.grid(row=6, column=2)
		self.MeanMedMil100Label = Label(self, text="[Initial Text]", relief="groove")
		self.MeanMedMil100Label.grid(row=6, column=3)
		self.Pct90MedMil100Label = Label(self, text="[Initial Text]", relief="groove")
		self.Pct90MedMil100Label.grid(row=6, column=4)
		self.MedQ1Label = Label(self, text="[Initial Text]", relief="groove")
		self.MedQ1Label.grid(row=6, column=6)
		self.Pct10LowMil10Label = Label(self, text="[Initial Text]", relief="groove")
		self.Pct10LowMil10Label.grid(row=7, column=2)
		self.MeanLowMil10Label = Label(self, text="[Initial Text]", relief="groove")
		self.MeanLowMil10Label.grid(row=7, column=3)
		self.Pct90LowMil10Label = Label(self, text="[Initial Text]", relief="groove")
		self.Pct90LowMil10Label.grid(row=7, column=4)
		self.LowQ1Label = Label(self, text="[Initial Text]", relief="groove")
		self.LowQ1Label.grid(row=7, column=6)
		self.PctMil10il1Label = Label(self, text="[Initial Text]", relief="groove")
		self.PctMil10il1Label.grid(row=8, column=2)
		self.MeanMil1Label = Label(self, text="[Initial Text]", relief="groove")
		self.MeanMil1Label.grid(row=8, column=3)
		self.Pct90Mil1Label = Label(self, text="[Initial Text]", relief="groove")
		self.Pct90Mil1Label.grid(row=8, column=4)
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
		self.ReptoLabel = Label(self, text="[Initial Text]", relief="groove")
		self.ReptoLabel.grid(row=29, column=0, sticky="E")
		self.ReptoSalLabel = Label(self, text="[Initial Text]", relief="groove")
		self.ReptoSalLabel.grid(row=29, column=4)
		self.ReptoYr3Label = Label(self, text="[Initial Text]", relief="groove")
		self.ReptoYr3Label.grid(row=29, column=6)
		self.XRefLabel = Label(self, text="[Initial Text]", relief="groove")
		self.XRefLabel.grid(row=30, column=0)
		self.XrefUSLabel = Label(self, text="[Initial Text]", relief="groove")
		self.XrefUSLabel.grid(row=30, column=4)
		self.XRefCanLabel = Label(self, text="[Initial Text]", relief="groove")
		self.XRefCanLabel.grid(row=30, column=6)
		self.DegreeNameLabel = Label(self, text="[Initial Text]", relief="groove")
		self.DegreeNameLabel.grid(row=31, column=0)
		self.CPCSalLabel = Label(self, text="[Initial Text]", relief="groove")
		self.CPCSalLabel.grid(row=31, column=4)
		self.AdderLabel = Label(self, text="[Initial Text]", relief="groove")
		self.AdderLabel.grid(row=31, column=6)
		self.JobDescriptionLabel = Label(self, text="[Initial Text]", relief="groove")
		self.JobDescriptionLabel.grid(row=33, column=0)
		####
		###########################
		self.JobIdSearchEntry.bind('<Return>',self.jobidsearch)
		self.JobIdSearchEntry.insert(0, "1")

## Navigation
	def nextpage(self, event):
		self.JobTitleLabel.config(foreground="Black")
		self.clear_Entries()
		self.data.index_next()
		self.labels_reload()
		self.jobentryreplace()
		#jobtext = self.data.jobname
		#print(jobtext)
		#self.foundit(jobtext)
		#self.exec_job()
		#self.load_Entries()

	def priorpage(self, event):
		self.JobTitleLabel.config(foreground="Black")
		self.clear_Entries()
		self.data.index_prior()
		self.labels_reload()
		self.jobentryreplace()
		#jobtext = self.data.jobname
		#print(jobtext)
		#self.foundit(jobtext)
		#self.exec_job()
		#self.load_Entries()

	def jobidsearch(self, event):
		self.labels_clear()
		#self.clear_Entries()
		try:
			self.intJobIdSearchEntry = int(self.JobIdSearchEntry.get())
			print(str(self.JobIdSearchEntry.get()))
			self.data.find_by_erijobid(self.intJobIdSearchEntry)
			#jobtext = self.data.jobname
			#self.exec_job()
			self.invalidsearchwarning.grid_forget()
			self.labels_reload()
			if self.data.jobname=="No job found":
				self.JobTitleLabel.config(foreground="Red")
				self.labels_clear()
			else:
				self.JobTitleLabel.config(foreground="Black")
				#self.load_Entries()
			#self.JobTitleLabel.grid(row=2, column=0)
		except ValueError:
			#self.JobTitleLabel.grid_forget()
			#self.execjoblabel.grid_forget()
			#print("Not a valid search entry.")
			#self.invalidsearchwarning.grid(row=2, column=0)
			#self.clear_Entries()
			self.JobTitleLabel.config(foreground="Red")
			self.JobTitleLabel.config(text="Not a valid search entry")
			self.labels_clear()

### Text Editing
	def jobentryreplace(self):
		self.JobIdSearchEntry.delete(0, END)
		self.JobIdSearchEntry.insert(0, str(self.data.current_id))

	def foundit(self, entry):
		self.JobTitleLabel.config(text=entry, foreground="Black")
		self.JobTitleLabel.grid(row=2, column=0)
		self.invalidsearchwarning.grid_forget()

	#def exec_job(self):
		#self.ExecJobLabel.grid(row=2, column=1)
		#if self.data.jobexec == 1:
			#self.ExecJobLabel.config(text="Executive Job")
		#else: 
			#self.ExecJobLabel.config(text="Non-Executive Job")

	def clear_Entries(self, *event):
		pass

	def load_Entries(self, *event):
		pass

	def labels_clear(self, *event):
		self.JobDotLabel.config(text="    ")
		self.ExecJobLabel.config(text="    ")
		self.HighPredPctLabel.config(text="    ")
		self.LowPredPctLabel.config(text="    ")

	def labels_reload(self, *event):
		if self.data.jobexec==1 : self.ExecJobLabel.config(text="Exec")
		else: self.ExecJobLabel.config(text="Non-Exec")
		self.JobTitleLabel.config(text= self.data.jobname)
		self.JobDotLabel.config(text= self.data.JobDotData)
		self.HighPredPctLabel.config(text= self.data.HighPredPctData)
		self.LowPredPctLabel.config(text= self.data.LowPredPctData)

	def write_output(self, *event):
		#If any changes are made, these will update those; else, these will input what was there before
		self.data.write_to_outputdf()

	def write_sql(self, *event):
		self.data.write_to_sql()


root = Tk()
root.geometry("1100x750")
app = Application(root)
root.mainloop()





