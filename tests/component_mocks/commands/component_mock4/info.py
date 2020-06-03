from fjfnaranjobot.common import Command

commands = (
    Command('desc1', 'only_prod', None),
    Command('desc2', None, 'only_dev'),
    Command('desc3', 'both_prod_and_dev', 'both_prod_and_dev'),
)
