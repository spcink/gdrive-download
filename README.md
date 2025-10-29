# Download Google Drive Files

## Overview

Download Google drive files from a folder and its subfolders using Python. Native Google Drive formats such as Google Docs, Google Sheets, and Google Slides will be converted to PDFs. MS Office files will be downloaded in their original format. Only docs, sheets, slides and pdfs will be downloaded.

## Setup

1. Install uvicorn if you haven't already:

```bash
brew install uv
```

2. Setup a project in the Google Cloud Console and enable the Google Drive API. Create OAuth 2.0 credentials and download the `credentials.json` file to this project's root folder.

## Usage

1. Install the required libraries:

```bash
uv sync
```

2. Run the script

```bash
uv run downloadGDrive.py
```

The first time you will be prompted to authenticate with your Google account. Follow the instructions in the terminal to complete the authentication process.

Then you will be prompted to enter the Google Drive folder ID you want to download files from. You can get the folder id by opening the folder in Google Drive and copying the id at the end of the url. The script will create a local folder named `downloads` in the current directory and download all supported files from the specified Google Drive folder and its subfolders into this local folder.
