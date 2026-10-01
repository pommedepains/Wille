# ═══════════════════════════════════════════════════════════════════
# Wille default .bashrc
# Personal overrides go in ~/.bashrc.local — never touched by updates.
# ═══════════════════════════════════════════════════════════════════

# Source system bashrc if it exists
[ -f /etc/bash.bashrc ] && . /etc/bash.bashrc

# Stop here if not running interactively
[[ $- != *i* ]] && return

# ─── Standard aliases ──────────────────────────────────────────────
alias ls='ls --color=auto'
alias grep='grep --color=auto'

# ─── Wille terminal ────────────────────────────────────────────
_wille_shell_dir="${XDG_CONFIG_HOME:-$HOME/.config}/quickshell"
if [[ -r "$_wille_shell_dir/wille-prompt.sh" ]]; then
    . "$_wille_shell_dir/wille-prompt.sh"
fi

# Show the header once per interactive Bash process, including new windows.
if [[ -x "$_wille_shell_dir/wille-welcome.sh" && ${_wille_welcome_pid-} != "$BASHPID" ]]; then
    _wille_welcome_pid=$BASHPID
    "$_wille_shell_dir/wille-welcome.sh"
fi
unset _wille_shell_dir

# ─── User-specific overrides ───────────────────────────────────────
[ -f ~/.bashrc.local ] && . ~/.bashrc.local

# Add user-local executables to PATH
export PATH="$HOME/.local/bin:$PATH"
