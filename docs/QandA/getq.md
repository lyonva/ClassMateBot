# About $getq _(New Project 3 Command)_

Sends DM of requested question and answer.

# Location of Code

The code that implements the above mentioned functionality is located in [cogs/qanda.py](https://github.com/lyonva/ClassMateBot/blob/main/cogs/qanda.py).

# Code Description

## Functions

getQuestion(self, ctx): <br>
This function takes as arguments the values provided by the constructor through self, context in which the command was called.

# How to run it? (Small Example)

You are in the direct message channel with the bot and enter the command `getq` and the bot will show you a list of servers you are in with where the bot is used. Once you choose the server, the bot will ask you for a question number. It will then send you the requested question and answer (where applicable) from the selected server.

```
$getq"
```

Successful execution of this command will display the requested question and answer (where applicable) for the requested server. If a server or question is requested that doesn't exist, the bot returns a message saying the user has selected an invalid option.
