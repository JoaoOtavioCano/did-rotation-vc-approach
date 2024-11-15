import argparse
import asyncio
import json
import didkit
import datetime


async def main():
    try:
        with open("key.jwk", "r") as f:
            key = f.read().strip()
        f.close()
    except FileNotFoundError:
        print("Error: add a key.jwk file with the key to the directory")
        return

    parser = argparse.ArgumentParser()
    parser.add_argument("old_did", help="DID of the old method")
    parser.add_argument("new_did", help="DID of the new method")
    args = parser.parse_args()

    issuance_date = datetime.datetime.utcnow().isoformat() + "Z"

    verification_method = await didkit.key_to_verification_method("key", key)

    credential = {
        "@context": "https://www.w3.org/2018/credentials/v1",
        "type": ["VerifiableCredential", "DIDRotationCredential"],
        "issuer": f"{args.old_did}",
        "issuanceDate": f"{issuance_date}",
        "credentialSubject": {
            "id": f"{args.new_did}",
            "sameControllerAs": f"{args.old_did}",
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
            key)
    except didkit.DIDKitException:
        print("Error: DID not found")
        return
    
    with open("signed_credential.json", "w") as f:
        f.write(signed_credential)



if __name__ == '__main__':
    asyncio.run(main())