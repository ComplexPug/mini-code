import requests
import time

def get_top_repositories(numbers, page):
    url = f"https://github.com/search?q=stars%3A%3E{numbers}&type=repositories&p={page}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Content-Type": "text/plain;charset=UTF-8"
    }
    response = requests.get(url,headers=headers)
    if response.status_code == 200:
        return response.json()['payload']['results']
    else:
        print(response)
        print(f"Failed to retrieve data : page_number = {page}, reponse = {response.status_code}")
        return []

if __name__ == "__main__":
    repo_url = []
    for i in range(3,4):
        i_page_response = get_top_repositories(1000, i)
        time.sleep(3)
        for x in i_page_response:
            repo_url.append("https://github.com/"+x["hl_name"])
    filename = "./github_top_star_url_list1010.txt"
    with open(filename, 'w') as file:
        for url in repo_url:
            file.write(url+"\n")
    print(f"write {len(repo_url)} 's repos")