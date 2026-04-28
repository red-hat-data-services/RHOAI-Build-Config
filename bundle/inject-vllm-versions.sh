#!/usr/bin/env bash
#
# inject-vllm-versions.sh
#
# Extracts the upstream vLLM version from container image SBOMs (via cosign)
# for each RHAIIS vLLM image found in the operator CSV, and injects
# corresponding _UPSTREAM_VERSION env vars back into the CSV.
#
# The script uses sed for surgical edits to avoid reformatting the YAML.
#
# Usage:
#   ./inject-vllm-versions.sh <csv-path>
#
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <csv-path>" >&2
  exit 1
fi

CSV_PATH="$1"

if [[ ! -f "$CSV_PATH" ]]; then
  echo "ERROR: CSV not found: $CSV_PATH" >&2
  exit 1
fi

ERRORS=0
INJECTED=0

# extract_vllm_version <image-ref>
#
# Downloads the SBOM for a multi-arch image index, finds the first
# per-architecture image digest, then downloads that arch-specific SBOM
# and extracts the vLLM Python package version.
extract_vllm_version() {
  local image_ref="$1"

  # Step 1: Get a per-arch digest from the index-level SBOM.
  # The index SBOM only lists image variants; actual packages are in per-arch SBOMs.
  local arch_digest
  arch_digest=$(cosign download sbom "$image_ref" 2>/dev/null | python3 -c "
import sys, json
data = json.load(sys.stdin)
for pkg in data.get('packages', []):
    for ref in pkg.get('externalRefs', []):
        loc = ref.get('referenceLocator', '')
        if ref.get('referenceType') == 'purl' and 'arch=' in loc:
            import re
            m = re.search(r'sha256:[a-f0-9]+', loc)
            if m:
                print(m.group(0))
                sys.exit(0)
sys.exit(1)
") || return 1

  # Build the per-arch image reference (same repo, arch-specific digest)
  local repo
  repo="${image_ref%%@*}"
  local arch_ref="${repo}@${arch_digest}"

  # Step 2: Download the per-arch SBOM and extract the vLLM package version.
  cosign download sbom "$arch_ref" 2>/dev/null | python3 -c "
import sys, json
data = json.load(sys.stdin)
for pkg in data.get('packages', []):
    if pkg.get('name') == 'vllm':
        print(pkg.get('versionInfo', ''))
        sys.exit(0)
sys.exit(1)
" || return 1
}

# Read RELATED_IMAGE_RHAII[S]_VLLM_*_IMAGE entries directly from the CSV
while IFS= read -r line; do
  # Extract the env var name (e.g. RELATED_IMAGE_RHAII_VLLM_CUDA_IMAGE or RELATED_IMAGE_RHAIIS_VLLM_CUDA_IMAGE)
  name=$(echo "$line" | sed -n 's/.*- name: \(RELATED_IMAGE_RHAII[S]\?_VLLM_[A-Z_]*_IMAGE\)$/\1/p')
  [[ -z "$name" ]] && continue

  # Read the next line to get the value
  value_line=$(grep -A1 "name: ${name}$" "$CSV_PATH" | tail -1)
  value=$(echo "$value_line" | sed 's/.*value: //')

  version_name="${name}_UPSTREAM_VERSION"
  echo "-> Inspecting SBOM for ${name}..."

  # Image values may have the format: registry/org/repo:tag@sha256:digest
  # cosign needs: registry/org/repo@sha256:digest
  image_ref="${value}"
  if [[ "$image_ref" == *:*@* ]]; then
    image_ref="${image_ref%%@*}"
    image_ref="${image_ref%:*}@${value#*@}"
  fi

  version=$(extract_vllm_version "$image_ref") || true

  if [[ -z "$version" ]]; then
    echo "ERROR: Failed to extract vLLM version from SBOM for ${name} (${image_ref})" >&2
    ERRORS=$((ERRORS + 1))
    continue
  fi

  echo "   ${version_name} = ${version}"

  # Remove any existing _UPSTREAM_VERSION entry for this image (if re-running)
  sed -i "/- name: ${version_name}$/{N;d;}" "$CSV_PATH"

  # Detect the indentation from the _IMAGE line
  indent=$(grep "name: ${name}$" "$CSV_PATH" | sed 's/\(^[[:space:]]*\).*/\1/')

  # Insert _UPSTREAM_VERSION entry right after the _IMAGE value line
  sed -i "/- name: ${name}$/{N;a\\
${indent}- name: ${version_name}\n${indent}  value: \"${version}\"
}" "$CSV_PATH"

  INJECTED=$((INJECTED + 1))
done < <(grep -E "RELATED_IMAGE_RHAIIS?_VLLM_.*_IMAGE$" "$CSV_PATH")

if [[ $INJECTED -eq 0 ]]; then
  echo "ERROR: No RELATED_IMAGE_RHAII[S]_VLLM_*_IMAGE entries found in $CSV_PATH" >&2
  exit 1
fi

echo ""
echo "=== vLLM Version Injection Summary ==="
grep -E -A1 "RELATED_IMAGE_RHAIIS?_VLLM_.*_UPSTREAM_VERSION" "$CSV_PATH" | grep -v "^--$" | paste - - | sed 's/.*name: /  /;s/[[:space:]]*value: / = /'
echo "======================================="

if [[ $ERRORS -gt 0 ]]; then
  echo "ERROR: Failed to extract version for $ERRORS image(s)" >&2
  exit 1
fi

echo "Done. Injected ${INJECTED} version env var(s)."
