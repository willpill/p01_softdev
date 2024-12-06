'''
Team livecrylove: Princeden, Sascha, Jackie, Yinwei
SoftDev
P01: ArRESTed Development - Zenith
2024-12-5
Time Spent:
'''
# Inspired by Team Bareustoph 
import os
PATH = "app\keys"
# return a key if file is found, otherwise returns "EMPTY_KEY"
def get_key(key_name):
    key_path = os.path.join(PATH, key_name)
    # print(key_path)
    try:
        with open(key_path, 'r') as f:
            return f.read().strip()  
    except FileNotFoundError: 
        print(f"File not found exception for {key_name}.")
        return "EMPTY_KEY"


