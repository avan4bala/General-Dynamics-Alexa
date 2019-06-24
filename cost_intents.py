from ask_sdk_core.utils import is_intent_name
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from cost_utils import *
import random


INFORMATION = None
IS_PREDICT = False


def set_information(info: dict, metrics: str = '', granularity: str = ''):
    """
    Function that sets the information global dictionary to be sent in an email
    :param info: The dictionary returned from get_cost_and_usage or get_cost_forecast
    :param metrics: the metrics associated with :param: info
    :param granularity: the granularity associated with :param: info
    :return:
    """
    global INFORMATION
    print("Value of INFORMATION before {}".format(INFORMATION))
    INFORMATION = {
        'Info': info,
        'Metrics': metrics,
        'Granularity': granularity
    }
    print("Value of INFORMATION after {}".format(INFORMATION))


class PredictYearlyCostsIntentClass(AbstractRequestHandler):

    def can_handle(self, handler_input):  # type (HandlerInput) -> bool
        return is_intent_name("PredictYearlyCostsIntent")(handler_input)

    def handle(self, handler_input):  # type (HandlerInput) -> Union[None, Response]
        """
        Function that handles the PredictYearlyCostsIntent. Predicts how much money will be spent in a year.
        :param handler_input: the Response object to interact with Alexa
        :return: Alexa's response
        """

        # makes a CostExplorer client
        cost_explorer = get_role()

        slots = handler_input.request_envelope.request.intent.slots
        start_date = slots['startDate'].value
        end_date = slots['endDate'].value

        print("Start date type: {}, and end date type {}".format(type(start_date), type(end_date)))

        if start_date is None or end_date is None:
            print("start date {} is either none or end date is either none {} ebfore".format(start_date, end_date))

            tomorrow: datetime.date = get_next_day(TODAY)
            start_date: datetime.date = tomorrow
            end_date: datetime.date = get_year_bef_and_after()[1]
            print("start date {} is either none or end date is either none {} after".format(start_date, end_date))

        else:
            start_date = get_date_object(start_date)
            end_date = get_date_object(end_date)

        # creates the time period dict needed for the get_cost_forecast method
        if not within_a_year_range(start_date, end_date):

            speech = f"Dates must be between {get_next_day(TODAY)}, and {get_year_bef_and_after()[1]}"

        elif not is_date_in_future(start_date) or not is_date_in_future(end_date):

            print("start date {} and end date {}".format(start_date.isoformat(), end_date.isoformat()))

            speech = "Dates must be specified in the future to predict account spending accurately."

        elif not is_valid_date_range(start_date, end_date):

            speech = "End date is before the start date."

        else:

            time_period = {
                'Start': start_date.isoformat(),
                'End': end_date.isoformat()
            }

            # needs to be one string unlike get_cost_and_useage, where that is a list of strings
            metrics = 'NET_UNBLENDED_COST'

            # gets the prediction info collected within a dict
            prediction_info = cost_explorer.get_cost_forecast(TimePeriod=time_period,
                                                              Metric=metrics,
                                                              Granularity=GRANULARITY_DEFAULT)

            # gives the information to the INFORMATION dictionary to be sent in an email if the user requests
            set_information(prediction_info)
            global IS_PREDICT
            IS_PREDICT = True

            speech = "The estimated amount of money that you will " \
                     "spend from {} to {} is ${:.2f} {}".format(time_period['Start'],
                                                                time_period['End'],
                                                                float(prediction_info['Total']['Amount']),
                                                                prediction_info['Total']['Unit'])

        # handles the response to alexa
        handler_input.response_builder.speak(speech).set_should_end_session(False)
        return handler_input.response_builder.response


class GetCostsFromRangeIntentClass(AbstractRequestHandler):

    def can_handle(self, handler_input):  # type (HandlerInput) -> Union[None, Response]
        return is_intent_name("GetCostsFromRangeIntent")(handler_input)

    def handle(self, handler_input):  # type (HandlerInput) -> bool
        """
        Function that handles the GetCostsFromRangeIntent. Allows the user to get costs for their account from a range
        of dates.
        :param handler_input: the Response object to interact with Alexa
        :return: Alexa's response
        """

        # make a cost explorer assuming into a role
        cost_explorer = get_role()

        # make a slot object to get the slots
        dates = handler_input.request_envelope.request.intent.slots
        start_date = dates['startDate'].value
        end_date = dates['endDate'].value
        target_date = dates['targetDate'].value

        print("target_date type {}".format(type(target_date)))

        if start_date is None or end_date is None:

            if target_date is None:

                start_date = get_year_bef_and_after()[0]
                end_date = get_yesterday(TODAY)

            else:

                target_date = get_date_object(target_date)
                tomorrows_date = get_next_day(target_date)

                if within_current_year(target_date, tomorrows_date) and not is_date_in_future(target_date) and \
                        not is_date_in_future(tomorrows_date):

                    start_date = target_date
                    end_date = tomorrows_date

                    time = {
                        'Start': target_date.isoformat(),
                        'End': tomorrows_date.isoformat()
                    }
                else:

                    speech = "You must select a valid date range from {} to {}, sorry.".format(
                        get_year_bef_and_after()[0],
                        get_yesterday(TODAY))
                    handler_input.response_builder.speak(speech).set_should_end_session(False)
                    return handler_input.response_builder.response

        # make a time dictionary for get_cost_and_usage. If two dates are not provided, then one year from current date
        # default is set.
        else:
            start_date = get_date_object(start_date)
            end_date = get_date_object(end_date)

        if not is_valid_date_range(start_date, end_date):

            speech = 'The start date is after the end date'

        elif is_date_in_future(start_date) or is_date_in_future(end_date):

            print("Start date {} and end date {}".format(start_date, end_date))
            speech = f"Date in future. Dates need to be between {get_year_bef_and_after()[0]} and {TODAY}."

        elif not within_current_year(start_date, end_date):

            speech = f"Dates need to be between {get_year_bef_and_after()[0]} and {TODAY}."

        elif not within_a_year_range(start_date, end_date):

            speech = f"Dates need to be between one year of each other."

        else:

            time = {
                'Start': start_date.isoformat(),
                'End': end_date.isoformat()
            }

            metrics = dates['metrics'].value
            metrics_unchanged = dates['metrics'].value

            # parsing the user specified cost into acceptable format. i.e blended cost -> BlendedCost
            metrics: str = metrics_formatter(metrics)

            # gets the granularity
            granularity = dates['granularity'].value

            # checks to see if the granularity is None/null and if it isn't,
            # convert it into a string and make it upper case

            # checks to see if Metrics is none, if it is set it to the default metrics
            if metrics is None or metrics == "None":
                metrics = METRICS_DEFAULT

            # checks to see if the granularity is none; if it is then set it to the default granularity
            if granularity is None:
                granularity: str = GRANULARITY_DEFAULT
            else:
                granularity: str = str(granularity).upper()

            # checks to see if the metrics_unchanged variable is None; if it is None then set to default granularity
            if metrics_unchanged is None:
                metrics_unchanged = METRICS_DEFAULT

            # if metrics is NetAmortizedCost or NetUnblendedCost, these services aren't available
            # from before October 2018, so we must change the time period.
            if metrics == "NetAmortizedCost" or metrics == 'NetUnblendedCost':
                before_year: datetime.date = datetime.date(TODAY.year-1, 10, 1)
                is_within_year: bool = within_a_year_range(before_year, end_date)

                if check_if_after_oct(start_date) and within_a_year_range(start_date, end_date):
                    time = {
                        'Start': start_date.isoformat(),
                        'End': end_date.isoformat()
                    }

                else:

                    if is_within_year:
                        time = {
                            'Start': before_year.isoformat(),
                            'End': end_date.isoformat()
                        }

                    else:

                        time = {
                            'Start': before_year.isoformat(),
                            'End': TODAY.isoformat()
                        }

            # gets the cost and usage as a dictionary
            # sets metrics to a default of BlendedCost and granularity to MONTHLY if
            # these values are not provided
            info = cost_explorer.get_cost_and_usage(TimePeriod=time, Granularity=granularity, Metrics=[metrics])

            # gives the information to the INFORMATION dictionary to be sent in an email if the user requests
            set_information(info, metrics, granularity)

            # gets the amount of money summed up from the cost_and_usage method dictionary
            amount = sum_money_dict(info=info, metrics=metrics)

            if target_date is not None:
                speech = "This account has spent {:.2f} USD on {}".format(amount, target_date)

            else:

                speech = "The amount of money you have spent from {} to" \
                         " {} is ${:.2f} USD, using the metrics {}.".format(
                            time['Start'],
                            time['End'],
                            amount,
                            metrics_unchanged
                            )

        # handles the response that alexa will say back to you
        handler_input.response_builder.speak(speech).set_should_end_session(False)
        return handler_input.response_builder.response


class CurrentMonthlyTotalIntentClass(AbstractRequestHandler):
    """
    Class that handles the CurrentMonthlyTotalIntent intent.
    """

    def can_handle(self, handler_input):
        return is_intent_name("CurrentMonthlyTotalIntent")(handler_input)

    def handle(self, handler_input):
        """
        Handles the CurrentMonthlyTotalIntent
        :param handler_input:
        :return:
        """

        cost_explorer = get_role('ce')

        today = datetime.datetime.now().date()
        start_of_month = str(datetime.date(today.year, today.month, 1))
        time_period = {
            'Start': start_of_month,
            'End': str(today)
        }

        info = cost_explorer.get_cost_and_usage(
            TimePeriod=time_period,
            Metrics=[METRICS_DEFAULT],
            Granularity='DAILY'
        )

        # gives the information to the INFORMATION dictionary to be sent in an email if the user requests
        set_information(info, METRICS_DEFAULT, 'DAILY')

        amount = sum_money_dict(info, METRICS_DEFAULT)

        speech = "Your current monthly total is {:.2f} USD.".format(amount)

        handler_input.response_builder.speak(speech).set_should_end_session(False)

        return handler_input.response_builder.response


class AverageMonthlyCostIntent(AbstractRequestHandler):
    """
    Handles the Average Monthly costs intent.
    """

    def can_handle(self, handler_input):
        return is_intent_name("AverageMonthlyCostIntent")(handler_input)

    def handle(self, handler_input):

        cost_explorer = get_role("ce")
        time_period = {
            'Start': get_year_bef_and_after()[0].isoformat(),
            'End': TODAY.isoformat()
        }

        info = cost_explorer.get_cost_and_usage(
            TimePeriod=time_period,
            Metrics=[METRICS_DEFAULT],
            Granularity=GRANULARITY_DEFAULT
        )

        set_information(info, METRICS_DEFAULT, GRANULARITY_DEFAULT)

        amount = sum_money_dict(info, METRICS_DEFAULT)

        speech = 'Your monthly average cost is {:.2f} USD over the previous 12 months.'.format(amount/12)

        handler_input.response_builder.speak(speech).set_should_end_session(False)

        return handler_input.response_builder.response


class EasterEggIntentClass(AbstractRequestHandler):

    def can_handle(self, handler_input):  # type (HandlerInput) -> bool
        return is_intent_name("EasterEggIntent")(handler_input)

    def handle(self, handler_input):  # type (HandlerInput) -> Union[None, Response]
        """
        Easter egg function
        :param handler_input: The response object
        :return: Alexas response
        """
        responses = [
            'Congrats you found the hidden phrase',
            'Took you this long huh?',
            'The amount of money that you spent over 4 thousand year is 1 half of a cent',
            'You were not supposed to say that'
        ]

        random_phrase = random.randint(0, len(responses) - 1)

        handler_input.response_builder.speak(responses[random_phrase]).set_should_end_session(False)

        return handler_input.response_builder.response


class EmailReportIntent(AbstractRequestHandler):
    """
    This class handles the EmailReportIntent which is designed to send the user an email with a summary report.
    """
    def can_handle(self, handler_input):  # type: (HandlerInput) -> bool
        return is_intent_name("EmailReportIntent")(handler_input)

    def handle(self, handler_input):  # type: (HandlerInput) -> Union[None, Response]
        """
        Function that actually sends the email
        :param handler_input: The Response object for Alexa
        :return: Alexas response
        """
        # Information holds the information to send in an email
        global INFORMATION

        # This boolean dictates if the information came from the get_forecast method from the PredictYearlyCostsClass
        global IS_PREDICT

        slots = handler_input.request_envelope.request.intent.slots
        email_address = slots['emailAddress'].value

        # sets a default value of my fake gmail account for testing purposes
        if email_address is None:
            recipient = "floodspamdude@gmail.com"
        else:
            recipient = email_address

        print("INFO inside email report handler {}".format(INFORMATION))

        # if the INFORMATION is None, then no data has been sent to the INFORMATION dict
        if INFORMATION is None:
            speech = "No data to send! Make sure to add some data."

        # The INFORMATION has available content, so we make sure to send the email.
        else:
            speech = "Sending email!"
            if IS_PREDICT:
                response = get_predict_dict_info(INFORMATION['Info'])
            else:
                response = get_dict_info(INFORMATION['Info'], INFORMATION['Metrics'], INFORMATION['Granularity'])
            # Sends the email with the response
            send_email(response, sender="Cosmin.Velea@gdit.com", recipient=recipient)

            # sets both of these variables back to None and False.
            INFORMATION = None
            IS_PREDICT = False

        # handles and returns alexas response
        handler_input.response_builder.speak(speech).set_should_end_session(False)
        return handler_input.response_builder.response


class CancelSummaryReportIntentClass(AbstractRequestHandler):

    def can_handle(self, handler_input):  # type: (HandlerInput) -> bool
        return is_intent_name("CancelEmailReportIntent")(handler_input)

    def handle(self, handler_input):  # type: (HandlerInput) -> Union[None, Response]

        global INFORMATION

        if INFORMATION is None:
            speech = "There was no data to begin with, but I'll forget about it, dont worry."
        else:
            speech = "Email summary report erased."
            INFORMATION = None

        handler_input.response_builder.speak(speech).set_should_end_session(False)
        return handler_input.response_builder.response
