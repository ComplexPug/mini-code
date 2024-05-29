# %%
import requests
import subprocess
import time,os
import concurrent.futures
import json
import urllib,zipfile

STORGE_PATH = "/home/dsr/project/github_top/"
input_filename = "./github_top_star_url_list100.txt"
output_filename = "github_repos_codeline.txt"


# %%

def get_name(repo_url):
    return repo_url.split('/')[-1].replace('.git', '')

# Note: The size of the repository can be significantly increased by the .git directory (e.g., in the Linux repository). 
# To avoid this, you can download the repository as a zip file using curl.

def download_zip(url, repo_path, zip_path):
    urllib.request.urlretrieve(url, zip_path)
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(repo_path)
    os.remove(zip_path)

def download_repo(repo_url):
    repo_name = get_name(repo_url)
    repo_path = os.path.join(STORGE_PATH, repo_name)

    if not os.path.exists(repo_path):
        os.makedirs(repo_path)
        print(f"Downloading {repo_name} as zip")
        
        zip_path = os.path.join(STORGE_PATH, f"{repo_name}.zip")
        branch_list = ["main", "master"]
        
        for branch in branch_list:
            try:
                zip_url = f"{repo_url.rstrip('.git')}/archive/refs/heads/{branch}.zip"
                download_zip(zip_url, repo_path, zip_path)
                print(f"Downloaded {repo_name} from branch {branch}")
                break
            except Exception as e:
                print(f"Failed to download from branch {branch}: {e}")
                if branch == branch_list[-1]:
                    raise Exception(f"Failed to download repository from all known branches: {repo_url}")
    else:
        if len(os.listdir(repo_path)) <= 1:
            print(f"Deleting empty directory {repo_name}: cmd = \"rm -rf {repo_path}\"")
            subprocess.run(['rm', '-rf', repo_path], check=True)
            time.sleep(3)
            download_repo(repo_url)
        else:
            pass
            # print(f"{repo_name} already exists")


# %%
with open(input_filename, 'r') as file:
    repo_urls = [line.strip() for line in file]

# download all repos
for repo_url in repo_urls:
    download_repo(repo_url)

# %%
counts = {}
def count_lines_of_repo(repo_url):
    if repo_url in counts: return
    repo_name = get_name(repo_url)
    repo_path = STORGE_PATH+repo_name

    stdout_str_json = subprocess.run(["cloc", repo_path, "--json"], capture_output=True, text=True).stdout
    result = json.loads(stdout_str_json)

    counts[repo_url] = result["SUM"]["code"]
    print(f"{get_name(repo_url):<30} : {counts[repo_url]:>10}")

# %%
# count all repos by cloc tools
with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
    futures = [executor.submit(count_lines_of_repo, repo_url) for repo_url in repo_urls]
    for future in concurrent.futures.as_completed(futures):
        future.result()  # 等待所有线程完成

# %%
sorted_results = sorted(counts.items(), key=lambda x: x[1], reverse=True)
formatted_lines = []
for repo_url,count_lines in sorted_results:
    formatted_line = f"{get_name(repo_url):<30} : {count_lines:>10}"
    formatted_lines.append(formatted_line)
with open(output_filename,"w") as file:
    for formatted_line in formatted_lines:
        file.write(formatted_line + '\n')

print(formatted_lines)

# %%



