from modules.tool_call.common import GenericTool

class FakeWeather(GenericTool):
	tool_name = "fake weather"
	properties = {"default": False}

	def get_current_temperature(self, location):
		"""Get current temperature at a location."""
		res = {"temperature": 26.1, "location": "San Francisco, CA, USA", "unit": "celsius"}
		return res

	def get_temperature_date(self, location, date):
		"""Get temperature at a location and date."""
		res = {"temperature": 25.9, "location": "San Francisco, CA, USA", "date": "2024-10-01", "unit": "celsius"}
		return res