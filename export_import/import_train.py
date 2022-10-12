from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
import json

"""
This is an example showing how to create an export file from
an existing chat bot that can then be used to train other bots.
"""

chatbot = ChatBot("MikuBot")

# First, lets train our bot with some data
trainer = ListTrainer(chatbot)
with open("export.json") as f:
    data = json.load(f)

convos = data["conversations"]

new_list = []

for l in convos:
    if l not in new_list:
        new_list.append(l)

for x in new_list:
    trainer.train(x)
print("done")
