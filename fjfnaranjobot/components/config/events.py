from fjfnaranjobot.logging import getLogger
from fjfnaranjobot.scheduler import PeriodicEvent

logger = getLogger(__name__)


@PeriodicEvent(2)
def decorated():
    logger.info('called')
