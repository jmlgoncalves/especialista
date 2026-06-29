@echo off
echo A verificar modelos em GPU...

powershell -NoProfile -Command ^
  "$r = Invoke-RestMethod -Uri 'http://localhost:11434/api/ps' -ErrorAction Stop;" ^
  "if (-not $r.models -or $r.models.Count -eq 0) { Write-Host 'Nenhum modelo carregado.'; exit 0 }" ^
  "foreach ($m in $r.models) {" ^
  "  Write-Host ('A descarregar: ' + $m.name);" ^
  "  Invoke-RestMethod -Uri 'http://localhost:11434/api/generate' -Method Post -ContentType 'application/json' -Body ('{\"model\":\"' + $m.name + '\",\"keep_alive\":0}') | Out-Null" ^
  "}" ^
  "Write-Host 'GPU limpa.'"

if errorlevel 1 (
    echo Erro: nao foi possivel conectar ao Ollama. Verifique se esta em execucao.
)
