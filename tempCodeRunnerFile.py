name=(input("enter the name of student:"))
age=int(input("the student age:"))
subject1=int(input("the subject1 mark:"))
subject2=int(input("the subject2 mark:"))
subject3=int(input("the subject3 mark:"))
total=subject1+subject2+subject3
average=total/3
print("Student Name:",name)
print("Age:",age)
print("Total=",total)
print("Average=",average)
if(average>80):
  print("A Grade")
elif(average>60):
   print("B Grade")  
elif(average>40):
    print("c Grade") 
else: 
    print("UA")  