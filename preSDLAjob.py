import mimetypes
import os
import subprocess
import tarfile

'''
1. Get ExP from version control
'''

'''
2. Extract ExP tar.gz
'''
def extract_tar_gz(file_path, extract_path):
    try:
        with tarfile.open(file_path, 'r:gz') as tar:
            tar.extractall(path=extract_path)
            print(f"Extracted '{file_path}' to '{extract_path}'")
    except Exception as e:
        print(f"Error extracting file: {e}")

'''
3. Copy content of ExP JSON to CAS pod
'''
def get_pod_name(namespace):
    
    pass

def copy_file_between_pods(file_path, dest_path, namespace="sdlcdt11"):
    dest_pod = get_pod_name(namespace=namespace)
    try:
        subprocess.run(["kubectl", "cp", file_path, f"{namespace}/{dest_pod}:{dest_path}"], check=True)

        print("File copied successfully!")

    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")


'''
4. Inject envvars to pod as config at runtime
'''

PASSWORD=os.getenv("PASSWORD")
NAMESPACE=os.getenv("NAMESPACE")
CASSERVER=f"cas.{NAMESPACE}.svc.cluster.local"
SERVER=f"https://{CASSERVER}:28809"


def get_files(directory):
    files = os.listdir(directory)
    print(files)

def get_fileType(file_path):
    mime_type, _ = mimetypes.guess_type(file_path)
    print(mime_type)

def get_fileName(file_path):
    file_name = os.path.basename(file_path)
    print(file_name.split(".tar")[0])


if __name__=='__main__':
    filePath = "C:\\Users\\JG\\Documents\\DT\\Onyx\\service_primitive\\SDL-SDLA-23.11.0-1-WX-ExP.tar"
    extractPath = "C:\\Users\\JG\\Documents\\DT\\Onyx\\service_primitive\\"
    get_fileName(file_path=filePath)
    # get_fileType(file_path=filePath)
    # get_files(directory=extractPath)
    # extract_tar_gz(file_path=filePath, extract_path=extractPath)
