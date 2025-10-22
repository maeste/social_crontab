# Shell Completion for SocialCLI

SocialCLI supports tab completion for all commands, options, and flags in Bash, Zsh, Fish, and PowerShell shells. This guide shows you how to install and use completion in your preferred shell.

## Quick Start

Generate a completion script for your shell:

```bash
socialcli completion bash    # For Bash
socialcli completion zsh     # For Zsh
socialcli completion fish    # For Fish
socialcli completion powershell  # For PowerShell
```

Then follow the installation instructions below for your shell.

## Bash

### Installation

1. Generate the completion script:
   ```bash
   socialcli completion bash > ~/.socialcli-completion.bash
   ```

2. Add the following line to your `~/.bashrc`:
   ```bash
   source ~/.socialcli-completion.bash
   ```

3. Reload your shell configuration:
   ```bash
   source ~/.bashrc
   ```

### Alternative: System-Wide Installation

For system-wide installation (requires sudo):

```bash
socialcli completion bash | sudo tee /etc/bash_completion.d/socialcli > /dev/null
```

Then restart your shell or run `source /etc/bash_completion.d/socialcli`.

## Zsh

### Installation

1. Generate the completion script:
   ```zsh
   socialcli completion zsh > ~/.socialcli-completion.zsh
   ```

2. Add the following line to your `~/.zshrc`:
   ```zsh
   source ~/.socialcli-completion.zsh
   ```

3. Reload your shell configuration:
   ```zsh
   source ~/.zshrc
   ```

### Alternative: Using Completion Directory

If you have a completion directory in your `$fpath` (common in Oh My Zsh):

```zsh
socialcli completion zsh > ~/.oh-my-zsh/completions/_socialcli
```

Then restart your shell or run `compinit` to reload completions.

## Fish

### Installation

Fish completions are automatically loaded from `~/.config/fish/completions/`.

1. Ensure the completions directory exists:
   ```fish
   mkdir -p ~/.config/fish/completions
   ```

2. Generate the completion script:
   ```fish
   socialcli completion fish > ~/.config/fish/completions/socialcli.fish
   ```

3. Completions will be available immediately (no need to restart the shell).

### System-Wide Installation

For system-wide installation:

```fish
socialcli completion fish | sudo tee /usr/share/fish/vendor_completions.d/socialcli.fish > /dev/null
```

## PowerShell

### Installation

1. Find your PowerShell profile location:
   ```powershell
   echo $PROFILE
   ```

2. Create the profile directory if it doesn't exist:
   ```powershell
   New-Item -ItemType Directory -Path (Split-Path $PROFILE) -Force
   ```

3. Add the completion script to your profile:
   ```powershell
   socialcli completion powershell | Out-File -Append $PROFILE -Encoding UTF8
   ```

4. Reload your profile:
   ```powershell
   . $PROFILE
   ```

## Using Tab Completion

Once installed, you can use tab completion for:

### Commands

```bash
socialcli <TAB>
# Shows: comment, completion, login, post, prune, queue, run-scheduler
```

### Options and Flags

```bash
socialcli post --<TAB>
# Shows: --file, --provider, --help

socialcli queue --<TAB>
# Shows: --list, --provider, --status, --help
```

### Command Help

```bash
socialcli login <TAB><TAB>
# Shows available options for the login command
```

## Troubleshooting

### Completion Not Working

1. **Verify installation**: Make sure you sourced the completion script or restarted your shell.

2. **Check if completion is loaded** (Bash):
   ```bash
   complete -p socialcli
   ```
   This should show the completion function registered for `socialcli`.

3. **Check if completion is loaded** (Zsh):
   ```zsh
   which _socialcli
   ```
   This should show the path to the completion function.

4. **Regenerate the script**: If you updated SocialCLI, regenerate the completion script to get the latest commands.

### Completion Shows Errors

If you see errors when using tab completion:

1. Make sure Click is up to date:
   ```bash
   pip install --upgrade click
   ```

2. Regenerate the completion script:
   ```bash
   socialcli completion bash > ~/.socialcli-completion.bash
   source ~/.socialcli-completion.bash
   ```

### Completion Conflicts

If you have multiple versions of SocialCLI installed:

1. Check which version is active:
   ```bash
   which socialcli
   ```

2. Ensure the completion script matches the active version.

## Advanced Usage

### Temporary Completion (Testing)

To temporarily enable completion without modifying your shell config:

**Bash:**
```bash
eval "$(socialcli completion bash)"
```

**Zsh:**
```zsh
eval "$(socialcli completion zsh)"
```

This enables completion for the current shell session only.

### Custom Completion Location

You can save the completion script anywhere and source it:

```bash
# Generate
socialcli completion bash > /path/to/my/completions/socialcli.bash

# Source in ~/.bashrc
source /path/to/my/completions/socialcli.bash
```

## How It Works

SocialCLI uses Click's built-in shell completion system. When you press Tab:

1. Your shell calls the completion function
2. The function invokes `socialcli` with special environment variables
3. SocialCLI returns available completions based on the current context
4. Your shell displays the completions

This means completions are always up-to-date with your installed version of SocialCLI.

## See Also

- [Click Documentation on Shell Completion](https://click.palletsprojects.com/en/8.1.x/shell-completion/)
- [SocialCLI README](../README.md)
- [SocialCLI Commands Documentation](COMMANDS.md)
