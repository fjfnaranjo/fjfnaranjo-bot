from time import sleep

from boto3 import resource
from celery import chain
from requests import get as requests_get

from fjfnaranjobot.bot import ensure_bot
from fjfnaranjobot.components.terraria.models import TerrariaProfile
from fjfnaranjobot.components.terraria.utils import register_activity
from fjfnaranjobot.logging import getLogger
from fjfnaranjobot.tasks import app

logger = getLogger(__name__)


def _build_microapi_url(host, token, endpoint):
    return "http://{}:7979/{}/".format(host, token) + endpoint


def _build_tshock_url(host, endpoint, token, params):
    url = "http://{}:7878/{}?token={}".format(host, endpoint, token)
    if len(params) > 0:
        url = url + "&" + ("&".join(params))
    return url


@app.task(bind=True)
def _giving_ec2_instance_state_and_ip(self, payload):
    logger.debug(f"Entering inner task {self.name} .")
    profile = TerrariaProfile(payload["profile_id"])
    ec2 = resource(
        "ec2",
        region_name=profile.aws_default_region,
        aws_access_key_id=profile.aws_access_key_id,
        aws_secret_access_key=profile.aws_secret_access_key,
    )
    instance = ec2.Instance(profile.instance_id)
    payload["instance_ip"] = instance.public_ip_address
    payload["instance_state"] = instance.state["Name"]
    return payload


@app.task(bind=True)
def _log_user_activity_report_giving_ec2_instance_state_and_ip(self, payload):
    logger.debug(f"Entering inner task {self.name} .")
    return payload


@app.task(bind=True)
def _giving_microapi_state(self, payload):
    logger.debug(f"Entering inner task {self.name} .")
    profile = TerrariaProfile(payload["profile_id"])
    status_url = _build_microapi_url(
        payload["instance_ip"], profile.microapi_token, "status"
    )
    payload["status_response"] = requests_get(status_url).text
    return payload


@app.task(bind=True)
def _log_user_activity_report_giving_microapi_state(self, payload):
    logger.debug(f"Entering inner task {self.name} .")
    return payload


@app.task(bind=True)
def _giving_tshock_status_and_players(self, payload):
    logger.debug(f"Entering inner task {self.name} .")
    profile = TerrariaProfile(payload["profile_id"])
    active_list_url = _build_tshock_url(
        payload["instance_ip"],
        "v2/server/status",
        profile.tshock_token,
        ["players=true"],
    )
    tshock_status = requests_get(active_list_url).json()
    payload["tshock_status"] = tshock_status["status"]
    payload["tshock_players"] = tshock_status["players"]
    return payload


@app.task(bind=True)
def _log_user_activity_report_giving_tshock_status_and_players(self, payload):
    logger.debug(f"Entering inner task {self.name} .")
    return payload


@app.task(bind=True)
def _log_user_activity(self, payload):
    logger.debug(f"Entering inner task {self.name} .")
    register_activity(payload["tshock_players"])


def log_user_activity_chain(profile_id, message_id):
    logger.info(
        "Registering chain 'log_user_activity' with "
        f"profile id {profile_id} and message_id {message_id}."
    )
    payload = {"profile_id": profile_id, "message_id": message_id}
    return chain(
        _giving_ec2_instance_state_and_ip.s(payload),
        _log_user_activity_report_giving_ec2_instance_state_and_ip.s(),
        _giving_microapi_state.s(),
        _log_user_activity_report_giving_microapi_state.s(),
        _giving_tshock_status_and_players.s(),
        _log_user_activity_report_giving_tshock_status_and_players.s(),
        _log_user_activity.s(),
    )()


@app.task(bind=True)
def _stop_server_report_giving_ec2_instance_state_and_ip(self, payload):
    logger.debug(f"Entering inner task {self.name} .")
    return payload


@app.task(bind=True)
def _stop_server_report_giving_tshock_status_and_players(self, payload):
    logger.debug(f"Entering inner task {self.name} .")
    return payload


@app.task(bind=True)
def _tshock_stop(self, payload):
    logger.debug(f"Entering inner task {self.name} .")
    profile = TerrariaProfile(payload["profile_id"])
    off_url = _build_tshock_url(
        payload["instance_ip"], "v2/server/off", profile.tshock_token, ["confirm=true"]
    )
    sleep(10)
    payload["off_status"] = requests_get(off_url).json()["status"] == "200"
    return payload


@app.task(bind=True)
def _stop_server_report_tshock_stop(self, payload):
    logger.debug(f"Entering inner task {self.name} .")
    return payload


@app.task(bind=True)
def _microapi_backup(self, payload):
    logger.debug(f"Entering inner task {self.name} .")
    profile = TerrariaProfile(payload["profile_id"])
    status_url = _build_microapi_url(
        payload["instance_ip"], profile.microapi_token, "backup"
    )
    sleep(20)
    payload["backup_response"] = requests_get(status_url).text
    return payload


@app.task(bind=True)
def _stop_server_report_microapi_backup(self, payload):
    logger.debug(f"Entering inner task {self.name} .")
    return payload


@app.task(bind=True)
def _stop_instance(self, payload):
    logger.debug(f"Entering inner task {self.name} .")
    profile = TerrariaProfile(payload["profile_id"])
    ec2 = resource(
        "ec2",
        region_name=profile.aws_default_region,
        aws_access_key_id=profile.aws_access_key_id,
        aws_secret_access_key=profile.aws_secret_access_key,
    )
    instance = ec2.Instance(profile.instance_id)
    instance.stop()
    return payload


@app.task(bind=True)
def _stop_server_report_stop_instance(self, payload):
    logger.debug(f"Entering inner task {self.name} .")
    bot = ensure_bot()
    bot.bot.send_message(payload["message_id"], "stopped")


def stop_server_chain(profile_id, message_id):
    logger.info(
        "Registering chain 'stop_server' with "
        f"profile id {profile_id} and message_id {message_id}."
    )
    payload = {"profile_id": profile_id, "message_id": message_id}
    return chain(
        _giving_ec2_instance_state_and_ip.s(payload),
        _stop_server_report_giving_ec2_instance_state_and_ip.s(),
        _giving_tshock_status_and_players.s(),
        _stop_server_report_giving_tshock_status_and_players.s(),
        _tshock_stop.s(),
        _stop_server_report_tshock_stop.s(),
        _microapi_backup.s(),
        _stop_server_report_microapi_backup.s(),
        _stop_instance.s(),
        _stop_server_report_stop_instance.s(),
    )()


@app.task(bind=True)
def _start_server_report_giving_ec2_instance_state_and_ip(self, payload):
    logger.debug(f"Entering inner task {self.name} .")
    return payload


@app.task(bind=True)
def _start_server_report_stop_instance(self, payload):
    logger.debug(f"Entering inner task {self.name} .")
    return payload


@app.task(bind=True)
def _start_instance(self, payload):
    logger.debug(f"Entering inner task {self.name} .")
    profile = TerrariaProfile(payload["profile_id"])
    ec2 = resource(
        "ec2",
        region_name=profile.aws_default_region,
        aws_access_key_id=profile.aws_access_key_id,
        aws_secret_access_key=profile.aws_secret_access_key,
    )
    instance = ec2.Instance(profile.instance_id)
    instance.start()
    sleep(60)
    return payload


@app.task(bind=True)
def _start_server_report_start_instance(self, payload):
    logger.debug(f"Entering inner task {self.name} .")
    return payload


@app.task(bind=True)
def _start_server_report_giving_ec2_instance_state_and_ip_after(self, payload):
    logger.debug(f"Entering inner task {self.name} .")
    return payload


@app.task(bind=True)
def _microapi_start(self, payload):
    logger.debug(f"Entering inner task {self.name} .")
    profile = TerrariaProfile(payload["profile_id"])
    status_url = _build_microapi_url(
        payload["instance_ip"], profile.microapi_token, "start"
    )
    payload["start_response"] = requests_get(status_url).text
    return payload


@app.task(bind=True)
def _start_server_report_microapi_start(self, payload):
    logger.debug(f"Entering inner task {self.name} .")
    bot = ensure_bot()
    bot.bot.send_message(payload["message_id"], "started")


def start_server_chain(profile_id, message_id):
    logger.info(
        "Registering chain 'start_server' with "
        f"profile id {profile_id} and message_id {message_id}."
    )
    payload = {"profile_id": profile_id, "message_id": message_id}
    return chain(
        _giving_ec2_instance_state_and_ip.s(payload),
        _start_server_report_giving_ec2_instance_state_and_ip.s(),
        _start_instance.s(),
        _giving_ec2_instance_state_and_ip.s(),
        _start_server_report_giving_ec2_instance_state_and_ip_after.s(),
        _start_server_report_start_instance.s(),
        _microapi_start.s(),
        _start_server_report_microapi_start.s(),
    )()


@app.task(bind=True)
def _server_status_report_giving_ec2_instance_state_and_ip(self, payload):
    logger.debug(f"Entering inner task {self.name} .")
    return payload


@app.task(bind=True)
def _server_status_report_giving_microapi_state(self, payload):
    logger.debug(f"Entering inner task {self.name} .")
    return payload


@app.task(bind=True)
def _server_status_report_giving_tshock_status_and_players(self, payload):
    logger.debug(f"Entering inner task {self.name} .")
    return payload


@app.task(bind=True)
def _report_server_status(self, payload):
    bot = ensure_bot()
    bot.bot.send_message(payload["message_id"], payload["status_response"])


def server_status_chain(profile_id, message_id):
    logger.info(
        "Registering chain 'server_status' with "
        f"profile id {profile_id} and message_id {message_id}."
    )
    payload = {"profile_id": profile_id, "message_id": message_id}
    return chain(
        _giving_ec2_instance_state_and_ip.s(payload),
        _server_status_report_giving_ec2_instance_state_and_ip.s(),
        _giving_microapi_state.s(),
        _server_status_report_giving_microapi_state.s(),
        _giving_tshock_status_and_players.s(),
        _server_status_report_giving_tshock_status_and_players.s(),
        _report_server_status.s(),
    )()
