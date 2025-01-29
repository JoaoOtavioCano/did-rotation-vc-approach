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
            old_key = f.readline()

    except FileNotFoundError:
        print("Error: add a .jwk file with the old DID method key to the directory")
        exit()
    
    try:
        with open(args.new_did_key_file, "r") as f:
            new_key = f.readline()

    except FileNotFoundError:
        print("Error: add a .jwk file with the new DID method key to the directory")
        exit()
    
    await issue_vc(args.new_did, new_key, args.old_did, "old_did_signed_credential.jsonld")
    await issue_vc(args.old_did, old_key, args.new_did, "new_did_signed_credential.jsonld")


async def issue_vc(issuer_did, issuer_key, holder_did, output):
    issuance_date = datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


    credential = {
        "@context": [
            "https://www.w3.org/2018/credentials/v1",
            {
                "sameControllerAs": "ex:did"
            }
        ],
        "type": ["VerifiableCredential", "DIDRotationCredential"],
        "issuer": issuer_did,
        "issuanceDate": issuance_date,
        "credentialSubject": {
            "id": holder_did,
            "sameControllerAs": issuer_did
        }
    }


    signed_credential = await didkit.issue_credential(
        json.dumps(credential),
        json.dumps({}),
        issuer_key)

    
    with open(output, "w") as f:
        f.write(signed_credential)


async def issue_presentation(holder, key_path, signed_credential01_path, signed_credential02_path):

    try:
        with open(key_path, "r") as f:
            key = f.read()
    except FileNotFoundError:
        print("Error: key not found")
        exit()
    
    try:
        with open(signed_credential01_path, "r") as f:
            signed_credential01 = json.loads(f.read())
    except FileNotFoundError:
        print("Error: signed credential not found")
        exit()
    
    try:
        with open(signed_credential02_path, "r") as f:
            signed_credential02 = json.loads(f.read())
    except FileNotFoundError:
        print("Error: signed credential not found")
        exit()

    presentation = {
        "@context": ["https://www.w3.org/2018/credentials/v1"],
        "type": ["VerifiablePresentation"],
        "holder": holder,
        "verifiableCredential": [signed_credential01, signed_credential02]
    }

    try:    
        signed_presentation = await didkit.issue_presentation(
            json.dumps(presentation),
            json.dumps({}),
            key
        )
    except:
        print("Error: something went wrong")
        exit()

    with open("presentation.jsonld", "w") as f:
        f.write(signed_presentation)

async def verify_presentation(presentation_path):
    try:
        with open(presentation_path, "r") as f:
            signed_presentation = json.loads(f.read())
    except FileNotFoundError:
        print("Error: presentation not found")
        exit()

    holder = signed_presentation["holder"]
    if len(signed_presentation["verifiableCredential"]) < 2:
        print("Presentation invalid because does not contain all the credentials")
        return
    credential01 = signed_presentation["verifiableCredential"][0]
    credential02 = signed_presentation["verifiableCredential"][1]

    try:
        verification_result = await didkit.verify_credential(
            json.dumps(credential01),
            json.dumps({"proofPurpose":"assertionMethod"})
        )
    except:
        print("Error: something went wrong")
        exit()
    verification_result = json.loads(verification_result)
    if verification_result["errors"] != [] or verification_result["warnings"] != []:
        print("Presentation invalid because one of the credentials is invalid")
        print("Errors:" + verification_result["errors"])
        print("Warnings:" + verification_result["warnings"])
        return
    
    try:
        verification_result = await didkit.verify_credential(
            json.dumps(credential02),
            json.dumps({"proofPurpose":"assertionMethod"})
        )
    except:
        print("Error: something went wrong")
        exit()
    verification_result = json.loads(verification_result)
    if verification_result["errors"] != [] or verification_result["warnings"] != []:
        print("Presentation invalid because one of the credentials is invalid")
        print("Errors:" + verification_result["errors"])
        print("Warnings:" + verification_result["warnings"])
        return


    
    try:
        verification_result = await didkit.verify_presentation(
            json.dumps(signed_presentation),
            json.dumps({"proofPurpose":"authentication"})
        )
    except:
        print("Error: something went wrong")
        exit()

    verification_result = json.loads(verification_result)
    if verification_result["errors"] != [] or verification_result["warnings"] != []:
        print("Errors:" + verification_result["errors"])
        print("Warnings:" + verification_result["warnings"])
        return

    print("Presentation verified successfuly")


if __name__ == '__main__':
    asyncio.run(main())