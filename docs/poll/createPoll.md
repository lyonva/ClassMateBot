# About $poll _(New Project 3 Command)_
This command lets instructors going through the steps to create a poll. 

# Location of Code
The code that implements the above mentioned functionality is located in [cogs/poll.py](https://github.com/lyonva/ClassMateBot/blob/main/cogs/poll.py).

# Code Description
## Functions
createPoll(self, ctx, qs: str, ans: str): <br>
This function takes as arguments the values provided by the constructor through self, context in which the command was called, the question string, and the answer string.

# How to run it? (Small Example)
You are in the server that has the Classmate Bot active and online. You enter the command `poll` and type the test of the poll followed by the different options sperated by commas. 
```
$addQuestion "PollText" "Options"
$addQuestion "when do you want to take a quiz" "today,next week,next month"
```
Successful execution of this command will post a poll with options as reactions .

<img src="data/media/poll.JPG" width="400">
