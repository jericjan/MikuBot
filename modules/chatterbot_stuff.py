from chatterbot.trainers import Trainer
from chatterbot.conversation import Statement
from chatterbot import utils


class ListTrainerWithTags(Trainer):
    """
    Allows a chat bot to be trained using a list of strings
    where the list represents a conversation.
    """

    def train(self, conversation, convo_type):
        """
        Train the chat bot based on the provided list of
        statements that represents a single conversation.
        """
        previous_statement_text = None

        statements_to_create = []

        for conversation_count, text in enumerate(conversation):
            if self.show_training_progress:
                utils.print_progress_bar(
                    "List Trainer", conversation_count + 1, len(conversation)
                )

            statement = self.get_preprocessed_statement(
                Statement(
                    text=text,
                    in_response_to=previous_statement_text,
                    conversation=convo_type,
                )
            )

            previous_statement_text = statement.text

            statements_to_create.append(statement)

        self.chatbot.storage.create_many(statements_to_create)
