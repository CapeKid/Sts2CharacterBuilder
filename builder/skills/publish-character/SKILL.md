---
name: publish-character
description: Prepare and publish a standalone character using Mega Crit's official Workshop uploader.
---

Read [publishing](../../PUBLISHING.md). Run test, build and stage. Inspect the exact closed package and all evidence gaps; a staged prototype is not release-ready.
Use a new project-owned Workshop workspace and explicit target identity/visibility. Never reuse the imported Spire Legacy workshop.json, publishing scripts or mod_id.txt. New projects start private. Preserve a project's own existing item marker for updates.
Use Mega Crit's official uploader and the workspace schema supplied with its pinned release. Prepare content, image, description, dependencies, credits and licenses. Ask only for external publication authorization missing from the session; creative expedited mode alone is insufficient.
After upload, authenticate to verify item identity/visibility, download the content and run compare-delivery. Record exact package/DLL hashes and the Workshop URL. A successful process exit alone does not prove delivery.
Skip outcome: provide the staged private-test package and publishing instructions without uploading.
