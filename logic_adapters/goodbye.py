# scrapped

# from chatterbot.logic import LogicAdapter
# from chatterbot.search import IndexedTextSearch
# from chatterbot.conversation import Statement
# from chatterbot.response_selection import get_first_response
# from chattermiku import Goodbye

# class GoodbyeAdapter(LogicAdapter):
#     def __init__(self, chatbot, **kwargs):
#         super().__init__(chatbot, **kwargs)

#     def can_process(self, statement):

#         words = ['goodbye', 'cya', 'byebye', "sayonara"]
#         if any(x in statement.text.lower() for x in words)
#             return True
#         else:
#             return False

#     def process(self, input_statement, additional_response_selection_parameters):
#         raise Goodbye()
