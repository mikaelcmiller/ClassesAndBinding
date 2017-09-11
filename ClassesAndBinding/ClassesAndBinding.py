### DATA AUDIT WORK

import pandas as pd
import numpy as np
import pandas.io.sql as psql
import pyodbc
from tkinter import *
from tkinter.ttk import *


class Datatraverse:
	def __init__(self):
		self.inititalizedataframe()
		self.current_index = 0
		self.current_id = 0
		print("DF Initialized")

	def inititalizedataframe(self):
		self.pyocnxn = pyodbc.connect("DRIVER={SQL Server};SERVER=SNADSSQ3;DATABASE=assessorwork;trusted_connection=yes;")
		self.sql = """SELECT erijobid,jobdot,jobdottitle FROM sa.fname WHERE jobsource = 'E' and jobactive not in (0,3,5,7,9)"""
		self.jobsdf = pd.DataFrame(psql.read_sql(self.sql, self.pyocnxn))
		print(self.jobsdf)
		print("Dataframe loaded from SQL")
		self.last_index = self.jobsdf.last_valid_index()

	def find_by_erijobid(self, entry):
		idsearch = int(entry)
		try:
			try:
				self.jobsdf.set_index('erijobid', inplace=True)
			except:
				pass
			jobname = self.jobsdf.loc[idsearch,'jobdottitle']
			self.current_index = self.jobsdf.index.get_loc(idsearch)
			return jobname
		except KeyError:
			return "No job found"

	def index_next(self ,*event):
		try:
			self.jobsdf.reset_index(inplace=True)
		except:
			pass
		if self.current_index < self.last_index: self.current_index = self.current_index + 1
		else: self.current_index = 0
		self.current_id = self.jobsdf.loc[self.current_index,'erijobid']
		jobname = self.jobsdf.loc[self.current_index,'jobdottitle']
		return jobname

	def index_prior(self, *event):
		try:
			self.jobsdf.reset_index(inplace=True)
		except:
			pass
		if self.current_index > 0: self.current_index = self.current_index - 1
		else: self.current_index = self.last_index
		jobname = self.jobsdf.loc[self.current_index,'jobdottitle']
		self.current_id = self.jobsdf.loc[self.current_index,'erijobid']
		return jobname


class Application(Frame):
	def __init__(self, master):
		"""Initialize the Frame"""
		Frame.__init__(self, master)
		self.master = master
		self.master.title("Data Audit Window")
		self.create_widgets()
		self.bind_all('<Next>', self.nextpage)
		self.bind_all('<Prior>', self.priorpage)

	def create_widgets(self):
		self.pack(fill=BOTH, expand=1)
		self.data = Datatraverse()
		#self.jid = StringVar()
		self.jobidentry = Entry(self, width=15)
		self.jobidentry.place(x=5,y=5)
		self.jobidentry.bind('<Return>',self.jobidsearch)
		self.jobfound = Label(self)
		self.invalidsearchwarning = Label(self,text="Invalid search",foreground="Red")

	def nextpage(self, event):
		jobtext = self.data.index_next()
		print(jobtext)
		self.foundit(jobtext)
		self.jobentryreplace()

	def priorpage(self, event):
		jobtext = self.data.index_prior()
		print(jobtext)
		self.foundit(jobtext)
		self.jobentryreplace()

	def jobentryreplace(self):
		self.jobidentry.delete(0, END)
		self.jobidentry.insert(0, str(self.data.current_id))

	def foundit(self, entry):
		self.jobfound.config(text=entry, foreground="Black")
		self.jobfound.place(x=5, y=26)
		self.invalidsearchwarning.place_forget()

	def jobidsearch(self, event):
		try:
			self.intjobidentry = int(self.jobidentry.get())
			jobtext = self.data.find_by_erijobid(self.intjobidentry)
			self.invalidsearchwarning.place_forget()
			print(jobtext)
			self.jobfound.config(text=jobtext)
			if jobtext=="No job found": self.jobfound.config(foreground="Red")
			else: self.jobfound.config(foreground="Black")
			self.jobfound.place(x=5, y=26)
		except ValueError:
			self.jobfound.place_forget()
			print("Not a valid search entry.")
			self.invalidsearchwarning.place(x=5,y=26)

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