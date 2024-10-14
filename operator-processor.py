import sys
from datetime import datetime
from pathlib import Path
from ruamel.yaml.comments import CommentedMap
from jsonupdate_ng import jsonupdate_ng
import requests
import argparse
import yaml
import ruamel.yaml as ruyaml
import os
from ruamel.yaml.scalarstring import DoubleQuotedScalarString

import json
class operator_processor:
    PRODUCTION_REGISTRY = 'registry.redhat.io'
    OPERATOR_NAME = 'rhods-operator'
    GIT_URL_LABEL_KEY = 'git.url'
    GIT_COMMIT_LABEL_KEY = 'git.commit'

    def __init__(self, patch_yaml_path:str, rhoai_version:str, operands_map_path:str, nudging_yaml_path:str, manifest_config_path:str):
        self.patch_yaml_path = patch_yaml_path
        self.operands_map_path = operands_map_path
        self.nudging_yaml_path = nudging_yaml_path
        self.manifest_config_path = manifest_config_path
        self.rhoai_version = rhoai_version

        self.patch_dict = self.parse_patch_yaml()

        #uncomment this if we face id001 problem in the operands map yaml
        #ruyaml.representer.RoundTripRepresenter.ignore_aliases = lambda x, y: True

        self.operands_map_dict = ruyaml.load(open(self.operands_map_path), Loader=ruyaml.RoundTripLoader, preserve_quotes=True)
        self.nudging_yaml_dict = ruyaml.load(open(self.nudging_yaml_path), Loader=ruyaml.RoundTripLoader, preserve_quotes=True)
        self.manifest_config_dict = ruyaml.load(open(self.manifest_config_path), Loader=ruyaml.RoundTripLoader,
                                             preserve_quotes=True)

    def parse_patch_yaml(self):
        return yaml.safe_load(open(self.patch_yaml_path))
    def generate_latest_operands_map(self):
        self.sync_yamls_from_bundle_patch()

        self.latest_images, self.git_labels_meta = [], {}
        self.latest_images, self.git_labels_meta = self.get_all_latest_images_using_operands_map()

        if self.latest_images:
            self.update_operands_map()
        if self.git_labels_meta:
            self.update_manifest_config()

        self.write_output_files()



    def write_output_files(self):
        ruyaml.dump(self.nudging_yaml_dict, open(self.nudging_yaml_path, 'w'), Dumper=ruyaml.RoundTripDumper, default_flow_style=False)
        ruyaml.dump(self.operands_map_dict, open(self.operands_map_path, 'w'), Dumper=ruyaml.RoundTripDumper,
                    default_flow_style=False)
        ruyaml.dump(self.manifest_config_dict, open(self.manifest_config_path, 'w'), Dumper=ruyaml.RoundTripDumper,
                    default_flow_style=False)

        # ruyaml.dump(self.nudging_yaml_dict, open('nudging_output.yaml', 'w'), Dumper=ruyaml.RoundTripDumper, default_flow_style=False)
        # ruyaml.dump(self.operands_map_dict, open('operands_map_output.yaml', 'w'), Dumper=ruyaml.RoundTripDumper,
        #             default_flow_style=False)
        # ruyaml.dump(self.manifest_config_dict, open('manifests_config_output.yaml', 'w'), Dumper=ruyaml.RoundTripDumper,
        #             default_flow_style=False)

    def update_operands_map(self):
        self.operands_map_dict = jsonupdate_ng.updateJson(self.operands_map_dict, {'relatedImages': self.latest_images }, meta={'listPatchScheme': {'$.relatedImages': {'key': 'name'}}} )

    def update_manifest_config(self):
        missing_git_labels = []
        for component, manifest_config in self.manifest_config_dict['map'].items():
            if 'ref_type' not in manifest_config or ('ref_type' in manifest_config and manifest_config['ref_type'] != 'branch'):
                git_url = self.git_labels_meta['map'][component][self.GIT_URL_LABEL_KEY]
                git_commit = self.git_labels_meta['map'][component][self.GIT_COMMIT_LABEL_KEY]
                if git_url and git_commit:
                    manifest_config[self.GIT_URL_LABEL_KEY] = git_url
                    manifest_config[self.GIT_COMMIT_LABEL_KEY] = git_commit
                else:
                    missing_git_labels.append(component)
        if missing_git_labels:
            print('git.url and git.commit labels missing/empty for : ', missing_git_labels)
            sys.exit(1)
    def sync_yamls_from_bundle_patch(self):
        # operands map sync
        existing_components = [component['name'] for component in self.operands_map_dict['relatedImages']]
        new_components = [component for component in self.patch_dict['patch']['relatedImages'] if component['name'] not in existing_components]
        new_components = [CommentedMap(component) for component in new_components]
        self.operands_map_dict['relatedImages'] += new_components

        #nudging yaml sync
        existing_components = [component['name'] for component in self.nudging_yaml_dict['relatedImages']]
        new_components = [component for component in self.patch_dict['patch']['relatedImages'] if component['name'] not in existing_components]
        new_components = [CommentedMap(component) for component in new_components]
        self.nudging_yaml_dict['relatedImages'] += new_components

    def patch_related_images(self):
        SCHEMA = 'relatedImages'
        PATCH_SCHEMA = 'olm.channels'
        env_list = self.csv_dict['spec']['install']['spec']['deployments'][0]['spec']['template']['spec']['containers'][0][
                'env']
        env_list = [dict(item) for item in env_list]
        env_object = jsonupdate_ng.updateJson({'env': env_list}, {'env': self.latest_images}, meta={'listPatchScheme': {'$.env': {'key': 'name', 'keyType': 'partial', 'keySeparator': '@'}}})
        self.csv_dict['spec']['install']['spec']['deployments'][0]['spec']['template']['spec']['containers'][0][
            'env'] = env_object['env']
        relatedImages = []
        for name, value in self.csv_dict['metadata']['annotations'].items():
            if value.startswith(self.PRODUCTION_REGISTRY) and '@sha256:' in value:
                relatedImages.append({'name': f'{value.split("/")[-1].replace("@sha256:", "-")}-annotation', 'image': value})
        relatedImages += [{'name': image['name'].replace('RELATED_IMAGE_', '').lower(), 'image': image['value']} for image in self.latest_images]
        self.csv_dict['spec']['relatedImages'] = relatedImages


    def get_all_latest_images_using_operands_map(self):
        latest_images = []
        git_labels_meta = {'map': {}}
        missing_images = []
        for image_entry in [image for image in self.operands_map_dict['relatedImages']  if 'FBC' not in image['name'] and 'BUNDLE' not in image['name'] and 'ODH_OPERATOR' not in image['name'] ]:
            parts = image_entry['value'].split('@')[0].split('/')
            registry = parts[0]
            org = parts[1]
            qc = quay_controller(org)
            repo = '/'.join(parts[2:])
            tags = qc.get_all_tags(repo, self.rhoai_version)
            component_name = repo.replace('-rhel8', '') if repo.endswith('-rhel8') else repo

            if not tags:
                print(f'no tags found for {repo}')
                missing_images.append(repo)
            for tag in tags:
                sig_tag = f'{tag["manifest_digest"].replace(":", "-")}.sig'
                signature = qc.get_tag_details(repo, sig_tag)
                if signature:
                    value = f'{registry}/{org}/{repo}@{tag["manifest_digest"]}'
                    # if image_entry['value'] != value:
                    image_entry['value'] = DoubleQuotedScalarString(value)
                    latest_images.append(image_entry)

                    labels = qc.get_git_labels(repo, tag["manifest_digest"])
                    labels = {label['key']:label['value'] for label in labels if label['value']}
                    git_url = labels[self.GIT_URL_LABEL_KEY] if self.GIT_URL_LABEL_KEY in labels else ''
                    git_commit = labels[self.GIT_COMMIT_LABEL_KEY] if self.GIT_COMMIT_LABEL_KEY in labels else ''
                    git_labels_meta['map'][component_name] = {}
                    git_labels_meta['map'][component_name][self.GIT_URL_LABEL_KEY] = git_url
                    git_labels_meta['map'][component_name][self.GIT_COMMIT_LABEL_KEY] = git_commit

                    break
        if missing_images:
            print('Images missing for following components : ', missing_images)
            sys.exit(1)
        print('latest_images', json.dumps(latest_images, indent=4))
        return latest_images, git_labels_meta



def str_presenter(dumper, data):
    if data.count('\n') > 0:
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    # if '"' in data:
    #     return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='"')

    return dumper.represent_scalar('tag:yaml.org,2002:str', data)


BASE_URL = 'https://quay.io/api/v1'
class quay_controller:
    def __init__(self, org:str):
        self.org = org
    def get_tag_details(self, repo, tag):
        result_tag = {}
        url = f'{BASE_URL}/repository/{self.org}/{repo}/tag/?specificTag={tag}&onlyActiveTags=true'
        headers = {'Authorization': f'Bearer {os.environ[self.org.upper() + "_QUAY_API_TOKEN"]}',
                   'Accept': 'application/json'}
        response = requests.get(url, headers=headers)
        tags = response.json()['tags']
        if tags:
            result_tag = tags[0]
        return result_tag
    def get_all_tags(self, repo, tag):
        url = f'{BASE_URL}/repository/{self.org}/{repo}/tag/?specificTag={tag}&onlyActiveTags=false'
        headers = {'Authorization': f'Bearer {os.environ[self.org.upper() + "_QUAY_API_TOKEN"]}',
                   'Accept': 'application/json'}
        response = requests.get(url, headers=headers)
        if 'tags' in response.json():
            tag = response.json()['tags']
            return tag
        else:
            print(response.json())
            sys.exit(1)

    def get_git_labels(self, repo, tag):
        url = f'{BASE_URL}/repository/{self.org}/{repo}/manifest/{tag}/labels?filter=git'
        headers = {'Authorization': f'Bearer {os.environ[self.org.upper() + "_QUAY_API_TOKEN"]}',
                   'Accept': 'application/json'}
        response = requests.get(url, headers=headers)
        if 'labels' in response.json():
            labels = response.json()['labels']
            return labels
        else:
            print(response.json())
            sys.exit(1)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-op', '--operation', required=False,
                        help='Operation code, supported values are "process-operator-yamls"', dest='operation')
    parser.add_argument('-p', '--patch-yaml-path', required=False,
                        help='Path of the bundle-patch.yaml from the release branch.', dest='patch_yaml_path')
    parser.add_argument('-o', '--operands-map-path', required=False,
                        help='Path of the operands map yaml', dest='operands_map_path')
    parser.add_argument('-n', '--nudging-yaml-path', required=False,
                        help='Path of the nudging yaml', dest='nudging_yaml_path')
    parser.add_argument('-m', '--manifest-config-path', required=False,
                        help='Path of the manifest config yaml', dest='manifest_config_path')
    parser.add_argument('-v', '--rhoai-version', required=False,
                        help='The version of Openshift-AI being processed', dest='rhoai_version')
    args = parser.parse_args()

    if args.operation.lower() == 'process-operator-yamls':
        processor = operator_processor(patch_yaml_path=args.patch_yaml_path, rhoai_version=args.rhoai_version, operands_map_path=args.operands_map_path, nudging_yaml_path=args.nudging_yaml_path, manifest_config_path=args.manifest_config_path)
        processor.generate_latest_operands_map()

    # patch_yaml_path = '/home/dchouras/RHODS/DevOps/RHOAI-Build-Config/bundle/bundle-patch.yaml'
    # operands_map_path = '/home/dchouras/RHODS/DevOps/rhods-operator/build/operands-map.yaml'
    # nudging_yaml_path = '/home/dchouras/RHODS/DevOps/rhods-operator/build/operator-nudging.yaml'
    # manifest_config_path = '/home/dchouras/RHODS/DevOps/rhods-operator/build/manifests-config.yaml'
    # rhoai_version = 'rhoai-2.13'
    #
    #
    # processor = operator_processor(patch_yaml_path=patch_yaml_path, rhoai_version=rhoai_version,
    #                                operands_map_path=operands_map_path, nudging_yaml_path=nudging_yaml_path,
    #                                manifest_config_path=manifest_config_path)
    # processor.generate_latest_operands_map()


