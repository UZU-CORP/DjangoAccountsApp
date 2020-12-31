from pyotp import totp
url = totp.TOTP('JBSWY3DPEHPK3PXP').provisioning_uri(
    name='anselem16m@gmail.com', issuer_name='UzuCorp'
)
print(totp.TOTP('JBSWY3DPEHPK3PXP').verify(otp="310195", valid_window=3))