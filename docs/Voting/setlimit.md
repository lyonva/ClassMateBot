# About $setLimit _(Modified Command in Project 2)_
This command lets the class instructor change the limit of the number of votes one project can receive

# Location of Code
The code that implements the above-mentioned gits functionality is located [here](https://github.com/lyonva/ClassMateBot/blob/main/cogs/setlimit.py)

# Code Description
## Functions
setlimit(self, ctx, count : int): <br>
This function takes as arguments the values provided by the constructor through self, context in which the command was called, and the new limit value as argument.

# How to run it? (Small Example)
Let's say that you are in the server or bot dm that has the Classmate Bot active and online. All you have to do is 
enter the command 'setlimit <number>'.
```
$setlimit <NUMBER>
$setlimit 2
```
Successful execution of this command will return a message saying the limit has been set to update value.

![image](https://user-images.githubusercontent.com/32313919/140250549-8de514c0-d411-41fe-976c-6b43c7bd1edf.png)
  
It is simple enough to change the limit by just setting the limit to a different value.
  
![image](https://github.com/lyonva/ClassMateBot/blob/main/data/media/votechange.gif)
