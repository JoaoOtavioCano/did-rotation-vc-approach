# DID Rotation Verifiable Credential Approach

This project demonstrates a practical approach to DID (Decentralized Identifier) rotation using Verifiable Credentials (VCs). It implements the issuance and verification of VCs related to DID rotation, showcasing how to establish trust and manage changes in DIDs over time.  This approach allows for a smooth transition when rotating DIDs, ensuring that relying parties can still verify the validity of credentials issued by previous DIDs.

## Overview

The core concept is to issue a "DID Rotation Credential" that links a previous DID (the old DID) to a new DID. This credential acts as proof that the new DID is authorized to act on behalf of the old DID. When a holder needs to prove control over the old DID, they present both the original credential (issued by the old DID) and the DID Rotation Credential (issued by the new DID).  This allows verifiers to establish a chain of trust from the old DID to the new DID.

This project provides a command-line interface (CLI) for:

1.  Issuing DID Rotation Credentials.
3.  Creating Verifiable Presentations containing both DID Rotation Credentials.
4.  Verifying Verifiable Presentations.

## Project Structure
did-rotation-vc-approach/  
|─ main.py         # The main Python script containing the CLI logic.  
|─ Makefile        # Makefile for building and running the project in Docker.  
|─ Dockerfile      # Dockerfile for creating the project's containerized environment.  
|─ requirements.txt # List of Python dependencies.  
|─ README.md       # This file.  

## Getting Started

### Prerequisites

1.  **Docker:** This project uses Docker for containerization, ensuring a consistent environment. Install Docker Desktop (or Docker Engine for Linux) from [https://www.docker.com/](https://www.docker.com/).
2.  **Make:** Make is used for simplifying build and run commands. It's usually pre-installed on macOS and Linux. If you don't have it, install it using your system's package manager (e.g., `brew install make` on macOS).
3.  **JWK Files:** You'll need JWK (JSON Web Key) files for your old and new DIDs.  These files contain the private keys necessary for signing credentials and presentations.  **Do not share your private keys.** You can generate JWK files using tools like `didkit` or other key management libraries.

### Installation and Build

1.  **Clone the repository:**

```bash
git clone https://github.com/JoaoOtavioCano/did-rotation-vc-approach.git
```

2.  **Go to the directory:**

```bash
cd did-rotation-vc-approach/ 
```

3.  **Build the Docker image:**

```bash
make build
```

4.  **Add your JWK key files to the directory:**

5. **You can delete the docker image if needed:**

```bash
make docker-clean
```

### Usage

The project provides a CLI through the `main.py` script inside the Docker container.  Use the following `make` commands to interact with the CLI:

#### 1. Issue Verifiable Credentials:

```bash
make issue_vcs DID_01=did:example:1 KEY_FILE_01=key1.jwk DID_02=did:example:2 KEY_FILE_02=key2.jwk
```

* `DID_01:` The DID of the issuer (e.g., the old DID).
* `KEY_FILE_01:` The name of the issuer's JWK file.
* `DID_02:` The DID of the holder (e.g., the new DID).
* `KEY_FILE_02:` The name of the holder's JWK file.

This command will generate two signed credentials: signed_credential_01.jsonld (issued by DID_01 to DID_02) and signed_credential_02.jsonld (issued by DID_02 to DID_01).

#### 2. Issue Verifiable Presentation:

```bash
make issue_presentation HOLDER=did:example:1 KEY_FILE=key1.jwk SIGNED_CREDENTIAL1=signed_credential_01.jsonld SIGNED_CREDENTIAL2=signed_credential_02.jsonld
```

* `HOLDER:` The DID of the presentation holder.
* `KEY_FILE:` The name of the holder's JWK file.
* `SIGNED_CREDENTIAL1:`  The name of the first signed credential.
* `SIGNED_CREDENTIAL2:`  The name of the second signed credential.

This command will generate a presentation.jsonld file containing the verifiable presentation.

#### 3. Verify Presentation:

```bash
make verify_presentation PRESENTATION_FILE=presentation.jsonld
```

* `PRESENTATION_FILE:` The name of the presentation file.

This command will verify the presentation and print the result.

## Key Concepts
* `DID Rotation:` The process of changing a DID while maintaining trust in credentials issued by the previous DID.
* `Verifiable Credentials (VCs):` Digital credentials that are cryptographically signed and can be verified by relying parties.
* `Verifiable Presentations (VPs):` Collections of VCs presented together to prove certain claims.
* `JSON Web Key (JWK):` A JSON data structure that represents cryptographic keys.