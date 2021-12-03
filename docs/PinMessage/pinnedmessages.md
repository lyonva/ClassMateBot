# About $pinnedmessages _(Modified Command in Project 3)_

This command lets the student to retrieve all the pinned messages from their private pinning board with an optional given tagname.

# Location of Code

The code that implements the above mentioned gits functionality is located [here](https://github.com/lyonva/ClassMateBot/blob/main/cogs/pinning.py).

# Code Description

## Functions

<em> <b> retrieveMessages(self, ctx, tagname: str = "") </b> </em>: This function takes as arguments the values provided by the constructor through self, context in which the command was called, the optional tag-name of the pinned message(s).

##### How to run it? (Small Example)

You want to see all your pinned messages or the ones with a particular tag? Enter the command "$pinnedmessage" as a DM. To get messages with a particular tag, just pass the tag as an argument.

```
$pinnedmessages TAGNAME(optional)
$pinnedmessages HW
```

The bot will ask you to enter the server from which you want to see the pinned messages.

Successful execution would give the result as shown

![](https://github.com/lyonva/ClassMateBot/blob/main/data/media/pinnedmessages.JPG)
