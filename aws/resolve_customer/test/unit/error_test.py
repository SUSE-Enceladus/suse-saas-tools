from resolve_customer.error import (
    classify_error, error_record
)


class TestErrorMethods:
    def test_classify_error(self):
        error = error_record(400, 'some_error', 'Some')
        error_classified = classify_error(
            error, 'App.Error.Some', 500
        )
        assert error_classified['ResponseMetadata']['HTTPStatusCode'] == 500
