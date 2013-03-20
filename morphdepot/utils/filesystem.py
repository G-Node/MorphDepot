import hashlib

def get_file_sha1(file_path):
    print "file_path:", file_path
    source_file = open(file_path, mode='rb')
    print source_file
    hash = hashlib.sha1()
    # if source_file.multiple_chunks():
    #     for chunk in file_path.chunks():
    #         hash.update(chunk)
    # else:
    hash.update(source_file.read())
    source_file.close()
    return hash.hexdigest()
