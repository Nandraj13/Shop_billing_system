from asyncio.windows_events import NULL
from cgitb import text
from datetime import date
from operator import add
import tkinter
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from tkinter.tix import Tree
from tkinter.ttk import *
import tkinter as tk
from webbrowser import get
import pymysql
from fpdf import FPDF
import os

db=pymysql.connect(
        host='localhost',
        user='root', 
        password = "",
        db='shopbill',
        )
cursor=db.cursor()
#all windows declaration and top window creation

top = tkinter.Tk()
second=NULL
userhome=NULL
profilewindow=NULL
addproductswindow=NULL
displaybillwindow=''
top.title('Shop Billing System')
top.minsize(400,400)
top.maxsize(400,400)
top.geometry("400x400")

#profile variables
profilename=''
profileusername=''
#addproducts variables
addproductslist=''
productnameentry=''
productpriceentry=''
product_id=''
#user details save for future purpose
userid=''
user_name=''
fname=''
shopname=''
#generate bill variables
itemselectforbill=''
billitemlist=''
quantityentry=''
customername=''
customernumber=''
billamount=0
billamtotal=''

#displaybillwindow variables
tree=''
byname=''
bydate=''
bycont=''
var1=''

#functions  for different functionalities
def registeruser():
   query="insert into users (username,password,shopname,name) values(%s,%s,%s,%s)"
   val=(username.get(),password.get(),shopname.get(),name.get())
   if(val[0]=="" or val[1]=="" or val[2]=="" or val[3]==""):
      messagebox.showinfo("Incoplete details","All feilds are mandatory")
   else:
      try:
         cursor.execute(query,val)
         db.commit()
         if(cursor.rowcount>0):
            messagebox.showinfo("Success","User registered")
            showLogin()
         else:
            messagebox.showinfo("Error","User not registered")
      except:
         db.rollback()
         messagebox.showinfo("Error","User not registered")

def showLogin():
   top.withdraw()
   global second
   second = Toplevel()
   second.title("Shop Billing System")
   second.geometry("400x400")
   second.maxsize(400,400)
   second.minsize(400,400)
   LoginLabel=Label(second,text="LOGIN",font='calibre 18 bold')
   loginusername=Label(second,text="Email",font='calibre 12')
   loginpassword=Label(second,text="Password",font='calibre 12')
   usernamel=Entry(second)
   passwordl=Entry(second,show="*")
   Login=tk.Button(second,text="Login",bg="#3285a8",fg="white",command=lambda:checklogin(usernamel.get(),passwordl.get()))
   LoginLabel.grid(row=0,column=2)
   loginusername.grid(row=1,column=1,pady=10)
   loginpassword.grid(row=2,column=1,pady=10)
   usernamel.grid(row=1,column=2)
   passwordl.grid(row=2,column=2)
   Login.grid(row=3,column=2)
   second.protocol("WM_DELETE_WINDOW",on_closing)

def checklogin(un,ps):
   if(un=="" or ps==""):
      messagebox.showinfo("Incomplete details","All feilds are mandatory")
   else:
      global userid,user_name,fname,shopname
      query="select * from users where username=%s and password=%s"
      val=(un,ps)
      try:
         cursor.execute(query,val)
         result=cursor.fetchall()
         if(len(result)>0):
            for row in result:
               #shopname fetch
               shopname=row[2]
               userid=row[4]
               user_name=row[0]
               fname=row[3]
            userhomepage(shopname)
         else:
            messagebox.showinfo("Invalid credentials","No user such user exists")
      except:
            messagebox.showinfo("Invalid credentials","No user such user exists")
def userhomepage(shopname):
   global second,userhome,itemselectforbill,quantityentry,customername,customernumber,billitemlist,billamtotal
   second.withdraw()
   userhome=Toplevel()
   userhome.title(shopname+" - Home")
   userhome.geometry("600x400")
   userhome.minsize(600,400)
   userhome.maxsize(600,400)
   userhome.protocol("WM_DELETE_WINDOW",on_closing)

   homemenubar=Menu(userhome)

   homefileviewmenu=Menu(homemenubar,tearoff=0)
   homefileviewmenu.add_command(label='Profile',command=lambda:profileview(shopname))
   homefileviewmenu.add_command(label='Manage products',command=lambda:addproductswindowfunc(shopname))

   homemenubar.add_cascade(label='View',menu=homefileviewmenu)

   homefilemoremenu=Menu(homemenubar,tearoff=0)
   homefilemoremenu.add_command(label='View Bill Data',command=DispBill)
   homefilemoremenu.add_command(label='Logout',command=logout)

   homemenubar.add_cascade(label='More',menu=homefilemoremenu)

   userhome.config(menu=homemenubar)
   clearbillbutton=tk.Button(userhome,text="Clear",bg="#3285a8",fg="white",command=clearbill)
   addtobillbox=tk.Button(userhome,text='Add item',bg="#3285a8",fg="white",command=additemtobilllist)
   removefrombillbox=tk.Button(userhome,text='Remove item',bg="#3285a8",fg="white",command=removeitemlist)
   generatebillbutton=tk.Button(userhome,text='Generate bill',bg="#3285a8",fg="white",command=generatebillfunc)
   billitemlist=Listbox(userhome,width=45)
   quantityentry=Entry(userhome)
   #tracing phone number for checking user name
   var = StringVar()
   var.trace("w", lambda name, index,mode, var=var: fillcustomername(var))   
   customername=Entry(userhome)
   customernumber=Entry(userhome,textvariable=var)
   customernamelabel=Label(userhome,text="Customer name",font="calibre 12")
   billamtotal=Label(userhome,text="Total: 0",font="calibre 14 bold")
   customernumberlabel=Label(userhome,text="Contact number",font="calibre 12")
   Generatebilllabel=Label(userhome,text="Generate bill",font="calibre 18 bold")
   n = tk.StringVar()
   itemselectforbill=Combobox(userhome, width = 27, textvariable = n,state="readonly")
   Generatebilllabel.grid(row=0,column=0)
   #filling combobox
   fillcombobox()
   itemselectforbill.grid(row=1,column=0,pady=10)
   quantityentry.grid(row=1,column=1,padx=5)
   billitemlist.grid(row=1,column=2)
   addtobillbox.grid(row=2,column=2)
   removefrombillbox.place(x=500,y=197)
   customernamelabel.grid(row=3,column=0)
   customername.grid(row=4,column=0,pady=5)
   customernumberlabel.grid(row=5,column=0)
   customernumber.grid(row=6,column=0,pady=5)
   generatebillbutton.place(x=265,y=350)
   billamtotal.place(x=320,y=7)
   clearbillbutton.grid(row=7,column=0)

def DispBill():
   global displaybillwindow,shopname,userhome,user_name,tree,byname,bydate,bycont,var1
   userhome.withdraw()
   displaybillwindow=Toplevel()
   displaybillwindow.title(shopname+" - View Bills")
   displaybillwindow.geometry("1000x400")
   displaybillwindow.maxsize(1000,400)
   displaybillwindow.minsize(1000,400)
   displaybillwindow.protocol("WM_DELETE_WINDOW",on_closing)

   var1 = IntVar()
   bydate = Radiobutton(displaybillwindow, text="By date", variable=var1, value=1)
   byname = Radiobutton(displaybillwindow, text="By name", variable=var1, value=2)
   bycont = Radiobutton(displaybillwindow, text="By contact", variable=var1, value=3)

   var = StringVar()
   var.trace("w", lambda name, index,mode, var=var: fillbilltree(var)) 
   searchbill=Entry(displaybillwindow,textvariable=var)
   backbutton=tk.Button(displaybillwindow,text='Back',bg="#3285a8",fg="white",command=backtohomefromviewbill)
   backbutton.place(x=470,y=250) 
   tree = ttk.Treeview(displaybillwindow, column=("c1", "c2", "c3","c4","c5"), show='headings')
   tree.column("#1", anchor=tk.CENTER)
   tree.heading("#1", text="Bill id")
   tree.column("#2", anchor=tk.CENTER)
   tree.heading("#2", text="Date")
   tree.column("#3", anchor=tk.CENTER)
   tree.heading("#3", text="Customer Name")
   tree.column("#4", anchor=tk.CENTER)
   tree.heading("#4", text="Customer Contact")
   tree.column("#5", anchor=tk.CENTER)
   tree.heading("#5", text="Amount")

   searchbill.grid(row=0,column=0)
   bydate.place(x=580,y=4)
   byname.place(x=650,y=4)
   bycont.place(x=730,y=4)

   tree.grid(row=1,column=0)

   cursor.execute("select * from bill where biller=%s",user_name)
   rows = cursor.fetchall()    
   for row in rows:
    print(row) 
    tree.insert("", tk.END, values=row)        
def fillbilltree(key):
   global tree,user_name
   for item in tree.get_children():
    tree.delete(item)
   if(var1.get()==1):
      cursor.execute("select * from bill where biller=%s and date LIKE %s",(user_name,key.get()+"%"))
   elif(var1.get()==2):
      cursor.execute("select * from bill where biller=%s and cname LIKE %s",(user_name,key.get()+"%"))
   elif(var1.get==3):
      cursor.execute("select * from bill where biller=%s and ccontact LIKE %s",(user_name,key.get()+"%"))
   else:
      cursor.execute("select * from bill where biller=%s and ccontact LIKE %s",(user_name,key.get()+"%"))

   rows = cursor.fetchall()    
   for row in rows:
    tree.insert("", tk.END, values=row)
   
def clearbill():
   global customername,customernumber,quantityentry,billamtotal,billitemlist,billamount
   billitemlist.delete(0,END)
   billamount=0
   quantityentry.delete(0,END)
   customername.delete(0,END)
   customernumber.delete(0,END)
   billamtotal.config(text="Total: "+str(billamount))

def generatebillfunc():
   pdfx=30
   pdfy=65
   id=0
   global customername,customernumber,quantityentry,user_name,billamount,shopname,billitemlist,fname
   today = str(date.today())
   if(customername.get()=="" or customernumber.get()=="" or quantityentry.get()=="" or billitemlist.size()==0):
      messagebox.showinfo("Insufficient data","All fields are mandatory")
   else:
      query="select * from customer where ccontact=%s"
      val=(customernumber.get())
      query3="insert into bill(date,cname,ccontact,amount,shopname,biller) values(%s,%s,%s,%s,%s,%s)"
      val3=(today,customername.get(),customernumber.get(),billamount,shopname,user_name)
      try:
         cursor.execute(query3,val3)
         if(cursor.rowcount>0):
            messagebox.showinfo("Success","Bill generated and saved to your default directory")
         id=cursor.lastrowid
         db.commit()
         cursor.execute(query,val)
         res=cursor.fetchall()
         if(len(res)):
            pass
         else:
            query2="insert into customer (cname,ccontact) values(%s,%s)"
            val2=(customername.get(),customernumber.get())
            cursor.execute(query2,val2)
            db.commit()
         pdf=FPDF()
         pdf.add_page()
         pdf.set_font('Arial','B',10)
         pdf.cell(200, 10, txt = "Thank you, Please visit again..!",
            ln = 1, align = 'C')
         pdf.set_font('Arial','B',14)
         pdf.cell(200, 10, txt = shopname,
            ln = 1, align = 'C')
         pdf.set_font('Arial','',12)
         pdf.cell(200, 10, txt = "Date:"+str(today),ln=1, align = 'R')
         pdf.cell(200,10,align='L',txt="Customer name: "+customername.get(),ln=1)
         pdf.cell(200,10,align='L',txt="Customer Number: "+customernumber.get(),ln=1)
         pdf.set_font('Arial','B',12)
         pdf.set_xy(pdfx,pdfy)
         pdf.cell(h=5,w=65,txt="Item",border=1)
         pdf.cell(h=5,w=30,txt="Quantity",border=1)
         pdf.cell(h=5,w=30,txt="Price",border=1)
         pdf.cell(h=5,w=30,txt="Total",border=1,ln=1)
         pdf.set_font('Arial','',10)
         for i in billitemlist.get(0,END):
            temp=i.split()
            tempstr=''
            for x in i:
               if(x.isalpha() or x.isspace()):
                  tempstr=tempstr+x
               else:
                  break
            pdfy=pdfy+5
            pdf.set_xy(pdfx,pdfy)
            pdf.cell(h=5,w=65,txt=tempstr,border=0,ln=0)
            pdf.cell(h=5,w=30,txt=temp[len(temp)-3],border=0)
            pdf.cell(h=5,w=30,txt=temp[len(temp)-2],border=0)
            pdf.cell(h=5,w=30,txt=temp[len(temp)-1],border=0)
            

            print(temp[len(temp)-3],temp[len(temp)-2],temp[len(temp)-1])
            print(tempstr)
         pdf.set_font('Arial','B',12)
         pdf.cell(h=5,w=30,txt="",ln=1)
         pdf.cell(h=5,w=30,txt="",ln=1)
         pdf.cell(h=5,w=30,txt="Grand total: "+str(billamount),border=0,ln=1)
         pdf.cell(200,10,align='L',txt="Biller name: "+fname)
         pdf.output(str(id)+"_"+customernumber.get()+".pdf")
      except Exception as e:
            print(e)
            db.rollback()

def fillcustomername(key):
   #print(key.get())
   global customername
   customername.delete(0,END)
   cusname=''
   query="select * from customer where ccontact LIKE %s"
   value=(key.get())
   try:
      cursor.execute(query,value)
      res=cursor.fetchall()
      for row in res:
         cusname=row[2]
      customername.insert(0,cusname)
   except Exception as e:
      print(e)


def removeitemlist():
   global billitemlist,billamtotal,billamount
   selection=billitemlist.curselection()
   save=billitemlist.get(selection)
   save=save.split()
   billitemlist.delete(selection[0])
   billamount=billamount-int(save[len(save)-1])
   billamtotal.config(text="Total: "+str(billamount))
  

def additemtobilllist():
   global quantityentry,itemselectforbill,user_name,billamount,billitemlist
   if(quantityentry.get()==""):
      messagebox.showinfo("Error","Please enter quantity")
   query="select * from products where username=%s and product_name=%s"
   val=(user_name,itemselectforbill.get())
   price=''
   temp=''
   try:
      cursor.execute(query,val)
      res=cursor.fetchall()
      for row in res:
         price=row[2]
      billamount=billamount+(int(price)*int(quantityentry.get()))
      temp=int(price)*int(quantityentry.get())
      billitemlist.insert(0,str(row[1])+" "+quantityentry.get()+" "+str(row[2])+" "+str(temp)) 
      billamtotal.config(text="Total: "+str(billamount))
   except Exception as e:
      print(str(e))
   
def fillcombobox():
   global username,itemselectforbill
   query="select * from products where username=%s"
   val=(user_name)
   prod_names=[]
   try:
      cursor.execute(query,val)
      res=cursor.fetchall()
      for row in res:
         prod_names.append(row[1])
      itemselectforbill['values']=prod_names
   except:
      pass

def on_closing():
   top.destroy()
def logout():
   global userhome,second
   userhome.withdraw()
   second.deiconify()
def profileview(shopname):
   global userhome,profilewindow,profilename,profileusername
   userhome.withdraw()
   profilewindow=Toplevel()
   profilewindow.title(shopname+" - Profile")
   profilewindow.geometry("400x400")
   profilewindow.maxsize(400,400)
   profilewindow.maxsize(400,400)
   profilewindow.protocol("WM_DELETE_WINDOW",on_closing)
   usernamelabel=Label(profilewindow,text="Email:",font='calibre 14 bold')
   namelabel=Label(profilewindow,text="Name: ",font='calibre 14 bold')
   profileusername=Label(profilewindow,text="",font='calibre 14 bold')
   profilename=Label(profilewindow,text="",font='calibre 14 bold')
   changenamelabel=Label(profilewindow,text='Change name',font='calibre 14 bold')
   changepasswordlabel=Label(profilewindow,text='Change password',font='calibre 14 bold')
   changeusernamelabel=Label(profilewindow,text='Change Email',font='calibre 14 bold')
   changename=Entry(profilewindow)
   changeusername=Entry(profilewindow)
   changepasswordnew=Entry(profilewindow)
   changepasswordold=Entry(profilewindow)
   updateusername=tk.Button(profilewindow,text="Update email",bg="#3285a8",fg="white",command=lambda:updatenewusername(changeusername.get()))
   updatename=tk.Button(profilewindow,text="Update name",bg="#3285a8",fg="white",command=lambda:updatenewname(changename.get()))
   updatepassword=tk.Button(profilewindow,text="Update password",bg="#3285a8",fg="white",command=lambda:updatenewpassword(changepasswordnew.get(),changepasswordold.get()))
   backbutton=tk.Button(profilewindow,text='Back',bg="#3285a8",fg="white",command=backtohomefromprofile)
   try:
      cursor.execute("select * from users where user_id=%s",userid)
      result=cursor.fetchall()
      for row in result:
         profileusername.config(text=row[0])
         profilename.config(text=row[3])
   except:
      pass

   profileusername.grid(row=0,column=1)
   usernamelabel.grid(row=0,column=0)
   profilename.grid(row=1,column=1)
   namelabel.grid(row=1,column=0)
   changeusernamelabel.grid(row=2,column=0,pady=10)
   changeusername.grid(row=2,column=1,padx=5)
   updateusername.grid(row=3,column=1)
   changenamelabel.grid(row=4,column=0,pady=10)
   changename.grid(row=4,column=1,padx=5)
   updatename.grid(row=5,column=1)
   changepasswordlabel.grid(row=6,column=0,pady=10)
   changepasswordnew.grid(row=6,column=1,padx=5)
   changepasswordold.grid(row=7,column=1,padx=5)
   updatepassword.grid(row=8,column=1,pady=10)
   backbutton.grid(row=9,column=1)

def backtohomefromprofile():
   global profilewindow,userhome
   fillcombobox()
   profilewindow.withdraw()
   userhome.deiconify()

def backtohomefromviewbill():
   global userhome,displaybillwindow
   displaybillwindow.withdraw()
   userhome.deiconify()

def updatenewname(newname):
   global profilename,fname
   query="update users set name=%s where user_id=%s"
   val=(newname,userid)
   try:
      cursor.execute(query,val)
      if(cursor.rowcount>0):
         db.commit()
         messagebox.showinfo("success","Name updated")
         profilename.config(text=newname)
         fname=newname
   except:
      messagebox.showinfo("Error","Try again after sometime")
      db.rollback()

def updatenewusername(username):
   global profileusername,user_name
   query="update users set username=%s where user_id=%s"
   val=(username,userid)
   try:
      cursor.execute(query,val)
      if(cursor.rowcount>0):
         db.commit()
         messagebox.showinfo("success","Email updated")
         profileusername.config(text=username)
         user_name=username
      else:
          messagebox.showinfo("Try other Email","Email not updated")
   except:
      messagebox.showinfo("Error","Try again after sometime")
      db.rollback()

def updatenewpassword(newpass,oldpass):
   global userid
   query="update users set password=%s where user_id=%s and password=%s"
   val=(newpass,userid,oldpass)
   try:
      cursor.execute(query,val)
      if(cursor.rowcount>0):
         db.commit()
         messagebox.showinfo("success","Password updated")
      else:
          messagebox.showinfo("Password mismatch","Old password incorrect")
   except:
      messagebox.showinfo("Error","Try again after sometime")
      db.rollback()
      
def addproductswindowfunc(shopname):
   global addproductswindow,userhome,addproductslist,productnameentry,productpriceentry
   var = StringVar()
   var.trace("w", lambda name, index,mode, var=var: livesearch(var))
   userhome.withdraw()
   addproductswindow=Toplevel()
   addproductswindow.title(shopname+" - Manage products")
   addproductswindow.geometry("400x400")
   addproductswindow.minsize(400,400)
   addproductswindow.maxsize(400,400)
   addproductswindow.protocol("WM_DELETE_WINDOW",on_closing)
   
   productnamelabel=Label(addproductswindow,text='Product name',font='calibre 12')
   productpricelabel=Label(addproductswindow,text='Product price',font='calibre 12')
   searchlabel=Label(addproductswindow,text='Search Product',font='calibre 12')
   searchboxentry=Entry(addproductswindow,textvariable=var)
   productnameentry=Entry(addproductswindow)
   productpriceentry=Entry(addproductswindow)
   addproductsbutton=tk.Button(addproductswindow,text='Add product',bg="#3285a8",fg="white",command=lambda:addproducts(productnameentry.get(),productpriceentry.get()))
   deletebutton=tk.Button(addproductswindow,text='Delete selected product',bg="#3285a8",fg="white",command=selected_item)
   updatebutton=tk.Button(addproductswindow,text='Update product',bg="#3285a8",fg="white",command=updateproduct)
   backbutton=tk.Button(addproductswindow,text='Back',bg="#3285a8",fg="white",command=backtohomefromaddproducts)

   addproductslist=Listbox(addproductswindow,width=35)
   addproductslist.bind('<Double-1>', clicktoupdate)
   addproductslist.grid(row=0,column=0)
   searchlabel.place(x=218,y=40)
   searchboxentry.grid(row=0,column=1)
   productnamelabel.grid(row=1,column=0,pady=10)
   productnameentry.grid(row=1,column=1,padx=5)
   productpricelabel.grid(row=2,column=0,pady=10)
   productpriceentry.grid(row=2,column=1,padx=5)
   addproductsbutton.grid(row=3,column=1,pady=5)
   deletebutton.grid(row=4,column=1,pady=5)
   updatebutton.grid(row=5,column=1,pady=5)
   backbutton.grid(row=6,column=1,pady=5)
   fetchproductsfromdatabase()

def addproducts(productname,productprice):
   global user_name,productpriceentry,productnameentry
   query="insert into products (product_name,product_price,username) values(%s,%s,%s)"
   val=(productname,productprice,user_name)
   val1=(productname,user_name)
   query1="select * from products where product_name=%s and username=%s"
   cursor.execute(query1,val1)
   results=cursor.fetchall()

   if(productname=="" or productprice==""):
      messagebox.showinfo("Insufficient data","All fields are mandatory")
   else:
         if(len(results)>0):
            messagebox.showinfo("Replication not allowed","Product with same specification already exists")
         else:
            try:
                  cursor.execute(query,val)
                  db.commit()
                  if(cursor.rowcount>0):
                     productpriceentry.delete(0,END)
                     productnameentry.delete(0,END)
                     fetchproductsfromdatabase()
                  else:
                     messagebox.showinfo("Error","Product not added")
            except:
                  db.rollback()
                  messagebox.showinfo("Error","Product not added")

def backtohomefromaddproducts():
   global addproductswindow,userhome
   fillcombobox()
   userhome.deiconify()
   addproductswindow.withdraw()

def fetchproductsfromdatabase():
   global user_name,addproductslist
   addproductslist.delete(0,END)
   query="select * from products where username=%s"
   value=(user_name)
   try:
    cursor.execute(query,value)
    result=cursor.fetchall()
    i=1
    for row in result:
       addproductslist.insert(i,str(row[0])+"-"+row[1]+"-"+row[2])
       i+1
   except:
      pass

def livesearch(key):
   global user_name
   #print(key.get()+"%")
   addproductslist.delete(0,END)
   query="select * from products where product_name LIKE %s and username=%s"
   value=(key.get()+"%",user_name)
   try:
    cursor.execute(query,value)
    result=cursor.fetchall()
    i=1
    for row in result:
       addproductslist.insert(i,str(row[0])+"-"+row[1]+"-"+row[2]) 
       i+1
   except:
      pass

def selected_item():
   global user_name
   products=addproductslist.curselection()
   onlynameslist=[]
   for i in products:
      onlynames=addproductslist.get(i)
      temp=onlynames.split("-")
      onlynameslist.append(temp[0])
   if(len(onlynameslist)==0):
      messagebox.showinfo("No product selected","Please select a product")
   else:
      try:
         query="delete from products where product_id=%s and username=%s"
         for name in onlynameslist:
            val=(name,user_name)
            cursor.execute(query,val)
            db.commit()
         messagebox.showinfo("success","Selected product deleted")
         productnameentry.delete(0,END)
         productpriceentry.delete(0,END)
         fetchproductsfromdatabase()
      except:
            messagebox.showinfo("Error","Try again later")
            db.rollback()

def clicktoupdate(event):
   global user_name,productnameentry,productpriceentry,product_id
   products=addproductslist.curselection()
   for i in products:
      onlynames=addproductslist.get(i)
   splitednames=onlynames.split("-")
   product_id=splitednames[0]
   productnameentry.delete(0,END)
   productpriceentry.delete(0,END)
   productnameentry.insert(0,splitednames[1])
   productpriceentry.insert(0,splitednames[2])

def updateproduct():
   global user_name,productnameentry,productpriceentry,product_id
   val1=(productnameentry.get(),productpriceentry.get(),user_name)
   query1="select * from products where product_name=%s and product_price=%s and username=%s"
   try:
      cursor.execute(query1,val1)
      results=cursor.fetchall()
      if(len(results)>0):
            messagebox.showinfo("Replication not allowed","Product with same specification already exists")
      else:
            query="update products set product_name=%s , product_price=%s where username=%s and product_id=%s"
            val=(productnameentry.get(),productpriceentry.get(),user_name,product_id)
            cursor.execute(query,val)
            if(cursor.rowcount>0):
               messagebox.showinfo("Success","Product updated")   
               productnameentry.delete(0,END)
               productpriceentry.delete(0,END)
               fetchproductsfromdatabase() 
   except:
      messagebox.showinfo("Error","Try again later")
      

#registration window components
welcome=Label(top,text="WELCOME",font='calibre 18 bold')
shopnamelabel=Label(top,text="Shopname",font='calibre 12')
usernamelabel=Label(top,text="Email",font='calibre 12')
passwordlabel=Label(top,text="Password",font='calibre 12')
namelabel=Label(top,text="Name",font='calibre 12')
register=tk.Button(top,text="Register",bg="#3285a8",fg="white",command=registeruser)
alreadyuser=tk.Button(top,text="Already registered ?",bg="#3285a8",fg="white",command=showLogin)

shopname=Entry(top)
username=Entry(top)
password=Entry(top,show="*")
name=Entry(top)

welcome.grid(row=0,column=2)
shopnamelabel.grid(row=1,column=1,pady=10)
usernamelabel.grid(row=3,column=1,pady=10)
passwordlabel.grid(row=4,column=1,pady=10)
namelabel.grid(row=2,column=1,pady=10)

shopname.grid(row=1,column=2)
name.grid(row=2,column=2)
username.grid(row=3,column=2)
password.grid(row=4,column=2)

register.grid(row=5,column=2)
alreadyuser.grid(row=6,column=2,pady=5)

top.mainloop()