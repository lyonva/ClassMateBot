# This functionality provides mechanism for students to ask and answer questions
# Students and instructors can choose ask and answer questions anonymously or have their names displayed
from discord import NotFound
from discord.ext import commands
import db
import utils


class Qanda(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # -----------------------------------------------------------------------------------------------------------------
    #    Function: askQuestion(self, ctx, qs: str, anonymous)
    #    Description: takes question from user and reposts anonymously and numbered
    #    Inputs:
    #       - ctx: context of the command
    #       - qs: question text
    #       - anonymous: option if user wants their question to be shown anonymously
    #    Outputs:
    #       - User question in new post
    # -----------------------------------------------------------------------------------------------------------------
    @commands.command(
        name="ask",
        help="Ask question. Please put question text in quotes. Add *anonymous* if desired."
        'EX: $ask /"When is the exam?/" anonymous',
    )
    async def askQuestion(self, ctx, qs: str, anonymous=""):

        # make sure to check that this is actually being asked in the Q&A channel
        if not ctx.channel.name == "q-and-a":
            await ctx.author.send("Please send questions to the #q-and-a channel.")
            await ctx.message.delete()
            return

        # get author
        if anonymous == "":
            author = ctx.message.author.id
        elif anonymous == "anonymous":
            author = None
        else:
            await ctx.author.send("Unknown input for *anonymous* option. Please type **anonymous** or leave blank.")
            await ctx.message.delete()
            return

        # get number of questions + 1
        num = 0
        questions = db.query("SELECT * FROM questions WHERE guild_id = %s", (ctx.guild.id,))
        if questions == []:
            num = 1
        else:
            num = db.query("SELECT MAX(number) FROM questions WHERE guild_id = %s", (ctx.guild.id,))[0][0] + 1

        # format question
        author_str = "anonymous" if author is None else (await self.bot.fetch_user(author)).name
        q_str = f"Q{num}: {qs} by {author_str}"

        message = await ctx.send(q_str)

        # add to db
        db.query(
            "INSERT INTO questions (guild_id, number, question, author_id, msg_id) VALUES (%s, %s, %s, %s, %s)",
            (ctx.guild.id, num, qs, author, message.id),
        )

        # delete original question
        await ctx.message.delete()

    # -----------------------------------------------------------------------------------------------------------------
    #    Function: ask_error(self, ctx, error)
    #    Description: prints error message for ask command
    #    Inputs:
    #       - ctx: context of the command
    #       - error: error message
    #    Outputs:
    #       - Error details
    # -----------------------------------------------------------------------------------------------------------------
    @askQuestion.error
    async def ask_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.author.send(
                'To use the ask command, do: $ask "QUESTION" anonymous*<optional>* \n '
                '(For example: $ask "What class is this?" anonymous)'
            )
        else:
            await ctx.author.send(error)
        await ctx.message.delete()

    # -----------------------------------------------------------------------------------------------------------------
    # Function: answer
    # Description: adds user answer to specific question and post anonymously
    # Inputs:
    #      - ctx: context of the command
    #      - num: question number being answered
    #      - ans: answer text to question specified in num
    #      - anonymous: option if user wants their question to be shown anonymously
    # Outputs:
    #      - User answer added to question post
    # -----------------------------------------------------------------------------------------------------------------
    @commands.command(
        name="answer",
        help="Answer question. Please put answer text in quotes. Add *anonymous* if desired."
        'EX: $answer 1 /"Oct 12/" anonymous',
    )
    async def answer(self, ctx, num, ans, anonymous=""):
        """answer the specific question"""
        # make sure to check that this is actually being asked in the Q&A channel
        if not ctx.channel.name == "q-and-a":
            await ctx.author.send("Please send answers to the #q-and-a channel.")
            await ctx.message.delete()
            return

        # get author
        if anonymous == "":
            author = ctx.message.author.id
        elif anonymous == "anonymous":
            author = None
        else:
            await ctx.author.send("Unknown input for *anonymous* option. Please type **anonymous** or leave blank.")
            await ctx.message.delete()
            return

        # check if question number exists
        q = db.query(
            "SELECT number, question, author_id, msg_id FROM questions WHERE guild_id = %s AND number = %s",
            (ctx.guild.id, num),
        )
        if len(q) == 0:
            await ctx.author.send("Invalid question number: " + str(num))
            # delete user msg
            await ctx.message.delete()
            return
        q = q[0]

        # check if message exists
        try:
            message = await ctx.fetch_message(q[3])
        except NotFound:
            await ctx.author.send("Invalid question number: " + str(num))
            # delete user msg
            await ctx.message.delete()
            return

        # add answer to db
        if "instructor" in [y.name.lower() for y in ctx.author.roles]:
            role = "Instructor"
        else:
            role = "Student"
        db.query(
            "INSERT INTO answers (guild_id, q_number, answer, author_id, author_role) VALUES (%s, %s, %s, %s, %s)",
            (ctx.guild.id, num, ans, author, role),
        )

        # generate and edit msg with answer
        q_author_str = "anonymous" if q[2] is None else (await self.bot.fetch_user(q[2])).name
        new_answer = f"Q{q[0]}: {q[1]} by {q_author_str}\n"

        # get all answers for question and add to msg
        answers = db.query(
            "SELECT answer, author_id, author_role FROM answers WHERE guild_id = %s AND q_number = %s",
            (ctx.guild.id, num),
        )
        for answer, author, role in answers:
            a_author = "anonymous" if author is None else (await self.bot.fetch_user(author)).name
            new_answer += f"{a_author} ({role}) Ans: {answer}\n"

        # edit message
        try:
            await message.edit(content=new_answer)
        except NotFound:
            await ctx.author.send("Invalid question number: " + str(num))

        # delete user msg
        await ctx.message.delete()

    # -----------------------------------------------------------------------------------------------------------------
    #    Function: answer_error(self, ctx, error)
    #    Description: prints error message for answer command
    #    Inputs:
    #       - ctx: context of the command
    #       - error: error message
    #    Outputs:
    #       - Error details
    # -----------------------------------------------------------------------------------------------------------------
    @answer.error
    async def answer_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.author.send(
                'To use the answer command, do: $answer QUESTION_NUMBER "ANSWER" anonymous*<optional>*\n '
                '(For example: $answer 2 "Yes")'
            )
        else:
            await ctx.author.send(error)
        await ctx.message.delete()

    # -----------------------------------------------------------------------------------------------------------------
    # Function: getQAs
    # Description: returns all questions and answers
    # Inputs:
    #      - ctx: context of the command
    # Outputs:
    #      - User answer added to question post
    # -----------------------------------------------------------------------------------------------------------------
    @commands.command(name="getQAs", help="Sends DM of all questions and answers" "EX: $getQAs")
    async def getQAs(self, ctx):
        results = await utils.chooseGuild(self, ctx)
        guild_list = results[0]
        msg = results[1]
        result = ""
        questions = db.query(
            "SELECT number, question FROM questions WHERE guild_id = %s",
            (guild_list[msg - 1],),
        )
        if questions == []:
            result = "No questions have been asked"
        else:
            for q_num, question in questions:
                num = q_num
                question_string = question
                result += f"Q{num}: {question_string}\n"
                answers = db.query(
                    "SELECT answer FROM answers WHERE guild_id = %s AND q_number = %s",
                    (guild_list[msg - 1], num),
                )
                if answers == []:
                    answer_string = "No answer"
                    result += f"Answer: {answer_string}\n\n"
                else:
                    for answer in answers:
                        answer_string = answer[0]
                        result += f"Answer: {answer_string}\n\n"
        await ctx.author.send(result)

    # -----------------------------------------------------------------------------------------------------------------
    # Function: getq
    # Description: returns the requested question and answer
    # Inputs:
    #      - ctx: context of the command
    #      - num: question number to get
    # Outputs:
    #      - Question and appropriate answer (if one exists)
    # -----------------------------------------------------------------------------------------------------------------
    @commands.command(name="getq", help="Sends DM of all questions and answers" "EX: $getq 1")
    async def getQuestion(self, ctx):
        results = await utils.chooseGuild(self, ctx)
        msg = results[1]
        guild_list = str(results[0][msg - 1])
        result = ""
        num = str(await chooseNumber(self, ctx))
        questions = db.query(
            "SELECT number, question FROM questions WHERE guild_id = %s and number = %s",
            (guild_list, num),
        )
        if questions == []:
            result = "This question doesn't exist"
        else:
            for q_num, question in questions:
                num = q_num
                question_string = question
                result += f"Q{num}: {question_string}\n"
                answers = db.query(
                    "SELECT answer FROM answers WHERE guild_id = %s AND q_number = %s",
                    (guild_list[msg - 1], num),
                )
                if answers == []:
                    answer_string = "No answer"
                    result += f"Answer: {answer_string}\n\n"
                else:
                    for answer in answers:
                        answer_string = answer[0]
                        result += f"Answer: {answer_string}\n\n"
        await ctx.author.send(result)

    # -----------------------------------------------------------------------------------------------------------------
    # Function: deleteq
    # Description: deletes a specific question/answer (if it exists) if you are an instructor
    # Inputs:
    #      - ctx: context of the command
    #      - num: question number to delete
    # Outputs:
    #      - Confirmation/denial that question/answer was deleted
    # -----------------------------------------------------------------------------------------------------------------
    @commands.command(name="deleteq", help="Deletes a requested question if you are an instructor" "EX: $deleteq")
    @commands.has_role("Instructor")
    async def deleteQuestion(self, ctx):
        await ctx.message.delete()
        guild_id = ctx.guild.id
        num = str(await chooseNumber(self, ctx))
        questions = db.query(
            "SELECT number FROM questions WHERE guild_id = %s and number = %s",
            (guild_id, num),
        )

        # If a question isn't found for a particular server, an error is given
        if questions == []:
            await ctx.send(f"Question {num} does not exist")
        else:
            for q_num in questions:
                num = str(q_num[0])
                answers = db.query(
                    "SELECT answer FROM answers WHERE guild_id = %s AND q_number = %s",
                    (guild_id, num),
                )

                # If a question doesn't have an answer, just the question is deleted
                if answers == []:
                    db.query(
                        "DELETE FROM questions WHERE guild_id = %s and number = %s",
                        (guild_id, num),
                    )

                # If a question does have an answer, the question and answer is deleted
                else:
                    db.query(
                        "DELETE FROM questions WHERE guild_id = %s and number = %s",
                        (guild_id, num),
                    )
                    db.query(
                        "DELETE FROM answers WHERE guild_id = %s and q_number = %s",
                        (guild_id, num),
                    )
                await ctx.send(
                    f"Question {num} has been deleted\n"
                )  # Tells the user a question and/or answer has been deleted


# -----------------------------------------------------------------------------------------------------------------
# Function: chooseNumber
# Description: asks for user input to enter a number which is used by various other functionalities
# Inputs:
#      - ctx: context of the command
# Outputs:
#      - msg_int: int representation of the number the user entered
# -----------------------------------------------------------------------------------------------------------------
async def chooseNumber(self, ctx):
    msg = ""
    msg_int = 0

    def check(m):
        return m.content is not None and m.channel == ctx.channel and m.author == ctx.author

    valid_answer = False
    msg_array = []
    while valid_answer == False:
        msg = ""
        if ctx.guild == None:
            await ctx.author.send("Please enter a question number: \n")
        else:
            first = await ctx.send("Please enter a question number: \n")
            msg_array.append(first.id)
        msg = await self.bot.wait_for("message", check=check)
        msg_array.append(msg.id)
        try:
            msg_int = int(msg.content)
            valid_answer = True
        except Exception as e:
            print(e)
            if ctx.guild == None:
                await ctx.author.send(
                    "You have entered an invalid option\n" + "Please make sure you are entering an integer"
                )
            else:
                second = await ctx.send(
                    "You have entered an invalid option\n" + "Please make sure you are entering an integer"
                )
                array_count = 0
                for id in msg_array:
                    to_delete = await ctx.fetch_message(str(id))
                    await to_delete.delete()
                    array_count += 1
                current_count = 0
                while current_count < array_count:
                    msg_array.pop(0)
                    current_count += 1
                msg_array.append(second.id)
    for id in msg_array:
        to_delete = await ctx.fetch_message(str(id))
        await to_delete.delete()
    return msg_int


def setup(bot):
    n = Qanda(bot)
    bot.add_cog(n)
