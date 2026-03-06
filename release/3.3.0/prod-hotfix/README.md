# 3.3.0 Prod Hotfix

This hotfix addresses an issue where the recent 2.25.3 release unpublished the 3.3.0 bundle from OCP v4.19 and v4.20.

For more context, see the [Slack thread](https://redhat-internal.slack.com/archives/C0A6R461R46/p1772722438237279?thread_ts=1772718400.742349&cid=C0A6R461R46).

## Steps to Apply

Ensure you are logged into the `rhoai-tenant` namespace before proceeding.

### 1. Apply Snapshots

```bash
oc apply -f snapshot-fbc/
```

### 2. Apply Release FBCs

Once the snapshots are created, apply the release FBC resources:

```bash
oc apply -f release-fbc/
```
