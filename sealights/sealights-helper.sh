function get_sealights_image {
  REAL_QUAY_URI=$1
  SEALIGHTS_BUILD_STEP=$2
  AUTH_JSON=
  if [ -e "$XDG_RUNTIME_DIR/containers/auth.json" ]; then
    AUTH_JSON="$XDG_RUNTIME_DIR/containers/auth.json"
  elif [ -e "$HOME/.docker/config.json" ]; then
    AUTH_JSON="$HOME/.docker/config.json"
  else
    echo "warning: cannot find registry authentication file." 1>&2
  fi
  declare -r AUTH_JSON ### get the correct credential
  # export AUTHFILE=/tekton/creds-secrets/rhoai-quay-secret
  # mkdir -p /tmp/auth
  # select-oci-auth "$REAL_QUAY_URI" > /tmp/auth/config.json

  ### Get the attestation info from the actual build URI
  DOCKER_CONFIG="$AUTH_JSON" cosign download attestation $REAL_QUAY_URI > attestation.json

  SEALIGHTS_BUILD_RESULTS=$(jq '.payload|@base64d|fromjson' attestation.json \
    | jq -r --arg N "$SEALIGHTS_BUILD_STEP" '.predicate.buildConfig.tasks[] | select(.name == $N)| .results')

  ### Find the sealights build URI from the attestation

  # this has the form 'sha256:<digest>'
  SEALIGHTS_IMAGE_DIGEST=$(echo $SEALIGHTS_BUILD_RESULTS | jq -r '.[] | select(.name == "IMAGE_DIGEST") | .value' | head -n 1)

  # using sed to remove the tag, leaving just the repo url
  SEALIGHTS_IMAGE_REPO=$(echo $SEALIGHTS_BUILD_RESULTS | jq -r '.[] | select(.name == "IMAGE_URL") | .value' | sed 's/:.*//' | head -n 1)

  echo "${SEALIGHTS_IMAGE_REPO}@${SEALIGHTS_IMAGE_DIGEST}"
  rm attestation.json
  rm /tmp/auth/config.json
}
