from celery import task, chain

from fjfnaranjobot.logging import getLogger

logger = getLogger(__name__)


@task(bind=True)
def _giving_ec2_instance_state(self, message_id, profile_id):
    logger.debug(f"Entering inner task {self.name} .")
    instance_state = None
    return instance_state, message_id, profile_id


@task(bind=True)
def _report_on_faulty_ec2_instance_state(self, last_args):
    logger.debug(f"Entering inner task {self.name} .")
    _instance_state, message_id, profile_id = last_args
    return message_id, profile_id


@task(bind=True)
def _giving_microapi_state(self, last_args):
    logger.debug(f"Entering inner task {self.name} .")
    message_id, profile_id = last_args
    microapi_state = None
    return microapi_state, message_id, profile_id


@task(bind=True)
def _report_on_faulty_microapi_state(self, last_args):
    logger.debug(f"Entering inner task {self.name} .")
    _microapi_state, message_id, profile_id = last_args
    return message_id, profile_id


@task(bind=True)
def _giving_tshock_state(self, last_args):
    logger.debug(f"Entering inner task {self.name} .")
    message_id, profile_id = last_args
    tshock_state = None
    return tshock_state, message_id, profile_id


@task(bind=True)
def _report_on_faulty_tshock_state(self, last_args):
    logger.debug(f"Entering inner task {self.name} .")
    _tshock_state, message_id, profile_id = last_args
    return message_id, profile_id


@task(bind=True)
def _log_user_activity(self, last_args):
    logger.debug(f"Entering inner task {self.name} .")
    _message_id, _profile_id = last_args


def log_user_activity_chain(profile_id, message_id):
    logger.info(
        "Registering chain 'log_user_activity' with "
        f"profile id {profile_id} and message_id {message_id}."
    )
    return chain(
        _giving_ec2_instance_state.s(message_id, profile_id),
        _report_on_faulty_ec2_instance_state.s(),
        _giving_microapi_state.s(),
        _report_on_faulty_microapi_state.s(),
        _giving_tshock_state.s(),
        _report_on_faulty_tshock_state.s(),
        _log_user_activity.s(),
    )()
