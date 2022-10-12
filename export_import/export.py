from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer

"""
This is an example showing how to create an export file from
an existing chat bot that can then be used to train other bots.
"""

chatbot = ChatBot("MikuBot")

# First, lets train our bot with some data
trainer = ChatterBotCorpusTrainer(chatbot)

# Now we can export the data to a file
trainer.export_for_training("export.json")
