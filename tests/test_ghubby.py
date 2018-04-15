#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2018 Bitergia
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, 51 Franklin Street, Fifth Floor, Boston, MA 02110-1335, USA.
#
# Authors:
#     Valerio Cosentino <valcos@bitergia.com>
#

import datetime
import os
import unittest

import httpretty

from ghubby.ghubby import (Ghubby,
                           GhubbyClient,
                           GHubbyCommand)


GITHUB_API_URL = "https://api.github.com"
GITHUB_RATE_LIMIT = GITHUB_API_URL + "/rate_limit"
GITHUB_USER_EVENTS_URL = GITHUB_API_URL + "/users/valeriocos/events/public"
GITHUB_REPO_1_URL = GITHUB_API_URL + "/repos/valeriocos/GrimoireELK"
GITHUB_REPO_2_URL = GITHUB_API_URL + "/repos/chaoss/grimoirelab-mordred"


def read_file(filename, mode='r'):
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           filename),
              mode) as f:
        content = f.read()
    return content


class TestGHubby(unittest.TestCase):
    """GHubby tests"""

    @httpretty.activate
    def test_initialization(self):
        """Test whether attributes are initializated"""

        rate_limit = read_file('data/rate_limit')
        httpretty.register_uri(httpretty.GET,
                               GITHUB_RATE_LIMIT,
                               body=rate_limit,
                               status=200,
                               forcing_headers={
                                   'X-RateLimit-Remaining': '20',
                                   'X-RateLimit-Reset': '15'
                               })

        ghubby = Ghubby('valeriocos', 'aaa')

        self.assertEqual(ghubby.user, 'valeriocos')
        self.assertEqual(ghubby.api_token, 'aaa')

    @httpretty.activate
    def test_fetch_events(self):
        """Test whether events are correctly returned"""

        repo_1 = read_file('data/repo_1')
        repo_2 = read_file('data/repo_2')
        events_page_1 = read_file('data/events_page_1')
        events_page_2 = read_file('data/events_page_2')
        rate_limit = read_file('data/rate_limit')

        httpretty.register_uri(httpretty.GET,
                               GITHUB_RATE_LIMIT,
                               body=rate_limit,
                               status=200,
                               forcing_headers={
                                   'X-RateLimit-Remaining': '20',
                                   'X-RateLimit-Reset': '15'
                               })

        httpretty.register_uri(httpretty.GET,
                               GITHUB_USER_EVENTS_URL,
                               body=events_page_1,
                               status=200,
                               forcing_headers={
                                   'X-RateLimit-Remaining': '20',
                                   'X-RateLimit-Reset': '5',
                                   'Link': '<' + GITHUB_USER_EVENTS_URL +
                                           '/?&page=2>; rel="next", <' +
                                           GITHUB_USER_EVENTS_URL +
                                           '/?&page=3>; rel="last"'
                               })
        httpretty.register_uri(httpretty.GET,
                               GITHUB_USER_EVENTS_URL + '/?&page=2',
                               body=events_page_2,
                               status=200,
                               forcing_headers={
                                   'X-RateLimit-Remaining': '20',
                                   'X-RateLimit-Reset': '5'
                               })
        httpretty.register_uri(httpretty.GET,
                               GITHUB_REPO_1_URL,
                               body=repo_1, status=200,
                               forcing_headers={
                                   'X-RateLimit-Remaining': '20',
                                   'X-RateLimit-Reset': '15'
                               })
        httpretty.register_uri(httpretty.GET,
                               GITHUB_REPO_2_URL,
                               body=repo_2, status=200,
                               forcing_headers={
                                   'X-RateLimit-Remaining': '20',
                                   'X-RateLimit-Reset': '15'
                               })

        ghubby = Ghubby('valeriocos', 'aaa')
        events = [events for events in ghubby.fetch(from_date=None)]

        self.assertEqual(len(events), 3)

        event = events[0]
        self.assertEqual(event['actor']['login'], 'valeriocos')
        self.assertEqual(event['type'], 'PushEvent')
        self.assertEqual(event['repo_data']['name'], 'GrimoireELK')

        event = events[1]
        self.assertEqual(event['actor']['login'], 'valeriocos')
        self.assertEqual(event['type'], 'PullRequestEvent')
        self.assertEqual(event['repo_data']['name'], 'mordred')

        event = events[2]
        self.assertEqual(event['actor']['login'], 'valeriocos')
        self.assertEqual(event['type'], 'CreateEvent')
        self.assertEqual(event['repo_data']['name'], 'GrimoireELK')

    @httpretty.activate
    def test_fetch_from_date(self):
        """Test when return from date"""

        repo_1 = read_file('data/repo_1')
        repo_2 = read_file('data/repo_2')
        events_page_1 = read_file('data/events_page_1')
        events_page_2 = read_file('data/events_page_2')
        rate_limit = read_file('data/rate_limit')

        httpretty.register_uri(httpretty.GET,
                               GITHUB_RATE_LIMIT,
                               body=rate_limit,
                               status=200,
                               forcing_headers={
                                   'X-RateLimit-Remaining': '20',
                                   'X-RateLimit-Reset': '15'
                               })

        httpretty.register_uri(httpretty.GET,
                               GITHUB_USER_EVENTS_URL,
                               body=events_page_1,
                               status=200,
                               forcing_headers={
                                   'X-RateLimit-Remaining': '20',
                                   'X-RateLimit-Reset': '5',
                                   'Link': '<' + GITHUB_USER_EVENTS_URL +
                                           '/?&page=2>; rel="next", <' +
                                           GITHUB_USER_EVENTS_URL +
                                           '/?&page=3>; rel="last"'
                               })
        httpretty.register_uri(httpretty.GET,
                               GITHUB_USER_EVENTS_URL + '/?&page=2',
                               body=events_page_2,
                               status=200,
                               forcing_headers={
                                   'X-RateLimit-Remaining': '20',
                                   'X-RateLimit-Reset': '5'
                               })
        httpretty.register_uri(httpretty.GET,
                               GITHUB_REPO_1_URL,
                               body=repo_1, status=200,
                               forcing_headers={
                                   'X-RateLimit-Remaining': '20',
                                   'X-RateLimit-Reset': '15'
                               })
        httpretty.register_uri(httpretty.GET,
                               GITHUB_REPO_2_URL,
                               body=repo_2, status=200,
                               forcing_headers={
                                   'X-RateLimit-Remaining': '20',
                                   'X-RateLimit-Reset': '15'
                               })

        from_date = datetime.datetime(2018, 4, 13, 15, 45)
        ghubby = Ghubby('valeriocos', 'aaa')
        events = [events for events in ghubby.fetch(from_date=from_date)]

        self.assertEqual(len(events), 2)

        event = events[0]
        self.assertEqual(event['actor']['login'], 'valeriocos')
        self.assertEqual(event['type'], 'PushEvent')
        self.assertEqual(event['repo_data']['name'], 'GrimoireELK')

        event = events[1]
        self.assertEqual(event['actor']['login'], 'valeriocos')
        self.assertEqual(event['type'], 'PullRequestEvent')
        self.assertEqual(event['repo_data']['name'], 'mordred')

    @httpretty.activate
    def test_fetch_empty(self):
        """Test when return empty"""

        body = ""
        rate_limit = read_file('data/rate_limit')

        httpretty.register_uri(httpretty.GET,
                               GITHUB_RATE_LIMIT,
                               body=rate_limit,
                               status=200,
                               forcing_headers={
                                   'X-RateLimit-Remaining': '20',
                                   'X-RateLimit-Reset': '15'
                               })

        httpretty.register_uri(httpretty.GET,
                               GITHUB_USER_EVENTS_URL,
                               body=body, status=200,
                               forcing_headers={
                                   'X-RateLimit-Remaining': '20',
                                   'X-RateLimit-Reset': '15'
                               })

        ghubby = Ghubby('valeriocos', 'aaa')
        events = [events for events in ghubby.fetch()]

        self.assertEqual(len(events), 0)


class TestGHubbyClient(unittest.TestCase):
    """GHubbyClient tests"""

    @httpretty.activate
    def test_init(self):
        rate_limit = read_file('data/rate_limit')
        httpretty.register_uri(httpretty.GET,
                               GITHUB_RATE_LIMIT,
                               body=rate_limit,
                               status=200,
                               forcing_headers={
                                   'X-RateLimit-Remaining': '20',
                                   'X-RateLimit-Reset': '15'
                               })

        client = GhubbyClient('valeriocos', 'aaa')

        self.assertEqual(client.user, 'valeriocos')
        self.assertEqual(client.token, 'aaa')

    @httpretty.activate
    def test_events(self):
        """Test events API call"""

        events = read_file('data/events_page_1')
        rate_limit = read_file('data/rate_limit')

        httpretty.register_uri(httpretty.GET,
                               GITHUB_RATE_LIMIT,
                               body=rate_limit,
                               status=200,
                               forcing_headers={
                                   'X-RateLimit-Remaining': '20',
                                   'X-RateLimit-Reset': '15'
                               })

        httpretty.register_uri(httpretty.GET,
                               GITHUB_USER_EVENTS_URL,
                               body=events, status=200,
                               forcing_headers={
                                   'X-RateLimit-Remaining': '5',
                                   'X-RateLimit-Reset': '5'
                               })

        client = GhubbyClient("valeriocos", "aaa")
        raw_events = [events for events in client.events()]
        self.assertEqual(raw_events[0], events)

        # Check requests
        expected = {
            'per_page': ['30']
        }

        self.assertDictEqual(httpretty.last_request().querystring, expected)
        self.assertEqual(httpretty.last_request().headers["Authorization"],
                         "token aaa")

    @httpretty.activate
    def test_repo(self):
        """Test repo API call"""

        repo = read_file('data/repo_1')
        rate_limit = read_file('data/rate_limit')

        httpretty.register_uri(httpretty.GET,
                               GITHUB_RATE_LIMIT,
                               body=rate_limit,
                               status=200,
                               forcing_headers={
                                   'X-RateLimit-Remaining': '20',
                                   'X-RateLimit-Reset': '15'
                               })
        httpretty.register_uri(httpretty.GET,
                               GITHUB_REPO_1_URL,
                               body=repo,
                               status=200,
                               forcing_headers={
                                   'X-RateLimit-Remaining': '20',
                                   'X-RateLimit-Reset': '15'
                               })

        client = GhubbyClient("valeriocos", "aaa")

        repo_raw = client.repo("valeriocos/GrimoireELK")
        self.assertEqual(repo_raw, repo)

    @httpretty.activate
    def test_get_empty_events(self):
        """ Test when no events are available """

        events = []
        rate_limit = read_file('data/rate_limit')

        httpretty.register_uri(httpretty.GET,
                               GITHUB_RATE_LIMIT,
                               body=rate_limit,
                               status=200,
                               forcing_headers={
                                   'X-RateLimit-Remaining': '20',
                                   'X-RateLimit-Reset': '15'
                               })

        httpretty.register_uri(httpretty.GET,
                               GITHUB_USER_EVENTS_URL,
                               body=events, status=200,
                               forcing_headers={
                                   'X-RateLimit-Remaining': '20',
                                   'X-RateLimit-Reset': '15'
                               })

        client = GhubbyClient("valeriocos", "aaa")

        raw_events = [events for events in client.events()]
        self.assertEqual(raw_events, [])

        # Check requests
        expected = {
            'per_page': ['30']
        }

        self.assertDictEqual(httpretty.last_request().querystring, expected)
        self.assertEqual(httpretty.last_request().headers["Authorization"],
                         "token aaa")


class TestGHubbyCommand(unittest.TestCase):
    """GHubbyCommand unit tests"""

    def test_setup_cmd_parser(self):
        """Test if it parser object is correctly initialized"""

        parser = GHubbyCommand.setup_cmd_parser()
        args = ['--api-token', 'abcdefgh',
                '--from-date', '1970-01-01',
                '-u', 'valeriocos']

        parsed_args = parser.parse_args(args)
        self.assertEqual(parsed_args.from_date, '1970-01-01')
        self.assertEqual(parsed_args.api_token, 'abcdefgh')
        self.assertEqual(parsed_args.user, 'valeriocos')


if __name__ == "__main__":
    unittest.main(warnings='ignore')
