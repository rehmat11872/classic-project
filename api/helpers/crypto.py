
from Crypto.PublicKey import RSA
# from Crypto.Random import get_random_bytes
from Crypto.Cipher import PKCS1_OAEP

public_key = "C:/nginx/ssl/star_cidb_gov_my.pem"
private_key = "C:/nginx/ssl/qlassicstg.key"


# Encrypt
def encrypt_data_rsa(data):
    # data = "I met aliens in UFO. Here is the map.".encode("utf-8")
    # file_out = open("encrypted_data.bin", "wb")
    recipient_key = RSA.import_key(open(public_key).read())
    # session_key = get_random_bytes(16)

    # Encrypt the session key with the public RSA key
    cipher_rsa = PKCS1_OAEP.new(recipient_key)
    encrypted_data = cipher_rsa.encrypt(data)
    return encrypted_data

# Decrypt
def decrypt_data_rsa(encrypted_data):
    private_key = RSA.import_key(open(private_key).read())

    # Decrypt the session key with the private RSA key
    cipher_rsa = PKCS1_OAEP.new(private_key)
    data = cipher_rsa.decrypt(encrypted_data)
    return data