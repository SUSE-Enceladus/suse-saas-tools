from sqs_event_manager.defaults import Defaults


class TestDefaults:
    def test_get_sqs_event_manager_config(self):
        assert Defaults.get_sqs_event_manager_config('../data/sqs_event_manager.yml') == {
            'entitlement_change_url': 'https://inform-me-of-changes.com',
            'subscribe_success_url': 'https://inform-me-of-changes.com',
            'unsubscribe_success_url': 'https://inform-me-of-changes.com',
            'subscribe_fail_url': 'https://inform-me-of-changes.com',
            'auth_token': 'some'
        }
