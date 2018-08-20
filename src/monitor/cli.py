# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import logging
import os
import sys

import click

from monitor.main import Source, Mirror, determine_commit_replication_lag
from monitor.pulse import run_pulse_listener


@click.command()
@click.option(
    "--debug",
    envvar="DEBUG",
    is_flag=True,
    help="Print debugging messages about the script's progress.",
)
@click.argument("node_ids", nargs=-1)
def show_lag(debug, node_ids):
    """Display the replication lag for a repo or an individual commit.

    Does not drain any queues or send any data.
    """
    if debug:
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    source = Source(repo_url="https://hg.mozilla.org/integration/autoland/")
    mirror = Mirror(
        url="https://phabricator.services.mozilla.com", repo_callsign="MOZILLACENTRAL"
    )

    if node_ids:
        for node_id in node_ids:
            lag = determine_commit_replication_lag(source, mirror, node_id)
            lag_seconds = lag.timedelta.seconds
            if lag_seconds == 0:
                report = click.style("0", fg="green", bold=True)
            else:
                report = click.style(lag_seconds, fg="yellow", bold=True)
            click.echo("replication lag (seconds): ", nl=False)
            click.echo(report)
    else:
        run_pulse_listener(
            os.environ['PULSE_USERNAME'],
            os.environ['PULSE_PASSWORD'],
            os.environ['PULSE_EXCHANGE'],
            os.environ['PULSE_QUEUE_NAME'],
            os.environ['PULSE_QUEUE_ROUTING_KEY'],
            0,
            True
        )
