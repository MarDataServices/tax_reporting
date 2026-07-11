import subprocess

def run_dbt():
    subprocess.run(
        ["dbt","build"],
        cwd="/app/dbt"
    )