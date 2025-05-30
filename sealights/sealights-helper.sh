apk add cosign jq

function get_sealights_image {
  REAL_QUAY_URI=$1
  SEALIGHTS_BUILD_STEP=$2

  ### Get the attestation info from the actual build URI
  SEALIGHTS_BUILD_RESULTS=$(cosign download attestation $REAL_QUAY_URI \
    | jq '.payload|@base64d|fromjson' \
    | jq -r --arg N "$SEALIGHTS_BUILD_STEP" '.predicate.buildConfig.tasks[] | select(.name == $N)| .results')

  ### Find the sealights build URI from the attestation

  # this has the form 'sha256:<digest>'
  SEALIGHTS_IMAGE_DIGEST=$(echo $SEALIGHTS_BUILD_RESULTS | jq -r '.[] | select(.name == "IMAGE_DIGEST") | .value' | head -n 1)

  # using sed to remove the tag, leaving just the repo url
  SEALIGHTS_IMAGE_REPO=$(echo $SEALIGHTS_BUILD_RESULTS | jq -r '.[] | select(.name == "IMAGE_URL") | .value' | sed 's/:.*//' | head -n 1)

  echo "${SEALIGHTS_IMAGE_REPO}@${SEALIGHTS_IMAGE_DIGEST}"
}
