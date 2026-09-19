import socket
import ssl
import unittest

import httpx

from backend.providers.deepseek import _request_error_category, _request_error_message


class DeepSeekDiagnosticsTests(unittest.TestCase):
    def _connect_error(self, cause: BaseException) -> httpx.ConnectError:
        try:
            raise cause
        except BaseException as inner:
            try:
                raise httpx.ConnectError("connection failed") from inner
            except httpx.ConnectError as error:
                return error

    def test_classifies_permission_denied_connect_failure(self) -> None:
        error = self._connect_error(PermissionError(10013, "socket access denied"))
        self.assertEqual(_request_error_category(error), "connect_permission")
        self.assertIn("PermissionError", _request_error_message(error))

    def test_classifies_permission_denied_inside_exception_group(self) -> None:
        grouped = ExceptionGroup(
            "multiple connection attempts failed",
            [self._connect_error(PermissionError(10013, "socket access denied"))],
        )
        error = self._connect_error(grouped)
        self.assertEqual(_request_error_category(error), "connect_permission")
        self.assertIn("PermissionError", _request_error_message(error))

    def test_classifies_dns_and_tls_failures(self) -> None:
        self.assertEqual(_request_error_category(self._connect_error(socket.gaierror(-2, "name lookup failed"))), "dns")
        self.assertEqual(_request_error_category(self._connect_error(ssl.SSLError("handshake failed"))), "tls")

    def test_classifies_timeout_as_retryable_timeout_evidence(self) -> None:
        error = httpx.ConnectTimeout("timed out")
        self.assertEqual(_request_error_category(error), "timeout")
        self.assertIn("ConnectTimeout", _request_error_message(error))


if __name__ == "__main__":
    unittest.main()
