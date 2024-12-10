import argparse
import asyncio
import json
import didkit
import datetime


async def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("old_did", help="DID of the old method")
    parser.add_argument("old_did_key_file", help="jwk file with keys of the old method")
    parser.add_argument("new_did", help="DID of the new method")
    parser.add_argument("new_did_key_file", help="jwk file with keys of the new method")
    args = parser.parse_args()

    try:
        with open(args.old_did_key_file, "r") as f:
            old_key = f.read().strip()
        f.close()
    except FileNotFoundError:
        print("Error: add a .jwk file with the old DID method key to the directory")
        return
    
    try:
        with open(args.new_did_key_file, "r") as f:
            new_key = f.read().strip()
        f.close()
    except FileNotFoundError:
        print("Error: add a .jwk file with the new DID method key to the directory")
        return
    
    await issue_vc(args.new_did, new_key, args.old_did, "old_did_signed_credential.json")
    await issue_vc(args.old_did, old_key, args.new_did, "new_did_signed_credential.json")


async def issue_vc(issuer_did, issuer_key, holder_did, output):
    issuance_date = datetime.datetime.utcnow().isoformat() + "Z"

    did_method = str(issuer_did).split(":")[1]

    verification_method = await didkit.key_to_verification_method(did_method, issuer_key)

    credential = {
        "@context": "https://www.w3.org/2018/credentials/v1",
        "type": ["VerifiableCredential", "DIDRotationCredential"],
        "issuer": f"{issuer_did}",
        "issuanceDate": f"{issuance_date}",
        "credentialSubject": {
            "id": f"{holder_did}",
            "sameControllerAs": f"{holder_did}",
        },
    }

    didkit_options = {
        "proofPurpose": "assertionMethod",
        "verificationMethod": verification_method,
        "proofFormat": "jwt"
    }

    try: 
        signed_credential = await didkit.issue_credential(
            json.dumps(credential),
            json.dumps(didkit_options),
            issuer_key)
    except didkit.DIDKitException:
        print("Error: DID not found")
        return
    
    with open(output, "w") as f:
        f.write(signed_credential)

if __name__ == '__main__':
    asyncio.run(main())