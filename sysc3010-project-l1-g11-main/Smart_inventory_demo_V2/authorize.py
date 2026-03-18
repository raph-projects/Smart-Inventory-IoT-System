from backend import Backend
from mydbconfig import *
backend = Backend(config, email, firstname, lastname)

# Add each of your teammates'
backend.add_authorized_users('kumudbansal@cmail.carleton.ca' )
backend.add_authorized_users('adeljaber@cmail.carleton.ca' )
backend.add_authorized_users('Abderrezakfoura@cmail.carleton.ca' )
backend.add_authorized_users('raphael@cmail.carleton.ca')
