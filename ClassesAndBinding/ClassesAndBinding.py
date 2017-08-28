


########################################################
### AUDIT BAREBONE STRUCTURE

import pandas as pd
import numpy as np
import pandas.io.sql as psql
import pyodbc
from tkinter import *
from tkinter.ttk import *

##Testing Github mikael_test branch

class Datatraverse:
	def __init__(self):
		self.inititalizedataframe()
	
	def inititalizedataframe(self):
		self.pyocnxn = pyodbc.connect("DRIVER={SQL Server};""SERVER=SNADSSQ3;DATABASE=assessorwork;""trusted_connection=yes;")
		self.sql = """SELECT erijobid,jobdot,jobdottitle FROM sa.fname WHERE jobsource = 'E' and jobactive not in (0,3,5,7,9)"""
		self.jobsdf = psql.read_sql(self.sql, self.pyocnxn)
		print(self.jobsdf)
		print("Dataframe loaded from SQL")

	def find_by_erijobid(self, entry):
		idsearch = int(entry)
		#print("Set_Index to erijobid | Search index==erijobid | Return if found, else error message")
		try:
			self.jobsdf.set_index('erijobid', inplace=True, drop=True)
		except:
			pass
		jobname = self.jobsdf.loc[idsearch,'jobdottitle']
		print(jobname)

	def index_next(self):
		print("Reset_index | Index = index+1 | If last_available_index, index=0")

	def index_last(self):
		print("Reset_index | Index = index-1 | If index==0, index=last_available_index")


class Application(Frame):
	def __init__(self, master):
		"""Initialize the Frame"""
		Frame.__init__(self, master)
		self.master = master
		self.master.title("Data Audit Window")
		self.create_widgets()
		#self.bind_all('<Return>', self.entercommand) #Only needs to be bound to the erijobid input
		self.bind_all('<Next>', self.nextpage)
		self.bind_all('<Prior>', self.priorpage)
		#self.bind_all('<Control-f>',self.findfunction)
		self.bind_all('<Control-F>',self.findfunction)

	
	def create_widgets(self):
		self.pack(fill=BOTH, expand=1)
		
		self.data = Datatraverse()
		
		testButton = Button(self,text="Print Command", command=self.user_command)
		testButton.place(x=50,y=200)
	#	testButton.bind('<Return>',self.buttonentercommand)
		
		self.jobidentry = Entry(self, width=15)
		self.jobidentry.place(x=5,y=5)
		self.jobidentry.bind('<Return>',self.jobidsearch)
		

	def user_command(self):
		print("User clicked Button")

	#def entercommand(self, event): # need two positional arguments (both self and event) to operate correctly.
	#	#print("User hit 'Enter' key")
	#	#print(event.keysym)
	#	self.navigation(event.keysym)

	def nextpage(self, event):
		print("User hit 'Page Down' key")
		print(event.keysym)
		self.navigation(event.keysym)

	def priorpage(self, event):
		print("User hit 'Page Up' key")
		print(event.keysym)
		self.navigation(event.keysym)

	def navigation(self, x):
		print (":::RUNNAV:::")
		if x=='Next':
			#print("Change index to original index | Obs# + 1 | Return row for review")
			self.data.index_next()
		if x=='Prior':
			#print("Change index to original index | Obs# - 1 | Return row for review")
			self.data.index_last()
		if x=='F':
			print("Why would the user hit Ctrl+Shift+f? That's strange..")

	def findfunction(self, event):
		#print(event.keysym)
		self.navigation(event.keysym)

	def jobidsearch(self, event):
		try:
			self.intjobidentry = int(self.jobidentry.get())
			print("User wishes to search for erijobid: %d " % self.intjobidentry)
			self.data.find_by_erijobid(self.intjobidentry)
		except ValueError:
			print("Not a valid search entry.")
			# Place a hidden error message that appears below entry box for this

root = Tk()
root.geometry("400x300")
app = Application(root)
root.mainloop()



########################################################
### Multi-Function Class Examples, Cross-Class Function Connections, Inheritance Examples
#class classwithtwofunctions():
#	def function1(self):
#		print("this is classwithtwofunctions' function1")
#	def function2(self):
#		print("this is classwithtwofunctions' f2")

#class secondclass():
#	def f111(self):
#		test = classwithtwofunctions
#		test.function1(test)
#		print("end of f111()")
#	def f112(self):
#		self.f111(self)
#		print("f112 mid")
#		t2 = classwithtwofunctions
#		t2.function2(t2)
#		print("f112 end")
#	def f113(self, input):
#		print("This is the function input: {0}".format(input))

#class inherited(secondclass, classwithtwofunctions):
#	def function1(self):
#		print("New function 1 in place")

#b = secondclass
#b.f111(b)
#b.f112(b)
#b.f113(b,13)

#c = classwithtwofunctions
#c.function1(c)
#c.function2(c)
#c.function2(c.function2(c))

#d = inherited
#d.function1(d)
#d.f112(d)



########################################################
### TheNewBoston youtube tutorial 35 (Word Frequency Counter): https://www.youtube.com/watch?v=ZxiJ92-4Qys

#import requests
#from bs4 import BeautifulSoup
#import operator

#def start(url):
#	wordlist = []
#	source_code = requests.get(url).text
#	soup = BeautifulSoup(source_code,'lxml')
#	for post_text in soup.find_all('a',{"class":"title text-semibold"}):
#		content = post_text.string
#		words = content.lower().split()
#		for each_word in words:
#			#print(each_word)
#			wordlist.append(each_word)
#	clean_up_list(wordlist)

#def clean_up_list(wordlist):
#	clean_word_list = [] # List to store cleaned words
#	for word in wordlist:
#		symbols = "~!@#$%^&*()-_+=[]{}\|;:',./?<>\""
#		for i in range(0,len(symbols)):
#			word = word.replace(symbols[i], "")
#		if len(word) > 0 :
#			#print(word)
#			clean_word_list.append(word)
#	create_dictionary(clean_word_list)

#def create_dictionary(clean_word_list):
#	word_count = {}
#	for word in clean_word_list:
#		if word in word_count:
#			word_count[word] += 1
#		else:
#			word_count[word] = 1
#	for key, value in sorted(word_count.items(), key=operator.itemgetter(1)):
#		print(key, value)

#start('https://thenewboston.com/forum/')


########################################################
### TheNewBoston youtube tutorial 33 (Multiple Inheritance): https://www.youtube.com/watch?v=YCEVvs5BhpY

#class Mario():
#	def move(self):
#		print("I am moving!")
#class Shroom():
#	def eat_shroom(self):
#		print("Now I am big!")

#class BigMario(Mario,Shroom):
#	## Bigmario inherits all functions from Mario and Shroom
#	pass

#bm = BigMario()
#bm.move()
#bm.eat_shroom()


########################################################
### TheNewBoston youtube tutorial 32 (Inheritance): https://www.youtube.com/watch?v=oROcVrgz91Y

#class Parent():
#	def print_last_name(self):
#		print("Roberts")

#class Child(Parent): # Name of class you want to inherit from in parentheses
#	def print_first_name(self):
#		print("Bucky")
#	#def print_last_name(self): # Overwriting parent function
#	#	print("Schnitzelberg")

#b1 = Child()
#b1.print_first_name()
#b1.print_last_name() ## Inherited function print_last_name() from Parent class


########################################################
### TheNewBoston youtube tutorial 31 (Class vs Instance Variables): https://www.youtube.com/watch?v=qSDiHI1kP98

#class Girl:
#	gender = "female" # Class variable: anytime an object is created from this class, this is the variable that object will have by default (ie gender = 'female' for class=Girl)
#	def __init__(self, name):
#		self.name = name

#r = Girl("Rachel")
#s = Girl("Sophia")
#print(r.name)
#print(r.gender)
#print(s.name)
#print(s.gender)


########################################################
### TheNewBoston youtube tutorial 30 (Init): https://www.youtube.com/watch?v=G8kS24CtfoI

### Concept __init__
##class Tuna:
##	def __init__(self):
##		print("Blrrbleblurblur")
##	def swim(self):
##		print("I am swimming.")

##flipper = Tuna()
##flipper.swim()

#class Enemy:
#	def __init__(self, x):
#		self.energy = x
#	def get_energy(self):
#		print(self.energy)

#enemy1 = Enemy(5)
#enemy2 = Enemy(18)

#enemy1.get_energy()
#enemy2.get_energy()

########################################################
#### TheNewBoston youtube tutorial 29 (Classes and Objects): https://www.youtube.com/watch?v=POQIIKb1BZA

#class Enemy: # Tend to capitalize class names to differentiate from variables or functions
#	life = 3
#	def attack(self):
#		print("ouch!")
#		self.life -= 1
#	def checkLife(self):
#		if self.life <= 0:
#			print("I am dead")
#		else:
#			print(str(self.life) + " life left")

#enemy1 = Enemy()
#enemy2 = Enemy()

#enemy1.checkLife
#enemy1.attack()
#enemy1.attack()
#enemy1.checkLife()
#enemy2.checkLife()



########################################################
##### TheMonkeyLords youtube tutorial 21 (Inheritance): https://www.youtube.com/watch?v=QFNaBiHob50
#class Person():
#	def __init__(self, name, age):
#		self.name = name
#		self.age = age
#	def __str__(self): # Displays in print(Object)
#		print("Person -- ")
#		return "My name is {0}. I am {1} years old.".format(self.name,self.age)

#class Military(Person):
#	def __init__(self, name, age, rank):
#		Person.__init__(self, name, age)
#		self.rank = rank
#	def __str__(self): # Overrides Person __str__
#		print("Miliary -- ")
#		return Person.__str__(self) + " I am a {0}".format(self.rank)

#class Teacher(Person):
#	def __init__(self, name, age, subject):
#		Person.__init__(self, name, age)
#		self.subject = subject
#	def __str__(self): # Overrides Person __str__
#		print("Teacher -- ")
#		return "My name is {0}. I am {1} years old. I teach {2}.".format(self.name, self.age, self.subject)

#class Student(Person):
#	def __init__(self, name, age, loans):
#		Person.__init__(self, name, age)
#		self.loans = loans

#p1 = Person("Mikael",33)
#print(p1)
#m1 = Military("Michael", 40, "General")
#print(m1)
#t1 = Teacher("Jonas", 48, "Circuits")
#print(t1)
#s1 = Student("Ted", 20, 100000)
#print(s1)


########################################################
#### TheMonkeyLords youtube tutorial 20 (More Classes): https://www.youtube.com/watch?v=gGMwx9JHpWc

#class Person:
#	population = 0 # class variable, must be referred to with classname.variablename
#	## Can keep track of number of objects in the class you have, etc
#	## Self.population would be an object variable, Person.population is a class variable
#	## Can be accessed inside and outside the class at any time
#	def __init__(self, name, age):
#		self.name = name
#		self.age = age
#		print('{0} has been born!'.format(self.name))
#		Person.population += 1
#	def __str__(self): # What is returned when you call print(created object)
#		return "{0} is {1} years old.".format(self.name,self.age)
#	def __del__(self): # What happens when object is deleted
#		print("{0} is dying! :( ".format(self.name))
#		Person.population -= 1
#	def totalPop(): ## Class method or static method, accessed using class name instead of object
#		print("There are {} people in the world.".format(Person.population))

#print(Person.population)
#Hubs = Person("Michael",33)
#print(Person.population)
#Person.totalPop() ## cannot use an object for this -> no Johnny.totalPop()
#print(Hubs)
#print(Hubs.name+" Miller"+"-"+"Domingo")

########################################################
### TheMonkeyLords youtube tutorial 19 (Classes): https://www.youtube.com/watch?v=b9wfg-oXAKU
#class student:
#	def __init__(self, name):
#		self.name = name
#		self.attend = 0
#		self.grades = []
#		print("Hi! My name is {0}".format(self.name))
#	def addGrade(self, grade):
#		self.grades.append(grade)
#	def attendDay(self):
#		self.attend += 1
#	def getAverage(self):
#		return sum(self.grades) / len(self.grades)

#student1 = student("Mikael")
#student1.addGrade(100)
#student1.addGrade(50)
#student1.addGrade(75)
#student1.addGrade(70)
#student1.addGrade(80)
#print(student1.getAverage())

#student2 = student("Sophia")
#for x in range(1, 11):
#	student2.attendDay()

#print(student2.attend)

########################################################


#class x:
#	varx1 = 4
#	def function1():
#		function1output = "function 1 output"
#		print(function1output)
#		return function1output

#class y:
#	varxy = x.varx1
#	vary1 = 5
#	varxyout = vary1 + varxy

#x1 = x()
#y1 = y()

#print(x1.varx1)
#print(y1.vary1)
#print(y1.varxy)
#print(y1.varxyout)
#print(type(x1.function1))


########################################################



###################################################
### Creating a list in a frame

#from tkinter import *

#root = Tk()

#listbox = Listbox(root)
#listbox.pack()

#for i in range(20):
#	listbox.insert(END, str(i))

#mainloop()

###################################################

#import tkinter as tk

#counter = 0 
#def counter_label(label):
#  def count():
#	global counter
#	counter += 1
#	label.config(text=str(counter))
#	label.after(1000, count)
#  count()
 
 
#root = tk.Tk()
#root.title("Counting Seconds")
#label = tk.Label(root, fg="green")
#label.pack()
#counter_label(label)
#button = tk.Button(root, text='Stop', width=25, command=root.destroy)
#button.pack()
#root.mainloop()

########################################################

#import tkinter as tk

#class Example(tk.Frame):
#	def __init__(self, parent):
#		tk.Frame.__init__(self, parent)
#		b = tk.Button(self, text="Done!", command=self.upload_cor)
#		b.pack()
#		table = tk.Frame(self)
#		table.pack(side="top", fill="both", expand=True)

#		data = (
#			(45417, "rodringof", "CSP L2 Review", 0.000394, "2014-12-19 10:08:12", "2014-12-19 10:08:12"),
#			(45418, "rodringof", "CSP L2 Review", 0.000394, "2014-12-19 10:08:12", "2014-12-19 10:08:12"),
#			(45419, "rodringof", "CSP L2 Review", 0.000394, "2014-12-19 10:08:12", "2014-12-19 10:08:12"),
#			(45420, "rodringof", "CSP L2 Review", 0.000394, "2014-12-19 10:08:12", "2014-12-19 10:08:12"),
#			(45421, "rodringof", "CSP L2 Review", 0.000394, "2014-12-19 10:08:12", "2014-12-19 10:08:12"),
#			(45422, "rodringof", "CSP L2 Review", 0.000394, "2014-12-19 10:08:12", "2014-12-19 10:08:12"),
#			(45423, "rodringof", "CSP L2 Review", 0.000394, "2014-12-19 10:08:12", "2014-12-19 10:08:12"),
#		)

#		self.widgets = {}
#		row = 0
#		for rowid, reviewer, task, num_seconds, start_time, end_time in (data):
			
#			self.widgets[rowid] = {
#				"rowid": tk.Label(table, text=rowid),
#				"reviewer": tk.Label(table, text=reviewer),
#				"task": tk.Label(table, text=task),
#				"num_seconds_correction": tk.Entry(table),
#				"num_seconds": tk.Label(table, text=num_seconds),
#				"start_time": tk.Label(table, text=start_time),
#				"end_time": tk.Label(table, text=start_time)
#			}
#			row += 1

#			self.widgets[rowid]["rowid"].grid(row=row, column=0, sticky="nsew")
#			self.widgets[rowid]["reviewer"].grid(row=row, column=1, sticky="nsew")
#			self.widgets[rowid]["task"].grid(row=row, column=2, sticky="nsew")
#			self.widgets[rowid]["num_seconds_correction"].grid(row=row, column=3, sticky="nsew")
#			self.widgets[rowid]["num_seconds"].grid(row=row, column=4, sticky="nsew")
#			self.widgets[rowid]["start_time"].grid(row=row, column=5, sticky="nsew")
#			self.widgets[rowid]["end_time"].grid(row=row, column=6, sticky="nsew")

#		table.grid_columnconfigure(1, weight=1)
#		table.grid_columnconfigure(2, weight=1)
#		# invisible row after last row gets all extra space
#		table.grid_rowconfigure(row+1, weight=1)

#	def upload_cor(self):
#		for rowid in sorted(self.widgets.keys()):
#			entry_widget = self.widgets[rowid]["num_seconds_correction"]
#			new_value = entry_widget.get()
#			print("%s: %s" % (rowid, new_value))

#if __name__ == "__main__":
#	root = tk.Tk()
#	Example(root).pack(fill="both", expand=True)
#	root.mainloop()


#########################################################

#### CALCULATOR EXAMPLE 
#-*-coding: utf-8-*-
#from tkinter import *
#import math

#class calc:
# def getandreplace(self):
#  """replace x with * and ÷ with /"""
  
#  self.expression = self.e.get()
#  self.newtext=self.expression.replace(self.newdiv,'/')
#  self.newtext=self.newtext.replace('x','*')

# def equals(self):
#  """when the equal button is pressed"""

#  self.getandreplace()
#  try: 
#   self.value= eval(self.newtext) #evaluate the expression using the eval function
#  except SyntaxError or NameErrror:
#   self.e.delete(0,END)
#   self.e.insert(0,'Invalid Input!')
#  else:
#   self.e.delete(0,END)
#   self.e.insert(0,self.value)
 
# def squareroot(self):
#  """squareroot method"""
  
#  self.getandreplace()
#  try: 
#   self.value= eval(self.newtext) #evaluate the expression using the eval function
#  except SyntaxError or NameErrror:
#   self.e.delete(0,END)
#   self.e.insert(0,'Invalid Input!')
#  else:
#   self.sqrtval=math.sqrt(self.value)
#   self.e.delete(0,END)
#   self.e.insert(0,self.sqrtval)

# def square(self):
#  """square method"""
  
#  self.getandreplace()
#  try: 
#   self.value= eval(self.newtext) #evaluate the expression using the eval function
#  except SyntaxError or NameErrror:
#   self.e.delete(0,END)
#   self.e.insert(0,'Invalid Input!')
#  else:
#   self.sqval=math.pow(self.value,2)
#   self.e.delete(0,END)
#   self.e.insert(0,self.sqval)
 
# def clearall(self): 
#  """when clear button is pressed,clears the text input area"""
#  self.e.delete(0,END)
 
# def clear1(self):
#  self.txt=self.e.get()[:-1]
#  self.e.delete(0,END)
#  self.e.insert(0,self.txt)

# def action(self,argi): 
#  """pressed button's value is inserted into the end of the text area"""
#  self.e.insert(END,argi)
 
# def __init__(self,master):
#  """Constructor method"""
#  master.title('Calulator') 
#  master.geometry()
#  self.e = Entry(master)
#  self.e.grid(row=0,column=0,columnspan=6,pady=3)
#  self.e.focus_set() #Sets focus on the input text area
	
#  self.div='÷'
#  self.newdiv=self.div

#  #Generating Buttons
#  Button(master,text="=",width=10,command=lambda:self.equals()).grid(row=4, column=4,columnspan=2)
#  Button(master,text='AC',width=3,command=lambda:self.clearall()).grid(row=1, column=4)
#  Button(master,text='C',width=3,command=lambda:self.clear1()).grid(row=1, column=5)
#  Button(master,text="+",width=3,command=lambda:self.action('+')).grid(row=4, column=3)
#  Button(master,text="x",width=3,command=lambda:self.action('x')).grid(row=2, column=3)
#  Button(master,text="-",width=3,command=lambda:self.action('-')).grid(row=3, column=3)
#  Button(master,text="÷",width=3,command=lambda:self.action(self.newdiv)).grid(row=1, column=3) 
#  Button(master,text="%",width=3,command=lambda:self.action('%')).grid(row=4, column=2)
#  Button(master,text="7",width=3,command=lambda:self.action(7)).grid(row=1, column=0)
#  Button(master,text="8",width=3,command=lambda:self.action(8)).grid(row=1, column=1)
#  Button(master,text="9",width=3,command=lambda:self.action(9)).grid(row=1, column=2)
#  Button(master,text="4",width=3,command=lambda:self.action(4)).grid(row=2, column=0)
#  Button(master,text="5",width=3,command=lambda:self.action(5)).grid(row=2, column=1)
#  Button(master,text="6",width=3,command=lambda:self.action(6)).grid(row=2, column=2)
#  Button(master,text="1",width=3,command=lambda:self.action(1)).grid(row=3, column=0)
#  Button(master,text="2",width=3,command=lambda:self.action(2)).grid(row=3, column=1)
#  Button(master,text="3",width=3,command=lambda:self.action(3)).grid(row=3, column=2)
#  Button(master,text="0",width=3,command=lambda:self.action(0)).grid(row=4, column=0)
#  Button(master,text=".",width=3,command=lambda:self.action('.')).grid(row=4, column=1)
#  Button(master,text="(",width=3,command=lambda:self.action('(')).grid(row=2, column=4)
#  Button(master,text=")",width=3,command=lambda:self.action(')')).grid(row=2, column=5)
#  Button(master,text="√",width=3,command=lambda:self.squareroot()).grid(row=3, column=4)
#  Button(master,text="x²",width=3,command=lambda:self.square()).grid(row=3, column=5)
##Main
#root = Tk()
#obj=calc(root) #object instantiated
#root.mainloop()

##################################

#from tkinter import *
#from tkinter.ttk import *

#root = Tk()
#var = StringVar()
##var.set('hello') #optional

#l = Label(root, textvariable = var)
#l.pack()

#t = Entry(root, textvariable = var)
#t.pack()

#root.mainloop()


##################################


#class Obj1:
#	x = 2

#	def prints(self):
#		print("This is the prints function in Obj1")

#o = Obj1()
##print(o.x + 2)
##o.prints()

#class Obj2:
#	x = 5

#	def prints(self):
#		print("This is the prints function in Obj2")
#		return 5

#p = Obj2()
##print(p.x)
##print(p.prints()) ## p.prints automatically prints "This...Obj2", then returns 5 for the outer print statement

#############################

#class Customer(object):
#	def __init__(self, name='Normal', balance=0.0):
#		self.name = name
#		self.balance = balance

#	def withdraw(self, amount):
#		if amount > self.balance:
#			raise RuntimeError('Amount greater than available balance')
#		self.balance -= amount
#		return self.balance

#	def deposit(self, amount):
#		self.balance += amount
#		return self.balance

#cx1 = Customer('mikael')
##print(cx1.deposit(250))
##print(cx1.withdraw(111))
##print(cx1.balance)
##print(cx1.name)

#cx2 = Customer()
##print(cx2.deposit(1100))
##print(cx2.withdraw(543))
##print(cx2.balance)
##print(cx2.name)

###############################

#import pandas as pd #This is a data analysis library
#import numpy as np #This allows for arrays and matrices. Not used yet...might need it.
#import pandas.io.sql as psql #This uses pandas to read SQL into a dataframe
#import pyodbc #This is the ODBC connection to SQL

#from tkinter import *
#from tkinter.ttk import *

#root = Tk()
#frame = Frame(root)
#frame.pack()

#bottomframe=Frame(root)
#bottomframe.pack(side=BOTTOM)

#lastframe = Frame(root)
#lastframe.pack(side=BOTTOM)

#redbutton = Button(frame, text="Red")
#redbutton.pack(side=LEFT)

#greenbutton = Button(frame, text="Green")
#greenbutton.pack( side = LEFT )

#bluebutton = Button(bottomframe, text="Blue")
#bluebutton.pack( side = LEFT )

#blackbutton = Button(bottomframe, text="Black")
#blackbutton.pack( side = BOTTOM)

#w = Label(lastframe, text="Hello World!")
#w.pack(side = BOTTOM)

#root.mainloop()




