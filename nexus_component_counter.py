import aiohttp
import asyncio
import json
import argparse
import os

# Environment variable-based credentials for Nexus API
NEXUS_AUTH = (os.environ.get("NEXUS_USERNAME"), os.environ.get("NEXUS_PASSWORD"))

async def fetch(url, session):
   """Asynchronous request to fetch data from a URL."""
   auth = aiohttp.BasicAuth(login=NEXUS_AUTH[0], password=NEXUS_AUTH[1])
   async with session.get(url, auth=auth) as response:
       response.raise_for_status()
       return await response.json()

async def get_repositories(base_url, session, repo_type=None, repo_format=None):
   """Asynchronously fetch the list of repositories, filtered by type and format if provided."""
   url = f"{base_url}/repositories"
   repositories = await fetch(url, session)
   filtered_repos = [{
       'name': repo['name'],
       'type': repo['type'],
       'format': repo['format']
   } for repo in repositories if (not repo_type or repo['type'] == repo_type) and (not repo_format or repo['format'] == repo_format)]
   print(f"Total repositories fetched: {len(filtered_repos)}")
   return filtered_repos

async def get_component_count(base_url, repo_info, session, sem, results_dict, file_lock, completion_counter, total_repos, file_name):
   """Fetch the count of components for a given repository, handling pagination, limited by a semaphore."""
   repository = repo_info['name']
   component_count = 0
   url = f"{base_url}/components?repository={repository}"
   print(f"Starting processing repository {repository}")
   async with sem:  # Control access to this section
       while url:
           data = await fetch(url, session)
           component_count += len(data['items'])
           print(f"Found {component_count} components so far in {repository}     (Completed repos: {completion_counter.value}/{total_repos})")
           url = f"{base_url}/components?repository={repository}&continuationToken={data['continuationToken']}" if 'continuationToken' in data and data['continuationToken'] else None
       results_dict[repository] = {
           'type': repo_info['type'],
           'format': repo_info['format'],
           'count': component_count
       }
   # Sort results by component count and write updated results to a file after each completion
   async with file_lock:
       sorted_results = dict(sorted(results_dict.items(), key=lambda item: item[1]['count'], reverse=True))
       with open(file_name, 'w') as file:
           json.dump(sorted_results, file, indent=4)
   async with completion_counter:
       completion_counter.value += 1
       print(f"Completed {completion_counter.value}/{total_repos}: {repository}")
   return repository, component_count

async def main():
   parser = argparse.ArgumentParser(description="Fetch component counts from Nexus repositories asynchronously.")
   parser.add_argument("--url", required=True, help="The base URL for the Nexus API.")
   parser.add_argument("--type", help="The type of repository to filter by (optional).")
   parser.add_argument("--format", help="The format of the repository to filter by (optional).")
   parser.add_argument("--concurrency", type=int, default=10, help="Maximum number of concurrent requests.")
   parser.add_argument("--output-dir", default="./", help="Directory to store output JSON files.")
   args = parser.parse_args()
   # Determine file name based on type and format provided
   file_name = f"{args.type if args.type else 'all'}_{args.format if args.format else 'all'}_components.json"
   os.makedirs(args.output_dir, exist_ok=True)
   file_name = os.path.join(args.output_dir, file_name)
   sem = asyncio.Semaphore(args.concurrency)  # Use the concurrency level from command-line args
   file_lock = asyncio.Lock()  # Lock for file writing operations
   results_dict = {}  # Shared dictionary to store results
   completion_counter = asyncio.Lock()  # Lock to protect the counter
   completion_counter.value = 0  # Initialize counter for completed repos
   async with aiohttp.ClientSession() as session:
       repositories = await get_repositories(args.url, session, args.type, args.format)
       total_repos = len(repositories)
       tasks = [
           get_component_count(args.url, repo, session, sem, results_dict, file_lock, completion_counter, total_repos, file_name)
           for repo in repositories
       ]
       await asyncio.gather(*tasks)

if __name__ == "__main__":
   asyncio.run(main())
