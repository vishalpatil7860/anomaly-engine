import os
import sys
from pathlib import Path
import click
from rich.console import Console
from rich.table import Table
from rich.text import Text
from anomalyd.config import AnomalyConfig
from anomalyd.engine import DetectionEngine

console = Console()

@click.group()
@click.option("--config", "-c", default="anomaly_config.yaml")
@click.pass_context
def cli(ctx, config):
    ctx.ensure_object(dict)
    ctx.obj["config_path"] = config

@cli.command()
@click.option("--tables", "-t", help="Comma-separated table names")
@click.pass_context
def profile(ctx, tables):
    cp = ctx.obj["config_path"]
    if not os.path.exists(cp):
        console.print(f"[red]Config not found: {cp}[/red]")
        sys.exit(1)
    config = AnomalyConfig.from_file(cp)
    engine = DetectionEngine(config)
    results = engine.profile()
    engine.close()
    t = Table(title="Profile Results")
    t.add_column("Table", style="cyan")
    t.add_column("Rows", justify="right")
    t.add_column("Columns", justify="right")
    for name, info in results.items():
        t.add_row(name, str(info["rows"]), str(info["cols"]))
    console.print(t)

@cli.command()
@click.option("--tables", "-t", help="Comma-separated table names")
@click.pass_context
def detect(ctx, tables):
    cp = ctx.obj["config_path"]
    if not os.path.exists(cp):
        console.print(f"[red]Config not found: {cp}[/red]")
        sys.exit(1)
    config = AnomalyConfig.from_file(cp)
    engine = DetectionEngine(config)
    results = engine.detect()
    engine.close()
    total = sum(len(v) for v in results.values())
    if total == 0:
        console.print("[green]No anomalies detected.[/green]")
        return
    for table, events in results.items():
        if not events:
            continue
        t = Table(title=f"Anomalies in {table} ({len(events)} found)")
        t.add_column("Type", style="blue")
        t.add_column("Column")
        t.add_column("Severity", style="bold")
        t.add_column("Value")
        for e in events:
            sev = "red" if e.severity == "high" else "yellow"
            t.add_row(e.anomaly_type, e.column or "multi", Text(e.severity.upper(), style=sev), str(e.observed_value)[:30])
        console.print(t)
    console.print(f"\n[red]Total anomalies: {total}[/red]")

@cli.command()
@click.option("--limit", "-l", default=20)
@click.pass_context
def history(ctx, limit):
    cp = ctx.obj["config_path"]
    config = AnomalyConfig.from_file(cp)
    engine = DetectionEngine(config)
    runs = engine.storage.get_runs(limit)
    engine.close()
    if not runs:
        console.print("[yellow]No runs found.[/yellow]")
        return
    t = Table(title="Detection History")
    t.add_column("Timestamp", style="dim")
    t.add_column("Table", style="cyan")
    t.add_column("Anomalies", justify="right")
    t.add_column("Status")
    for r in runs:
        t.add_row(r.get("ts", "")[:19], r.get("table_name", ""), str(r.get("total_anomalies", 0)), r.get("status", ""))
    console.print(t)

@cli.command()
@click.option("--limit", "-l", default=50)
@click.pass_context
def anomalies(ctx, limit):
    cp = ctx.obj["config_path"]
    config = AnomalyConfig.from_file(cp)
    engine = DetectionEngine(config)
    rows = engine.storage.get_anomalies(limit)
    engine.close()
    if not rows:
        console.print("[green]No anomalies found.[/green]")
        return
    t = Table(title="Anomalies")
    t.add_column("Timestamp", style="dim")
    t.add_column("Table", style="cyan")
    t.add_column("Type")
    t.add_column("Severity", style="bold")
    t.add_column("Value")
    for r in rows:
        sev = "red" if r.get("severity") == "high" else "yellow"
        t.add_row(r.get("ts", "")[:19], r.get("table_name", ""), r.get("atype", ""), Text(r.get("severity", "").upper(), style=sev), str(r.get("observed", ""))[:40])
    console.print(t)

@cli.command()
@click.option("--port", "-p", default=8501)
@click.pass_context
def dashboard(ctx, port):
    cp = ctx.obj["config_path"]
    console.print("[green]Starting Dashboard...[/green]")
    app = Path(__file__).parent / "dashboard" / "app.py"
    os.execvp(sys.executable, [sys.executable, "-m", "streamlit", "run", str(app), "--", "--config", cp, "--server.port", str(port)])

@cli.command()
@click.pass_context
def report(ctx):
    cp = ctx.obj["config_path"]
    config = AnomalyConfig.from_file(cp)
    engine = DetectionEngine(config)
    sm = engine.storage.summary()
    engine.close()
    console.print(f"[bold]Summary:[/bold] {sm["total"]} anomalies, [red]{sm["high"]} high[/red]")

if __name__ == "__main__":
    cli()