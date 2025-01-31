import argparse
import asyncio
import json
import didkit
import datetime


async def main():
    args = parse_args()
    if args.command == "issue_vcs":
        await issue_vc(args.did_01, args.key_file_01, args.did_02, "./signed_credential_01.jsonld")
        await issue_vc(args.did_02, args.key_file_02, args.did_01, "./signed_credential_02.jsonld")
    elif args.command == "issue_presentation":
        await issue_presentation(args.holder, args.key_file, args.signed_credential1, args.signed_credential2)
    elif args.command == "verify_presentation":
        await verify_presentation(args.presentation_file)

async def issue_vc(issuer_did, issuer_key_file, holder_did, output):
    try:
        with open(issuer_key_file, "r") as f:
            issuer_key = f.readline()

    except FileNotFoundError:
        print("Error: " + issuer_key_file + " not found")
        exit()

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

    with open("./presentation.jsonld", "w") as f:
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
        print("Errors:" + str(verification_result["errors"]))
        print("Warnings:" + str(verification_result["warnings"]))
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
        print("Errors:" + str(verification_result["errors"]))
        print("Warnings:" + str(verification_result["warnings"]))
        return
    
    if "DIDRotationCredential" not in credential01["type"]:
        print("Presentation invalid because one of the credentials is invalid")
        return
    credential01_issuer = credential01["issuer"]
    credential01_subject_id = credential01["credentialSubject"]["id"]
    credential01_subject_sameControllerAs = credential01["credentialSubject"]["sameControllerAs"]
    if credential01_issuer != credential01_subject_sameControllerAs:
        print("Presentation invalid because one of the credentials is invalid")
        return
    if credential01_issuer != holder and credential01_subject_id != holder:
        print("Presentation invalid")
        return
    
    if "DIDRotationCredential" not in credential02["type"]:
        print("Presentation invalid because one of the credentials is invalid")
        return
    credential02_issuer = credential02["issuer"]
    credential02_subject_id = credential02["credentialSubject"]["id"]
    credential02_subject_sameControllerAs = credential02["credentialSubject"]["sameControllerAs"]
    if credential02_issuer != credential02_subject_sameControllerAs:
        print("Presentation invalid because one of the credentials is invalid")
        return
    if credential02_issuer != holder and credential02_subject_id != holder:
        print("Presentation invalid")
        return
    
    if credential02_issuer != credential01_subject_id or credential02_subject_id != credential01_issuer:
        print("Presentation invalid")
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
        print("Errors:" +str( verification_result["errors"]))
        print("Warnings:" + str(verification_result["warnings"]))
        return

    print("Presentation verified successfuly")

def parse_args():
    parser = argparse.ArgumentParser(description="DID Rotation Tool")
    subparsers = parser.add_subparsers(dest="command", required=True, help="Available commands")

    # issue_vc subcommand
    vc_parser = subparsers.add_parser("issue_vcs", help="Issue a verifiable credential")
    vc_parser.add_argument("did_01", help="DID#1")
    vc_parser.add_argument("key_file_01", help="JWK file with keys of did method #1")
    vc_parser.add_argument("did_02", help="DID#2")
    vc_parser.add_argument("key_file_02", help="JWK file with keys of did method #2")

    # issue_presentation subcommand
    vp_parser = subparsers.add_parser("issue_presentation", help="Issue a verifiable presentation")
    vp_parser.add_argument("holder", help="DID of the holder")
    vp_parser.add_argument("key_file", help="JWK file with keys of the holder")
    vp_parser.add_argument("signed_credential1", help="Path to the first signed credential")
    vp_parser.add_argument("signed_credential2", help="Path to the second signed credential")
    
    # verify_presentation subcommand
    verify_parser = subparsers.add_parser("verify_presentation", help="Verify a verifiable presentation")
    verify_parser.add_argument("presentation_file", help="Path to the signed presentation file")
    
    return parser.parse_args()

if __name__ == '__main__':
    asyncio.run(main())