from resolve_customer.defaults import Defaults


class TestDefaults:
    def test_get_assume_role_config(self):
        assert Defaults.get_assume_role_config('../data/assume_role.yml') == {
            'role': {
                'us-east-1': {
                    'arn': 'arn:aws:iam::123:role/Some',
                    'session': 'some_session_name',
                },
                'eu-central-1': {
                    'arn': 'arn:aws:iam::456:role/SomeOther',
                    'session': 'some_session_name'
                }
            }
        }
