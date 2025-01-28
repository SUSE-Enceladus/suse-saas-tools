from resolve_customer.defaults import Defaults


class TestDefaults:
    def test_get_assume_role_config(self):
        assert Defaults.get_assume_role_config('../data/assume_role.yml') == {
            'role': {
                'arn': 'arn:aws:iam::123:role/Some',
                'session': 'some_session_name',
                'region': 'us-east-1'
            }
        }
