from boto3 import resource

from fjfnaranjobot.components.terraria.models import TerrariaProfile

_SECONDS_PER_PORTION = 60 * 5


def _resource_from_profile_id(service_name, profile_id):
    profile = TerrariaProfile(profile_id)
    return resource(
        service_name,
        region_name=profile.aws_default_region,
        aws_access_key_id=profile.aws_access_key_id,
        aws_secret_access_key=profile.aws_secret_access_key,
    )


def aproximate_datetime(datetime):
    date = datetime.date()
    time = datetime.time()
    total_seconds = time.second + (time.minute * 60) + (time.hour * 60 * 60)
    return date, int(total_seconds / _SECONDS_PER_PORTION)
