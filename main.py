import argparse
import asyncio
import json
import didkit
import datetime


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("old_did", help="DID of the old method")
    parser.add_argument("new_did", help="DID of the new method")
    args = parser.parse_args()
    print(f"old: {args.old_did}\nnew: {args.new_did}")

    issuance_date = datetime.datetime.utcnow().isoformat() + "Z"
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

    print(json.dumps(credential, indent=2))



if __name__ == '__main__':
    main()