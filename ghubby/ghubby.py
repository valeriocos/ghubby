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

import argparse
import json
import logging

from grimoirelab.toolkit.datetime import (datetime_to_utc,
                                          str_to_datetime)
from grimoirelab.toolkit.uris import urijoin
from perceval.backends.core.github import (GitHubClient,
                                           DEFAULT_DATETIME)

logger = logging.getLogger(__name__)


class Ghubby:
    """Ghubby collects the activities within the past 90 days
    of a user on GitHub by querying the API, which is accessed via a token.
    In case the token rate limit is reached, the program will
    sleep until rate limit is reset.

    :param user: GitHub user
    :param api_token: GitHub auth token to access the API
    """
    version = '0.1.0'

    def __init__(self, user, api_token):
        self.user = user
        self.api_token = api_token

        self.client = GhubbyClient(user, api_token)

    def fetch(self, from_date=DEFAULT_DATETIME):
        """Fetch the user events from GitHub.

        :param from_date: obtain events since this date. Note that
        the API returns at most the events within the past 90 days

        :returns: a generator of events
        """
        if not from_date:
            from_date = DEFAULT_DATETIME

        from_date = datetime_to_utc(from_date)
        items = self.fetch_items(from_date)

        return items

    def fetch_items(self, from_date):
        """Fetch the items

        :param from_date: obtain events since this date

        :returns: a generator of items
        """

        items = self.__fetch_events(from_date)
        return items

    def __fetch_events(self, from_date):
        """Fetch the events"""

        events_groups = self.client.events()

        for raw_events in events_groups:
            events = json.loads(raw_events)
            for event in events:

                if str_to_datetime(event['created_at']) < from_date:
                    continue

                event['repo_data'] = self.__fetch_repo(event['repo']['name'])

                yield event

    def __fetch_repo(self, repo_name):
        """Fetch repo information"""

        repo_raw = self.client.repo(repo_name)
        repo = json.loads(repo_raw)

        return repo


class GhubbyClient(GitHubClient):
    """Client for retieving information from GitHub API. It
    leverages on the GitHubClient of grimoirelab-perceval

    :param user: GitHub user
    :param api_token: GitHub auth token to access the API
    """

    def __init__(self, user, api_token):
        self.user = user
        self.token = api_token
        self._repos = {}  # internal repos cache

        super().__init__("", "", api_token, sleep_for_rate=True)
        self._init_rate_limit()

    def events(self):
        """Collect the user events"""

        payload = {
            'per_page': 30
        }

        path = urijoin("users", self.user, "events", "public")
        return self.fetch_items(path, payload)

    def repo(self, name):
        """Collect repo data"""

        if name in self._repos:
            return self._repos[name]

        path = urijoin(self.base_url, "repos", name)
        r = self.fetch(path)
        repo = r.text
        self._repos.update({name: repo})

        return repo

    def fetch_items(self, path, payload):
        """Return the items from github API using links pagination"""

        page = 0  # current page
        last_page = None  # last page
        url_next = urijoin(self.base_url, path)

        logger.debug("Get GitHub paginated items from " + url_next)

        response = self.fetch(url_next, payload=payload)

        items = response.text
        page += 1

        if 'last' in response.links:
            last_url = response.links['last']['url']
            last_page = last_url.split('&page=')[1].split('&')[0]
            last_page = int(last_page)
            logger.debug("Page: %i/%i" % (page, last_page))

        while items:
            yield items

            items = None

            if 'next' in response.links:
                url_next = response.links['next']['url']
                response = self.fetch(url_next, payload=payload)
                page += 1

                items = response.text
                logger.debug("Page: %i/%i" % (page, last_page))


class GHubbyCommand():
    """Class to run GHubby from the command line."""

    @staticmethod
    def setup_cmd_parser():
        """Returns the GitHub argument parser."""

        parser = argparse.ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter,
            add_help=False)
        parser.add_argument('-u', '--user',
                            help="GitHub user", dest='user')
        parser.add_argument('-t', '--api-token',
                            help="GitHub token", dest='api_token')
        parser.add_argument('-d', '--from-date',
                            default='1970-01-01',
                            help="fetch events updated since this date",
                            dest='from_date')

        return parser


if __name__ == '__main__':
    logging.info("Looking for events.")

    parser = GHubbyCommand.setup_cmd_parser()
    args = parser.parse_args()

    ghubby = Ghubby(user=args.user, api_token=args.api_token)

    from_date = str_to_datetime(args.from_date)
    for event in ghubby.fetch(from_date=from_date):
        print(json.dumps(event, sort_keys=True, indent=4))

    logging.info("Events fetched.")
