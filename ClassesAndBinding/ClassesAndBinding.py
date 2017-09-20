### DATA AUDIT WORK

import pandas as pd
import numpy as np
import pandas.io.sql as psql
import pyodbc
import sqlalchemy
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
		self.sql = """SELECT f.erijobid, f.jobdot, f.jobdottitle, j.execjob FROM assessorwork.sa.fname f join (select erijobid, case when (yearsmediansalaryexperience>40 and yearsmediansalaryexperience<99) then 1 else 0 end as execjob from assessorwork.sa.job) j on j.erijobid=f.erijobid WHERE f.jobsource = 'E' and f.jobactive not in (0,3,5,7,9) order by execjob desc, erijobid"""
		self.jobsdf = pd.DataFrame(psql.read_sql(self.sql, self.pyocnxn))
		self.jobsdf['indexmaster'] = self.jobsdf.index
		self.jobsdf['index1'] = self.jobsdf['indexmaster']
		self.jobsdf['indexsearch'] = self.jobsdf['erijobid']
		self.outputdf = pd.DataFrame(columns=self.jobsdf.columns)
		print(self.jobsdf)
		print(self.outputdf)
		print("Dataframe loaded from SQL")
		self.last_index = self.jobsdf.last_valid_index()

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

	def write_to_sql(self, *event):
		print("writing data to sql")
		try:
			self.jobsdf.set_index('indexsearch', inplace=True)
			self.jobsdf['indexsearch'] = self.jobsdf['erijobid']
		except:
			pass
		self.outputdf = self.outputdf.append(self.jobsdf.loc[self.current_id,:])
		print((self.outputdf['erijobid']==self.current_id).any())
		#print(self.outputdf)
		#jobid = int(self.jobsdf.loc[self.current_id,'erijobid'])
		#jobtitle = str(self.jobsdf.loc[self.current_id,'jobdottitle'])
		#servconnect = pyodbc.connect("DRIVER={SQL Server};SERVER=SNADSSQ3;DATABASE=assessorwork;trusted_connection=yes;")
		#cur = servconnect.cursor()
		## Might consider an update statement or temporary dataframe to store new values
		## Will compare all new/old values before writing to SQL, row by row?
		#cur.execute('''INSERT INTO dbo.AuditTest(erijobid, title) VALUES (?,?)''',jobid,jobtitle)
		#cur.commit()
		#cur.close()


class Application(Frame):
	def __init__(self, master):
		"""Initialize the Frame"""
		Frame.__init__(self, master)
		self.master = master
		self.master.title("Data Audit Window")
		self.create_widgets()
		self.bind_all('<Next>', self.nextpage)
		self.bind_all('<Prior>', self.priorpage)
		self.bind_all('<Insert>', self.write_sql)

	def create_widgets(self):
		self.pack(fill=BOTH, expand=1)
		self.data = Dataverse()
		#self.jid = StringVar()
		self.jobidentry = Entry(self, width=15)
		self.jobidentry.grid(row=0, column=0)
		self.jobidentry.bind('<Return>',self.jobidsearch)
		self.jobfound = Label(self)
		self.execjoblabel = Label(self)
		self.execjoblabel.grid(row=2, column=0)
		self.invalidsearchwarning = Label(self,text="Invalid search",foreground="Red")

	def nextpage(self, event):
		jobtext = self.data.index_next()
		print(jobtext)
		self.foundit(jobtext)
		self.exec_job()
		self.jobentryreplace()

	def priorpage(self, event):
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
		self.jobfound.grid(row=1, column=0)
		self.invalidsearchwarning.grid_forget()

	def exec_job(self):
		self.execjoblabel.grid(row=2, column=0)
		if self.data.jobexec == 1:
			self.execjoblabel.config(text="Executive Job")
		else: 
			self.execjoblabel.config(text="Non-Executive Job")

	def jobidsearch(self, event):
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
			self.jobfound.grid(row=1, column=0)
		except ValueError:
			self.jobfound.grid_forget()
			self.execjoblabel.grid_forget()
			print("Not a valid search entry.")
			self.invalidsearchwarning.grid(row=1, column=0)

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