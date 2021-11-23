# About $reminderdelete
This command lets the user delete a reminder for a specified coursename and homework. If used my an instructor, the reminder is deleted for every user. Otherwise, the reminder is deleted just for you.

# Location of Code
The code that implements the above mentioned gits functionality is located [here](https://github.com/lyonva/ClassMateBot/blob/main/src/cogs/deadline.py).

# Code Description
## Functions
reminderdelete(self, ctx, hwName: str): <br>
This function takes as arguments the values provided by the constructor through self and the context in which the command was called. It also takes homework name as input.

# How to run it? (Small Example)
Let's say that you are in the server that has the ClassMate Bot active and online. All you have to do is 
enter the command '$reminderdelete' with space seperated coursename and homeworkname as a parameter:

```
$reminderdelete homeworkname
$reminderdelete HW2
```
Successful execution of this command will delete the reminder for a specified homework.

<!-- ![$deletereminder CSC510 HW2](https://github.com/lyonva/ClassMateBot/blob/main/data/media/deletereminder.gif) -->
