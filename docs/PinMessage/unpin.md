# About $unpin _(Modified Command in Project 3)_

This command lets the student to delete a pinned message from their private pinning board.

# Location of Code

The code that implements the above mentioned gits functionality is located [here](https://github.com/lyonva/ClassMateBot/blob/main/cogs/pinning.py).

# Code Description

## Functions

<em> <b> deleteMessage(self, ctx, tagname: str)</b> </em>: <br> This function takes as arguments the values provided by the constructor through self, context in which the command was called, and the tag-name of the pinned message.

##### How to run it? (Small Example)

Want to remove a pin you made? Just use the "$unpin" command with the tag name for the pin you want to remove as a DM.

```
$unpin TAGNAME
$unpin HW
```

The bot will ask you to choose which server you want to unpin the message from.

[insert image of bot asking for server]

Successful execution of this command will unpin the message with the tagname.

![image]()
