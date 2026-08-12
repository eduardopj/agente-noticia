Set-Location "$PSScriptRoot\..\apps\web"
$env:API_BASE_URL = "http://127.0.0.1:8000"
npm run dev
