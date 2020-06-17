from boto3 import resource
from celery import chain, task
from requests import get as requests_get

from fjfnaranjobot.components.terraria.models import TerrariaProfile
from fjfnaranjobot.logging import getLogger

logger = getLogger(__name__)


_MICROAPI_URL = 'http://{}:7979/{}/'
_TSHOCK_URL = 'http://{}:7878/{}?token={}'


@task(bind=True)
def _giving_ec2_instance_state_and_ip(self, profile_id, message_id):
    logger.debug(f"Entering inner task {self.name} .")
    profile = TerrariaProfile(profile_id)
    ec2 = resource(
        'ec2',
        region_name=profile.aws_default_region,
        aws_access_key_id=profile.aws_access_key_id,
        aws_secret_access_key=profile.aws_secret_access_key,
    )
    instance = ec2.Instance(profile.instance_id)
    return instance.public_ip_address, instance.state['Name'], message_id, profile_id


@task(bind=True)
def _report_on_faulty_ec2_instance_state(self, last_args):
    logger.debug(f"Entering inner task {self.name} .")
    instance_ip, _instance_state, message_id, profile_id = last_args
    return instance_ip, message_id, profile_id


@task(bind=True)
def _giving_microapi_state(self, last_args):
    logger.debug(f"Entering inner task {self.name} .")
    instance_ip, message_id, profile_id = last_args
    profile = TerrariaProfile(profile_id)
    status_url = _MICROAPI_URL.format(instance_ip, profile.microapi_token) + 'status'
    microapi_state = requests_get(status_url).text
    return microapi_state, instance_ip, message_id, profile_id


@task(bind=True)
def _report_on_faulty_microapi_state(self, last_args):
    logger.debug(f"Entering inner task {self.name} .")
    _microapi_state, instance_ip, message_id, profile_id = last_args
    return instance_ip, message_id, profile_id


@task(bind=True)
def _giving_tshock_players(self, last_args):
    logger.debug(f"Entering inner task {self.name} .")
    instance_ip, message_id, profile_id = last_args
    profile = TerrariaProfile(profile_id)
    active_list_url = _TSHOCK_URL.format(
        instance_ip, 'v2/server/status', profile.tshock_token
    )
    active_list_url = active_list_url + '&players=true'
    tshock_status = requests_get(active_list_url).json()
    players = tshock_status['players']
    return players, message_id, profile_id


@task(bind=True)
def _report_on_faulty_tshock_state(self, last_args):
    logger.debug(f"Entering inner task {self.name} .")
    players, message_id, profile_id = last_args
    return players, message_id, profile_id


@task(bind=True)
def _log_user_activity(self, last_args):
    logger.debug(f"Entering inner task {self.name} .")
    players, _message_id, _profile_id = last_args
    logger.error(str(players))


def log_user_activity_chain(profile_id, message_id):
    logger.info(
        "Registering chain 'log_user_activity' with "
        f"profile id {profile_id} and message_id {message_id}."
    )
    return chain(
        _giving_ec2_instance_state_and_ip.s(profile_id, message_id),
        _report_on_faulty_ec2_instance_state.s(),
        _giving_microapi_state.s(),
        _report_on_faulty_microapi_state.s(),
        _giving_tshock_players.s(),
        _report_on_faulty_tshock_state.s(),
        _log_user_activity.s(),
    )()
