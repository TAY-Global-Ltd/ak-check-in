from termcolor import colored
import boto3
from datetime import datetime, timedelta
from settings import LAMBDA_FUNCTION_MAP
import click


@click.group()
def cli():
    """A CLI tool to watch logs"""
    pass


@cli.command()
@click.option("--stage", default="uat", help="The stage to watch logs for")
@click.option("--lookback", default=5, help="The number of minutes to look back")
def print_logs(stage: str, lookback: int):
    logs = boto3.client("logs")

    start_time = int((datetime.now() - timedelta(minutes=lookback)).timestamp() * 1000)

    response = logs.filter_log_events(
        logGroupName="/aws/lambda/" + LAMBDA_FUNCTION_MAP[stage],
        startTime=start_time,
        interleaved=True,
    )

    for event in response["events"]:
        dt = datetime.fromtimestamp(event["timestamp"] / 1000)
        dt = colored(str(dt), "green")
        msg = event["message"]
        print(f"{dt}: {msg}")


if __name__ == "__main__":
    cli()
