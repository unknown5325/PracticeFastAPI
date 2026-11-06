import pandas as pd
import hashlib
import os


class Functions:

    def getHexPassword(self, password):
        hex_obj = hashlib.sha256(password.encode('utf-8'))
        hex_dig = hex_obj.hexdigest()
        return hex_dig

    def writeCharacteristics(self, name, email, password):
        hexDig = self.getHexPassword(password)
        df = pd.DataFrame({'Name' : name, 'Email' : email, 'Password' : password, 'HashPassword' : hexDig}, index=[0])
        df.to_csv('UserList.csv', index=False,  mode="a", sep=",", header=not os.path.isfile("UserList.csv"))

    def getCollumn():
        df = pd.read_csv('UserList.csv')
        nameCollumn = df['Name']
        emailCollumn = df['Email']
        passwordCollumn = df['Password']
        hexPasswordCollumn = df['HashPassword']
        return nameCollumn, emailCollumn, passwordCollumn, hexPasswordCollumn