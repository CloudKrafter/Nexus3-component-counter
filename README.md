# Nexus Repository Component Counter

## Objective
This script asynchronously fetches component counts from Nexus Repository Manager and outputs the data to a JSON file. 
It is designed to handle multiple repositories concurrently, adjusting to network conditions and server response times. 
This utility is especially useful for administrators and teams who manage large Nexus repository instances and require regular reports on repository contents.

## Usage
### Requirements
- Python 3.7+
- `aiohttp` `asyncio` `argparse` libraries
- Nexus Repository Manager with REST API access
- `NEXUS_USERNAME` and `NEXUS_PASSWORD` environment variables for authentication

### Installation
Install the required Python library using pip:
```bash
pip install aiohttp asyncio argparse
```

### Command-Line Arguments
The script supports several command-line arguments to customize its operation:

• `--url` (required): The base URL for the Nexus API.

• `--type` (optional): Filters repositories by type (e.g., hosted, proxy).

• `--format` (optional): Filters repositories by format (e.g., maven, npm).

• `--concurrency` (optional): Specifies the maximum number of concurrent requests (default is 10).

• `--output-dir` (optional): Specifies the directory to store the output JSON files (default is the current directory).

ALL flags can be used together.

### Important note
The speed of this script depends on the performance of your Nexus instance and its total component count.
During testing it processed roughly 60.0000 components within 8~10 minutes against a Nexus instance with MINIMUM load.

### Examples
#### Basic Usage:
Run the script with the minimum required parameters:
```bash
export NEXUS_USERNAME=<yourUserName> && export NEXUS_PASSWORD='<yourPassword>'
python nexus_component_counter.py --url http://localhost:8081/service/rest/v1
```

#### Filtered Usage:
Run the script for only maven format repositories of ALL types:
```bash
python nexus_component_counter.py --url http://localhost:8081/service/rest/v1 --format maven
```

Run the script for only maven format repositories with type 'hosted':
```bash
python nexus_component_counter.py --url http://localhost:8081/service/rest/v1 --format maven --type hosted
```

#### Concurrent Usage:
Run the script with a higher level of concurrency to handle more repositories simultaneously:
```bash
python nexus_component_counter.py --url http://localhost:8081/service/rest/v1 --concurrency 20
```

#### Specified Output Directory:
Run the script and specify an output directory for the results:
```bash
python nexus_component_counter.py --url http://localhost:8081/service/rest/v1 --output-dir /path/to/output
```

### Output / Result
The script generates a JSON file named based on the type and format parameters provided. If no type or format is specified, it defaults to “all”. For example:
`hosted_maven_components.json` for hosted Maven repositories.
`all_all_components.json` if no type or format is specified.

The JSON file will contain a dictionary -sorted by count number- where each key is a repository name and the value specifying the type, format, and count of components within that repository:
```json
{
 "repo1": {
   "type": "hosted",
   "format": "maven",
   "count": 1200
 },
 "repo2": {
   "type": "proxy",
   "format": "npm",
   "count": 3000
 }
}
```
This file provides a clear and organized view of component counts across your Nexus repositories, useful for auditing, monitoring, and reporting purposes.
