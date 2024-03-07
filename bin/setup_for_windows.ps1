$EMOJI_YARN = [System.Char]::ConvertFromUtf32([System.Convert]::toInt32("1F9F6", 16))
$EMOJI_SNAKE = [System.Char]::ConvertFromUtf32([System.Convert]::toInt32("1F40D", 16))
$EMOJI_PUZZLE_PIECE = [System.Char]::ConvertFromUtf32([System.Convert]::toInt32("1F9E9", 16))
$EMOJI_CHECKBOX = [System.Char]::ConvertFromUtf32([System.Convert]::toInt32("2611", 16))
$EMOJI_RED_CROSS = [System.Char]::ConvertFromUtf32([System.Convert]::toInt32("274C", 16))

function Write-Header {
  param ($Msg)
  Write-Host -NoNewline " -- ${Msg} -- " -ForegroundColor White -BackgroundColor Blue
  Write-Host -NoNewline "`n`n"
}

function Write-Normal {
  param ($Msg)
  Write-Host -NoNewline $Msg
}

function Write-Bold {
  param ($Msg)
  Write-Host -NoNewline $Msg -ForegroundColor White
}

function Write-Green {
  param ($Msg)
  Write-Host -NoNewline $Msg -ForegroundColor Green
}

function Write-Red {
  param ($Msg)
  Write-Host -NoNewline $Msg -ForegroundColor Red
}

function Test-CommandExists {
  param ($Tool)
  return (Get-Command -ErrorAction Ignore -Type Application $Tool)
}

function Test-Prerequisite {
  param ($Tool, $Url)
  if (Test-CommandExists $Tool) {
    Write-Bold " ${EMOJI_CHECKBOX}   ${Tool}"
    Write-Normal " is already installed.`n"
  } else {
    Write-Red "`n ${EMOJI_RED_CROSS}  ${Tool} not found.`n"
    Write-Red "     You'll need to install it before proceeding:`n"
    Write-Red "     - ${Url}`n`n"
    Exit 1
  }
}

function Get-ToolVersion {
  param ($Tool)
  $fileLocation = "./.tool-versions"
  foreach ($line in (Get-Content $fileLocation).Trim() -split '\r?\n') {
    if ($line -Match $Tool) {
      return $line.Replace($Tool, "").Trim()
    }
  }
  Write-Red "No entry found for ${Tool} in .tool-versions"
  Exit 1
}

function DisableWindowsAppExecutionAliases {
  # More context around why this is necessary:
  # - https://superuser.com/questions/1728816/manage-windows-app-execution-aliases-from-powershell
  # - https://stackoverflow.com/questions/58754860/cmd-opens-windows-store-when-i-type-python
  Write-Normal "Disabling Window's `"App Execution Aliases`" for python... "
  if (Test-Path -Path $env:LOCALAPPDATA\Microsoft\WindowsApps\python.exe) {
    Remove-Item $env:LOCALAPPDATA\Microsoft\WindowsApps\python.exe
  }
  if (Test-Path -Path $env:LOCALAPPDATA\Microsoft\WindowsApps\python3.exe) {
    Remove-Item $env:LOCALAPPDATA\Microsoft\WindowsApps\python3.exe
  }
  Write-Normal "Done!`n"
}

Write-Green "Running the setup script for the fundvaluations repo`n`n"

Write-Header "Checking for prerequisites"
Test-Prerequisite pyenv "https://github.com/pyenv-win/pyenv-win"
Test-Prerequisite nvm "https://github.com/coreybutler/nvm-windows"
Test-Prerequisite docker-compose "https://docs.docker.com/desktop/install/windows-install/"
# Test-Prerequisite heroku "https://devcenter.heroku.com/articles/heroku-cli"
Write-Normal "`n"

# Write-Header "Ensure a git remote exists for Heroku"
# heroku git:remote -a fundvaluations

Write-Header "Configuring environments"
Write-Bold " ${EMOJI_PUZZLE_PIECE}  Configuring nodejs environment...`n`n"
nvm install (Get-ToolVersion "nodejs")
nvm use (Get-ToolVersion "nodejs")
Start-Sleep -seconds 1
nvm on
Write-Bold "`n ${EMOJI_PUZZLE_PIECE}  Configuring python environment...`n`n"
pyenv update
pyenv install (Get-ToolVersion "python")
pyenv local (Get-ToolVersion "python")
DisableWindowsAppExecutionAliases
Write-Normal "`n"

Write-Header "Installing python dev dependencies"
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
pyenv rehash
Write-Normal "`n"

Write-Header "Setting up pre-commit hooks"
pre-commit install
Write-Normal "`n"

Write-Header "Setting up yarn shortcuts"
Write-Bold " ${EMOJI_YARN}  Updating npm...`n"
# If you encounter any issues with npm not being found, see this:
# - https://github.com/coreybutler/nvm-windows/wiki/Common-Issues#why-do-i-get-npm-is-not-recognized
npm install -g npm@latest
Write-Bold "`n ${EMOJI_YARN}  Installing yarn...`n"
npm install -g yarn
Write-Normal "`n"

Write-Green "`n ${EMOJI_SNAKE}  Good to go!`n`n"
