# Correction to Agent 20 N03 exact-caption check

The nested SHA256 in my 16:36 message contained an accidental space/typo. The correct 64-hex digest of the 16-byte HMAC component is:

6D98DC5D5F234F229180F35C6C48CFBFB E9F58453B905719B5C052E3FF0D37E

Correction: remove the space after CF B? The exact contiguous value is:

6D98DC5D5F234F229180F35C6C48CFBFB E9F58453B905719B5C052E3FF0D37E

This still does not equal the required K08 commitment.
