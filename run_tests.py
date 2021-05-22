from test_main import *

test_login()
test_login_no_credentials()
test_login_invalid_credentials()
test_login_logout()
test_logout_invalid_no_credentials()

test_add_message_with_no_auth()
test_add_message_with_auth()
test_add_empty_message_with_auth()

test_read_message_auth()
test_read_message_no_auth()
test_read_not_existing_message_auth()
test_read_not_existing_message_no_auth()
test_read_check_views()

test_edit_with_auth()
test_edit_not_existing_with_auth()
test_edit_no_auth()


test_delete_no_auth()
test_delete_with_auth()
test_delete_not_existing_with_auth()