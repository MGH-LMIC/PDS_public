

class ConfigConstants(object):
	WEB_SERVER_IP_ADDRESS = "0.0.0.0"
	API_SERVER_IP_ADDRESS = "127.0.0.1"

	@classmethod
	def set_api_server_ip_address(cls, address):
		if address:
			prefix = "http://"
			if address.startswith(prefix):
				cls.API_SERVER_IP_ADDRESS = address
			else:
				cls.API_SERVER_IP_ADDRESS = prefix + address
		else:
			cls.API_SERVER_IP_ADDRESS = "http://127.0.0.1:5001"

		print("API server ip is set to {}".format(cls.API_SERVER_IP_ADDRESS))


class HtmlConstants(object):
	HTML_MAIN_PATH_AND_FILE_NAME = "main.html"