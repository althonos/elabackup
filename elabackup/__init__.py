# coding: utf-8
from __future__ import unicode_literals
from __future__ import print_function

import codecs
import contextlib
import datetime
import gzip
import json
import logging
import locale
import os
import signal
import ssl
import sys
import textwrap
import time
import traceback

import docopt
import six
import tqdm


class Session(object):
    def __init__(self, apikey):
        self.apikey = apikey

    if six.PY3:

        def _get(self, url, strict=False):
            req = six.moves.urllib.request.Request(url)
            req.add_header("Authorization", self.apikey)
            ctx = ssl.create_default_context()
            if strict:
                ctx.check_hostname = True
                ctx.verify_mode = ssl.CERT_OPTIONAL
            else:
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
            return six.moves.urllib.request.urlopen(req, context=ctx)

    else:

        def _get(self, url, strict=False):
            req = six.moves.urllib.request.Request(url)
            req.add_header("Authorization", self.apikey)
            return six.moves.urllib.request.urlopen(req)


class App(object):
    @classmethod
    def main(cls, argv=None, stream=sys.stderr):
        """
        elabackup - save / load backups of eLabFTW data using the API.

        Usage:
            elabackup dump -a <apikey> -s <server> [-o <output>] [--traceback]
            elabackup load -a <apikey> -s <server>  -i <input>   [--traceback]

        Parameters:
            -a <apikey>, --apikey <apikey>  The eLabFTW OAuth token to use.
            -s <server>, --server <server>  The adress of the server.

        Parameters - Dump:
            -o <output>, --output <output>  The name of the output file. Defaults
                                            to `elab-backup-<date>.json.gz`.

        Parameters - Load:
            -i <input>, --input <input>     The name of the input file.

        Parameters - Debug:
            --traceback                     Show full traceback on error.
        """

        # Parse arguments
        try:
            args = docopt.docopt(textwrap.dedent(cls.main.__doc__), argv)
        except docopt.DocoptExit as de:
            print(de, file=stream)
            return 1

        # Run the app
        try:
            app = cls(args["--server"], args["--apikey"])
            if args["dump"]:
                app.dump(args.get("--output"))
            elif args["load"]:
                app.load(args.get("--input"))
        # catched a Ctrl+C
        except KeyboardInterrupt:
            print("Interrupted", file=stream)
            return signal.SIGINT + 128  # POSIX standard
        # catched an error
        except Exception as e:
            print("Errored: {0}".format(e), file=stream)
            if args["--traceback"]:
                traceback.print_exc()
            return getattr(e, "errno", 1)
        # exited normally
        else:
            return 0

    def __init__(self, server, apikey):
        self.server = server
        self.apikey = apikey
        self.session = Session(self.apikey)

    def _dump_attachments(self, item):
        data_url = "{0}/uploads/{{long_name}}".format(self.server)
        pbar = tqdm.tqdm(item["uploads"], " (attachments)".ljust(20), leave=False, miniters=1)
        with contextlib.closing(pbar):
            for upload in pbar:
                url = data_url.format(**upload)
                with contextlib.closing(self.session._get(url)) as res:
                    upload["data"] = res.read().encode("base64")

    def _dump_section(self, section_url):
        dump = []

        # Load item summary
        with contextlib.closing(self.session._get(section_url)) as res:
            short = json.load(res)

        with contextlib.closing(tqdm.tqdm(short, miniters=1)) as pbar:
            for item_short in pbar:
                # update title
                title = item_short['title'].ljust(20)
                if len(title) > 20:
                    title = '{0}...'.format(title[:17])
                pbar.set_description(title)
                # get item metadata
                url = "{0}/{1}".format(section_url, item_short['id'])
                with contextlib.closing(self.session._get(url)) as res:
                    item = json.load(res)
                # download attachments
                self._dump_attachments(item)
                # add item
                dump.append(item)

        return dump




    def dump(self, output=None):

        if output is None:
            today = datetime.date.today().isoformat()
            output = "elab-backup-{0}.json.gz".format(today)

        # Pre-format some URLS
        items_url = "{0}/api/v1/items/".format(self.server)
        experiments_url = "{0}/api/v1/experiments/".format(self.server)

        # Prepare dump dictionary
        dump = {
            "timestamp": int(time.time()),
            "experiments": self._dump_section(experiments_url),
            "items": self._dump_section(items_url),
        }

        # # Load item summary
        # with contextlib.closing(self.session._get(items_url)) as res:
        #     items_short = json.load(res)

        # Load items
        # dump["items"] = items = []
        # with contextlib.closing(tqdm.tqdm(items_short, miniters=1)) as pbar:
        #     for item_short in pbar:
        #         # update title
        #         title = item_short['title'].ljust(20)
        #         if len(title) > 20:
        #             title = '{}...'.format(title[:17])
        #         pbar.set_description(title)
        #         # get item metadata
        #         url = item_url.format(**item_short)
        #         with contextlib.closing(self.session._get(url)) as res:
        #             item = json.load(res)
        #         # download attachments
        #         self._download_attachments(item)
        #         # add item
        #         items.append(item)
        #
        # # Load experiments summary
        # with contextlib.closing(self.session._get(experiments_url)) as res:
        #     exps_short = json.load(res)
        #
        # # Load experiments
        # dump["experiments"] = experiments = []
        # with contextlib.closing(tqdm.tqdm(exps_short, miniters=1)) as pbar:
        #     for experiment_short in pbar:
        #         # update title
        #         pbar.set_description(experiment_short["title"].ljust(20))
        #         # get experiment metadata
        #         url = experiment_url.format(**experiment_short)
        #         with contextlib.closing(self.session._get(url)) as res:
        #             experiment = json.load(res)
        #         # download attachments
        #         self._download_attachments(experiment)
        #         # add experiment
        #         experiments.append(experiment)

        # Write the dump
        with contextlib.closing(gzip.open(output, "w")) as dst:
            json.dump(dump, dst)


        return 0
