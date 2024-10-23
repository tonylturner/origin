# Origin

## Overview

The **Origin** OSINT project is a tool designed to fetch and analyze contributors, forks, and commit details from any GitHub repository. The tool is designed around the idea of provenance for open-source software and other associated risk characteristics related to software origins.

## Features

- Fetch contributors, forks, and commit details from a GitHub repository.
- Display commit deltas and code changes for each contributor.
- Identify contributors from a predefined list of adversarial countries.
- Export contributor data to CSV.
  
## Adversarial Country Detection

The tool checks the geographic location of contributors and identifies contributors from adversarial countries based on a predefined list: [China, Russia, Iran, North Korea, Cuba, Venezuela]


## Installation

### Prerequisites

- Python 3.8+
- GitHub API Token (stored in `.env` file)
- LocationIQ API key (optional, for additional location verification)

### Dependencies

Install the required dependencies by running:

```bash
pip install -r requirements.txt
```

# Usage:

Fetch project contributors and display them and their origins:

```bash
python3 origin.py -p <GITHUB_REPOSITORY_URL>
```

Show commit deltas for each contributor:

```bash
python3 origin.py -p <GITHUB_REPOSITORY_URL> -c
```

Show detailed commit information and code changes for each contributor:

```bash
python3 origin.py -p <GITHUB_REPOSITORY_URL> --show-code
```

Identify contributors from adversarial countries:

```bash
python3 origin.py -p <GITHUB_REPOSITORY_URL> --adversarial
```

Export results to CSV:

```bash
python3 origin.py -p <GITHUB_REPOSITORY_URL> --csv
```

Check rate limits for GitHub and LocationIQ API:

```bash
python3 origin.py --rate-limit
```

Verbose output:

```bash
python3 origin.py -p <GITHUB_REPOSITORY_URL> -v/-vv/-vvv
```

Environment variables:

Origin uses a .env file to store sensitive configuration such as the GitHub API token and LocationIQ API key. Create a .env file in the root of your project with the following content:

```
GITHUB_TOKEN=your_github_token_here
LOCATIONIQ_API_KEY=your_locationiq_key_here
NLTK_DATA=./data/nltk
```

License
This project is licensed under the Apache 2.0 license
