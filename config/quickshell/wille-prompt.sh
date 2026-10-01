#!/bin/bash
# Source from .bashrc. Keep Bash and Kitty's existing command hooks intact.
if [[ $- != *i* || ! -t 1 || ${TERM-} == dumb ]]; then
    return 0 2>/dev/null || exit 0
fi

_wille_prompt() {
    # Capture the command result before any formatting or Git commands run.
    local status=$? path=$PWD branch width=80 rule_width suffix_width
    # Byte lengths leave conservative spacing for non-ASCII directory names.
    local LC_ALL=C
    if [[ -n ${HOME-} ]]; then
        case "$path" in
            "$HOME") path='~' ;;
            "$HOME/"*) path="~/${path#"$HOME/"}" ;;
        esac
    fi
    _wille_prompt_parent=''
    _wille_prompt_directory=$path
    if [[ $path == */* && $path != / ]]; then
        _wille_prompt_parent="${path%/*}/"
        _wille_prompt_directory=${path##*/}
    fi
    _wille_prompt_branch=''
    if command -v git >/dev/null 2>&1; then
        if branch=$(command git symbolic-ref --quiet --short HEAD 2>/dev/null); then
            _wille_prompt_branch=$branch
        elif branch=$(command git rev-parse --short HEAD 2>/dev/null); then
            _wille_prompt_branch="detached:$branch"
        fi
    fi
    _wille_prompt_error=''
    (( status == 0 )) || _wille_prompt_error="exit $status"
    # Keep the bracket pair visible even when there is no Git branch.
    suffix_width=$((${#_wille_prompt_branch} + 5))
    [[ -z $_wille_prompt_error ]] || (( suffix_width += ${#_wille_prompt_error} + 1 ))
    if [[ ${COLUMNS-} =~ ^[0-9]{1,4}$ ]] && (( 10#$COLUMNS > 0 )); then
        width=$((10#$COLUMNS))
    fi
    rule_width=$((width - ${#path} - suffix_width - 2))
    (( rule_width >= 3 )) || rule_width=3
    printf -v _wille_prompt_rule '%*s' "$rule_width" ''
    _wille_prompt_rule=${_wille_prompt_rule// /─}

    # P4: directory, quiet divider, then branch; a cyan corner starts the command.
    # Expand values as data at render time, never interpolate them into prompt code.
    PS1='\n\[\e[38;2;146;144;141m\]${_wille_prompt_parent}'
    PS1+='\[\e[38;2;232;232;232m\]${_wille_prompt_directory}'
    PS1+=' \[\e[38;2;60;64;68m\]${_wille_prompt_rule}'
    PS1+=' \[\e[38;2;30;200;240m\][ \[\e[38;2;146;144;141m\]${_wille_prompt_branch}\[\e[38;2;30;200;240m\] ]'
    if (( status != 0 )); then
        PS1+=' \[\e[38;2;30;200;240m\]${_wille_prompt_error}'
    fi
    PS1+='\[\e[0m\]\n\[\e[38;2;30;200;240m\]└\[\e[0m\] '

    return "$status"
}

_wille_install_prompt() {
    local hook
    local -a retained_hooks=()
    for hook in "${PROMPT_COMMAND[@]}"; do
        case "$hook" in
            _wille_prompt|_tsugumori_prompt|_nier_prompt_cmd|'') continue ;;
            '_nier_prompt_cmd;'*) hook=${hook#'_nier_prompt_cmd;'} ;;
        esac
        retained_hooks+=("$hook")
    done
    PROMPT_COMMAND=(_wille_prompt "${retained_hooks[@]}")
}

_wille_install_prompt
unset -f _wille_install_prompt _nier_prompt_cmd
