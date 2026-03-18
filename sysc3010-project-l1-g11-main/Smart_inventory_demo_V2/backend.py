import pyrebase
import time
import json
import os
import re
from uuid import uuid4
from datetime import datetime
import coloredlogs, logging
import traceback
from picamera2 import Picamera2

logger = logging.getLogger("__sysc3010__")
coloredlogs.install(level='DEBUG', logger=logger)

class Backend():
    def __init__(self, config, email=None, firstname=None, lastname=None, fakeid: int = None):
        self._firebase = pyrebase.initialize_app(config)
        self._db = self._firebase.database()
        self._fakeid = '' if fakeid is None else str(fakeid)
        self.__load_user(email, firstname, lastname)
        self.__load_device_info()
        self._camera = None

        def get_camera(self):
            if self._camera is None:
                self._camera = Picamera2()
            return self._camera

    def __get_device_info(self, device_id):
        logger.debug(f"Retrieving device info for: {device_id}")
        device_info = dict()
        try:
            device_info = {**self._db.child('devices').child(device_id).child('device_info').get().val()}
        except Exception as e:
            logger.error(f"Device {device_id} does not exist in the database.")
        return device_info

    def __get_device_owner_id(self, device_id):
        logger.debug(f"Retrieving device owner id.")
        owner_id = ""
        try:
            owner_id = self._db.child('devices').child(device_id).child('device_info').child('owner').get().val()
        except Exception as e:
            logger.error(f"Error occured while retriving owner id for device {device_id}. {e}")
        return owner_id

    def __load_device_info(self):
        logger.debug("Loading device information.")
        if not os.path.isfile('/proc/cpuinfo'):
            logger.debug("File is not being executed from a RPi. Device info is an empty dict.")
            self._device_info = {}
            return
        try:
            data = dict()
            keywords = ['Serial','Hardware','Revision','Model']
            with open('/proc/cpuinfo', 'r') as f:
                for line in f:
                    for keyword in keywords :
                        lines = line.split(': ')
                        if re.sub(r'\s','',lines[0]) == keyword:
                            data[keyword.lower()] = re.sub(r'\s','',lines[1])
                f.close()
            if not "Raspberry" in data['model']:
                logger.debug("File is not being executed from a RPi. Device info is an empty dict.")
                self._device_info = {}
                return
            if len(data) >= 3:    #JRG changed from 3 in W2024 since RPi now returning 4 fields
                data['serial']+=self._fakeid
                rpiserial=data['serial']
                data['owner'] = self._user['id']
                data['authorized_users'] = [self._user['id'] ]
                try:
                    if rpiserial in self._db.child('devices').shallow().get().val():
                        logger.debug(f"Device already exist on database. _device_info is: {data}")
                        self._device_info = data
                        return
                except Exception as e:
                    logger.debug("Problems querying database: it was probably empty. We will create a new device entry.")
                # Create the new device entry on database and set initial values.
                self._db.child('devices').child(rpiserial).child('device_info').set(data)
                ledids=[ledn+1 for ledn in range(64)]
                brightled = [10,11,14,15,18,19,22,23,33,40,42,47,51,52,53,54]
                brightcolor=[random.randint(50,255),random.randint(50,255),random.randint(50,255)]
                for ledn in ledids:
                    ledcolor = [0,0,0] if ledn not in brightled else brightcolor
                    self._db.child('devices').child(rpiserial).child('leds').child(ledn).set(ledcolor)
                self.__led_last_update(rpiserial)
                self._device_info = data
                logger.debug(f"New device was added to the database. _device_info: {data}")
        except Exception as e:
            logger.error(f"Something went wrong when registering device. {e}")
            logger.error(traceback.format_exc())

    def __load_user(self, email=None, firstname=None, lastname=None):
        logger.debug(f"Loading user data.")
        if email is None:
            email = input("Enter your email: ")
        if firstname is None:
            firstname = input("Enter your first name: ")
        if lastname is None:
            lastname = input("Enter your last name: ")
        users=self._db.child('users').get()
        if users.val() is not None:
            user = [user for user in users if email == user.val()['email']]
            if user == []:
                self._user = self.__register_new_user(email, firstname, lastname)
            else:
                self._user = dict(
                    id=user[0].key(),
                    email=user[0].val()['email'],
                    firstname=user[0].val()['firstname'],
                    lastname=user[0].val()['lastname'],
                    )
        else:
            self._user = self.__register_new_user(email, firstname, lastname)
        logger.debug(f"User loaded: {self._user}")
    
    def __register_new_user(self, email, firstname, lastname):
        logger.debug(f"Registering new user.")
        id = str(uuid4())
        try:
            self._db.child('users').child(id).set(
                dict(
                    email= email,
                    firstname= firstname,
                    lastname= lastname
                    )
                )
            logger.debug(f"Registered new user: {firstname} {lastname}, {email}.")
            return dict(id=id, email=email, firstname=firstname, lastname=lastname)
        except Exception as e:
            raise ConnectionError("Error registering new user. {e}")

    def capture_image(self, filename="image.jpg"):
        try:
            self._camera.start()
            time.sleep(2)  # Give the camera time to adjust
            self._camera.capture_file(filename)
            self._camera.stop()
            logger.debug(f"Image captured and saved as {filename}.")
            return filename
        except Exception as e:
            logger.error(f"Error capturing image: {e}")
            return None

    def upload_image(self, filename, device_id):
        if self._device_info == {}:
            logger.info("Image upload should be done from a registered device.")
            return
        try:
            storage = self._firebase.storage()
            cloud_path = f"images/{device_id}/{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
            storage.child(cloud_path).put(filename)
            logger.debug(f"Image uploaded to {cloud_path}.")
            return cloud_path
        except Exception as e:
            logger.error(f"Error uploading image: {e}")
            return None

    def add_authorized_users(self, email):
        logger.debug("Adding authorized user.")
        if self._device_info == {}:
            logger.info("Adding authorized users should be done from the raspberry pi with a registered device")
            return
        valid_user = False
        users=self._db.child('users').get()
        for user in users:
            if email in user.val()['email']:
                valid_user = True
                userid = user.key()
        if valid_user:
            authorized_users = self._db.child('devices').child(self._device_info['serial']).child('device_info').child('authorized_users').get()
            if userid in authorized_users.val():
                logger.debug(f"{email} already is an authorized user for this device.")
            else:
                authorizedlist = authorized_users.val()
                authorizedlist.append(userid)
                try:
                    self._db.child('devices').child(self._device_info['serial']).child('device_info').child('authorized_users').set(authorizedlist)
                    self._device_info['authorized_users'] = authorizedlist
                    logger.debug(f"{email} added to list of authorized users for this device.")
                except Exception as e:
                    logger.error(f"Something went wrong authorizing user: {e}.")                
        else:
            logger.warning(f"User {email} does not exist in database. User was not authorized.")
            
    def get_device_id(self):
        if self.is_device():
            return self._device_info['serial']
        else:
            return None

    def get_device_owner(self, device_id):
        logger.debug(f"Retrieving device owner for device {device_id}.")
        device_owner = ""
        try:
            owner_id = self._db.child('devices').child(device_id).child('device_info').child('owner').get().val()
            user_info = {**self._db.child('users').child(owner_id).get().val()}
            device_owner = f"{user_info['firstname'].capitalize()} {user_info['lastname'].capitalize()}"
        except Exception as e:
            logger.error(f"Error occured while retriving owner for device {device_id}. {e}")
        return device_owner
    
    def get_my_devices(self):
        logger.debug("Retrieving devices that I am authorized to control.")
        self._my_device_ids = []
        devices = self._db.child('devices').get()

        if devices.val():  # Ensure devices exist
            self._my_device_ids = [
                device.key() for device in devices
                if 'device_info' in device.val() and
                'authorized_users' in device.val()['device_info'] and
                self._user['id'] in device.val()['device_info']['authorized_users']
            ]

        if not self._my_device_ids:
            logger.warning("No authorized devices found.")
            return []  # Always return a list, never None

        return self._my_device_ids


    def is_device(self):
        if self._device_info == {}:
            return False
        else:
            return True

    def remove_authorized_users(self,email):
        logger.debug(f"Removing user from authorized users: {email}")
        if self._device_info == {}:
            logger.info("Removing authorized users should be done from the raspberry pi with a registered device.")
            return
        valid_user = False
        users=self._db.child('users').get()
        for user in users:
            if email in user.val()['email']:
                valid_user = True
                userid = user.key()
        if valid_user:
            authorized_users = self._db.child('devices').child(self._device_info['serial']).child('device_info').child('authorized_users').get()
            authorizedlist = authorized_users.val()
            if userid in authorizedlist:
                try:
                    authorizedlist.remove(userid)
                    self._db.child('devices').child(self._device_info['serial']).child('device_info').child('authorized_users').set(authorizedlist)
                    self._device_info['authorized_users'] = authorizedlist
                    logger.debug(f"{email} removed to list of authorized users")
                except Exception as e:
                    logger.error(f"Something went wrong authorizing user: {e}.")
        else:
            logger.warning(f"User {email} does not exist in database.")

    def remove_device(self):
        try:
            logger.debug("Removing device from db.")
            self._db.child('devices').child(self._device_info['serial']).remove()
        except Exception as e:
            logger.error(f"Problems removing device from db. {e}")
