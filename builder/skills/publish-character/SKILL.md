---
name: publish-character
description: Prepare and publish a standalone character using Mega Crit's official Workshop uploader.
---

Read [publishing](../../PUBLISHING.md). Run test, build and stage. Inspect the exact closed package and all evidence gaps; a staged prototype is not release-ready.
Author publishing.json with a declared preview PNG, reviewed description/credits and the verified BaseLib Workshop item ID. Use prepare-publish with a pinned official uploader archive, then check-publish; see the linked contract for commands and supported release. These commands prepare an offline private workspace and record ready evidence; they never upload or establish release readiness. Choose a new workspace name for changes; existing directories are preserved.
New items omit existing_item_id and mod_id.txt. Updates require the project's explicitly selected existing_item_id plus a matching --existing-item argument. Never reuse imported Spire Legacy configuration, publishing scripts or item markers. Recheck current payload/tool bytes and authenticate target ownership before an actual update. Other visibility choices require separate deliberate metadata review; the preparation adapter fixes visibility to private.
Use the verified official uploader for actual publication. Ask only for external publication authorization missing from the session; creative expedited mode alone is insufficient. Run the reported argument array from its reported working directory only when that authorization covers this project, item and visibility.
After upload, authenticate to verify item identity/visibility, download the content and run compare-delivery. Record exact package/DLL hashes and the Workshop URL. A successful process exit alone does not prove delivery.
Skip outcome: provide the staged private-test package and publishing instructions without uploading.
