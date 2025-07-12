class UsersRepository:
    def __init__(self):
        self.users = [
            {'name': 'tota', 'password': sha256(b'password123').hexdigest()},
            {'name': 'alice', 'password': sha256(b'donthackme').hexdigest()},
            {'name': 'bob',   'password': sha256(b'qwerty').hexdigest()},
        ]

    def get_user(self, name, password):
        hashed = sha256(password.encode()).hexdigest()
        for user in self.users:
            if user['name'] == name and user['password'] == hashed:
                return user
