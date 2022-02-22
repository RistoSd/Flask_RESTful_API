import requests

BASE = "http://127.0.0.1:5000/"

while True:
    print("""1-put_project, 2-get_project, 3-patch_project, 4-delete_project,
          5-put_user, 6-get_user, 7-delete_user""")
    user_input = int(input())
    #  1
    if user_input == 1:
        response = requests.put(BASE + "project/9", {"name": "restful_api", "user_name": "Jackson"})
        print(response.json())

    #  2
    elif user_input == 2:
        response = requests.get(BASE + "project/9")
        print(response.json())

    #  3
    elif user_input == 3:
        response = requests.patch(BASE + "project/9", {"user_name": "Manny"})
        print(response.json())

    #  4
    elif user_input == 4:
        response = requests.delete(BASE + "project/9")
        print(response.json()) #  response [200]

    #  5
    elif user_input == 5:
        response = requests.put(BASE + "user/9", {"name": "Nina"})
        print(response.json())

    #  6
    elif user_input == 6:
        response = requests.get(BASE + "user/1")
        print(response.json())

    #  7
    elif user_input == 7:
        response = requests.delete(BASE + "user/9")
        print(response)

    else:
        print("input wrong")

    

