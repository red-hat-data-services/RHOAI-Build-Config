set -eo pipefail
source "$(dirname $0)/sealights-helper.sh"

sed=sed
if [[ "$(uname -s)" == "Darwin" ]]; then
  sed=gsed
fi

SEALIGHTS_INTEGRATED_REPOS=odh-dashboard-rhel9 

for SEALIGHTS_INTEGRATED_REPO in $SEALIGHTS_INTEGRATED_REPOS; do
  echo "Processing $SEALIGHTS_INTEGRATED_REPO"

  ### Find the actual build uri
  REAL_URI=$(grep "registry\.redhat\.io/rhoai" bundle/manifests/rhods-operator.clusterserviceversion.yaml | \
    grep -m 1 "$SEALIGHTS_INTEGRATED_REPO" | grep -E -o 'registry\.redhat\.io/rhoai/.*@sha256:.{64}')
  REAL_QUAY_URI=$(echo "$REAL_URI" | $sed 's/registry\.redhat\.io/quay.io/')
  echo "Found $REAL_URL"
  echo " -> converting to $REAL_QUAY_URI"

  SEALIGHTS_QUAY_URI=$(get_sealights_image "$REAL_QUAY_URI" "build-sealights-image-index" | tail -n 1)
  SEALIGHTS_URI=$(echo "$SEALIGHTS_QUAY_URI" | $sed 's/quay\.io/registry.redhat.io/')
  echo "Found sealights URI $SEALIGHTS_QUAY_URI"
  echo " -> converting to $SEALIGHTS_URI"

  # replace the real URI with the sealights ones
  echo "Replacing all instances of $REAL_URI"
  echo " with $SEALIGHTS_URI"
  $sed -i "s|$REAL_URI|$SEALIGHTS_URI|g" bundle/manifests/rhods-operator.clusterserviceversion.yaml
done

echo "finished processing"
