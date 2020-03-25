from requests import delete, get, put, post


print(get('http://localhost:8080/api/v2/users').json())
print(get('http://localhost:8080/api/v2/users/1').json())
print(post('http://localhost:8080/api/v2/users',
           json={'surname': 'asfge',
                 'name': 'asfge',
                 'age': 11,
                 'position': 'asfge',
                 'city_from': 'asfge',
                 'speciality': 'asfge',
                 'address': 'asfge',
                 'email': 'ewf',
                 'password': 'asfge'
                 }).json())
a = get('http://localhost:8080/api/v2/users').json()
print(a)
print(delete(f'http://localhost:8080/api/v2/users/{a["user"][-1]["id"]}').json())
print(get('http://localhost:8080/api/v2/users').json())
print(get('http://localhost:8080/api/v2/users/rgmjk').json())
print(post('http://localhost:8080/api/v2/users',
           json={'surname': 'asfge',
                 'name': 'asfge',
                 'age': 11,
                 'position': 'asfge',
                 'city_from': 'asfge',
                 'speciality': 'asfge',
                 'address': 'asfge',
                 }).json())