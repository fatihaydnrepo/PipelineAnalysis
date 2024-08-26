import requests
from datetime import datetime, timedelta, timezone
from collections import Counter
import matplotlib.pyplot as plt
import json
import base64


organization = "fatihaydn"
project = "Project Name"
pat = "Azure Devops PAT"

pat_bytes = f":{pat}".encode('ascii')
pat_base64 = base64.b64encode(pat_bytes).decode('ascii')

headers = {
    'Authorization': f'Basic {pat_base64}',
    'Content-Type': 'application/json'
}

two_weeks_ago = datetime.now(timezone.utc) - timedelta(days=14)
two_weeks_ago_iso = two_weeks_ago.strftime("%Y-%m-%dT%H:%M:%SZ")

TOTAL_DURATION_THRESHOLD = 1800

pipelines_url = f"https://dev.azure.com/{organization}/{project}/_apis/pipelines?api-version=6.0"
response = requests.get(pipelines_url, headers=headers)

if response.status_code == 200:
    pipelines = response.json()
else:
    print("Failed to retrieve pipelines.")
    pipelines = None

COST_PER_MINUTE_MICROSOFT_HOSTED = 0.008  # USD per minute after free tier

cumulative_duration = 0  # Cumulative duration in minutes
total_project_pipeline_cost = 0  # In USD
total_failure_cost = 0  # Cost of failed pipelines

if pipelines:
    for pipeline in pipelines['value']:
        pipeline_id = pipeline['id']
        print(f"\nAnalyzing Pipeline: {pipeline['name']} (ID: {pipeline_id})")

        runs_url = f"https://dev.azure.com/{organization}/{project}/_apis/pipelines/{pipeline_id}/runs?api-version=7.1-preview.1&minTime={two_weeks_ago_iso}"
        runs_response = requests.get(runs_url, headers=headers)

        try:
            runs_data = runs_response.json()
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            continue

        total_cost = 0
        durations = []
        dates = []
        success_count = 0
        failure_count = 0

        for run in runs_data.get('value', []):
            run_id = run['id']

            build_url = f"https://dev.azure.com/{organization}/{project}/_apis/build/builds/{run_id}?api-version=6.0"
            build_response = requests.get(build_url, headers=headers)
            build_data = build_response.json()

            if 'startTime' in build_data and 'finishTime' in build_data:
                start_time = datetime.fromisoformat(build_data['startTime'].rstrip('Z'))
                finish_time = datetime.fromisoformat(build_data['finishTime'].rstrip('Z'))
                duration_minutes = (finish_time - start_time).total_seconds() / 60  # Duration in minutes

                durations.append(duration_minutes)
                run_cost = 0  # Initialize run_cost variable

                if cumulative_duration < TOTAL_DURATION_THRESHOLD:
                    if cumulative_duration + duration_minutes > TOTAL_DURATION_THRESHOLD:
                        # Calculate the duration that exceeds the threshold
                        exceeding_duration = (cumulative_duration + duration_minutes) - TOTAL_DURATION_THRESHOLD
                        # Only add cost for the exceeding duration
                        run_cost = COST_PER_MINUTE_MICROSOFT_HOSTED * exceeding_duration
                        total_cost += run_cost
                        total_project_pipeline_cost += run_cost

                        print(f"Pipeline ID {run_id} exceeded threshold: Exceeding duration: {exceeding_duration:.2f} minutes, Cost: ${run_cost:.2f}")
                    else:
                        print(f"Pipeline ID {run_id} does not exceed threshold (cumulative duration: {cumulative_duration + duration_minutes:.2f} minutes)")
                else:
                    run_cost = COST_PER_MINUTE_MICROSOFT_HOSTED * duration_minutes
                    total_cost += run_cost
                    total_project_pipeline_cost += run_cost

                    print(f"Pipeline ID {run_id} duration: {duration_minutes:.2f} minutes, Cost: ${run_cost:.2f}")

                cumulative_duration += duration_minutes

                if build_data['result'] == 'failed':
                    total_failure_cost += run_cost

            else:
                print(f"Warning: 'finishTime' not found for run ID {run_id}. Skipping duration and cost calculation.")

            if run['result'] == 'succeeded':
                success_count += 1
            elif run['result'] == 'failed':
                failure_count += 1

            dates.append(run['createdDate'][:10])

        total_runs = success_count + failure_count
        success_rate = (success_count / total_runs) * 100 if total_runs > 0 else 0
        failure_rate = (failure_count / total_runs) * 100 if total_runs > 0 else 0
        average_duration = sum(durations) / len(durations) if durations else 0

        print(f"Pipeline: {pipeline['name']}")
        print(f"Total Cost (after exceeding threshold): ${total_cost:.2f}")
        print(f"Success rate: {success_rate:.2f}%")
        print(f"Failure rate: {failure_rate:.2f}%")
        print(f"Average pipeline duration: {average_duration:.2f} minutes")

        date_counts = Counter(dates)
        dates = list(date_counts.keys())
        counts = list(date_counts.values())
        plt.figure(figsize=(10, 6))
        plt.bar(dates, counts, color='blue')
        plt.xlabel('Date')
        plt.ylabel('Number of Pipeline Runs')
        plt.title(f'{pipeline["name"]} Pipeline Run Frequency (Last 2 Weeks)')
        plt.xticks(rotation=45)
        plt.show()

else:
    print("Pipeline data could not be retrieved.")

print("\n--- Project Summary ---")
print(f"Total Pipeline Duration: {cumulative_duration:.2f} minutes")
print(f"Total Pipeline Cost (after exceeding threshold): ${total_project_pipeline_cost:.2f}")
print(f"Total Failure Cost (after exceeding threshold): ${total_failure_cost:.2f}")
