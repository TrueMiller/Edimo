import unittest
from edimo import edimo

class SplitCommandTestCase(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    def test_multi_parameter_command(self):
        cmd_str = ["curl ",
                   "'https://www.reddit.com/' ",
                   "--2.0 ",
                   "-H 'Host: www.reddit.com' ",
                   ("-H 'User-Agent: Mozilla/5.0 "
                   "(Macintosh; Intel Mac OS X 10.12; rv:53.0) "
                   "Gecko/20100101 Firefox/53.0' "),
                   ("-H 'Accept: text/html,application/xhtml+xml,"
                   "application/xml;q=0.9,*/*;q=0.8' "),
                   "-H 'Accept-Language: en-US,en;q=0.5' ",
                   "--compressed ",
                   "-H 'Connection: keep-alive' ",
                   "-H 'Upgrade-Insecure-Requests: 1'"]
        cmd_expected_output = """curl 'https://www.reddit.com/' --2.0 \\
-H 'Host: www.reddit.com' \\
-H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:53.0) Gecko/20100101 Firefox/53.0' \\
-H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8' \\
-H 'Accept-Language: en-US,en;q=0.5' \\
--compressed \\
-H 'Connection: keep-alive' \\
-H 'Upgrade-Insecure-Requests: 1'"""
        cmd_input = "".join(cmd_str)
        print (cmd_expected_output)
        print (cmd_input)
        print (edimo.split_command(cmd_input))
        self.assertEqual(edimo.split_command(cmd_input), cmd_expected_output)

    def test_paramter_delim_equal_sign_command(self):
        cmd_str = ["wget ",
                   "-r ",
                   "--tries=10 ",
                   "http://fly.srk.fer.hr/ ",
                   "-o log "]
        cmd_expected_output = """wget \\
-r \\
--tries=10 http://fly.srk.fer.hr/ \\
-o log"""
        print (cmd_expected_output)
        self.assertEqual(edimo.split_command("".join(cmd_str)), cmd_expected_output)


if __name__ == "__main__":
    unittest.main()
