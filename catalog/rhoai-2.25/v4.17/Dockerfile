# The base image is expected to contain
# /bin/opm (with a serve subcommand) and /bin/grpc_health_probe
FROM registry.redhat.io/openshift4/ose-operator-registry-rhel9:v4.17

ARG RBC_RELEASE_BRANCH_COMMIT=
ARG ODH_RHEL8_OPERATOR_GIT_URL=
ARG ODH_RHEL8_OPERATOR_GIT_COMMIT=
ARG ODH_KF_NOTEBOOK_CONTROLLER_GIT_URL=
ARG ODH_KF_NOTEBOOK_CONTROLLER_GIT_COMMIT=
ARG ODH_NOTEBOOK_CONTROLLER_GIT_URL=
ARG ODH_NOTEBOOK_CONTROLLER_GIT_COMMIT=
ARG ODH_DATA_SCIENCE_PIPELINES_OPERATOR_CONTROLLER_GIT_URL=
ARG ODH_DATA_SCIENCE_PIPELINES_OPERATOR_CONTROLLER_GIT_COMMIT=
ARG ODH_CODEFLARE_OPERATOR_GIT_URL=
ARG ODH_CODEFLARE_OPERATOR_GIT_COMMIT=
ARG ODH_KUBERAY_OPERATOR_CONTROLLER_GIT_URL=
ARG ODH_KUBERAY_OPERATOR_CONTROLLER_GIT_COMMIT=
ARG ODH_KUEUE_CONTROLLER_GIT_URL=
ARG ODH_KUEUE_CONTROLLER_GIT_COMMIT=
ARG ODH_TRUSTYAI_SERVICE_OPERATOR_GIT_URL=
ARG ODH_TRUSTYAI_SERVICE_OPERATOR_GIT_COMMIT=
ARG ODH_MODEL_CONTROLLER_GIT_URL=
ARG ODH_MODEL_CONTROLLER_GIT_COMMIT=
ARG ODH_MODELMESH_GIT_URL=
ARG ODH_MODELMESH_GIT_COMMIT=
ARG ODH_DASHBOARD_GIT_URL=
ARG ODH_DASHBOARD_GIT_COMMIT=
ARG ODH_TRAINING_OPERATOR_GIT_URL=
ARG ODH_TRAINING_OPERATOR_GIT_COMMIT=
ARG ODH_MODELMESH_SERVING_CONTROLLER_GIT_URL=
ARG ODH_MODELMESH_SERVING_CONTROLLER_GIT_COMMIT=
ARG ODH_MM_REST_PROXY_GIT_URL=
ARG ODH_MM_REST_PROXY_GIT_COMMIT=
ARG ODH_MODELMESH_RUNTIME_ADAPTER_GIT_URL=
ARG ODH_MODELMESH_RUNTIME_ADAPTER_GIT_COMMIT=
ARG ODH_TRUSTYAI_SERVICE_GIT_URL=
ARG ODH_TRUSTYAI_SERVICE_GIT_COMMIT=
ARG ODH_MLMD_GRPC_SERVER_GIT_URL=
ARG ODH_MLMD_GRPC_SERVER_GIT_COMMIT=
ARG ODH_ML_PIPELINES_API_SERVER_V2_GIT_URL=
ARG ODH_ML_PIPELINES_API_SERVER_V2_GIT_COMMIT=
ARG ODH_ML_PIPELINES_PERSISTENCEAGENT_V2_GIT_URL=
ARG ODH_ML_PIPELINES_PERSISTENCEAGENT_V2_GIT_COMMIT=
ARG ODH_ML_PIPELINES_SCHEDULEDWORKFLOW_V2_GIT_URL=
ARG ODH_ML_PIPELINES_SCHEDULEDWORKFLOW_V2_GIT_COMMIT=
ARG ODH_ML_PIPELINES_DRIVER_GIT_URL=
ARG ODH_ML_PIPELINES_DRIVER_GIT_COMMIT=
ARG ODH_ML_PIPELINES_LAUNCHER_GIT_URL=
ARG ODH_ML_PIPELINES_LAUNCHER_GIT_COMMIT=
ARG ODH_DATA_SCIENCE_PIPELINES_ARGO_ARGOEXEC_GIT_URL=
ARG ODH_DATA_SCIENCE_PIPELINES_ARGO_ARGOEXEC_GIT_COMMIT=
ARG ODH_DATA_SCIENCE_PIPELINES_ARGO_WORKFLOWCONTROLLER_GIT_URL=
ARG ODH_DATA_SCIENCE_PIPELINES_ARGO_WORKFLOWCONTROLLER_GIT_COMMIT=
ARG ODH_MODEL_REGISTRY_GIT_URL=
ARG ODH_MODEL_REGISTRY_GIT_COMMIT=
ARG ODH_MODEL_REGISTRY_OPERATOR_GIT_URL=
ARG ODH_MODEL_REGISTRY_OPERATOR_GIT_COMMIT=
ARG ODH_OPERATOR_BUNDLE_GIT_COMMIT
ARG ODH_OPERATOR_BUNDLE_GIT_URL


# Configure the entrypoint and command
ENTRYPOINT ["/bin/opm"]
CMD ["serve", "/configs", "--cache-dir=/tmp/cache"]
# Copy declarative config root into image at /configs and pre-populate serve cache
ADD rhods-operator /configs/rhods-operator
RUN ["/bin/opm", "serve", "/configs", "--cache-dir=/tmp/cache", "--cache-only"]

# Set DC-specific label for the location of the DC root directory
# in the image
LABEL operators.operatorframework.io.index.configs.v1=/configs

LABEL \
      odh-rhel8-operator.git.url="${ODH_RHEL8_OPERATOR_GIT_URL}" \
      odh-rhel8-operator.git.commit="${ODH_RHEL8_OPERATOR_GIT_COMMIT}" \
      odh-kf-notebook-controller.git.url="${ODH_KF_NOTEBOOK_CONTROLLER_GIT_URL}" \
      odh-kf-notebook-controller.git.commit="${ODH_KF_NOTEBOOK_CONTROLLER_GIT_COMMIT}" \
      odh-notebook-controller.git.url="${ODH_NOTEBOOK_CONTROLLER_GIT_URL}" \
      odh-notebook-controller.git.commit="${ODH_NOTEBOOK_CONTROLLER_GIT_COMMIT}" \
      odh-data-science-pipelines-operator-controller.git.url="${ODH_DATA_SCIENCE_PIPELINES_OPERATOR_CONTROLLER_GIT_URL}" \
      odh-data-science-pipelines-operator-controller.git.commit="${ODH_DATA_SCIENCE_PIPELINES_OPERATOR_CONTROLLER_GIT_COMMIT}" \
      odh-codeflare-operator.git.url="${ODH_CODEFLARE_OPERATOR_GIT_URL}" \
      odh-codeflare-operator.git.commit="${ODH_CODEFLARE_OPERATOR_GIT_COMMIT}" \
      odh-kuberay-operator-controller.git.url="${ODH_KUBERAY_OPERATOR_CONTROLLER_GIT_URL}" \
      odh-kuberay-operator-controller.git.commit="${ODH_KUBERAY_OPERATOR_CONTROLLER_GIT_COMMIT}" \
      odh-kueue-controller.git.url="${ODH_KUEUE_CONTROLLER_GIT_URL}" \
      odh-kueue-controller.git.commit="${ODH_KUEUE_CONTROLLER_GIT_COMMIT}" \
      odh-trustyai-service-operator.git.url="${ODH_TRUSTYAI_SERVICE_OPERATOR_GIT_URL}" \
      odh-trustyai-service-operator.git.commit="${ODH_TRUSTYAI_SERVICE_OPERATOR_GIT_COMMIT}" \
      odh-model-controller.git.url="${ODH_MODEL_CONTROLLER_GIT_URL}" \
      odh-model-controller.git.commit="${ODH_MODEL_CONTROLLER_GIT_COMMIT}" \
      odh-modelmesh.git.url="${ODH_MODELMESH_GIT_URL}" \
      odh-modelmesh.git.commit="${ODH_MODELMESH_GIT_COMMIT}" \
      odh-dashboard.git.url="${ODH_DASHBOARD_GIT_URL}" \
      odh-dashboard.git.commit="${ODH_DASHBOARD_GIT_COMMIT}" \
      odh-training-operator.git.url="${ODH_TRAINING_OPERATOR_GIT_URL}" \
      odh-training-operator.git.commit="${ODH_TRAINING_OPERATOR_GIT_COMMIT}" \
      odh-modelmesh-serving-controller.git.url="${ODH_MODELMESH_SERVING_CONTROLLER_GIT_URL}" \
      odh-modelmesh-serving-controller.git.commit="${ODH_MODELMESH_SERVING_CONTROLLER_GIT_COMMIT}" \
      odh-mm-rest-proxy.git.url="${ODH_MM_REST_PROXY_GIT_URL}" \
      odh-mm-rest-proxy.git.commit="${ODH_MM_REST_PROXY_GIT_COMMIT}" \
      odh-modelmesh-runtime-adapter.git.url="${ODH_MODELMESH_RUNTIME_ADAPTER_GIT_URL}" \
      odh-modelmesh-runtime-adapter.git.commit="${ODH_MODELMESH_RUNTIME_ADAPTER_GIT_COMMIT}" \
      odh-trustyai-service.git.url="${ODH_TRUSTYAI_SERVICE_GIT_URL}" \
      odh-trustyai-service.git.commit="${ODH_TRUSTYAI_SERVICE_GIT_COMMIT}" \
      odh-mlmd-grpc-server.git.url="${ODH_MLMD_GRPC_SERVER_GIT_URL}" \
      odh-mlmd-grpc-server.git.commit="${ODH_MLMD_GRPC_SERVER_GIT_COMMIT}" \
      odh-ml-pipelines-api-server-v2.git.url="${ODH_ML_PIPELINES_API_SERVER_V2_GIT_URL}" \
      odh-ml-pipelines-api-server-v2.git.commit="${ODH_ML_PIPELINES_API_SERVER_V2_GIT_COMMIT}" \
      odh-ml-pipelines-persistenceagent-v2.git.url="${ODH_ML_PIPELINES_PERSISTENCEAGENT_V2_GIT_URL}" \
      odh-ml-pipelines-persistenceagent-v2.git.commit="${ODH_ML_PIPELINES_PERSISTENCEAGENT_V2_GIT_COMMIT}" \
      odh-ml-pipelines-scheduledworkflow-v2.git.url="${ODH_ML_PIPELINES_SCHEDULEDWORKFLOW_V2_GIT_URL}" \
      odh-ml-pipelines-scheduledworkflow-v2.git.commit="${ODH_ML_PIPELINES_SCHEDULEDWORKFLOW_V2_GIT_COMMIT}" \
      odh-ml-pipelines-driver.git.url="${ODH_ML_PIPELINES_DRIVER_GIT_URL}" \
      odh-ml-pipelines-driver.git.commit="${ODH_ML_PIPELINES_DRIVER_GIT_COMMIT}" \
      odh-ml-pipelines-launcher.git.url="${ODH_ML_PIPELINES_LAUNCHER_GIT_URL}" \
      odh-ml-pipelines-launcher.git.commit="${ODH_ML_PIPELINES_LAUNCHER_GIT_COMMIT}" \
      odh-data-science-pipelines-argo-argoexec.git.url="${ODH_DATA_SCIENCE_PIPELINES_ARGO_ARGOEXEC_GIT_URL}" \
      odh-data-science-pipelines-argo-argoexec.git.commit="${ODH_DATA_SCIENCE_PIPELINES_ARGO_ARGOEXEC_GIT_COMMIT}" \
      odh-data-science-pipelines-argo-workflowcontroller.git.url="${ODH_DATA_SCIENCE_PIPELINES_ARGO_WORKFLOWCONTROLLER_GIT_URL}" \
      odh-data-science-pipelines-argo-workflowcontroller.git.commit="${ODH_DATA_SCIENCE_PIPELINES_ARGO_WORKFLOWCONTROLLER_GIT_COMMIT}" \
      odh-model-registry.git.url="${ODH_MODEL_REGISTRY_GIT_URL}" \
      odh-model-registry.git.commit="${ODH_MODEL_REGISTRY_GIT_COMMIT}" \
      odh-model-registry-operator.git.url="${ODH_MODEL_REGISTRY_OPERATOR_GIT_URL}" \
      odh-model-registry-operator.git.commit="${ODH_MODEL_REGISTRY_OPERATOR_GIT_COMMIT}" \
      odh-operator-bundle.git.url="${ODH_OPERATOR_BUNDLE_GIT_URL}" \
      odh-operator-bundle.git.commit="${ODH_OPERATOR_BUNDLE_GIT_COMMIT}" \
      rbc-release-branch.commit="${RBC_RELEASE_BRANCH_COMMIT}"

LABEL com.redhat.component="rhoai-fbc-fragment" \
      description="rhoai-fbc-fragment" \
      distribution-scope="public" \
      name="managed-open-data-hub/rhoai-fbc-fragment" \
      vendor="Red Hat, Inc." \
      summary="rhoai-fbc-fragment" \
      maintainer="['managed-open-data-hub@redhat.com']" \
      io.k8s.display-name="rhoai-fbc-fragment" \
      io.k8s.description="rhoai-fbc-fragment" \
      com.redhat.delivery.operator.bundle="true" \
      com.redhat.license_terms="https://www.redhat.com/licenses/Red_Hat_Standard_EULA_20191108.pdf"