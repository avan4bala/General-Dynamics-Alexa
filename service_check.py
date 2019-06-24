import aws_utils
from cost_utils import get_role

ACCOUNT_ID = '927499810012'


def get_ec2_info(service_command='describe_instances'):
    # details of all ec2 instances
    resp = aws_utils.get_service_details(
        account_id=ACCOUNT_ID,
        service_command=service_command,
        service='ec2'
    )

    # this only gets total number of instances..
    num_instances = 0
    for reservation in resp['Reservations']:
        num_instances += len(reservation['Instances'])

    speech = "You have {} ec2 instances in your aws account.".format(num_instances)
    return speech


def get_subnet_info(service_command='describe_subnets'):

    resp = aws_utils.get_service_details(
        account_id = ACCOUNT_ID,
        service_command = service_command,
        service = 'ec2'
    )
    num_subnets = len(resp['Subnets'])

    speech = "You have {} subnets in your aws account.".format(num_subnets)
    return speech


def get_sg_info(service_command='describe_security_groups'):

    resp = aws_utils.get_service_details(
        account_id = ACCOUNT_ID,
        service_command = service_command,
        service = 'ec2'
    )
    num_groups = len(resp['SecurityGroups'])

    speech = "You have {} security groups in your aws account.".format(num_groups)
    return speech


def get_volume_info(service_command='describe_volumes'):

    resp = aws_utils.get_service_details(
        account_id = ACCOUNT_ID,
        service_command = service_command,
        service = 'ec2'
    )
    num_volumes = len(resp['Volumes'])

    speech = "You have {} volumes in your aws account.".format(num_volumes)
    return speech


def get_route_info(service_command='describe_route_tables'):

    resp = aws_utils.get_service_details(
        account_id=ACCOUNT_ID,
        service_command=service_command,
        service='ec2'
    )
    num_route_tables = len(resp['RouteTables'])

    num_routes = 0
    for routeTable in resp['RouteTables']:
        num_routes += len(routeTable['Routes'])

    speech = "You have {} routes and {} route tables in your aws account.".format(num_routes, num_route_tables)
    return speech


def get_snapshot_info(service_command='describe_snapshots'):

    resp = aws_utils.get_service_details(
        account_id = ACCOUNT_ID,
        service_command = service_command,
        service = 'ec2'
    )
    num_snapshots = len(resp['Snapshots'])

    speech = "You have {} snap shots in your aws account.".format(num_snapshots)
    return speech


def get_vpc_info(service_command='describe_vpcs'):

    resp = aws_utils.get_service_details(
        account_id = ACCOUNT_ID,
        service_command = service_command,
        service = 'ec2'
    )
    num_vpcs = len(resp['Vpcs'])
    print(num_vpcs)

    speech = "You have {} vpcs in your aws account.".format(num_vpcs)
    return speech


def get_num_ri_instances():

    client = aws_utils.create_service_client(
        role_arn=aws_utils.create_role_arn(ACCOUNT_ID),
        service='ec2'
    )

    resp = client.describe_reserved_instances()
    num_ris = len(resp['ReservedInstances'])
    return f"You have {num_ris} reserved instances in your aws account."


def get_ri_usage_info():

    client = get_role("ec2")


get_ri_usage_info()
