from requests import delete, get, put, post


print(get('http://localhost:8080/api/v2/jobs').json())
print(get('http://localhost:8080/api/v2/jobs/1').json())
print(post('http://localhost:8080/api/v2/jobs',
           json={'team_leader': 1,
                 'job': 'wefew',
                 'work_size': 22,
                 'collaborators': 'wefew',
                 'start_date': '2000',
                 'end_date': '2001',
                 'is_finished': True
                 }).json())
a = get('http://localhost:8080/api/v2/jobs').json()
print(a)
print(delete(f'http://localhost:8080/api/v2/jobs/{a["jobs"][-1]["id"]}').json())
print(get('http://localhost:8080/api/v2/jobs').json())
print(get('http://localhost:8080/api/v2/jobs/rgmjk').json())
print(post('http://localhost:8080/api/v2/jobs',
           json={'team_leader': 1,
                 'job': 'wefew',
                 'work_size': 22,
                 'collaborators': 'wefew',
                 'start_date': '2000'
                 }).json())