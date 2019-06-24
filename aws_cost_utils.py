import datetime
import boto3
from boto3.session import Session
from botocore.exceptions import ClientError


METRICS_DEFAULT = 'BlendedCost'
GRANULARITY_DEFAULT = 'MONTHLY'
TODAY = datetime.datetime.now().date()


def get_year_bef_and_after():
    """
    Function that gets a list of dates exactly one year before and one year after todays date.
    :return: The list of dates.
    """
    current_date = datetime.datetime.now().date()
    one_year_before_date = current_date - datetime.timedelta(365)
    one_year_after_date = current_date + datetime.timedelta(366)

    return [one_year_before_date, one_year_after_date]


def get_date_object(date: str):
    """
    Gets the date object of the current string. YYYY-MM-DD
    :param date: The string date that needs to be transformed into a date object
    :return: The specific date object
    """
    return datetime.datetime.strptime(date, '%Y-%m-%d').date()


def within_current_year(start_date: datetime.date, end_date: datetime.date):
    """
    Function that verifies that both parameters are within the current year.
    :param start_date: The start date
    :param end_date: End date
    :return: True if both parameters are in the current year.
    """

    return get_year_bef_and_after()[0] < start_date and end_date < get_year_bef_and_after()[1]


def within_a_year_range(start_date: datetime.date, end_date: datetime.date, num_days: int = 366):
    """
    Function that checks to see if a date is between a given range, which in this case is a year.
    :param start_date: The start date to be checked
    :param end_date: The end date to be checked
    :param num_days: The number of allowed days between those dates
    :return: True if the two dates are within the allotted num_days; False otherwise.
    """

    return end_date - start_date < datetime.timedelta(num_days)


def is_date_in_future(date: datetime.date):
    """
    Determines if the incoming date is in the future
    :param date: The incoming date
    :return: True if the incoming date is in the current future; False otherwise.
    """
    return date > datetime.datetime.now().date()


def is_valid_date_range(start_date: datetime.date, end_date: datetime.date) -> bool:
    """
    Function that checks to see if this date is a valid start date to end date. Format is YYYY-MM-DD
    :param start_date: the start date
    :param end_date: the end date
    :return: True if the end date is after the start date; False if otherwise
    """

    return start_date < end_date


def get_next_day(date: datetime.date):
    """
    Function that gets the next date based on the incoming parameter
    :param date: The date. Format must be YYYY-MM-DD
    :return: Tomorrows date based on :param date
    """
    return date + datetime.timedelta(1)


def get_yesterday(date: datetime.date):
    """
    Function that gets yesterdays date. absolute pain...
    :param date: The initial date. Must have the formal YYYY-MM-DD
    :return: the before date
    """

    return date - datetime.timedelta(1)


def sum_money_dict(info: dict, metrics: str):
    """
    Function that returns the total amount of money from the returned dictionary of get_cost_and_usage
    :param info: the dict returned from get_cost_and_usage
    :param metrics: the metrics the user requested; BlendedCost is the default
    :return: the amount of money
    """

    money = info['ResultsByTime']
    amount = 0

    # indexes into the money list/dict, which holds all of the information about the money per month, and totals it
    for dollars in money:
        amount += float(dollars['Total'][metrics]['Amount'])

    return amount


def get_money_from_target_date(info: dict, metrics, target_date):
    """
    Function that gets the money from the returned dictionary of get_cost_and_usage
    :param info: the dict returned of get_cost_and_usage
    :param metrics: the metrics the users requested
    :param target_date: the target date the user requested
    :return: the amount of money on the target date; None if no target date was found
    """

    for dates in info['ResultsByTime']:
        if dates['TimePeriod']['Start'] == target_date:
            return float(dates['Total'][metrics]['Amount'])
    return None


def metrics_formatter(metrics):
    """
    Formats the metrics to be the appropriate format. i.e blended cost -> BlendedCost.
    :param metrics: the metrics string to be formatted
    :return: the formatted metric. Returns None if metrics is None
    """

    if metrics is None or metrics == "None":
        return None

    metrics_date = metrics.split(' ')
    tmp_metrics_date = []

    for entries in metrics_date:
        new_entry = entries[0].upper() + entries[1:]
        tmp_metrics_date.append(new_entry)

    metrics = ''

    for entries2 in tmp_metrics_date:
        metrics += entries2

    return metrics


def check_if_after_oct(start_date: datetime.date) -> bool:
    """
    Function that checks to see if the date is after October 2018
    :param start_date: the date to be checked
    :return: True if it is after October 2018, False otherwise.
    """

    return start_date >= datetime.date(2018, 10, 1)


def get_role(svc='ce'):
    """
    Function that assumes into a role to get into the CostExplorer
    :return: the CostExplorer client object
    """

    cross_acc_role_arn = "arn:aws:iam::927499810012:role/aws-audit-crossacct-role"
    # create a sts client in order to assume into a role
    client = boto3.client('sts')
    response = client.assume_role(
        RoleArn=cross_acc_role_arn,
        RoleSessionName="NewSession",
    )

    # create a session object
    session = Session(
        aws_access_key_id=response['Credentials']['AccessKeyId'],
        aws_secret_access_key=response['Credentials']['SecretAccessKey'],
        aws_session_token=response['Credentials']['SessionToken']
    )

    # create a client with the assumed role
    new_client = session.client(svc)
    return new_client


def get_predict_dict_info(info: dict):
    """
    Gets the information from the dictionary returned from the get_cost_forecast
    :param info: the returned dictionary
    :return: the response to go into the email
    """

    response = '=========================================|<br>\n'
    total = float(info['Total']['Amount'])

    for data in info['ForecastResultsByTime']:
        forecast_time_period = data['TimePeriod']['Start'] + " to " + data['TimePeriod']['End']
        mean_value = data['MeanValue']
        prediction_lower_bound = ''#data['PredictionIntervalLowerBound']
        prediction_upper_bound = ''#data['PredictionIntervalUpperBound']
        response += "========================<br>Forecast time period {}, with mean value {} and prediction lower bound" \
                    " {} and prediction upper bound " \
                    "bound {}<br>\n=================".format(
                        forecast_time_period,
                        mean_value,
                        prediction_lower_bound,
                        prediction_upper_bound)

    return f"Total forecast spending ${total:.2f} USD {response}"


def get_dict_info(info: dict, metrics: str, granularity: str):
    """
    Gets the information from the dictionary returned from get_cost_and_usage
    :param info: the returned dictionary from get_cost_and_usage
    :param metrics: the metrics used
    :param granularity: the granularity used
    :return: the response
    """
    response = '===============================================|<br>\n'
    for information in info['ResultsByTime']:
        start_date = "{}".format(information['TimePeriod']['Start'])
        end_date = "{}".format(information['TimePeriod']['End'])
        money = "${:.2f}" .format(float(information['Total'][metrics]['Amount']))
        response += "|  {} USD on {} to {}    |<br>\n======================" \
                    "=========================|<br>\n".format(money, start_date, end_date)

    return granularity[0].upper() + granularity[1:] + " summary report using {}: <br>\n\n".format(metrics) + response


def test_utils():
    cost_explorer = get_role("ce")
    time_period = {
        'Start': get_year_bef_and_after()[0],
        'End': TODAY
    }
    granularity = 'MONTHLY'
    info = cost_explorer.get_cost_and_usage(
        TimePeriod=time_period,
        Metrics=[METRICS_DEFAULT],
        Granularity=granularity
    )
    return info


def send_email(response: str, sender: str = 'Cosmin.Velea@gdit.com', recipient: str = 'floodspamdude@gmail.com'):
    """
    Function that sends the response to the client from a sender.
    :param sender: The sender of the email
    :param recipient: The recipient of the email
    :param response: The message the email contains
    :return:
    """
    email_client = get_role('ses')
    destination = {
        'ToAddresses': [recipient],
    }
    # The HTML body of the email.
    BODY_HTML = """
    <html>
    <body>
       <h2 style="color:grey;padding:20px"> 
        AWS Account Spending Report Summary
      </h2>
      <div style="padding:20px;color:black"> Below are the account spending data usages. </div>


        <div style="border:3px solid black;padding:10px">
        {}

        </div>


        <h6 style="color:black"> General Dynamics Information Technology<br> 
                  Amazon Web Services<br>
                  This message was sent from Alexa using the CCS Account skill.

       </h6>
    </body>
    </html>
                """.format(response)
    CHARSET = "UTF-8"

    message = {
        'Subject': {
            'Data': 'AWS Report {}'.format(TODAY),
            'Charset': CHARSET
        },
        'Body': {
            'Text': {
                'Data': "bruh moment indeed",
                'Charset': CHARSET
            },
            'Html': {
                'Data': BODY_HTML,
                'Charset': CHARSET
            }
        }
    }

    try:
        response = email_client.send_email(
            Source=sender,
            Destination=destination,
            Message=message
        )

    except ClientError as client:
        print(client.response['Error']['Message'])

    else:
        print(response['MessageId'])


'''
client = get_role('ce')
time_pd = {
    'Start': "2019-01-01",
    'End': TODAY
}

filters = {
    'Dimensions': {
        'Key': 'INSTANCE_TYPE',
        'Values': ['GetDimensionValues']
    }
}


informashun = client.get_cost_and_usage(
    TimePeriod=time_pd,
    Metrics=[METRICS_DEFAULT],
    Granularity=GRANULARITY_DEFAULT,
    Filter=filters
)

print(informashun)
