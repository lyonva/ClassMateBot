# About $reminderadd
This command lets the user (either the TAs or professor) to add a reminder to the discord channel. This is useful for deliverables, such as homeworks, projects, quizes, tests, etc. If used my an instructor, the reminder is created for every user. Otherwise, the reminder is personal.

# Location of Code
The code that implements the above mentioned gits functionality is located [here](https://github.com/lyonva/ClassMateBot/blob/main/src/cogs/deadline.py).

# Code Description
## Functions
reminderadd(self, ctx, hwcount: str, *, date: str): <br>
This function takes as arguments the values provided by the constructor through self, context in which the command was called, name of the homework, and the date and time when the homework is due. 

# How to run it? (Small Example)
Let's say that you are in the server that has the Classmate Bot active and online. All you have to do is 
enter the command 'reminderadd' pass in all the parameters as a space seperated inputs in the following order:
homeworkname, duedate (in MMM DD YYYY optional(HH:MM) format)
```
$reminderadd HW_NAME MMM DD YYYY optional(HH:MM)
$reminderadd HW2 SEP 25 2024 17:02
```
Successful execution of this command will add the reminder for the specified homework on the specified time.

<!-- ![$reminderadd HW2 SEP 25 2024 17:02](https://github.com/lyonva/ClassMateBot/blob/main/data/media/addhomework.gif) -->
