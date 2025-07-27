from modules.tool_call.common import GenericTool

class FakeWeather(GenericTool):
	tool_name = "fake weather"
	properties = {"default": False, "priority": 10}

	def get_current_temperature(self, location: str, unit: str = "celsius") -> str:
		"""Get current temperature at a location."""
		res = {"temperature": 26.1, "location": "San Francisco, CA, USA", "unit": "celsius"}
		return res

	def get_temperature_date(self, location, date, unit="celsius"):
		"""Get temperature at a location and date."""
		res = {"temperature": 25.9, "location": "San Francisco, CA, USA", "date": "2024-10-01", "unit": "celsius"}
		return res

	def get_weather_forecast(self, location, days=5):
		"""Get 5-day weather forecast for a location (stubbed)."""
		forecast = [
			{"day": "2024-10-01", "temp": 26.0},
			{"day": "2024-10-02", "temp": 27.3}
		]
		return {
			"forecast": forecast[:days],
			"location": location,
			"unit": "celsius"
		}

	def get_humidity(self, location):
		"""Get current humidity percentage."""
		return {"humidity": 65, "unit": "%", "location": location}

	def get_wind_speed(self, location):
		"""Get current wind speed in km/h."""
		return {"wind_speed": 18.2, "unit": "km/h", "location": location}

	def get_precipitation_probability(self, location, date):
		"""Get precipitation chance for a specific date."""
		return {
			"precipitation_chance": 30,
			"date": date,
			"unit": "%",
			"location": location
		}
