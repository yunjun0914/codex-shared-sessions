#!/usr/bin/env bash
set -euo pipefail
source_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
destination=${CODEX_SHARED_INSTALL_DIR:-$HOME/.local/bin}
experiments=0
if [[ ${1:-} == --experiments && $# -eq 1 ]]; then
  experiments=1
elif [[ $# -ne 0 ]]; then
  echo 'usage: bash install.sh [--experiments]' >&2
  exit 2
fi
data_target=${CODEX_SHARED_DATA_DIR:-$HOME/.local/share/codex-shared-sessions}
mkdir -p "$destination"
target=$destination/codex-shared
if [[ -e $target || -L $target ]]; then
  if [[ $experiments -ne 1 ]] || ! cmp -s "$source_dir/codex-shared" "$target"; then
    echo "Refusing to overwrite $target. Review and back up the previous file first." >&2
    exit 1
  fi
fi
if [[ $experiments -eq 1 && ( -e $destination/codex-lab || -L $destination/codex-lab || -e $data_target || -L $data_target ) ]]; then
  echo 'Optional install targets already exist. Review and back up before upgrading.' >&2
  exit 1
fi
python3 -c 'import ast,sys; ast.parse(open(sys.argv[1]).read())' "$source_dir/codex-shared"
if [[ $experiments -eq 1 ]]; then
  python3 -c 'import ast,sys; ast.parse(open(sys.argv[1]).read())' "$source_dir/codex-lab"
  mkdir -p "$data_target"
  cp -a "$source_dir/templates" "$source_dir/skills" "$source_dir/examples" "$data_target/"
  install -m 755 "$source_dir/codex-lab" "$destination/codex-lab"
  echo "Installed optional codex-lab and guidance in $data_target"
fi
if [[ ! -e $target ]]; then
  install -m 755 "$source_dir/codex-shared" "$target"
fi
echo "Installed $target"
echo 'Add the destination to PATH, then run: codex-shared doctor'
echo 'No Codex login, daemon, tmux configuration or boot service was changed.'
