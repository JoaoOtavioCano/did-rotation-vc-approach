# Variables (You'll need to set these appropriately)
IMAGE_NAME := didkit-cli


# Phony targets (Important!)
.PHONY: build run docker-clean issue_vcs issue_presentation verify_presentation

# Build Docker image
build:
	@docker build -t $(IMAGE_NAME) .

# Run command with arguments
run:
	@docker run --rm -it -v $(PWD):/app $(IMAGE_NAME) $(ARGS)

# Issue Verifiable Credentials
issue_vcs:
	@$(MAKE) run ARGS="issue_vcs $(DID_01) $(KEY_FILE_01) $(DID_02) $(KEY_FILE_02)"

# Issue Verifiable Presentation
issue_presentation:
	@$(MAKE) run ARGS="issue_presentation $(HOLDER) $(KEY_FILE) $(SIGNED_CREDENTIAL1) $(SIGNED_CREDENTIAL2)"

# Verify Presentation (using a specific filename)
verify_presentation:
	@$(MAKE) run ARGS="verify_presentation $(PRESENTATION_FILE)"


# Clean up Docker resources
docker-clean:
	@docker rmi $(IMAGE_NAME)

# Example usage:
# make verify_presentation PRESENTATION_FILE=presentation.jsonld
# make issue_vcs DID_01=did:example:1 KEY_FILE_01=key1.jwk DID_02=did:example:2 KEY_FILE_02=key2.jwk
# make issue_presentation HOLDER=did:example:1 KEY_FILE=key1.jwk SIGNED_CREDENTIAL1=signed_credential_01.jsonld SIGNED_CREDENTIAL2=signed_credential_02.jsonld