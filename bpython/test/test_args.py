import re
import subprocess
import sys
import tempfile
import unittest

from textwrap import dedent
from bpython import args
from bpython.test import FixLanguageTestCase as TestCase


class TestExecArgs(unittest.TestCase):
    @unittest.skip("test broken under pytest")
    def test_exec_dunder_file(self):
        with tempfile.NamedTemporaryFile(mode="w") as f:
            f.write(
                dedent(
                    """\
                import sys
                sys.stderr.write(__file__)
                sys.stderr.flush()"""
                )
            )
            f.flush()
            p = subprocess.Popen(
                [sys.executable] + ["-m", "bpython.curtsies", f.name],
                stderr=subprocess.PIPE,
                universal_newlines=True,
            )
            (_, stderr) = p.communicate()

            self.assertEqual(stderr.strip(), f.name)

    def test_exec_nonascii_file(self):
        with tempfile.NamedTemporaryFile(mode="w") as f:
            f.write(
                dedent(
                    """\
                #!/usr/bin/env python
                # coding: utf-8
                "你好 # nonascii"
                """
                )
            )
            f.flush()
            try:
                subprocess.check_call(
                    [sys.executable, "-m", "bpython.curtsies", f.name]
                )
            except subprocess.CalledProcessError:
                self.fail("Error running module with nonascii characters")

    @unittest.skip("test broken under pytest")
    def test_exec_nonascii_file_linenums(self):
        with tempfile.NamedTemporaryFile(mode="w") as f:
            f.write(
                dedent(
                    """\
                #!/usr/bin/env python
                # coding: utf-8
                1/0
                """
                )
            )
            f.flush()
            p = subprocess.Popen(
                [sys.executable, "-m", "bpython.curtsies", f.name],
                stderr=subprocess.PIPE,
                universal_newlines=True,
            )
            (_, stderr) = p.communicate()

            self.assertIn("line 3", clean_colors(stderr))


def clean_colors(s):
    return re.sub(r"\x1b[^m]*m", "", s)


class TestParse(TestCase):
    def test_version(self):
        with self.assertRaises(SystemExit):
            args.parse(["--version"])
