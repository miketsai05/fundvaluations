[< Back to project readme](../README.md)

# Getting started

Before you begin working on this repository, you will need to have the following
tools installed on your machine.

## Prerequisites

### For macOS

- **Command Line Tools for Xcode**
  <details>
    <summary>Installation instructions</summary>

    ```bash
    xcode-select --install
    ```
  </details>

- **Homebrew** ([project website](https://brew.sh/))
  <details>
    <summary>Installation instructions</summary>

    ```bash
    /bin/bash -c '$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)'
    ```

    You may need to restart your terminal session after installing this.
  </details>

- **asdf** ([project website](https://asdf-vm.com/))
  <details>
    <summary>Installation instructions</summary>

    ```bash
    brew install asdf
    ```

    Follow the installation instructions very carefully: you will need to add a
    command to your ~/.zshrc file... Something like this should do:

    ```bash
    echo -n 'source /usr/local/homebrew/opt/asdf/libexec/asdf.sh' >> ~/.zshrc
    ```

    You may need to restart your terminal session after installing this.
  </details>

  **heroku** ([project website](https://devcenter.heroku.com/articles/heroku-cli))
  <details>
  <summary>Installation instructions</summary>

  ```bash
    brew tap heroku/brew && brew install heroku
  ```

   You may need to restart your terminal session after installing this.
  </details>

- **Docker for Mac**
  ([project website](https://docs.docker.com/desktop/install/mac-install/))

### For Windows

- **Powershell**

- **pyenv for windows**
  ([project website](https://github.com/pyenv-win/pyenv-win))

  <details>
    <summary>Installation instructions</summary>

    ```powershell
    # Run Powershell as an administrator
    Set-ExecutionPolicy Unrestricted -Scope CurrentUser

    # Installs pyenv for windows
    Invoke-WebRequest `
      -UseBasicParsing `
      -Uri "https://raw.githubusercontent.com/pyenv-win/pyenv-win/master/pyenv-win/install-pyenv-win.ps1" `
      -OutFile "./install-pyenv-win.ps1"; & "./install-pyenv-win.ps1"
    ```

    You may need to restart your terminal session after installing this.
  </details>

- **nvm for windows**
  ([project website](https://github.com/coreybutler/nvm-windows))

  <details>
    <summary>Installation instructions</summary>

    Make sure you uninstall any previously installed version of node.js, as per
    the official instructions (see link to project website above).

    Then use the provided executable installer.
  </details>

- **Docker for Windows**
  ([project website](https://docs.docker.com/desktop/install/windows-install/))

## Setup script

Once you have all the prerequisites installed, you may run the provided setup
script.

### For macOS

1. Run the setup script:

```bash
./bin/setup
```

### For Windows

1. Make sure you have "Developer Mode" enabled in your Windows settings
   ([troubleshooting reference](https://github.com/coreybutler/nvm-windows/wiki/Common-Issues#permissions-exit-1-exit-5-access-denied-exit-145)).

2. Run the setup script in Powershell (run as administrator):

```powershell
Set-ExecutionPolicy Unrestricted -Scope CurrentUser
./bin/setup_for_windows.ps1
```
