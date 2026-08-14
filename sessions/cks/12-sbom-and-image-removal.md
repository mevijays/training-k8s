# Question 12: Identify an Image, Generate an SPDX SBOM, and Remove Its Container

## Objective

For Deployment `alpine` in namespace `alpine`:

1. determine which container image contains `libcrypto3` version `3.1.4-r5`;
2. generate `/home/candidate/alpine.spdx` for that image using `bom`;
3. remove only the container using that image from the supplied Deployment manifest.

## What this lab does and why

**What we are doing:** We are inspecting each image rather than trusting its tag, identifying the exact image that contains the specified package version, and documenting that image's contents in an SPDX Software Bill of Materials. We then remove only the container that uses the identified image.

**Why it matters:** Image tags do not reveal every installed package and can sometimes move to different image digests. Package-level inspection and an SBOM provide traceable software-supply-chain evidence, while removing the affected container prevents the known component from continuing to run.

**Objective summary:** Determine the vulnerable image from evidence, save its SPDX inventory at the required path, and update the Deployment without disturbing its unaffected containers.

## Concept and theory

- **Image vs. package identity:** A container image is a layered filesystem plus metadata. Its tag does not directly describe every installed operating-system package, so the package database inside each candidate image must be queried.
- **Tags and digests:** Tags are human-readable references and may be mutable. A digest identifies exact image content. Security investigations should record the digest when possible so later analysis refers to the same bytes.
- **SBOM purpose:** A Software Bill of Materials inventories components, versions, files, licenses, and relationships. It supports vulnerability and compliance analysis, but an SBOM by itself is not a vulnerability verdict.
- **SPDX:** SPDX is a standardized SBOM format. The document namespace uniquely identifies the generated document, while packages and relationships describe the analyzed artifact and its contents.
- **Pod template change:** A multi-container Pod shares scheduling and lifecycle but each container retains its own image. Removing one container from a Deployment's Pod template creates a new revision and replaces Pods with versions that no longer include that image.

## List container-to-image mappings

```bash
kubectl get deployment alpine -n alpine \
  -o jsonpath='{range .spec.template.spec.containers[*]}{.name}{"\t"}{.image}{"\n"}{end}'
```

Also inspect init containers in case the question's wording is imprecise:

```bash
kubectl get deployment alpine -n alpine \
  -o jsonpath='{range .spec.template.spec.initContainers[*]}init/{.name}{"\t"}{.image}{"\n"}{end}'
```

## Inspect `libcrypto3` in each image

If Docker is available:

```bash
for image in $(kubectl get deployment alpine -n alpine \
  -o jsonpath='{.spec.template.spec.containers[*].image}'); do
  echo "=== $image"
  docker run --rm --entrypoint /bin/sh "$image" \
    -c 'apk info -v libcrypto3 2>/dev/null || true'
done
```

An alternative query is:

```bash
docker run --rm --entrypoint /bin/sh <image> \
  -c "apk list --installed 2>/dev/null | grep '^libcrypto3-'"
```

Record both the offending image and its container name:

```bash
BAD_IMAGE=<image-containing-libcrypto3-3.1.4-r5>
BAD_CONTAINER=<container-using-that-image>
```

## Generate the SPDX document

Check the locally installed CLI because exam images may carry different releases:

```bash
bom version
bom generate --help
```

Generate the file:

```bash
bom generate \
  --name alpine-image \
  --namespace "https://cks.local/sbom/alpine" \
  --image "$BAD_IMAGE" \
  --output /home/candidate/alpine.spdx
```

Verify without dumping the whole document:

```bash
test -s /home/candidate/alpine.spdx
head -20 /home/candidate/alpine.spdx
grep -E 'SPDXVersion|DocumentName|PackageName' /home/candidate/alpine.spdx | head
```

## Remove the identified container

The pasted path likely means `~/alpine-deployment.yaml`:

```bash
ls -l ~/alpine-deployment.yaml /alpine-deployment.yaml 2>/dev/null
cp ~/alpine-deployment.yaml ~/alpine-deployment.yaml.backup
vi ~/alpine-deployment.yaml
```

Under `spec.template.spec.containers`, remove the complete list item whose `name` is `$BAD_CONTAINER`. Do not remove the entire `containers` field and do not merely change the vulnerable tag.

```bash
kubectl apply --dry-run=server -f ~/alpine-deployment.yaml
kubectl apply -f ~/alpine-deployment.yaml
kubectl rollout status deployment/alpine -n alpine
```

## Verify

```bash
kubectl get deployment alpine -n alpine \
  -o jsonpath='{range .spec.template.spec.containers[*]}{.name}{"\t"}{.image}{"\n"}{end}'

kubectl get pods -n alpine
test -s /home/candidate/alpine.spdx && echo 'SPDX file exists'
```

## Source

- [Kubernetes SIGs `bom` quick start](https://kubernetes-sigs.github.io/bom/quick-start/)
- [`bom generate` reference](https://kubernetes-sigs.github.io/bom/cli-reference/bom_generate/)

---

[← Previous: Question 11](11-worker-node-upgrade.md) · [Index](README.md) · [Next: Question 13 →](13-restricted-pod-security.md)
