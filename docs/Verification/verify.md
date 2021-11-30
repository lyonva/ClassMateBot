# About $verify (Updated in Project 3)

This command verifies the user by getting their full name, storing this with their username in the database, and then granting access to the guild channels

# Location of Code

The code that implements the above mentioned gits functionality is located [here](https://github.com/lyonva/ClassMateBot/blob/main/bot.py) and [here](https://github.com/lyonva/ClassMateBot/blob/main/cogs/newComer.py).

# Code Description

## Functions

1. <em> <b> def on*guild_join(guild)</em> </b>: <br> This function gets called when the ClassMateBot joins a new guild. It first creates the "instructor-commands", "q-and-a" and "verification" channels if they don't already exist. It then check if the required roles (Instructor, verified and unverified) exist and if they don't, create them. The roles are then assigned to the members of the guild. <b>Note</b>: the bot must be running \_before* it is added to a new guild in order for this function to run.<br>

2. <em><b>def on_member_join(member)</em></b>: <br> This function gets called when a new member joins the guild. It sends a DM to the new member asking them to verify with appropriate instructions. It takes as arguments the object of the member who has joined the server. <br>

3. <em><b>def verify(self, ctx, \*, name: str = None)</em></b>: <br> This command is used to get the full name of the user and assign user the verified role. It takes as arguments the values provided by the constructor through self, context in which the command was called and full name of the user. It will then store the guild, username, and verified name of the user in the name_mapping table in the database. Once this information is stored, the bot will remove the "unverified" role from the user and replace it with the "verified" role, allowing the user to interact within the guild.

##### How to run it? (Small Example)

Let's say that you join the server that has the Classmate Bot active and online. You won't have the access to the channels as you will be assigned an unverified role. You will only be able to see the general channel and not send messages anywhere except the verification channel. You will receive a DM from the Classmate Bot telling you the verification steps. All you have to do is enter the command '$verify' and pass in your full name as a parameter.

```
$verify your_full_name
$verify Jane Doe
```

Successful execution of this command will assign you a verified role and give you the access to the channels. You will also receive a welcome message from ClassMateBot with important links related to the course.

![image]()
