from unittest.mock import patch

from fjfnaranjobot.components.friends.use_cases import friends, logger
from tests.base import THIRD_FRIEND_USERID

from ...base import FIRST_FRIEND_USERID, SECOND_FRIEND_USERID, BotHandlerTestCase

MODULE_PATH = 'fjfnaranjobot.components.friends.use_cases'


class FriendsUseCasesTests(BotHandlerTestCase):
    def test_friends_invalid_syntax_usage(self):
        cmd = ['cmd', 'add', 'add', 'add']
        with self.assertLogs(logger) as logs:
            replied = friends(cmd)
        assert 'Invalid syntax. Use: \'/friends [|add id|del id]\'.' == replied
        assert 'Invalid syntax for /friends command. Usage sent.' in logs.output[0]

    def test_friends_invalid_syntax_subcommand(self):
        cmd = ['cmd', 'invalid', '0']
        with self.assertLogs(logger) as logs:
            replied = friends(cmd)
        assert 'Unknown sub-command. Options are: \'add\' and \'del\'.' == replied
        assert (
            'Invalid syntax for /friends command. Unknown sub-command.'
            in logs.output[0]
        )

    @patch(f'{MODULE_PATH}.get_friends', return_value=[])
    def test_friends_no_friends(self, _get_friends):
        cmd = ['cmd']
        with self.assertLogs(logger) as logs:
            replied = friends(cmd)
        assert 'You don\'t have any friends.' == replied
        assert 'Sending no friends.' in logs.output[0]

    @patch(f'{MODULE_PATH}.get_friends', return_value=[FIRST_FRIEND_USERID])
    def test_friends_one_friend(self, _get_friends):
        cmd = ['cmd']
        with self.assertLogs(logger) as logs:
            replied = friends(cmd)
        assert f'You only have one friend: \'{FIRST_FRIEND_USERID}\'.' == replied
        assert 'Sending one friend.' in logs.output[0]

    @patch(
        f'{MODULE_PATH}.get_friends',
        return_value=[FIRST_FRIEND_USERID, SECOND_FRIEND_USERID],
    )
    def test_friends_two_friends(self, _get_friends):
        cmd = ['cmd']
        with self.assertLogs(logger) as logs:
            replied = friends(cmd)
        assert (
            f'You have two friends: \'{FIRST_FRIEND_USERID}\' and \'{SECOND_FRIEND_USERID}\'.'
            in replied
        )
        assert 'Sending two friends.' in logs.output[0]

    @patch(
        f'{MODULE_PATH}.get_friends',
        return_value=[FIRST_FRIEND_USERID, SECOND_FRIEND_USERID, THIRD_FRIEND_USERID],
    )
    def test_friends_many_friends(self, _get_friends):
        cmd = ['cmd']
        with self.assertLogs(logger) as logs:
            replied = friends(cmd)
        assert (
            f'Your friends are: \'{FIRST_FRIEND_USERID}\', '
            f'\'{SECOND_FRIEND_USERID}\' and \'{THIRD_FRIEND_USERID}\'.' == replied
        )
        assert 'Sending list of friends.' in logs.output[0]

    @patch(f'{MODULE_PATH}.get_friends', return_value=[])
    @patch(f'{MODULE_PATH}.add_friend')
    def test_friends_add_no_friends(self, add_friend, _get_friends):
        cmd = ['cmd', 'add', f'{FIRST_FRIEND_USERID}']
        with self.assertLogs(logger) as logs:
            replied = friends(cmd)
        assert f'Added @{FIRST_FRIEND_USERID} as a friend.' == replied
        add_friend.assert_called_once_with(FIRST_FRIEND_USERID)
        assert f'Adding @{FIRST_FRIEND_USERID} as a friend.' in logs.output[0]

    @patch(f'{MODULE_PATH}.get_friends', return_value=[FIRST_FRIEND_USERID])
    @patch(f'{MODULE_PATH}.add_friend')
    def test_friends_add_some_friends(self, add_friend, _get_friends):
        cmd = ['cmd', 'add', f'{SECOND_FRIEND_USERID}']
        with self.assertLogs(logger) as logs:
            replied = friends(cmd)
        assert f'Added @{SECOND_FRIEND_USERID} as a friend.' == replied
        add_friend.assert_called_once_with(SECOND_FRIEND_USERID)
        assert f'Adding @{SECOND_FRIEND_USERID} as a friend.' in logs.output[0]

    @patch(f'{MODULE_PATH}.get_friends', return_value=[FIRST_FRIEND_USERID])
    @patch(f'{MODULE_PATH}.add_friend')
    def test_friends_add_already_friend(self, _add_friend, _get_friends):
        cmd = ['cmd', 'add', f'{FIRST_FRIEND_USERID}']
        with self.assertLogs(logger) as logs:
            replied = friends(cmd)
        assert f'@{FIRST_FRIEND_USERID} is already a friend.' == replied
        assert (
            f'Not adding @{FIRST_FRIEND_USERID} because already a friend.'
            in logs.output[0]
        )

    @patch(f'{MODULE_PATH}.get_friends', return_value=[])
    @patch(f'{MODULE_PATH}.del_friend')
    def test_friends_del_no_friends(self, _del_friend, _get_friends):
        cmd = ['cmd', 'del', f'{FIRST_FRIEND_USERID}']
        with self.assertLogs(logger) as logs:
            replied = friends(cmd)
        assert f'@{FIRST_FRIEND_USERID} isn\'t a friend.' == replied
        assert (
            f'Not removing @{FIRST_FRIEND_USERID} because not a friend.'
            in logs.output[0]
        )

    @patch(f'{MODULE_PATH}.get_friends', return_value=[FIRST_FRIEND_USERID])
    @patch(f'{MODULE_PATH}.del_friend')
    def test_friends_del_not_friends(self, _del_friend, _get_friends):
        cmd = ['cmd', 'del', f'{SECOND_FRIEND_USERID}']
        with self.assertLogs(logger) as logs:
            replied = friends(cmd)
        assert f'@{SECOND_FRIEND_USERID} isn\'t a friend.' == replied
        assert (
            f'Not removing @{SECOND_FRIEND_USERID} because not a friend.'
            in logs.output[0]
        )

    @patch(
        f'{MODULE_PATH}.get_friends',
        return_value=[FIRST_FRIEND_USERID, SECOND_FRIEND_USERID],
    )
    @patch(f'{MODULE_PATH}.del_friend')
    def test_friends_del_some_friends(self, del_friend, _get_friends):
        cmd = ['cmd', 'del', f'{SECOND_FRIEND_USERID}']
        with self.assertLogs(logger) as logs:
            replied = friends(cmd)
        assert f'Removed @{SECOND_FRIEND_USERID} as a friend.' == replied
        del_friend.assert_called_once_with(SECOND_FRIEND_USERID)
        assert f'Removing @{SECOND_FRIEND_USERID} as a friend.' in logs.output[0]

    @patch(f'{MODULE_PATH}.get_friends', return_value=[FIRST_FRIEND_USERID])
    @patch(f'{MODULE_PATH}.del_friend')
    def test_friends_del_last_friend(self, del_friend, _get_friends):
        cmd = ['cmd', 'del', f'{FIRST_FRIEND_USERID}']
        with self.assertLogs(logger) as logs:
            replied = friends(cmd)
        assert f'Removed @{FIRST_FRIEND_USERID} as a friend.' == replied
        del_friend.assert_called_once_with(FIRST_FRIEND_USERID)
        assert f'Removing @{FIRST_FRIEND_USERID} as a friend.' in logs.output[0]
