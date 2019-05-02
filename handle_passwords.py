import os
import hashlib, uuid

users_login = {}

def load_file(path):    # returns array of strings representing lines
    ans = []
    if os.path.exists(path):
        with open(path, 'r') as file:
            for line in file:
                ans += [line.replace('\n', '')]

    return ans

def parse_users(users):
    users_data = {}
    for user in users:
        splitted = user.split(':')
        username = splitted[0]
        password = splitted[1]
        salt = splitted[2].encode('ISO-8859-1')
        users_data[username] = (password, salt)
    return users_data

def init(path):
    global users_login
    lines = load_file(path)
    users_login = parse_users(lines)

def save_users(users_data, path):
    file = open(path, 'w')
    lines = ''
    for u in users_data:
        (password,salt) = users_data[u] 
        lines += u+":"+password+":"+salt.decode('ISO-8859-1')+"\n"
    file.write(lines)
        

def hash_pass(password):
    password = password.encode('ISO-8859-1')
    salt = uuid.uuid4().bytes
    hashed_password = hashlib.sha512(password + salt).hexdigest()
    return (hashed_password, salt)

def hash_pass_with_salt(password, salt):
    password = password.encode('ISO-8859-1')
    hashed = hashlib.sha512(password+salt).hexdigest()
    return hashed

def add_user(username, password):
    if username in users_login:
        print("Username already exists")
        return
    else:
        users_login[username] = hash_pass(password)
        save_users(users_login, './passwords.txt')

def validate_user(username, password):
    if not username in users_login:
        return False
    else:
        p, salt = users_login[username]
        if(hash_pass_with_salt(password, salt) == p):
            return True
        else:
            return False
        

