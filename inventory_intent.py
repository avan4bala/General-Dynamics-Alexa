import logging

from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.utils import is_intent_name
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response, IntentRequest, Slot

from ask_sdk_model.ui import SimpleCard

import services

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class InventoryIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("InventoryIntent")(handler_input)

    def handle(self, handler_input):
        logger.info("In InventoryIntentHandler")
        # service slot resolution
        try:
            svc = handler_input.request_envelope.request.intent.slots['service']
            svc = svc.resolutions.resolutions_per_authority[0].values[0].value.name
        except Exception:
            svc = handler_input.request_envelope.request.intent.slots['service'].value
        # check if cost slot was used
        try:
            cst = handler_input.request_envelope.request.intent.slots['cost'].value
        except Exception:
            cst = None
        
        speech = f'There was a problem with the service {svc}'
        if 'vpc' in svc:
            speech = services.get_vpc_info()
        elif 'snapshot' in svc:
            speech = services.get_snapshot_info()
        elif 'route' in svc:
            speech = services.get_route_info()
        elif 'volume' in svc:
            speech = services.get_volume_info()
        elif 'security group' in svc:
            speech = services.get_sg_info()
        elif 'subnet' in svc:
            speech = services.get_subnet_info()
        elif 'ec two' in svc:
            speech = services.get_ec2_info()
        elif 'reserved instance' in svc:
            speech = services.get_num_ri_instances()
        # speech = f'Service {svc} and Cost {cst}'
        handler_input.response_builder.speak(speech).set_should_end_session(False)
        return handler_input.response_builder.response
