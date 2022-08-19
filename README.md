# TigerGraph Endpoints to Postman File

## About

This script will create a Postman file from a TigerGraph solution.

## Quick Start - Static

1. Clone and enter this repository.
```
git clone https://github.com/TigerGraph-DevLabs/TG_Endpoints_to_Postman.git
cd TG_Endpoints_to_Postman
```
2. Create a new virtual environment and activate it
```
python3 -m venv venv
source venv/bin/activate
```
3. Install pyTigerGraph
```
pip install pyTigerGraph
```
4. Update [`cred.py`](cred.py) to the appropriate graph credentials
5. Run `python3 endpoints_to_postman.py`

## Quick Start - Interactive

1. Clone and enter this repository.
```
git clone https://github.com/TigerGraph-DevLabs/TG_Endpoints_to_Postman.git
cd TG_Endpoints_to_Postman
```
2. Create a new virtual environment and activate it
```
python3 -m venv venv
source venv/bin/activate
```
3. Install pyTigerGraph and Rich
```
pip install pyTigerGraph rich
```
4. Run `python3 interactive_postman.py` and follow the prompts
