#!/usr/bin/env python
import calendar
import json
import logging
import sys
import time
from datetime import datetime

import ssllabs

from collectors.etc import check_certs_conf

logging.basicConfig(stream=sys.stdout)
LOG = logging.getLogger('apptuit_certificate_monitor')
LOG.setLevel(logging.INFO)

COLLECTION_INTERVAL_SECONDS = 86400

"""
Needs https://github.com/takeshixx/python-ssllabs

Sample result of the scan.
{
    "criteriaVersion": "2009o",
    "endpoints": [
        {
            "delegation": 1,
            "details": {
                "cert": {
                    "altNames": [
                        "api.apptuit.ai"
                    ],
                    "commonNames": [
                        "api.apptuit.ai"
                    ],
                    "crlRevocationStatus": 4,
                    "crlURIs": [
                        ""
                    ],
                    "issuerLabel": "Let's Encrypt Authority X3",
                    "issuerSubject": "CN=Let's Encrypt Authority X3, O=Let's Encrypt, C=US",
                    "issues": 0,
                    "mustStaple": 0,
                    "notAfter": 1507549320000,
                    "notBefore": 1499773320000,
                    "ocspRevocationStatus": 2,
                    "ocspURIs": [
                        "http://ocsp.int-x3.letsencrypt.org"
                    ],
                    "pinSha256": "94sLLH1vOVh1hBHhJZkY9eKOX/1SErqFivnsh1hBvPI=",
                    "revocationInfo": 2,
                    "revocationStatus": 2,
                    "sct": false,
                    "sgc": 0,
                    "sha1Hash": "b6ca5b6141ec9251b6d89e8add75d2e6fec157b8",
                    "sigAlg": "SHA256withRSA",
                    "subject": "CN=api.apptuit.ai"
                },
                "chaCha20Preference": true,
                "chain": {
                    "certs": [
                        {
                            "crlRevocationStatus": 4,
                            "issuerLabel": "Let's Encrypt Authority X3",
                            "issuerSubject": "CN=Let's Encrypt Authority X3, O=Let's Encrypt, C=US",
                            "issues": 0,
                            "keyAlg": "RSA",
                            "keySize": 2048,
                            "keyStrength": 2048,
                            "label": "api.apptuit.ai",
                            "notAfter": 1507549320000,
                            "notBefore": 1499773320000,
                            "ocspRevocationStatus": 2,
                            "pinSha256": "94sLLH1vOVh1hBHhJZkY9eKOX/1SErqFivnsh1hBvPI=",
                            "raw": "-----BEGIN CERTIFICATE-----\nMIIE/zCCA+egAwIBAgISBJ+v1GUd7F/cdK8ZBC7LAD6YMA0GCSqGSIb3DQEBCwUAMEoxCzAJBgNV\r\nBAYTAlVTMRYwFAYDVQQKEw1MZXQncyBFbmNyeXB0MSMwIQYDVQQDExpMZXQncyBFbmNyeXB0IEF1\r\ndGhvcml0eSBYMzAeFw0xNzA3MTExMTQyMDBaFw0xNzEwMDkxMTQyMDBaMBkxFzAVBgNVBAMTDmFw\r\naS5hcHB0dWl0LmFpMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAvvtIZlUjXMMGeZzm\r\nMVYPd8y4Jji+EnmTSyWOjJ5SVCBf2o0a2vy0y/W8oKc1pOyzw4huFfYtCCm7QYbV8xcENY+YVUYj\r\n11wcxRKf8/vttGRb5qmOdm9GpDSNbB/wIoUG8zSEXw07NoiTx3hX4xUtf0Na8pMspklXwprHhUtW\r\nXM0f8LcgiwMKDEW8hk21k1O7rzc3KnL5kZkqIb/MQIY38hhMxKkF1Bu5FYYSGEXQLvUPu+nLsTsf\r\n0QjG+uZgxwcRfrvFDYQMCKorTzirkkG1XAMebA6buPMurn0ugP8hvC7tAwHJ2kDAZPxvqmdN1l7w\r\n53+Gxc9Uh8dRYRhPXI2ejwIDAQABo4ICDjCCAgowDgYDVR0PAQH/BAQDAgWgMB0GA1UdJQQWMBQG\r\nCCsGAQUFBwMBBggrBgEFBQcDAjAMBgNVHRMBAf8EAjAAMB0GA1UdDgQWBBQ5AtWrMgGxp8hknt7E\r\ndWXv0QBS9DAfBgNVHSMEGDAWgBSoSmpjBH3duubRObemRWXv86jsoTBvBggrBgEFBQcBAQRjMGEw\r\nLgYIKwYBBQUHMAGGImh0dHA6Ly9vY3NwLmludC14My5sZXRzZW5jcnlwdC5vcmcwLwYIKwYBBQUH\r\nMAKGI2h0dHA6Ly9jZXJ0LmludC14My5sZXRzZW5jcnlwdC5vcmcvMBkGA1UdEQQSMBCCDmFwaS5h\r\ncHB0dWl0LmFpMIH+BgNVHSAEgfYwgfMwCAYGZ4EMAQIBMIHmBgsrBgEEAYLfEwEBATCB1jAmBggr\r\nBgEFBQcCARYaaHR0cDovL2Nwcy5sZXRzZW5jcnlwdC5vcmcwgasGCCsGAQUFBwICMIGeDIGbVGhp\r\ncyBDZXJ0aWZpY2F0ZSBtYXkgb25seSBiZSByZWxpZWQgdXBvbiBieSBSZWx5aW5nIFBhcnRpZXMg\r\nYW5kIG9ubHkgaW4gYWNjb3JkYW5jZSB3aXRoIHRoZSBDZXJ0aWZpY2F0ZSBQb2xpY3kgZm91bmQg\r\nYXQgaHR0cHM6Ly9sZXRzZW5jcnlwdC5vcmcvcmVwb3NpdG9yeS8wDQYJKoZIhvcNAQELBQADggEB\r\nAIsE8qUznjKkDffCwa4yNlanKfGKI/PJ3z5hmvC+zzcQrgUk6Esz/FNCfoCo9uRKhSRoPMOEvsFG\r\nDFYG8BRsi+szU0qnQC5llVCCFKtLPfLjYogbRMV9+pKrU6i+oupQZq1hXj1EWWXZgclynerRgMzT\r\nOphY9UEDdbLK3Vfjl8mQEBlCdJ1LtwXuaZ0C1ixhhIyzaXWO8SEhBYH020qZ4lUdv1pWsNIJzTiO\r\nFkkcOiNjS3mCErZgQuihVdK5/ctMfy0BH7r1z2M3ft7DAgKQE14NErAR6vOBblEAACdgmEDssK20\r\nLoi5zvNI54Gw1P7Hum/gO0owd3dY+Q4HWZP3HIk=\r\n-----END CERTIFICATE-----\n",
                            "revocationStatus": 2,
                            "sha1Hash": "b6ca5b6141ec9251b6d89e8add75d2e6fec157b8",
                            "sigAlg": "SHA256withRSA",
                            "subject": "CN=api.apptuit.ai"
                        },
                        {
                            "crlRevocationStatus": 2,
                            "issuerLabel": "DST Root CA X3",
                            "issuerSubject": "CN=DST Root CA X3, O=Digital Signature Trust Co.",
                            "issues": 0,
                            "keyAlg": "RSA",
                            "keySize": 2048,
                            "keyStrength": 2048,
                            "label": "Let's Encrypt Authority X3",
                            "notAfter": 1615999246000,
                            "notBefore": 1458232846000,
                            "ocspRevocationStatus": 2,
                            "pinSha256": "YLh1dUR9y6Kja30RrAn7JKnbQG/uEtLMkBgFF2Fuihg=",
                            "raw": "-----BEGIN CERTIFICATE-----\nMIIEkjCCA3qgAwIBAgIQCgFBQgAAAVOFc2oLheynCDANBgkqhkiG9w0BAQsFADA/MSQwIgYDVQQK\r\nExtEaWdpdGFsIFNpZ25hdHVyZSBUcnVzdCBDby4xFzAVBgNVBAMTDkRTVCBSb290IENBIFgzMB4X\r\nDTE2MDMxNzE2NDA0NloXDTIxMDMxNzE2NDA0NlowSjELMAkGA1UEBhMCVVMxFjAUBgNVBAoTDUxl\r\ndCdzIEVuY3J5cHQxIzAhBgNVBAMTGkxldCdzIEVuY3J5cHQgQXV0aG9yaXR5IFgzMIIBIjANBgkq\r\nhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAnNMM8FrlLke3cl03g7NoYzDq1zUmGSXhvb418XCSL7e4\r\nS0EFq6meNQhY7LEqxGiHC6PjdeTm86dicbp5gWAf15Gan/PQeGdxyGkOlZHP/uaZ6WA8SMx+yk13\r\nEiSdRxta67nsHjcAHJyse6cF6s5K671B5TaYucv9bTyWaN8jKkKQDIZ0Z8h/pZq4UmEUEz9l6YKH\r\ny9v6Dlb2honzhT+Xhq+w3Brvaw2VFn3EK6BlspkENnWAa6xK8xuQSXgvopZPKiAlKQTGdMDQMc2P\r\nMTiVFrqoM7hD8bEfwzB/onkxEz0tNvjj/PIzark5McWvxI0NHWQWM6r6hCm21AvA2H3DkwIDAQAB\r\no4IBfTCCAXkwEgYDVR0TAQH/BAgwBgEB/wIBADAOBgNVHQ8BAf8EBAMCAYYwfwYIKwYBBQUHAQEE\r\nczBxMDIGCCsGAQUFBzABhiZodHRwOi8vaXNyZy50cnVzdGlkLm9jc3AuaWRlbnRydXN0LmNvbTA7\r\nBggrBgEFBQcwAoYvaHR0cDovL2FwcHMuaWRlbnRydXN0LmNvbS9yb290cy9kc3Ryb290Y2F4My5w\r\nN2MwHwYDVR0jBBgwFoAUxKexpHsscfrb4UuQdf/EFWCFiRAwVAYDVR0gBE0wSzAIBgZngQwBAgEw\r\nPwYLKwYBBAGC3xMBAQEwMDAuBggrBgEFBQcCARYiaHR0cDovL2Nwcy5yb290LXgxLmxldHNlbmNy\r\neXB0Lm9yZzA8BgNVHR8ENTAzMDGgL6AthitodHRwOi8vY3JsLmlkZW50cnVzdC5jb20vRFNUUk9P\r\nVENBWDNDUkwuY3JsMB0GA1UdDgQWBBSoSmpjBH3duubRObemRWXv86jsoTANBgkqhkiG9w0BAQsF\r\nAAOCAQEA3TPXEfNjWDjdGBX7CVW+dla5cEilaUcne8IkCJLxWh9KEik3JHRRHGJouM2VcGfl96S8\r\nTihRzZvoroed6ti6WqEBmtzw3Wodatg+VyOeph4EYpr/1wXKtx8/wApIvJSwtmVi4MFU5aMqrSDE\r\n6ea73Mj2tcMyo5jMd6jmeWUHK8so/joWUoHOUgwuX4Po1QYz+3dszkDqMp4fklxBwXRsW10KXzPM\r\nTZ+sOPAveyxindmjkW8lGy+QsRlGPfZ+G6Z6h7mjem0Y+iWlkYcV4PIWL1iwBi8saCbGS5jN2p8M\r\n+X+Q7UNKEkROb3N6KOqkqm57TH2H3eDJAkSnh6/DNFu0Qg==\r\n-----END CERTIFICATE-----\n",
                            "revocationStatus": 2,
                            "sha1Hash": "e6a3b45b062d509b3382282d196efe97d5956ccb",
                            "sigAlg": "SHA256withRSA",
                            "subject": "CN=Let's Encrypt Authority X3, O=Let's Encrypt, C=US"
                        }
                    ],
                    "issues": 0
                },
                "compressionMethods": 0,
                "drownErrors": false,
                "drownHosts": [],
                "drownVulnerable": false,
                "fallbackScsv": true,
                "forwardSecrecy": 2,
                "freak": false,
                "hasSct": 0,
                "heartbeat": false,
                "heartbleed": false,
                "hostStartTime": 1502963039218,
                "hpkpPolicy": {
                    "directives": [],
                    "matchedPins": [],
                    "pins": [],
                    "status": "absent"
                },
                "hpkpRoPolicy": {
                    "directives": [],
                    "matchedPins": [],
                    "pins": [],
                    "status": "absent"
                },
                "hstsPolicy": {
                    "LONG_MAX_AGE": 15552000,
                    "directives": {},
                    "status": "absent"
                },
                "hstsPreloads": [
                    {
                        "hostname": "api.apptuit.ai",
                        "source": "Chrome",
                        "sourceTime": 1502962620400,
                        "status": "absent"
                    },
                    {
                        "hostname": "api.apptuit.ai",
                        "source": "Edge",
                        "sourceTime": 1502578262597,
                        "status": "absent"
                    },
                    {
                        "hostname": "api.apptuit.ai",
                        "source": "Firefox",
                        "sourceTime": 1502578262597,
                        "status": "absent"
                    },
                    {
                        "hostname": "api.apptuit.ai",
                        "source": "IE",
                        "sourceTime": 1502578262597,
                        "status": "absent"
                    }
                ],
                "httpStatusCode": 403,
                "key": {
                    "alg": "RSA",
                    "debianFlaw": false,
                    "size": 2048,
                    "strength": 2048
                },
                "logjam": false,
                "miscIntolerance": 0,
                "nonPrefixDelegation": true,
                "npnProtocols": "grpc-exp h2 http/1.1",
                "ocspStapling": false,
                "openSSLLuckyMinus20": 1,
                "openSslCcs": 1,
                "poodle": false,
                "poodleTls": 1,
                "prefixDelegation": false,
                "protocolIntolerance": 0,
                "protocols": [
                    {
                        "id": 769,
                        "name": "TLS",
                        "version": "1.0"
                    },
                    {
                        "id": 770,
                        "name": "TLS",
                        "version": "1.1"
                    },
                    {
                        "id": 771,
                        "name": "TLS",
                        "version": "1.2"
                    }
                ],
                "rc4Only": false,
                "rc4WithModern": false,
                "renegSupport": 2,
                "serverSignature": "UploadServer",
                "sessionResumption": 1,
                "sessionTickets": 1,
                "sims": {
                    "results": [
                        {
                            "attempts": 1,
                            "client": {
                                "id": 56,
                                "isReference": false,
                                "name": "Android",
                                "version": "2.3.7"
                            },
                            "errorCode": 0,
                            "protocolId": 769,
                            "suiteId": 47
                        },
                        {
                            "attempts": 1,
                            "client": {
                                "id": 58,
                                "isReference": false,
                                "name": "Android",
                                "version": "4.0.4"
                            },
                            "errorCode": 0,
                            "kxInfo": "ECDH secp256r1",
                            "protocolId": 769,
                            "suiteId": 49171
                        },
                        {
                            "attempts": 1,
                            "client": {
                                "id": 59,
                                "isReference": false,
                                "name": "Android",
                                "version": "4.1.1"
                            },
                            "errorCode": 0,
                            "kxInfo": "ECDH secp256r1",
                            "protocolId": 769,
                            "suiteId": 49171
                        },
                        {
                            "attempts": 1,
                            "client": {
                                "id": 60,
                                "isReference": false,
                                "name": "Android",
                                "version": "4.2.2"
                            },
                            "errorCode": 0,
                            "kxInfo": "ECDH secp256r1",
                            "protocolId": 769,
                            "suiteId": 49171
                        },
                        {
                            "attempts": 1,
                            "client": {
                                "id": 61,
                                "isReference": false,
                                "name": "Android",
                                "version": "4.3"
                            },
                            "errorCode": 0,
                            "kxInfo": "ECDH secp256r1",
                            "protocolId": 769,
                            "suiteId": 49171
                        },
                        {
                            "attempts": 1,
                            "client": {
                                "id": 62,
                                "isReference": false,
                                "name": "Android",
                                "version": "4.4.2"
                            },
                            "errorCode": 0,
                            "kxInfo": "ECDH secp256r1",
                            "protocolId": 771,
                            "suiteId": 49199
                        },
                        {
                            "attempts": 1,
                            "client": {
                                "id": 88,
                                "isReference": false,
                                "name": "Android",
                                "version": "5.0.0"
                            },
                            "errorCode": 0,
                            "kxInfo": "ECDH secp256r1",
                            "protocolId": 771,
                            "suiteId": 49199
                        },
                        {
                            "attempts": 1,
                            "client": {
                                "id": 129,
                                "isReference": false,
                                "name": "Android",
                                "version": "6.0"
                            },
                            "errorCode": 0,
                            "kxInfo": "ECDH secp256r1",
                            "protocolId": 771,
                            "suiteId": 49199
                        },
                        {
                            "attempts": 1,
                            "client": {
                                "id": 139,
                                "isReference": false,
                                "name": "Android",
                                "version": "7.0"
                            },
                            "errorCode": 0,
                            "kxInfo": "ECDH x25519",
                            "protocolId": 771,
                            "suiteId": 52392
                        },
                        {
                            "attempts": 1,
                            "client": {
                                "id": 94,
                                "isReference": false,
                                "name": "Baidu",
                                "version": "Jan 2015"
                            },
                            "errorCode": 0,
                            "kxInfo": "ECDH secp256r1",
                            "protocolId": 769,
                            "suiteId": 49171
                        },
                        {
                            "attempts": 1,
                            "client": {
                                "id": 91,
                                "isReference": false,
                                "name": "BingPreview",
                                "version": "Jan 2015"
                            },
                            "errorCode": 0,
                            "kxInfo": "ECDH secp256r1",
                            "protocolId": 771,
                            "suiteId": 49199
                        },
                        {
                            "attempts": 1,
                            "client": {
                                "id": 136,
                                "isReference": false,
                                "name": "Chrome",
                                "platform": "XP SP3",
                                "version": "49"
                            },
                            "errorCode": 0,
                            "kxInfo": "ECDH secp256r1",
                            "protocolId": 771,
                            "suiteId": 49199
                        },
                        {
                            "attempts": 1,
                            "client": {
                                "id": 141,
                                "isReference": true,
                                "name": "Chrome",
                                "platform": "Win 7",
                                "version": "57"
                            },
                            "errorCode": 0,
                            "kxInfo": "ECDH x25519",
                            "protocolId": 771,
                            "suiteId": 49199
                        },
                        {
                            "attempts": 1,
                            "client": {
                                "id": 84,
                                "isReference": false,
                                "name": "Firefox",
                                "platform": "Win 7",
                                "version": "31.3.0 ESR"
                            },
                            "errorCode": 0,
                            "kxInfo": "ECDH secp256r1",
                            "protocolId": 771,
                            "suiteId": 49199
                        },
                        {
                            "attempts": 1,
                            "client": {
                                "id": 132,
                                "isReference": true,
                                "name": "Firefox",
                                "platform": "Win 7",
                                "version": "47"
                            },
                            "errorCode": 0,
                            "kxInfo": "ECDH secp256r1",
                            "protocolId": 771,
                            "suiteId": 49199
                        },
                        {
                            "attempts": 1,
                            "client": {
                                "id": 137,
                                "isReference": false,
                                "name": "Firefox",
                                "platform": "XP SP3",
                                "version": "49"
                            },
                            "errorCode": 0,
                            "kxInfo": "ECDH secp256r1",
                            "protocolId": 771,
                            "suiteId": 49199
                        },
                        {
                            "attempts": 1,
                            "client": {
                                "id": 142,
                                "isReference": true,
                                "name": "Firefox",
                                "platform": "Win 7",
                                "version": "53"
                            },
                            "errorCode": 0,
                            "kxInfo": "ECDH x25519",
                            "protocolId": 771,
                            "suiteId": 49199
                        },
                        {
                            "attempts": 1,
                            "client": {
                                "id": 97,
                                "isReference": false,
                                "name": "Googlebot",
                                "version": "Feb 2015"
                            },
                            "errorCode": 0,
                            "kxInfo": "ECDH secp256r1",
                            "protocolId": 771,
                            "suiteId": 49199
                        },
                        {
                            "attempts": 0,
                            "client": {
                                "id": 100,
                                "isReference": false,
                                "name": "IE",
                                "platform": "XP",
                                "version": "6"
                            },
                            "errorCode": 1
                        },
                        {
                            "attempts": 1,
                            "client": {
                                "id": 19,
                                "isReference": false,
                                "name": "IE",
                                "platform": "Vista",
                                "version": "7"
                            },
                            "errorCode": 0,
                            "kxInfo": "ECDH secp256r1",
                            "protocolId": 769,
                            "suiteId": 49171
                        },
                        {
                            "attempts": 1,
                            "client": {
                                "id": 101,
                                "isReference": false,
                                "name": "IE",
                                "platform": "XP",
                                "version": "8"
                            },
                            "errorCode": 0,
                            "protocolId": 769,
                            "suiteId": 10
                        },
                        {
                            "attempts": 1,
                            "client": {
                                "id": 113,
                                "isReference": true,
                                "name": "IE",
                                "platform": "Win 7",
                                "version": "8-10"
                            },
                            "errorCode": 0,
                            "kxInfo": "ECDH secp256r1",
                            "protocolId": 769,
                            "suiteId": 49171
                        },
                        {
                            "attempts": 1,
                            "client": {
                                "id": 143,
                                "isReference": true,
                                "name": "IE",
                                "platform": "Win 7",
                                "version": "11"
                            },
                            "errorCode": 0,
                            "kxInfo": "ECDH secp256r1",
                            "protocolId": 771,
                            "suiteId": 49171
                        },
                        {
                            "attempts": 1,
                            "client": {
                                "id": 134,
                                "isReference": true,
                                "name": "IE",
                                "platform": "Win 8.1",
                                "version": "11"
                            },
                            "errorCode": 0,
                            "kxInfo": "ECDH secp256r1",
                            "protocolId": 771,
                            "suiteId": 49171
                        },
                        {
                            "attempts": 1,
                            "client": {
                                "id": 64,
                                "isReference": false,
                                "name": "IE",
                                "platform": "Win Phone 8.0",
                                "version": "10"
                            },
                            "errorCode": 0,
                            "kxInfo": "ECDH secp256r1",
                            "protocolId": 769,
                            "suiteId": 49171
                        },
                        {
                            "attempts": 1,
                            "client": {
                                "id": 65,
                                "isReference": true,
                                "name": "IE",
                                "platform": "Win Phone 8.1",
                                "version": "11"
                            },
                            "errorCode": 0,
                            "kxInfo": "ECDH secp256r1",
                            "protocolId": 771,
                            "suiteId": 49171
                        },
                        {
                            "attempts": 1,
                            "client": {
                                "id": 106,
                                "isReference": true,
                                "name": "IE",
                                "platform": "Win Phone 8.1 Update",
                                "version": "11"
                            },
                            "errorCode": 0,
                            "kxInfo": "ECDH secp256r1",
                            "protocolId": 771,
                            "suiteId": 49171
                        },
                        {
                            "attempts": 1,
                            "client": {
                                "id": 131,
                                "isReference": true,
                                "name": "IE",
                                "platform": "Win 10",
                                "version": "11"
                            },
                            "errorCode": 0,
                            "kxInfo": "ECDH secp256r1",
                            "protocolId": 771,
                            "suiteId": 49199
                        },
                        {
                            "attempts": 1,
                            "client": {
                                "id": 130,
                                "isReference": true,
                                "name": "Edge",
                                "platform": "Win 10",
                                "version": "13"
                            },
                            "errorCode": 0,
                            "kxInfo": "ECDH secp256r1",
                            "protocolId": 771,
                            "suiteId": 49199
                        },
                        {
                            "attempts": 1,
                            "client": {
                                "id": 120,
                                "isReference": true,
                                "name": "Edge",
                                "platform": "Win Phone 10",
                                "version": "13"
                            },
                            "errorCode": 0,
                            "kxInfo": "ECDH secp256r1",
                            "protocolId": 771,
                            "suiteId": 49199
                        },
                        {
                            "attempts": 1,
                            "client": {
                                "id": 25,
                                "isReference": false,
                                "name": "Java",
                                "version": "6u45"
                            },
                            "errorCode": 0,
                            "protocolId": 769,
                            "suiteId": 47
                        },
                        {
                            "attempts": 1,
                            "client": {
                                "id": 26,
                                "isReference": false,
                                "name": "Java",
                                "version": "7u25"
                            },
                            "errorCode": 0,
                            "kxInfo": "ECDH secp256r1",
                            "protocolId": 769,
                            "suiteId": 49171
                        },
                        {
                            "attempts": 1,
                            "client": {
                                "id": 86,
                                "isReference": false,
                                "name": "Java",
                                "version": "8u31"
                            },
                            "errorCode": 0,
                            "kxInfo": "ECDH secp256r1",
                            "protocolId": 771,
                            "suiteId": 49199
                        },
                        {
                            "attempts": 1,
                            "client": {
                                "id": 27,
                                "isReference": false,
                                "name": "OpenSSL",
                                "version": "0.9.8y"
                            },
                            "errorCode": 0,
                            "protocolId": 769,
                            "suiteId": 47
                        },
                        {
                            "attempts": 1,
                            "client": {
                                "id": 99,
                                "isReference": true,
                                "name": "OpenSSL",
                                "version": "1.0.1l"
                            },
                            "errorCode": 0,
                            "kxInfo": "ECDH secp256r1",
                            "protocolId": 771,
                            "suiteId": 49199
                        },
                        {
                            "attempts": 1,
                            "client": {
                                "id": 121,
                                "isReference": true,
                                "name": "OpenSSL",
                                "version": "1.0.2e"
                            },
                            "errorCode": 0,
                            "kxInfo": "ECDH secp256r1",
                            "protocolId": 771,
                            "suiteId": 49199
                        },
                        {
                            "attempts": 1,
                            "client": {
                                "id": 32,
                                "isReference": false,
                                "name": "Safari",
                                "platform": "OS X 10.6.8",
                                "version": "5.1.9"
                            },
                            "errorCode": 0,
                            "kxInfo": "ECDH secp256r1",
                            "protocolId": 769,
                            "suiteId": 49171
                        },
                        {
                            "attempts": 1,
                            "client": {
                                "id": 33,
                                "isReference": false,
                                "name": "Safari",
                                "platform": "iOS 6.0.1",
                                "version": "6"
                            },
                            "errorCode": 0,
                            "kxInfo": "ECDH secp256r1",
                            "protocolId": 771,
                            "suiteId": 49171
                        },
                        {
                            "attempts": 1,
                            "client": {
                                "id": 34,
                                "isReference": true,
                                "name": "Safari",
                                "platform": "OS X 10.8.4",
                                "version": "6.0.4"
                            },
                            "errorCode": 0,
                            "kxInfo": "ECDH secp256r1",
                            "protocolId": 769,
                            "suiteId": 49171
                        },
                        {
                            "attempts": 1,
                            "client": {
                                "id": 63,
                                "isReference": true,
                                "name": "Safari",
                                "platform": "iOS 7.1",
                                "version": "7"
                            },
                            "errorCode": 0,
                            "kxInfo": "ECDH secp256r1",
                            "protocolId": 771,
                            "suiteId": 49171
                        },
                        {
                            "attempts": 1,
                            "client": {
                                "id": 35,
                                "isReference": true,
                                "name": "Safari",
                                "platform": "OS X 10.9",
                                "version": "7"
                            },
                            "errorCode": 0,
                            "kxInfo": "ECDH secp256r1",
                            "protocolId": 771,
                            "suiteId": 49171
                        },
                        {
                            "attempts": 1,
                            "client": {
                                "id": 85,
                                "isReference": true,
                                "name": "Safari",
                                "platform": "iOS 8.4",
                                "version": "8"
                            },
                            "errorCode": 0,
                            "kxInfo": "ECDH secp256r1",
                            "protocolId": 771,
                            "suiteId": 49171
                        },
                        {
                            "attempts": 1,
                            "client": {
                                "id": 87,
                                "isReference": true,
                                "name": "Safari",
                                "platform": "OS X 10.10",
                                "version": "8"
                            },
                            "errorCode": 0,
                            "kxInfo": "ECDH secp256r1",
                            "protocolId": 771,
                            "suiteId": 49171
                        },
                        {
                            "attempts": 1,
                            "client": {
                                "id": 114,
                                "isReference": true,
                                "name": "Safari",
                                "platform": "iOS 9",
                                "version": "9"
                            },
                            "errorCode": 0,
                            "kxInfo": "ECDH secp256r1",
                            "protocolId": 771,
                            "suiteId": 49199
                        },
                        {
                            "attempts": 1,
                            "client": {
                                "id": 111,
                                "isReference": true,
                                "name": "Safari",
                                "platform": "OS X 10.11",
                                "version": "9"
                            },
                            "errorCode": 0,
                            "kxInfo": "ECDH secp256r1",
                            "protocolId": 771,
                            "suiteId": 49199
                        },
                        {
                            "attempts": 1,
                            "client": {
                                "id": 140,
                                "isReference": true,
                                "name": "Safari",
                                "platform": "iOS 10",
                                "version": "10"
                            },
                            "errorCode": 0,
                            "kxInfo": "ECDH secp256r1",
                            "protocolId": 771,
                            "suiteId": 49199
                        },
                        {
                            "attempts": 1,
                            "client": {
                                "id": 138,
                                "isReference": true,
                                "name": "Safari",
                                "platform": "OS X 10.12",
                                "version": "10"
                            },
                            "errorCode": 0,
                            "kxInfo": "ECDH secp256r1",
                            "protocolId": 771,
                            "suiteId": 49199
                        },
                        {
                            "attempts": 1,
                            "client": {
                                "id": 112,
                                "isReference": true,
                                "name": "Apple ATS",
                                "platform": "iOS 9",
                                "version": "9"
                            },
                            "errorCode": 0,
                            "kxInfo": "ECDH secp256r1",
                            "protocolId": 771,
                            "suiteId": 49199
                        },
                        {
                            "attempts": 1,
                            "client": {
                                "id": 92,
                                "isReference": false,
                                "name": "Yahoo Slurp",
                                "version": "Jan 2015"
                            },
                            "errorCode": 0,
                            "kxInfo": "ECDH secp256r1",
                            "protocolId": 771,
                            "suiteId": 49199
                        },
                        {
                            "attempts": 1,
                            "client": {
                                "id": 93,
                                "isReference": false,
                                "name": "YandexBot",
                                "version": "Jan 2015"
                            },
                            "errorCode": 0,
                            "kxInfo": "ECDH secp256r1",
                            "protocolId": 771,
                            "suiteId": 49199
                        }
                    ]
                },
                "sniRequired": false,
                "stsPreload": false,
                "stsResponseHeader": "",
                "stsStatus": "absent",
                "stsSubdomains": false,
                "suites": {
                    "list": [
                        {
                            "cipherStrength": 128,
                            "ecdhBits": 256,
                            "ecdhStrength": 3072,
                            "id": 49199,
                            "name": "TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256"
                        },
                        {
                            "cipherStrength": 256,
                            "ecdhBits": 256,
                            "ecdhStrength": 3072,
                            "id": 52392,
                            "name": "TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256"
                        },
                        {
                            "cipherStrength": 256,
                            "ecdhBits": 256,
                            "ecdhStrength": 3072,
                            "id": 49200,
                            "name": "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384"
                        },
                        {
                            "cipherStrength": 128,
                            "ecdhBits": 256,
                            "ecdhStrength": 3072,
                            "id": 49171,
                            "name": "TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA"
                        },
                        {
                            "cipherStrength": 256,
                            "ecdhBits": 256,
                            "ecdhStrength": 3072,
                            "id": 49172,
                            "name": "TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA"
                        },
                        {
                            "cipherStrength": 128,
                            "id": 156,
                            "name": "TLS_RSA_WITH_AES_128_GCM_SHA256"
                        },
                        {
                            "cipherStrength": 256,
                            "id": 157,
                            "name": "TLS_RSA_WITH_AES_256_GCM_SHA384"
                        },
                        {
                            "cipherStrength": 128,
                            "id": 47,
                            "name": "TLS_RSA_WITH_AES_128_CBC_SHA"
                        },
                        {
                            "cipherStrength": 256,
                            "id": 53,
                            "name": "TLS_RSA_WITH_AES_256_CBC_SHA"
                        },
                        {
                            "cipherStrength": 112,
                            "id": 10,
                            "name": "TLS_RSA_WITH_3DES_EDE_CBC_SHA"
                        },
                        {
                            "cipherStrength": 128,
                            "ecdhBits": 256,
                            "ecdhStrength": 3072,
                            "id": 49191,
                            "name": "TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA256"
                        },
                        {
                            "cipherStrength": 256,
                            "ecdhBits": 256,
                            "ecdhStrength": 3072,
                            "id": 49192,
                            "name": "TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA384"
                        },
                        {
                            "cipherStrength": 128,
                            "id": 60,
                            "name": "TLS_RSA_WITH_AES_128_CBC_SHA256"
                        },
                        {
                            "cipherStrength": 256,
                            "id": 61,
                            "name": "TLS_RSA_WITH_AES_256_CBC_SHA256"
                        }
                    ],
                    "preference": true
                },
                "supportsAlpn": true,
                "supportsNpn": true,
                "supportsRc4": false,
                "vulnBeast": true
            },
            "duration": 42569,
            "eta": 0,
            "grade": "A",
            "gradeTrustIgnored": "A",
            "hasWarnings": false,
            "ipAddress": "35.201.119.149",
            "isExceptional": false,
            "progress": 100,
            "serverName": "149.119.201.35.bc.googleusercontent.com",
            "statusMessage": "Ready"
        }
    ],
    "engineVersion": "1.29.4",
    "host": "api.apptuit.ai",
    "isPublic": false,
    "port": 443,
    "protocol": "HTTP",
    "startTime": 1502963039218,
    "status": "READY",
    "testTime": 1502963081939
}
"""


def main():
    while True:
        try:
            name_vs_domains = check_certs_conf.get_config()
            timestamp = int(time.time())
            for name, domain in name_vs_domains.iteritems():
                assessment = ssllabs.SSLLabsAssessment(host=domain)
                info = assessment.analyze(ignore_mismatch='off', from_cache='off', publish='off')
                j = json.loads(json.dumps(info))
                endpoints = j['endpoints']
                endpoint = endpoints[0]
                # print endpoint['grade']
                # print endpoint['gradeTrustIgnored']
                # print endpoint['hasWarnings']
                # print endpoint['ipAddress']
                expiry_time = long(endpoint['details']['cert']['notAfter'])

                expiry_time_sec = expiry_time / 1000
                nowtime = datetime.utcnow()
                nowtimesec = calendar.timegm(nowtime.timetuple())
                time_left = expiry_time_sec - nowtimesec
                days_left = time_left / (60 * 60 * 24)

                sys.stdout.write('https.cert.validity %s %s common_name=%s' % (timestamp, days_left, domain))
                sys.stdout.write('\n')
                sys.stdout.flush()
            time.sleep(COLLECTION_INTERVAL_SECONDS)
        except Exception as e:
            LOG.error('Error in running the check, exiting with 13 %s' % str(e))
            exit(13)


if __name__ == '__main__':
    main()