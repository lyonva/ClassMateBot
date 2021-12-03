# About $updatepin _(Modified Command in Project 3)_

This command lets the student to update a pinned message with a new link from the discord channel to their private pinning board.

# Location of Code

The code that implements the above mentioned gits functionality is located [here](https://github.com/lyonva/ClassMateBot/blob/main/cogs/pinning.py).

# Code Description

## Functions

<em> <b> updatePinnedMessage(self, ctx, tagname: str, \*, description: str) </b> </em>: <br> This function takes as arguments the values provided by the constructor through self, context in which the command was called, tagname of the old pinned message, and the new description given by the student.

##### How to run it? (Small Example)

Want to update an existing pin? Just use the "$updatepin" command.

```
$updatepin TAGNAME DESCRIPTION
$updatepin HW https://discordapp.com/channels/139565116151562240/139565116151562240/890814489480531969 HW8 reminder
```

The bot currently deletes the old pin and creates a new one to update a pin.Hence, the bot will first ask you which server you want the pin removed from and then which server you want the pin to be created in. (future improvement) 

![](https://github.com/lyonva/ClassMateBot/blob/main/data/media/updatepin.JPG)
