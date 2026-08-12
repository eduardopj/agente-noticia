Set-Location "$PSScriptRoot\.."
.\apps\api\.venv\Scripts\python.exe -m uvicorn radar_api.main:app --reload --host 127.0.0.1 --port 8000
