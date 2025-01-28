from resolve_customer.error import (
    classify_error, error_record
)


class TestErrorMethods:
    def test_classify_error(self):
        error = error_record(400, 'some_error', 'Some')
        assert error['ResponseMetadata']['HTTPStatusCode'] == 400
        assert error['Error']['Code'] == 'App.Error.Some'
        error_classified = classify_error(
            error, 'App.Error.Some', 500, 'SomeException'
        )
        assert error_classified['ResponseMetadata']['HTTPStatusCode'] == 500
        assert error_classified['Error']['Code'] == 'SomeException'
