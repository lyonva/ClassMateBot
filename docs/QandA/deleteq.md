# About $deleteq _(New Project 3 Command)_

Deletes a requested question if you are an instructor

# Location of Code

The code that implements the above mentioned functionality is located in [cogs/qanda.py](https://github.com/lyonva/ClassMateBot/blob/main/cogs/qanda.py).

# Code Description

## Functions

deleteQuestion(self, ctx, num): <br>
This function takes as arguments the values provided by the constructor through self, context in which the command was called, and the question number to be deleted

# How to run it? (Small Example)

You are in the server that has the Classmate Bot active and online. You go to
the #q-and-a channel, enter the command `deleteq` followed by the number of the question you want to delete.

```
$deleteq 1
```

Successful execution of this command will delete the question and accompanying answer (if applicable) from the database. An invalid question gives the user an error saying the question they are attempting to delete doesn't exist.
