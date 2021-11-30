# About $pin _(Modified Command in Project 3)_
This command lets the student to pin a message from the discord channel to their private pinning board.

# Location of Code
The code that implements the above mentioned gits functionality is located [here](https://github.com/lyonva/ClassMateBot/blob/main/cogs/pinning.py)

# Code Description
## Functions
<em><b> addMessage(self, ctx, tagname: str, *, description: str)</b> </em>: <br>
This function takes as arguments the values provided by the constructor through self, context in which the command was called, tagname of the pinned message, and the description of the pinned message.

##### How to run it? (Small Example)
Let's say you're are in multiple servers with the bot. You can ask the bot to pin a message for you by sending the "$pin" command as a direct message (dm) to the bot. The arguments passed are the tag and the description.
```
$pin TAGNAME DESCRIPTION
$pin HW https://discordapp.com/channels/139565116151562240/139565116151562240/890813190433292298 HW8 reminder
```

The bot will then ask you which server you want the message to be pinned to.

[insert image here]

Once you select the server, the command will pin the message.

[insert image of successful pin]
