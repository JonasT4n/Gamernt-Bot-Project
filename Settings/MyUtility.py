def convert_to_binary_type(filename):
    f = open(filename, 'rb')
    blobData = f.read()
    f.close()
    return blobData