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
			left join assessorwork.sa.bench bench on bench.erijobid=pct.erijobid and bench.releaseid=pct.releaseid order by execjob desc, pct.erijobid"""
		self.jobsdf = pd.DataFrame(psql.read_sql(self.sql, self.pyocnxn))
		self.jobsdf['indexmaster'] = self.jobsdf.index
		self.jobsdf['index1'] = self.jobsdf['indexmaster']
		self.jobsdf['indexsearch'] = self.jobsdf['erijobid']
		self.last_index = self.jobsdf.last_valid_index()
		self.outputdf = pd.DataFrame(columns=self.jobsdf.columns)
		self.outputdf['timestamp']=""
		print(self.jobsdf)
		print(self.outputdf)
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
			return self.jobname
		except KeyError:
			return "No job found"

	def index_next(self ,*event):
		try:
			self.jobsdf.set_index('index1', inplace=True)
			self.jobsdf['index1'] = self.jobsdf['indexmaster']
		except:
			pass
		if self.current_index < self.last_index: self.current_index = self.current_index + 1
		else: self.current_index = 0
		self.current_id = self.jobsdf.loc[self.current_index,'erijobid']
		jobname = self.jobsdf.loc[self.current_index,'jobdottitle']
		self.jobexec = self.jobsdf.loc[self.current_index,'execjob']
		return jobname

	def index_prior(self, *event):
		try:
			self.jobsdf.set_index('index1', inplace=True)
			self.jobsdf['index1'] = self.jobsdf['indexmaster']
		except:
			pass
		if self.current_index > 0: self.current_index = self.current_index - 1
		else: self.current_index = self.last_index
		jobname = self.jobsdf.loc[self.current_index,'jobdottitle']
		self.current_id = self.jobsdf.loc[self.current_index,'erijobid']
		self.jobexec = self.jobsdf.loc[self.current_index,'execjob']
		return jobname
	
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
		self.master.title("Data Audit Window")
		self.create_widgets()
		self.bind_all('<Next>', self.nextpage)
		self.bind_all('<Prior>', self.priorpage)
		self.bind_all('<Insert>', self.write_output)
		self.bind_all('<Control-p>', self.write_sql)

	def create_widgets(self):
		self.pack(fill=BOTH, expand=1)
		self.data = Dataverse()
		#self.jid = StringVar()
		self.JobIdLabel = Label(self,text="JobId")
		self.JobIdLabel.grid(row=0,column=0)
		self.jobidentry = Entry(self, width=15)
		self.jobidentry.grid(row=0, column=1)
		self.jobidentry.bind('<Return>',self.jobidsearch)
		self.jobfound = Label(self)
		self.blank = Label(self,text=" ")
		self.execjoblabel = Label(self)
		self.execjoblabel.grid(row=2, column=1)
		self.invalidsearchwarning = Label(self,text="Invalid search",foreground="Red")
		self.LowSalEntry = Entry(self, width=15)
		self.LowSalEntry.grid(row=6,column=2)
		self.LowSalEntry.bind('<Return>',self.SetLowSal)
		self.LowSalLabel = Label(self, text="LowSal")
		self.LowSalLabel.grid(row=6,column=1)
		self.Sal1MilEntry = Entry(self, width=15)
		self.Sal1MilEntry.grid(row=7,column=1)
		self.Sal1MilEntry.bind('<Return>',self.Set1Mil)

	def nextpage(self, event):
		self.clear_Overwrite_Entries()
		jobtext = self.data.index_next()
		print(jobtext)
		self.foundit(jobtext)
		self.exec_job()
		self.jobentryreplace()

	def priorpage(self, event):
		self.clear_Overwrite_Entries()
		jobtext = self.data.index_prior()
		print(jobtext)
		self.foundit(jobtext)
		self.exec_job()
		self.jobentryreplace()

	def jobentryreplace(self):
		self.jobidentry.delete(0, END)
		self.jobidentry.insert(0, str(self.data.current_id))

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

	def clear_Overwrite_Entries(self, *event):
		self.Sal1MilEntry.delete(0, END)
		self.LowSalEntry.delete(0, END)

	def jobidsearch(self, event):
		self.clear_Overwrite_Entries()
		try:
			self.intjobidentry = int(self.jobidentry.get())
			jobtext = self.data.find_by_erijobid(self.intjobidentry)
			self.exec_job()
			self.invalidsearchwarning.grid_forget()
			print(jobtext)
			self.jobfound.config(text=jobtext)
			if jobtext=="No job found": 
				self.jobfound.config(foreground="Red")
				self.execjoblabel.grid_forget()
			else: self.jobfound.config(foreground="Black")
			self.jobfound.grid(row=1, column=1)
		except ValueError:
			self.jobfound.grid_forget()
			self.execjoblabel.grid_forget()
			print("Not a valid search entry.")
			self.invalidsearchwarning.grid(row=1, column=1)

	def Set1Mil(self, event):
		#print(str(self.Sal1Mil.get()))
		#Update output DF Sal1Mil == self.Sal1Mil.get()
		if self.Sal1MilEntry.get() != "": self.data.set_Sal1Mil(int(self.Sal1MilEntry.get()))

	def SetLowSal(self, event):
		if self.LowSalEntry.get() != "": self.data.set_LowSal(int(self.LowSalEntry.get()))

	def write_output(self, event):
		self.data.write_to_outputdf()

	def write_sql(self, event):
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