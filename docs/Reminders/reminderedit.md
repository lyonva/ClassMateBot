# About $reminderedit
This command lets the user update the due date for a specific homework. If used by an instructor, the new date is set for every user. Otherwise, the reminder is changed just for you.

# Location of Code
The code that implements the above mentioned gits functionality is located [here](https://github.com/lyonva/ClassMateBot/blob/main/src/cogs/deadline.py).

# Code Description
## Functions
reminderedit(self, ctx, hwid: str, *, date: str): <br>
This function takes as arguments the values provided by the constructor through self, context in which the command was called, name of the homework, and the updated date and time. 

# How to run it? (Small Example)
Let's say that you are in the server that has the Classmate Bot active and online. All you have to do is 
enter the command '$reminderedit' and pass in all the parameters as a space seperated inputs in the following order:
homeworkname, updated duedate (in MMM DD YYYY optional(HH:MM) format)
```
$reminderedit HW_NAME MMM DD YYYY optional(HH:MM)
$reminderedit HW2 SEP 25 2024 17:02
```
Successful execution of this command will update the reminder for the specified coursework and homework on the specified time.

<!-- ![$changeduedate CSC510 HW2 SEP 25 2024 17:02](https://github.com/lyonva/ClassMateBot/blob/main/data/media/changeduedate.gif) -->
