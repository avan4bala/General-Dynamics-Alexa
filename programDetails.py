import boto3
import datetime
from boto3.session import Session
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_core.dispatch_components import AbstractExceptionHandler, AbstractRequestHandler

class InventoryInfoHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):  # type: (HandlerInput) -> bool
        return is_intent_name("inventoryInfo")(handler_input)
    def handle(self, handler_input):  # type: (HandlerInput) -> Union[None, Response]
        # ssm = get_role('ssm')
        instructions: str = "This service has the ability to retrieve inventory reports. This can be from stored accounts that are cached or running accounts from EC2."

        handler_input.response_builder.speak(instructions).set_should_end_session(False)

        return handler_input.response_builder.response

class CostInfoHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):  # type: (HandlerInput) -> bool
        return is_intent_name("costInfo")(handler_input)
    def handle(self, handler_input):  # type: (HandlerInput) -> Union[None, Response]
        # ssm = get_role('ssm')
        instructions = "This service has the ability to retrieve account spending data. It can predict spendings for upcoming years and tell you how much was spent in a previous time period."

        handler_input.response_builder.speak(instructions).set_should_end_session(False)

        return handler_input.response_builder.response

class ErrorCheck(AbstractRequestHandler):
    def can_handle(self, handler_input):  # type: (HandlerInput) -> bool
        return is_intent_name("errorSay")(handler_input)
    def handle(self, handler_input):  # type: (HandlerInput) -> Union[None, Response]
        # ssm = get_role('ssm')
        instructions = "That is all the information I can give you with this service. I have other services that can give you more information!"

        handler_input.response_builder.speak(instructions).set_should_end_session(False)

        return handler_input.response_builder.response

class ExceptionDraftHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):  # type: (HandlerInput) -> bool
        return is_intent_name("exceptionDraft")(handler_input)
    def handle(self, handler_input):  # type: (HandlerInput) -> Union[None, Response]
        # ssm = get_role('ssm')
        instructions = "I don't understand, that is all I can do."

        handler_input.response_builder.speak(instructions).set_should_end_session(False)

        return handler_input.response_builder.response
