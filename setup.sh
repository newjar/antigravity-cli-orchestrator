#!/bin/sh

set -eu

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)

cat <<'BANNER'
+---------------------------------------+
|    _    ______   __                   |
|   / \  / ___\ \ / /                   |
|  / _ \| |  _ \ V /                    |
| / ___ \ |_| | | |                     |
|/_/   \_\____| |_|                     |
|                                       |
|       O R C H E S T R A T O R         |
|       Choose models per role.         |
|    Configure Antigravity (agy).       |
+---------------------------------------+
BANNER

printf '%s\n' 'Interactive project setup for Antigravity (agy)'
printf '%s' 'Target repository path: '
IFS= read -r target_path || exit 1

if [ -z "$target_path" ] || [ ! -d "$target_path" ]; then
    printf 'Error: target must be an existing directory: %s\n' "${target_path:-<empty>}" >&2
    exit 1
fi

target_dir=$(CDPATH= cd -- "$target_path" && pwd -P)
if [ "$target_dir" = "$script_dir" ]; then
    printf 'Error: target repository must be different from the setup source directory.\n' >&2
    exit 1
fi

confirm() {
    prompt=$1
    default_yes=$2
    if [ "$default_yes" = yes ]; then
        suffix='[Y/n]'
    else
        suffix='[y/N]'
    fi

    while :; do
        printf '%s %s ' "$prompt" "$suffix"
        if ! IFS= read -r answer; then
            printf '\nSetup cancelled: input ended before setup was complete.\n' >&2
            exit 1
        fi

        case "$answer" in
            y|Y|yes|YES|Yes) return 0 ;;
            n|N|no|NO|No) return 1 ;;
            '') [ "$default_yes" = yes ] && return 0 || return 1 ;;
            *) printf '%s\n' 'Please answer yes or no.' ;;
        esac
    done
}

# Model catalog mapping (gemini-3.8-* and claude-*)
get_catalog_model() {
    case "$1" in
        1)  printf 'gemini-3.8-flash-high' ;;
        2)  printf 'gemini-3.8-flash-medium' ;;
        3)  printf 'gemini-3.8-flash-low' ;;
        4)  printf 'claude-opus-5-5-high' ;;
        5)  printf 'claude-opus-5-5-medium' ;;
        6)  printf 'claude-opus-5-5-low' ;;
        7)  printf 'claude-sonnet-5-5-high' ;;
        8)  printf 'claude-sonnet-5-5-medium' ;;
        9)  printf 'claude-sonnet-5-5-low' ;;
        *)  return 1 ;;
    esac
}

print_catalog() {
    printf '\n%s\n' 'Available Antigravity Models (Gemini 3.8 & Claude 5.5):'
    printf '  1)  gemini-3.8-flash-high      (Gemini 3.8 Flash - High)\n'
    printf '  2)  gemini-3.8-flash-medium    (Gemini 3.8 Flash - Medium)\n'
    printf '  3)  gemini-3.8-flash-low       (Gemini 3.8 Flash - Low)\n'
    printf '  4)  claude-opus-5-5-high       (Claude Opus 5.5 - High)\n'
    printf '  5)  claude-opus-5-5-medium     (Claude Opus 5.5 - Medium)\n'
    printf '  6)  claude-opus-5-5-low        (Claude Opus 5.5 - Low)\n'
    printf '  7)  claude-sonnet-5-5-high     (Claude Sonnet 5.5 - High)\n'
    printf '  8)  claude-sonnet-5-5-medium   (Claude Sonnet 5.5 - Medium)\n'
    printf '  9)  claude-sonnet-5-5-low      (Claude Sonnet 5.5 - Low)\n'
    printf '  10) custom                     (Enter custom model ID)\n'
}

select_model() {
    role_name=$1
    default_model=$2

    while :; do
        printf 'Model for %s [%s]: ' "$role_name" "$default_model"
        if ! IFS= read -r answer; then
            printf '\nSetup cancelled.\n' >&2
            exit 1
        fi

        case "$answer" in
            '') selected_model=$default_model; return ;;
            10|custom|CUSTOM)
                printf 'Enter custom model ID: '
                if ! IFS= read -r custom_id; then exit 1; fi
                selected_model=$custom_id
                return
                ;;
            *)
                if cat_model=$(get_catalog_model "$answer"); then
                    selected_model=$cat_model
                    return
                else
                    # Direct model string input
                    selected_model=$answer
                    return
                fi
                ;;
        esac
    done
}

select_concurrency() {
    concurrency_default=$1
    while :; do
        printf 'Maximum concurrent subagents [%s]: ' "$concurrency_default"
        if ! IFS= read -r answer; then
            printf '\nSetup cancelled.\n' >&2
            exit 1
        fi

        case "$answer" in
            '') chosen_concurrency=$concurrency_default; return ;;
            *[!0-9]*|0*) printf '%s\n' 'Enter a positive integer without leading zeroes.' ;;
            *) chosen_concurrency=$answer; return ;;
        esac
    done
}

overwrite_paths() {
    source_path=$1
    destination_path=$2
    component_name=$(basename "$source_path")

    if [ -f "$source_path" ]; then
        if [ -e "$destination_path" ] || [ -L "$destination_path" ]; then
            printf '%s\n' "$component_name"
        fi
        return
    fi

    find "$source_path" -type f -print | while IFS= read -r source_file; do
        relative_path=${source_file#"$source_path"/}
        destination_file=$destination_path/$relative_path
        if [ -e "$destination_file" ] || [ -L "$destination_file" ]; then
            printf '%s\n' "$component_name/$relative_path"
        fi
    done
}

print_overwrites() {
    source_path=$1
    destination_path=$2

    overwrite_list=$(overwrite_paths "$source_path" "$destination_path")
    if [ -z "$overwrite_list" ]; then
        return
    fi

    printf '%s\n' 'WARNING: the following existing files will be overwritten:'
    printf '%s\n' "$overwrite_list" | sed 's/^/  - /'
}

replace_toml_setting() {
    toml_file=$1
    toml_key=$2
    toml_val=$3
    toml_temp=$(mktemp "$toml_file.XXXXXX")

    awk -v key="$toml_key" -v value="$toml_val" '
        $0 ~ ("^" key "[[:space:]]*=") {
            print key " = \"" value "\""
            found = 1
            next
        }
        { print }
        END { if (!found) exit 1 }
    ' "$toml_file" > "$toml_temp"

    mv "$toml_temp" "$toml_file"
}

replace_toml_int() {
    toml_file=$1
    toml_key=$2
    toml_val=$3
    toml_temp=$(mktemp "$toml_file.XXXXXX")

    awk -v key="$toml_key" -v value="$toml_val" '
        $0 ~ ("^" key "[[:space:]]*=") {
            print key " = " value
            found = 1
            next
        }
        { print }
        END { if (!found) exit 1 }
    ' "$toml_file" > "$toml_temp"

    mv "$toml_temp" "$toml_file"
}

# 1. Print model options
print_catalog

# 2. Select models for each role
select_model 'root / orchestrator' 'claude-sonnet-5-5-high'
chosen_root=$selected_model

select_model 'default subagent' 'gemini-3.8-flash-high'
chosen_default_sub=$selected_model

select_model 'explorer' 'gemini-3.8-flash-high'
chosen_explorer=$selected_model

select_model 'worker' 'claude-sonnet-5-5-high'
chosen_worker=$selected_model

select_model 'tester' 'gemini-3.8-flash-high'
chosen_tester=$selected_model

select_model 'reviewer' 'claude-sonnet-5-5-high'
chosen_reviewer=$selected_model

select_model 'researcher' 'gemini-3.8-flash-high'
chosen_researcher=$selected_model

select_concurrency '4'

printf '\n%s\n' 'Selected configuration:'
printf '  root / orchestrator:   %s\n' "$chosen_root"
printf '  default subagent:      %s\n' "$chosen_default_sub"
printf '  explorer:              %s\n' "$chosen_explorer"
printf '  worker:                %s\n' "$chosen_worker"
printf '  tester:                %s\n' "$chosen_tester"
printf '  reviewer:              %s\n' "$chosen_reviewer"
printf '  researcher:            %s\n' "$chosen_researcher"
printf '  max subagents:         %s\n' "$chosen_concurrency"

# Component selection
printf '\n%s\n' 'Component installation:'
install_agy=no
install_skill=no
install_rules=no

if confirm 'Install .agy role configuration (.agy/config.toml and agents/*.toml)?' yes; then
    install_agy=yes
fi

if confirm 'Install agy-orchestrator skill (.agents/skills/agy-orchestrator/)?' yes; then
    install_skill=yes
fi

if confirm 'Install orchestration rules (GEMINI.md)?' yes; then
    install_rules=yes
fi

# Apply components
if [ "$install_agy" = yes ]; then
    print_overwrites "$script_dir/templates/agy" "$target_dir/.agy"
    mkdir -p "$target_dir/.agy/agents"
    cp -p "$script_dir/templates/agy/config.toml" "$target_dir/.agy/config.toml"
    for role in explorer worker tester reviewer researcher; do
        cp -p "$script_dir/templates/agy/agents/$role.toml" "$target_dir/.agy/agents/$role.toml"
    done

    # Update selected values
    replace_toml_setting "$target_dir/.agy/config.toml" model "$chosen_root"
    replace_toml_setting "$target_dir/.agy/config.toml" default_subagent_model "$chosen_default_sub"
    replace_toml_int "$target_dir/.agy/config.toml" max_concurrent_threads_per_session "$chosen_concurrency"

    replace_toml_setting "$target_dir/.agy/agents/explorer.toml" model "$chosen_explorer"
    replace_toml_setting "$target_dir/.agy/agents/worker.toml" model "$chosen_worker"
    replace_toml_setting "$target_dir/.agy/agents/tester.toml" model "$chosen_tester"
    replace_toml_setting "$target_dir/.agy/agents/reviewer.toml" model "$chosen_reviewer"
    replace_toml_setting "$target_dir/.agy/agents/researcher.toml" model "$chosen_researcher"

    printf 'Installed .agy configuration to %s/.agy\n' "$target_dir"
fi

if [ "$install_skill" = yes ]; then
    skill_src="$script_dir/.agents/skills/agy-orchestrator"
    skill_dst="$target_dir/.agents/skills/agy-orchestrator"
    print_overwrites "$skill_src" "$skill_dst"
    mkdir -p "$skill_dst"
    cp -p "$skill_src/SKILL.md" "$skill_dst/SKILL.md"
    printf 'Installed agy-orchestrator skill to %s\n' "$skill_dst"
fi

if [ "$install_rules" = yes ]; then
    gemini_target="$target_dir/GEMINI.md"
    rule_content=$(cat "$script_dir/templates/GEMINI.md")

    if [ -f "$gemini_target" ]; then
        if grep -q "agy-orchestrator" "$gemini_target"; then
            printf 'Orchestrator instructions already present in %s\n' "$gemini_target"
        else
            printf '\n\n%s\n' "$rule_content" >> "$gemini_target"
            printf 'Appended orchestrator instructions to %s\n' "$gemini_target"
        fi
    else
        printf '%s\n' "$rule_content" > "$gemini_target"
        printf 'Created %s\n' "$gemini_target"
    fi
fi

printf '\nSetup complete! You can now use Antigravity (agy) in %s with agy-orchestrator.\n' "$target_dir"
