import os
import tempfile
import unittest

from client_scan import (
    DEFAULT_EXCLUDE_DIRS,
    DEFAULT_EXCLUDE_FILES,
    build_manifest,
    diff_plan,
    looks_like_client,
    scan_client,
)

DIRS = set(DEFAULT_EXCLUDE_DIRS)
FILES = set(DEFAULT_EXCLUDE_FILES)


def f(path, sha="s"):
    return {"path": path, "size": 1, "sha256": sha}


class DiffPlanTest(unittest.TestCase):
    def test_diff_detecta_nuevos_modificados_y_sin_cambios(self):
        local = [f("main.exe", "a"), f("Data/x.bmd", "nuevo"), f("Data/n.bmd")]
        remote = [f("main.exe", "a"), f("Data/x.bmd", "viejo")]

        plan = diff_plan(local, remote, False, DIRS, FILES)

        self.assertEqual(plan["new"], ["Data/n.bmd"])
        self.assertEqual(plan["modified"], ["Data/x.bmd"])
        self.assertEqual(plan["delete"], [])
        self.assertEqual(plan["unchanged"], 1)

    def test_diff_sin_espejo_no_borra(self):
        plan = diff_plan([f("main.exe")], [f("main.exe"), f("Data/old.bmd")], False, DIRS, FILES)
        self.assertEqual(plan["delete"], [])

    def test_diff_espejo_borra_lo_que_no_esta_local(self):
        plan = diff_plan([f("main.exe")], [f("main.exe"), f("Data/old.bmd")], True, DIRS, FILES)
        self.assertEqual(plan["delete"], ["Data/old.bmd"])

    def test_diff_espejo_no_borra_launcher_ni_excluidos(self):
        remote = [f("main.exe"), f("launcher.exe"), f("Logs/a.log"), f("MuError.dmp")]
        plan = diff_plan([f("main.exe")], remote, True, DIRS, FILES)
        self.assertEqual(plan["delete"], [])

    def test_diff_ignora_mayusculas(self):
        plan = diff_plan([f("data/x.bmd", "a")], [f("Data/X.bmd", "a")], True, DIRS, FILES)
        self.assertEqual(plan["unchanged"], 1)
        self.assertEqual(plan["delete"], [])
        self.assertEqual(plan["new"], [])


class ScanTest(unittest.TestCase):
    def _touch(self, base, rel, content=b"x"):
        full = os.path.join(base, *rel.split("/"))
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "wb") as fh:
            fh.write(content)

    def test_scan_excluye_y_ordena(self):
        with tempfile.TemporaryDirectory() as base:
            for rel in ["main.exe", "Logs/x.txt", "a.log", "launcher.exe",
                        "Data/Launcher/updater.exe", "updater.exe"]:
                self._touch(base, rel)

            files = scan_client(base, DIRS, FILES)

            self.assertEqual([x["path"] for x in files], ["Data/Launcher/updater.exe", "main.exe"])
            self.assertEqual(files[1]["size"], 1)
            self.assertEqual(
                files[1]["sha256"],
                "2d711642b726b04401627ca9fbac32f5c8530fb1903cc4db02258717921a4881",
            )

    def test_looks_like_client(self):
        with tempfile.TemporaryDirectory() as base:
            self.assertFalse(looks_like_client(base))
            self._touch(base, "main.exe")
            self.assertTrue(looks_like_client(base))

    def test_build_manifest(self):
        files = [f("main.exe")]
        self.assertEqual(
            build_manifest(files, "1.0.1"),
            {"version": "1.0.1", "file_count": 1, "files": files},
        )


if __name__ == "__main__":
    unittest.main()
