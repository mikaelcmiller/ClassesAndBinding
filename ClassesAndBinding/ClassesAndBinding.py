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
		print("DF Initialized")

	def inititalizedataframe(self):
		self.pyocnxn = pyodbc.connect("DRIVER={SQL Server};SERVER=SNADSSQ3;DATABASE=assessorwork;trusted_connection=yes;")
		self.sql = """SELECT pct.*
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
			self.current_index = self.jobsdf.index.get_loc(idsearch)
			self.current_id = idsearch
			
			#Need to check if exists in outputdf, if so: pull from output df instead of jobsdf
			if self.jobsdf.loc[self.current_id,'Sal1Mil']==None: self.Sal1Mil=""
			else: self.Sal1Mil = self.jobsdf.loc[self.current_id,'Sal1Mil']
			if self.jobsdf.loc[self.current_id,'LOWSAL']==None: self.LowSal=""
			else: self.LowSal = self.jobsdf.loc[self.current_id,'LOWSAL']
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
		if self.jobsdf.loc[self.current_index,'Sal1Mil']==None: self.Sal1Mil=""
		else: self.Sal1Mil = self.jobsdf.loc[self.current_index,'Sal1Mil']
		if self.jobsdf.loc[self.current_index,'LOWSAL']==None: self.LowSal=""
		else: self.LowSal = self.jobsdf.loc[self.current_index,'LOWSAL']
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
		if self.jobsdf.loc[self.current_index,'Sal1Mil']==None: self.Sal1Mil=""
		else: self.Sal1Mil = self.jobsdf.loc[self.current_index,'Sal1Mil']
		if self.jobsdf.loc[self.current_index,'LOWSAL']==None: self.LowSal=""
		else: self.LowSal = self.jobsdf.loc[self.current_index,'LOWSAL']
		#return jobname

	def set_Sal1Mil(self, entry, *event):
		# Ensure a row for current_id exists to update Sal1Mil value
		self.write_to_outputdf()
		# Set Sal1Mil to entry (entry is set by user)
		self.outputdf.at[self.current_id,'Sal1Mil'] = entry
		print(self.outputdf.loc[self.current_id,'erijobid':'Sal1Mil'])

	def set_LowSal(self, entry, *event):
		self.write_to_outputdf()
		self.outputdf.at[self.current_id,'LOWSAL'] = entry
		print(str(self.outputdf.loc[self.current_id,'erijobid'])+" || "+str(self.outputdf.loc[self.current_id,'LOWSAL']))

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
		self.JobIdLabel.grid(row=0,column=0)
		self.jobidsearchentry = Entry(self, width=15)
		self.jobidsearchentry.grid(row=0, column=1)
		self.jobidsearchentry.bind('<Return>',self.jobidsearch)
		self.jobfound = Label(self)
		self.blank = Label(self,text=" ")
		self.execjoblabel = Label(self)
		self.execjoblabel.grid(row=2, column=1)
		self.invalidsearchwarning = Label(self,text="Invalid search",foreground="Red")
		self.LowSalLabel = Label(self, text="LowSal")
		self.LowSalLabel.grid(row=6,column=1)
		self.LowSalEntry = Entry(self, width=15)
		self.LowSalEntry.grid(row=6,column=2)
		self.LowSalEntry.bind('<Return>',self.write_output)
		self.AutoUpdateLabel = Label(self, text="Auto-update label", relief="groove")
		self.AutoUpdateLabel.grid(row=6, column=3)
		self.Sal1MilLabel = Label(self,text="Sal1Mil")
		self.Sal1MilLabel.grid(row=7,column=1)
		self.Sal1MilEntry = Entry(self, width=15)
		self.Sal1MilEntry.grid(row=7,column=2)
		self.Sal1MilEntry.bind('<Return>',self.write_output)
		self.ReloadBtn = Button(self, text="Reload data",command=self.load_Entries)
		self.ReloadBtn.grid(row=0,column=7)
		self.ReloadBtn.bind('<Return>', self.load_Entries)
		self.CommitBtn = Button(self,text="Save Changes",command=self.write_output)
		self.CommitBtn.grid(row=0,column=8)
		self.WriteSQLButton = Button(self, text="Send Changes to SQL",command=self.write_sql)
		self.WriteSQLButton.grid(row=0,column=9)
		
###########################
		
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
		self.TitleEri = Label(self,text="Title           ERI")
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
		
###########################

## Navigation
	def nextpage(self, event):
		self.clear_Entries()
		self.data.index_next()
		jobtext = self.data.jobname
		print(jobtext)
		self.foundit(jobtext)
		self.exec_job()
		self.jobentryreplace()
		self.load_Entries()

	def priorpage(self, event):
		self.clear_Entries()
		self.data.index_prior()
		jobtext = self.data.jobname
		print(jobtext)
		self.foundit(jobtext)
		self.exec_job()
		self.jobentryreplace()
		self.load_Entries()

	def jobidsearch(self, event):
		self.clear_Entries()
		try:
			self.intjobidsearchentry = int(self.jobidsearchentry.get())
			self.data.find_by_erijobid(self.intjobidsearchentry)
			jobtext = self.data.jobname
			self.exec_job()
			self.invalidsearchwarning.grid_forget()
			print(jobtext)
			self.jobfound.config(text=jobtext)
			if jobtext=="No job found": 
				self.jobfound.config(foreground="Red")
				self.execjoblabel.grid_forget()
				self.clear_Entries()
			else:
				self.jobfound.config(foreground="Black")
				self.load_Entries()
			self.jobfound.grid(row=1, column=1)
		except ValueError:
			self.jobfound.grid_forget()
			self.execjoblabel.grid_forget()
			print("Not a valid search entry.")
			self.invalidsearchwarning.grid(row=1, column=1)
			self.clear_Entries()

	def jobentryreplace(self):
		self.jobidsearchentry.delete(0, END)
		self.jobidsearchentry.insert(0, str(self.data.current_id))

	def foundit(self, entry):
		self.jobfound.config(text=entry, foreground="Black")
		self.jobfound.grid(row=1, column=1)
		self.invalidsearchwarning.grid_forget()

	def exec_job(self):
		self.execjoblabel.grid(row=2, column=1)
		if self.data.jobexec == 1:
			self.execjoblabel.config(text="Executive Job")
		else: 
			self.execjoblabel.config(text="Non-Executive Job")

	def clear_Entries(self, *event):
		self.Sal1MilEntry.delete(0, END)
		self.LowSalEntry.delete(0, END)
	
	def load_Entries(self, *event):
		self.clear_Entries()
		self.Sal1MilEntry.insert(0, str(self.data.Sal1Mil))
		self.LowSalEntry.insert(0, str(self.data.LowSal))

	def write_output(self, *event):
		#If any changes are made, these will update those; else, these will input what was there before
		if self.Sal1MilEntry.get() != "": self.data.set_Sal1Mil(int(self.Sal1MilEntry.get()))
		if self.LowSalEntry.get() != "": self.data.set_LowSal(int(self.LowSalEntry.get()))
		self.data.write_to_outputdf()

	def write_sql(self, *event):
		self.data.write_to_sql()


root = Tk()
root.geometry("1000x750")
app = Application(root)
root.mainloop()


########################################################
#### STACK OVERFLOW QUESTION EXAMPLE
## https://stackoverflow.com/questions/45945883/python-3-pandas-set-index-in-tkinter-application

#import pandas as pd
#from tkinter import *


#class CustomerData:
#	def __init__(self):
#		self.initializedataframe()

#	def initializedataframe(self):
#		col = ['CustomerId','CustomerName']
#		self.data = pd.DataFrame([[1,'Pat'],[2,'Kris'],[4,'Sam'],[5,'Ryan'],[6,'Alex']], columns=col) # Placeholder data
#		print(self.data)
#		print('-------------\n')

#	def findcustomerbyid(self, input):
#		cxid = int(input)
#		try:
#			self.data.set_index('CustomerId', inplace=True) # Trouble spot, can't set_index more than one time with same column
#		except KeyError:
#			pass
#		cx_out = self.data.loc[input,'CustomerName']
#		print(cx_out)
#		return(cx_out)


#class App(Frame):
#	def __init__(self, master):
#		"""Initialize the Frame"""
#		Frame.__init__(self, master)
#		self.master = master
#		self.create_widgets()

#	def create_widgets(self):
#		self.pack(fill=BOTH, expand=1)
#		self.data = CustomerData()
		
#		self.cxsearch = Entry(self, width=15)
#		self.cxsearch.place(x=5,y=5)
#		self.cxsearch.bind('<Return>',self.findcx)

#	def findcx(self, event):
#		intcxsearch = int(self.cxsearch.get())
#		self.data.findcustomerbyid(intcxsearch)


#root = Tk()
#root.geometry("400x300")
#app = App(root)
#root.mainloop()