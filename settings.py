import re
import email
from email import policy
import imaplib

connected_clients = []

class Mail:
    def __init__(self, secure_id):
        self.host = "mail.univ-rouen.fr"
        self.folders = []
        self.secure_id = secure_id

    def login(self, username, password):
        self.client = imaplib.IMAP4_SSL(self.host)

        try :
            self.client.login(username, password)
        except Exception as e:
            return "Votre nom d'utilisateur ou mot de passe est incorrect"

        self.username = username
        self.password = password
        connected_clients.append(self)
        status, folders_data = self.client.list()

        for data in folders_data:
            folders_name = re.search(r'"/" ([0[a-zA-Z0-9]+$)', data.decode())
            self.folders.append(folders_name.group(1))
        return False

    def logout(self):
        self.client.logout()
        connected_clients.remove(self)

    def parse(self, id):
        typ, msg_data = self.client.fetch(id, '(RFC822)')
        for part in msg_data:
            if isinstance(part, tuple):
                mail = email.message_from_bytes(part[1], policy=policy.default)
                return mail

    def show(self, folder, filter="RECENT"):
        status, data = self.client.select(folder)

        try:
            status, data = self.client.search(None, f"({filter})")
        except Exception as e:
            return [False, None, "Boite mail ou filtre incorrect"]

        id_list = data[0].decode()
        if not id_list:
            return [False, None, "Aucun mail n'a été trouvé"]
        return [True, id_list.split(" "), None]
