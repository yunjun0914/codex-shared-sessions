#!/usr/bin/env bash
set -euo pipefail
source_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
destination=${CODEX_SHARED_INSTALL_DIR:-$HOME/.local/bin}
mkdir -p "$destination"
target=$destination/codex-shared
if [[ -e $target || -L $target ]]; then
  echo "Refusing to overwrite $target. Review and back up the previous file first." >&2
  exit 1
fi
python3 -c 'import ast,sys; ast.parse(open(sys.argv[1]).read())' "$source_dir/codex-shared"
install -m 755 "$source_dir/codex-shared" "$target"
echo "Installed $target"
echo 'Add the destination to PATH, then run: codex-shared doctor'
echo 'No Codex login, daemon, tmux configuration or boot service was changed.'
