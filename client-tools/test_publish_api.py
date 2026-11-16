import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

import requests

from publish_api import PublishApi, PublishApiError, is_insecure_url


def response(status, payload):
    resp = MagicMock()
    resp.status_code = status
    resp.ok = 200 <= status < 300
    resp.json.return_value = payload
    resp.text = str(payload)
    return resp


class PublishApiTest(unittest.TestCase):
    def setUp(self):
        self.api = PublishApi("http://servidor/", "clave")
        fd, self.file = tempfile.mkstemp()
        os.write(fd, b"abc")
        os.close(fd)

    def tearDown(self):
        os.remove(self.file)

    @patch("requests.Session.request")
    def test_upload_codifica_path_y_manda_sha(self, request):
        request.return_value = response(200, {"path": "x", "size": 3})

        self.api.upload_file("sid", "Data/Música/a b.mp3", self.file, "f" * 64)

        method, url = request.call_args.args
        kwargs = request.call_args.kwargs
        self.assertEqual(method, "PUT")
        self.assertEqual(url, "http://servidor/api/v2/tools/client-publish/sessions/sid/files")
        self.assertEqual(kwargs["params"], {"path": "Data/Música/a b.mp3"})
        self.assertEqual(kwargs["headers"]["x-sha256"], "f" * 64)
        self.assertEqual(kwargs["headers"]["x-api-key"], "clave")

    @patch("requests.Session.request")
    def test_upload_reintenta_3_veces_y_falla(self, request):
        request.side_effect = requests.exceptions.ConnectionError("cortado")

        with self.assertRaises(PublishApiError):
            self.api.upload_file("sid", "main.exe", self.file, "f" * 64)
        self.assertEqual(request.call_count, 3)

    @patch("requests.Session.request")
    def test_error_usa_message_de_la_api(self, request):
        request.return_value = response(409, {"message": "Hay otra publicación en curso"})

        with self.assertRaises(PublishApiError) as ctx:
            self.api.create_session(force=False)
        self.assertIn("Hay otra publicación en curso", str(ctx.exception))

    @patch("requests.Session.request")
    def test_error_de_validacion_incluye_problemas(self, request):
        request.return_value = response(400, {
            "message": "El manifest no coincide con los archivos",
            "problems": ["a.bmd: no se subió"],
        })

        with self.assertRaises(PublishApiError) as ctx:
            self.api.publish("sid", {"files": []}, [], [])
        self.assertIn("a.bmd: no se subió", str(ctx.exception))

    @patch("requests.Session.request")
    def test_error_409_expone_el_status(self, request):
        request.return_value = response(409, {"message": "Hay otra publicación en curso"})

        with self.assertRaises(PublishApiError) as ctx:
            self.api.create_session(force=False)
        self.assertEqual(ctx.exception.status, 409)

    @patch("requests.Session.request")
    def test_publish_espera_hasta_10_minutos(self, request):
        request.return_value = response(200, {"uploaded": 0})

        self.api.publish("sid", {"files": []}, [], [])

        self.assertEqual(request.call_args.kwargs["timeout"], (10, 600))

    def test_is_insecure_url(self):
        self.assertTrue(is_insecure_url("http://93.127.142.139"))
        self.assertFalse(is_insecure_url("https://mu.example.com"))
        self.assertFalse(is_insecure_url("http://localhost:3000"))
        self.assertFalse(is_insecure_url("http://127.0.0.1:3000"))

    @patch("requests.Session.request")
    def test_get_state_devuelve_la_lista(self, request):
        files = [{"path": "main.exe", "size": 3, "sha256": "a"}]
        request.return_value = response(200, {"files": files})

        self.assertEqual(self.api.get_state(), files)


if __name__ == "__main__":
    unittest.main()
