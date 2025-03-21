# Toyoko MCP

This project is a tool for retrieving information from Toyoko Inn.

## Overview

This tool provides the following functions:

*   Display a list of Toyoko Inn tools
*   Login
*   Display a list of regions
*   Display a list of hotels
*   Check room availability

## Usage

### (common) Clone the repository

First, clone this repository to your local machine.


### Configure for Goose

```
goose configure

This will update your existing config file
  if you prefer, you can edit it directly at /Users/sonesuke/.config/goose/config.yaml

┌   goose-configure 
│
◇  What would you like to configure?
│  Add Extension 
│
◇  What type of extension would you like to add?
│  Command-line Extension 
│
◇  What would you like to call this extension?
│  toyoko-mcp
│
◇  What command should be run?
│  uvx --from /Users/sonesuke/workspace/toyoko-mcp toyoko_mcp_cli
│
◇  Please set the timeout for this tool (in secs):
│  30
│
◇  Would you like to add environment variables?
│  Yes 
│
◇  Environment variable name:
│  CORPORATE_ID
│
◇  Environment variable value:
│  ▪▪▪▪▪▪▪▪▪▪▪▪
│
◇  Add another environment variable?
│  Yes 
│
◇  Environment variable name:
│  USER_EMAIL
│
◇  Environment variable value:
│  ▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪
│
◇  Add another environment variable?
│  Yes 
│
◇  Environment variable name:
│  USER_PASSWORD
│
◇  Environment variable value:
│  ▪▪▪▪▪▪▪▪▪▪▪
│
◇  Add another environment variable?
│  Yes 
│
◇  Environment variable name:
│  TOYOKO_MCP_HEADLESS
│
◇  Environment variable value:
│  ▪▪▪▪▪
│
◇  Add another environment variable?
│  No 
│
└  Added toyoko-mcp extension
```


## Development

### 2. Installation of Aider (Optional)

To use Aider with this project, follow these steps:

```
pip install aider-chat 
```

For other methods, please refer to the [Aider documentation](https://aider-chat.github.io/aider-docs/).
